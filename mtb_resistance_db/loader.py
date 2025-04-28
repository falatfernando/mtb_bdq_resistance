"""
loader.py: Auto-drop indexes, bulk‐load staging Parquet → SQLite, then rebuild indexes,
with handling for stray Parquet files not in ORM schema.
"""
import sqlite3
import pandas as pd
from pathlib import Path
from database import paths
from models import Base

# Size of each executemany batch
BATCH_SIZE = 100_000

# Derive valid table names from ORM metadata
VALID_TABLES = set(Base.metadata.tables.keys())


def set_pragmas(conn):
    """Tune SQLite for high-speed bulk writes."""
    cur = conn.cursor()
    for k, v in [
        ("journal_mode", "MEMORY"),      # no durable journal file writes
        ("synchronous", "OFF"),          # no fsync per txn
        ("locking_mode", "EXCLUSIVE"),   # hold lock entire load
        ("temp_store", "MEMORY"),        # tmp tables in RAM
        ("page_size", "16384"),          # 16 KiB pages
        ("cache_size", "-20000"),        # ≈ 320 MiB cache
        ("foreign_keys", "OFF"),         # skip FK checks
    ]:
        cur.execute(f"PRAGMA {k} = {v};")
    conn.commit()


def gather_indexes(conn, table):
    """
    Return list of (name, sql) for all non-auto indexes on `table`.
    We filter sql NOT NULL to skip implicit PK indexes.
    """
    cur = conn.cursor()
    cur.execute("""
      SELECT name, sql
        FROM sqlite_master
       WHERE type='index'
         AND tbl_name=?
         AND sql NOT NULL;
    """, (table,))
    return cur.fetchall()


def drop_indexes(conn, index_list):
    """DROP each index by name."""
    cur = conn.cursor()
    for name, _ in index_list:
        cur.execute(f"DROP INDEX IF EXISTS \"{name}\";")
    conn.commit()


def recreate_indexes(conn, index_list):
    """Re-run each saved CREATE INDEX statement."""
    cur = conn.cursor()
    for _, sql in index_list:
        cur.execute(sql)
    conn.commit()


def load_table(conn, pq_path):
    """Chunked bulk‐insert of one parquet file into its matching table."""
    table = pq_path.stem
    # Read parquet fully; rows × small schema fits in RAM
    df = pd.read_parquet(pq_path)
    cols = list(df.columns)
    placeholders = ",".join("?" for _ in cols)
    sql = f"INSERT OR IGNORE INTO {table} ({','.join(cols)}) VALUES ({placeholders});"

    cur = conn.cursor()
    batch = []
    for row in df.itertuples(index=False, name=None):
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            cur.executemany(sql, batch)
            batch.clear()
    if batch:
        cur.executemany(sql, batch)
    conn.commit()


def main():
    db_file = Path(paths['DB_PATH'])
    staging = Path(paths['STAGING_DATA_DIR'])
    conn = sqlite3.connect(str(db_file))
    set_pragmas(conn)

    for pq in staging.glob("*.parquet"):
        tbl = pq.stem
        if tbl not in VALID_TABLES:
            print(f"Skipped {tbl}: not in ORM schema.")
            continue

        print(f"\n-- Loading table: {tbl} --")
        # 1) capture & drop indexes
        idxs = gather_indexes(conn, tbl)
        if idxs:
            print(f"Dropping {len(idxs)} indexes on {tbl}…")
            drop_indexes(conn, idxs)

        # 2) load data
        size_mb = pq.stat().st_size / 1e6
        print(f"Loading {tbl} ({size_mb:.1f} MB)…")
        load_table(conn, pq)

        # 3) recreate indexes
        if idxs:
            print(f"Rebuilding indexes on {tbl}…")
            recreate_indexes(conn, idxs)

    conn.close()
    print("\nAll tables processed.")

if __name__ == "__main__":
    main()
