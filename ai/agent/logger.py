import logging
from pathlib import Path


LOG_FILE = Path(__file__).resolve().parents[2] / "ai_debug.log"


logger = logging.getLogger("crud_ai")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE,encoding="utf-8")

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def debug(mensagem: str) -> None:
    logger.debug(mensagem)


def info(mensagem: str) -> None:
    logger.info(mensagem)


def warning(mensagem: str) -> None:
    logger.warning(mensagem)


def error(mensagem: str) -> None:
    logger.error(mensagem)


def separador(titulo: str = "") -> None:
    linha = "=" * 70

    if titulo:
        logger.debug(
            f"{linha}\n"
            f"{titulo}\n"
            f"{linha}"
        )
    else:
        logger.debug(linha)