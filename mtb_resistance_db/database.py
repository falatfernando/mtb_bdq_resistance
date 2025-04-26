from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from pathlib import Path

def setup_environment():
    project_root = Path(__file__).resolve().parent.parent

    paths = {
        "PROJECT_ROOT": project_root,
        "DB_PATH": project_root / "mtb_resistance_db" / "mtb_warehouse.db",
        "RAW_DATA_DIR": project_root / "mtb_resistance_db" / "raw",
    }
    return paths

paths = setup_environment()
db_path = paths['DB_PATH']

engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False) # Tuned for bulk loads
session = Session()

# Create tables
Base.metadata.create_all(engine)