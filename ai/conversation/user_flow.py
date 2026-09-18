from ai.api.api_client import (
    criar_usuario,
    atualizar_usuario,
    deletar_usuario
)

from ai.conversation.confirmation import (
    formatar_confirmacao
)


def descobrir_campo_faltante(usuario: dict) -> str | None:
    if not usuario.get("nome"):
        return "nome"

    idade = usuario.get("idade")

    if idade is None or idade <= 0:
        return "idade"

    if not usuario.get("cidade"):
        return "cidade"

    return None


def pergunta_campo(campo: str) -> str:
    perguntas = {
        "nome": "Qual o nome?",
        "idade": "Qual a idade?",
        "cidade": "Qual a cidade?"
    }

    return perguntas[campo]


def preparar_criacao(
    usuario: dict
) -> tuple[str, dict | None]:
    campo_faltante = descobrir_campo_faltante(usuario)

    if campo_faltante:
        return pergunta_campo(campo_faltante), None

    operacao = {
        "nome": "criar_usuario",
        "argumentos": {
            "usuario": usuario.copy()
        }
    }

    return formatar_confirmacao(usuario), operacao


def preparar_atualizacao(
    usuario_id: int,
    dados: dict
) -> tuple[str, dict]:
    operacao = {
        "nome": "atualizar_usuario",
        "argumentos": {
            "usuario_id": usuario_id,
            "dados": dados.copy()
        }
    }

    return (
        formatar_confirmacao(dados),
        operacao
    )


def preparar_exclusao(
    usuario: dict
) -> tuple[str, dict]:
    usuario_id = usuario["id"]

    operacao = {
        "nome": "deletar_usuario",
        "argumentos": {
            "usuario_id": usuario_id
        }
    }

    resposta = (
        f"ID: {usuario['id']}\n"
        f"Nome: {usuario['nome']}\n"
        f"Idade: {usuario['idade']}\n"
        f"Cidade: {usuario['cidade']}"
    )

    if usuario.get("email"):
        resposta += f"\nEmail: {usuario['email']}"

    resposta += "\n\nConfirmar?"

    return resposta, operacao


def executar_operacao(operacao: dict) -> str:
    nome = operacao["nome"]
    args = operacao["argumentos"]

    if nome == "criar_usuario":
        criar_usuario(args["usuario"])
        return "Usuário criado."

    if nome == "atualizar_usuario":
        atualizar_usuario(
            args["usuario_id"],
            args["dados"]
        )
        return "Usuário atualizado."

    if nome == "deletar_usuario":
        deletar_usuario(
            args["usuario_id"]
        )
        return "Usuário excluído."

    raise ValueError(
        f"Operação desconhecida: {nome}"
    )