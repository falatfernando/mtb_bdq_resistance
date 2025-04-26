from pathlib import Path

# Set project root manually — two levels up from this config.py file
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Set the path to the database inside "mtb_resistance_db"
DB_PATH = PROJECT_ROOT / "mtb_resistance_db" / "mtb_resistance.db"