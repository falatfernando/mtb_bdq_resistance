from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import DDL
from models import Base
from pathlib import Path

def setup_environment():
    project_root = Path(__file__).resolve().parent.parent

    paths = {
        "PROJECT_ROOT": project_root,
        "DB_PATH": project_root / "mtb_resistance_db" / "mtb_warehouse.db",
        "RAW_DATA_DIR": project_root / "mtb_resistance_db" / "raw",
        "STAGING_DATA_DIR": project_root / "mtb_resistance_db" / "staging",
    }
    return paths

paths = setup_environment()
db_path = paths['DB_PATH']

# Configure engine with performance optimizations
engine = create_engine(
    f'sqlite:///{db_path}',
    connect_args={'timeout': 30},  # Increase timeout for bulk operations
    echo=False  # Disable logging for faster inserts
)

# Add SQLite performance pragmas
@event.listens_for(engine, "connect")
def set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA mmap_size = 268435456")  # 256MB memory mapping
    cursor.execute("PRAGMA journal_mode = MEMORY")  # Faster than WAL for bulk loads
    cursor.execute("PRAGMA synchronous = OFF")      # Dangerous but fast
    cursor.execute("PRAGMA cache_size = -10000")    # 10MB cache
    cursor.execute("PRAGMA temp_store = MEMORY")    # Keep temp tables in RAM
    cursor.close()

# Configure session for bulk operations
Session = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    twophase=False  # Disable two-phase commit for single DB
)
session = Session()

# Create tables
Base.metadata.create_all(engine)