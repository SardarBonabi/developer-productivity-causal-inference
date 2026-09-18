"""Representative PostgreSQL page persistence. Research under review.

Full code/data proprietary. The private runtime supplies a dedicated psycopg-style
connection per worker; credentials, migrations and connection factory are absent.
"""
import json

from collection_contracts import Checkpoint, ConcurrentUpdate


class PostgresStore:
    def __init__(self, connection):
        self.connection = connection

    def load(self, job):
        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                cursor.execute(
                    'SELECT next_cursor, complete, revision FROM collection_checkpoint '
                    'WHERE project=%s AND snapshot=%s AND stage=%s AND partition_key=%s',
                    job.key,
                )
                row = cursor.fetchone()
        return Checkpoint(*row) if row else Checkpoint()

    def commit_page(self, job, previous, page, records):
        """A page and its checkpoint either commit together or roll back together.

        Locking plus revision checks rejects stale competing workers. The record
        primary key permits safe replay; it does not claim exactly-once fetching.
        """
        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO collection_checkpoint '
                    '(project, snapshot, stage, partition_key) VALUES (%s,%s,%s,%s) '
                    'ON CONFLICT DO NOTHING', job.key,
                )
                cursor.execute(
                    'SELECT next_cursor, complete, revision FROM collection_checkpoint '
                    'WHERE project=%s AND snapshot=%s AND stage=%s AND partition_key=%s '
                    'FOR UPDATE', job.key,
                )
                if Checkpoint(*cursor.fetchone()) != previous:
                    raise ConcurrentUpdate()
                cursor.executemany(
                    'INSERT INTO collection_record '
                    '(project, snapshot, stage, record_key, payload) VALUES (%s,%s,%s,%s,%s::jsonb) '
                    'ON CONFLICT (project, snapshot, stage, record_key) DO UPDATE '
                    'SET payload=EXCLUDED.payload',
                    [(job.project, job.snapshot, job.stage, record.key,
                      json.dumps(record.values, allow_nan=False)) for record in records],
                )
                cursor.execute(
                    'UPDATE collection_checkpoint SET next_cursor=%s, complete=%s, '
                    'revision=revision+1, updated_at=CURRENT_TIMESTAMP '
                    'WHERE project=%s AND snapshot=%s AND stage=%s AND partition_key=%s',
                    (page.next_cursor, page.complete, *job.key),
                )
        return Checkpoint(page.next_cursor, page.complete, previous.revision + 1)
