from pathlib import Path


RULES_DIR = Path(__file__).parent / "rules"


def carregar_regras() -> str:
    """
    Carrega todas as regras de comportamento do agente.
    """

    regras = []

    for arquivo in sorted(RULES_DIR.glob("*.txt")):
        regras.append(arquivo.read_text(encoding="utf-8"))

    return "\n\n".join(regras)