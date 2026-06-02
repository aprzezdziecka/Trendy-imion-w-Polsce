import logging
from datetime import datetime
from data_ingestion import load_csv, load_bdl

logger = logging.getLogger(__name__)


def refresh_data():
    logger.info(f"=== START SYNCHRONIZACJI DANYCH: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    try:
        logger.info("Ładowanie danych USC z CSV...")
        load_csv.run()
        logger.info("Ładowanie danych GUS BDL API...")
        load_bdl.run()
        logger.info("=== SYNCHRONIZACJA ZAKOŃCZONA POPRAWNIE ===")

    except Exception as e:
        logger.exception(f"Błąd podczas synchronizacji danych: {e}")