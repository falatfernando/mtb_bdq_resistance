# setup_project.py
import sys
from pathlib import Path

def setup_environment():
    """
    Sets up the Python environment:
    - Ensures the main project folders are in sys.path
    - Returns key paths for database and raw data
    """
    # Locate project root
    project_root = Path(__file__).resolve().parent.parent

    # Add 'mtb_resistance_db' and 'notebooks' to sys.path
    sys.path.append(str(project_root / "mtb_resistance_db"))
    sys.path.append(str(project_root / "notebooks"))

    # Define useful paths
    paths = {
        "PROJECT_ROOT": project_root,
        "DB_PATH": project_root / "mtb_resistance_db" / "mtb_warehouse.db",
        "RAW_DATA_DIR": project_root / "mtb_resistance_db" / "raw",
    }

    print("✅ Environment configured successfully!")
    return paths
