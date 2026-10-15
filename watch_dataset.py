
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from document_loader import DATASET_DIR
from build_vector_store import build_vector_store
from sync_excel_to_postgres import sync_data
from ingest_updates import ingest_updates

DOCUMENT_EXTENSIONS = {".txt", ".docx"}
EXCEL_EXTENSIONS = {".xlsx"}
DEBOUNCE_SECONDS = 3
RETRY_ATTEMPTS = 4
RETRY_DELAY_SECONDS = 2


class DatasetChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.timer = None
        self.timer_lock = threading.Lock()
        self.work_lock = threading.Lock()
        self.pending_documents = False
        self.pending_excel = False
        self.pending_updates = False

    def on_any_event(self, event):
        if event.is_directory:
            return

        if event.event_type not in {
            "created", "modified", "deleted", "moved"
        }:
            return

        paths = [event.src_path]
        if event.event_type == "moved":
            paths.append(event.dest_path)

        extensions = {Path(path).suffix.lower() for path in paths}

        if not extensions.intersection(
            DOCUMENT_EXTENSIONS | EXCEL_EXTENSIONS
        ):
            return

        is_update_file = any(
            Path(path).suffix.lower() == ".txt"
            and Path(path).parent.resolve()
            == (Path(DATASET_DIR) / "updates").resolve()
            for path in paths
        )

        with self.timer_lock:
            self.pending_documents |= bool(
                extensions & DOCUMENT_EXTENSIONS
            )
            self.pending_excel |= bool(
                extensions & EXCEL_EXTENSIONS
            )
            self.pending_updates |= is_update_file

            if self.timer is not None:
                self.timer.cancel()

            self.timer = threading.Timer(
                DEBOUNCE_SECONDS,
                self.process_changes
            )
            self.timer.daemon = True
            self.timer.start()

    def run_with_retry(self, operation, label):
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                operation()
                print(f"{label} completed successfully.")
                return True
            except PermissionError as error:
                print(
                    f"{label}: file locked "
                    f"(attempt {attempt}/{RETRY_ATTEMPTS})."
                )
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    print(f"{label} failed: {error}")
            except Exception as error:
                print(f"{label} failed: {error}")
                return False

        return False

    def process_changes(self):
        with self.timer_lock:
            documents_changed = self.pending_documents
            excel_changed = self.pending_excel
            updates_changed = self.pending_updates

            self.pending_documents = False
            self.pending_excel = False
            self.pending_updates = False
            self.timer = None

        with self.work_lock:
            if excel_changed:
                print("\nExcel changes detected. Syncing PostgreSQL...")
                self.run_with_retry(sync_data, "Excel sync")

            if updates_changed:
                print("\nUpdate text changed. Syncing PostgreSQL...")
                self.run_with_retry(ingest_updates, "Update ingestion")

            if documents_changed:
                print("\nDocument changes detected. Updating ChromaDB...")
                self.run_with_retry(
                    build_vector_store,
                    "Document indexing"
                )


if __name__ == "__main__":
    dataset_path = Path(DATASET_DIR)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {dataset_path}"
        )

    handler = DatasetChangeHandler()
    observer = Observer()
    observer.schedule(handler, str(dataset_path), recursive=True)
    observer.start()

    print(f"Watching dataset folder: {dataset_path}")
    print("Excel files → PostgreSQL")
    print("Update TXT files → PostgreSQL + ChromaDB")
    print("Other TXT/DOCX files → ChromaDB")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

        with handler.timer_lock:
            if handler.timer is not None:
                handler.timer.cancel()

        print("Stopping dataset watcher...")

    observer.join()
