from ai.config.config import client, MODEL
from ai.agent.logger import error


def verificar_confirmacao(
    mensagem: str,
    historico: list[dict],
    operacao: dict | None = None
) -> bool | None:

    operacao_texto = ""

    if operacao:
        operacao_texto = (
            f"\nOperação que está sendo analisada:\n"
            f"{operacao['nome']}\n"
            f"Argumentos: {operacao['argumentos']}\n"
        )

    try:
        analise = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Determine se a ÚLTIMA mensagem do usuário "
                        "confirma ou cancela uma operação.\n\n"

                        "Use o histórico apenas para entender o contexto.\n"

                        "Responda SIM somente quando a última mensagem "
                        "confirmar explicitamente a operação.\n"

                        "Responda NAO somente quando a última mensagem "
                        "cancelar ou negar explicitamente a operação.\n"

                        "Responda NENHUM quando a mensagem não for "
                        "confirmação nem cancelamento.\n\n"

                        "Uma nova solicitação de operação, como "
                        "'excluir o 22', não é confirmação por si só.\n"

                        "Responda SOMENTE:\n"
                        "SIM\n"
                        "NAO\n"
                        "NENHUM"
                        f"{operacao_texto}"
                    )
                },
                *historico
            ],
            tool_choice="none",
            reasoning_effort="low",
            reasoning_format="hidden",
            max_completion_tokens=512
        )

    except Exception as erro:
        error(f"Erro ao analisar confirmação: {erro}")
        return None

    resposta = (
        analise.choices[0].message.content or ""
    ).strip().casefold()

    if resposta.startswith("sim"):
        return True

    if resposta.startswith("nao"):
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