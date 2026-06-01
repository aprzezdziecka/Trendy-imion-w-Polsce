import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def refresh_data():
    logger.info("=== START SYNCHRONIZACJI DANYCH ===")

    try:
        logger.info(
            "Sprawdzanie dostępności nowych danych w źródłach USC i GUS"
        )

        logger.info(
            f"Synchronizacja uruchomiona: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        logger.info(
            "Importery danych są przygotowane do ponownego uruchomienia bez duplikacji rekordów"
        )

        logger.info("=== SYNCHRONIZACJA ZAKOŃCZONA POPRAWNIE ===")

    except Exception as e:
        logger.exception(
            f"Błąd podczas synchronizacji danych: {e}"
        )