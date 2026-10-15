
import os
from pathlib import Path
from datetime import datetime

import psycopg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
UPDATES_FOLDER = BASE_DIR / "dataset" / "updates"


def ingest_updates():
    load_dotenv(BASE_DIR / ".env")

    connection_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    if not all(connection_config.values()):
        raise ValueError("Check database settings in your .env file.")

    if not UPDATES_FOLDER.exists():
        raise FileNotFoundError(
            f"Updates folder not found: {UPDATES_FOLDER}"
        )

    with psycopg.connect(**connection_config) as connection:
        with connection.cursor() as cursor:
            for file_path in sorted(UPDATES_FOLDER.glob("*.txt")):
                content = file_path.read_text(encoding="utf-8")

                date_value = None
                submitted_by = None
                update_type = None

                for line in content.splitlines():
                    if line.startswith("Date:"):
                        date_value = datetime.strptime(
                            line.replace("Date:", "").strip(),
                            "%Y-%m-%d"
                        ).date()
                    elif line.startswith("From:"):
                        submitted_by = line.replace("From:", "").strip()
                    elif line.startswith("Type:"):
                        update_type = line.replace("Type:", "").strip()

                if date_value is None:
                    raise ValueError(
                        f"Missing or invalid Date in {file_path.name}"
                    )

                update_id = file_path.stem

                cursor.execute("""
                    INSERT INTO updates (
                        update_id, project_id, submitted_by,
                        update_date, update_type, source, content
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (update_id) DO UPDATE SET
                        submitted_by = EXCLUDED.submitted_by,
                        update_date = EXCLUDED.update_date,
                        update_type = EXCLUDED.update_type,
                        content = EXCLUDED.content
                """, (
                    update_id,
                    "P001",
                    submitted_by,
                    date_value,
                    update_type,
                    "TEXT_FILE",
                    content
                ))

                print(f"Processed: {file_path.name}")

    print("All project updates processed successfully.")


if __name__ == "__main__":
    ingest_updates()
