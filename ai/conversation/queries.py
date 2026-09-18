from ai.api.api_client import listar_usuarios, contar_usuarios


def formatar_usuarios(usuarios: list[dict]) -> str:
    if not usuarios:
        return "Não há usuários cadastrados."

    linhas = ["Usuários cadastrados:"]

    for usuario in usuarios:
        linha = (
            f"{usuario['id']}. "
            f"{usuario['nome']}, "
            f"{usuario['idade']} anos, "
            f"{usuario['cidade']}."
        )

        if usuario.get("email"):
            linha += f" Email: {usuario['email']}."

        linhas.append(linha)

    return "\n".join(linhas)


def consultar_usuarios(mensagem: str) -> str | None:
    texto = mensagem.lower()

    if any(termo in texto for termo in (
        "liste", "listar", "lista",
        "quais usuários", "quais usuarios",
        "mostre os usuários", "mostre os usuarios",
        "ver usuários", "ver usuarios"
    )):
        return formatar_usuarios(listar_usuarios())

    return None


def consultar_contagem(mensagem: str) -> str | None:
    texto = mensagem.lower()

    if not any(
        termo in texto
        for termo in ("quantos", "conte", "conta")
    ):
        return None

    nome = None

    if "nome joao" in texto or "nome joão" in texto:
        nome = "Joao"

    quantidade = contar_usuarios(nome=nome)

    if nome:
        return f"Existem {quantidade} usuários com o nome {nome}."

    return f"Existem {quantidade} usuários cadastrados."