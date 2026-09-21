CONFIRMACOES = {
    "sim",
    "s",
    "confirmo",
    "confirmar",
    "pode",
    "pode criar",
    "pode atualizar",
    "pode excluir",
    "pode deletar"
}

NEGACOES = {
    "não",
    "nao",
    "n",
    "cancela",
    "cancelar"
}


def verificar_confirmacao(mensagem: str) -> bool | None:
    texto = mensagem.strip().casefold()

    if texto in CONFIRMACOES:
        return True

    if texto in NEGACOES:
        return False

    return None


def formatar_confirmacao(dados: dict) -> str:
    linhas = []

    if "nome" in dados:
        linhas.append(f"Nome: {dados['nome']}")

    if "idade" in dados:
        linhas.append(f"Idade: {dados['idade']}")

    if "cidade" in dados:
        linhas.append(f"Cidade: {dados['cidade']}")

    if "email" in dados:
        linhas.append(f"Email: {dados['email']}")

    linhas.append("")
    linhas.append("Confirmar?")

    return "\n".join(linhas)