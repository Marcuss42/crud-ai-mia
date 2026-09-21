import requests

from ai.config.config import API_URL


def criar_usuario(usuario: dict) -> dict:
    """
    Cria usuário.
    Campos: nome obrigatório; idade obrigatória; cidade obrigatória; email opcional.
    Use somente dados fornecidos pelo usuário. Nunca invente valores.
    """
    response = requests.post(f"{API_URL}/usuarios", json=usuario)
    response.raise_for_status()
    return response.json()


def listar_usuarios(
    nome: str | None = None,
    cidade: str | None = None,
    idade: int | None = None,
    email: str | None = None
) -> list[dict]:
    """
    Lista usuários.
    nome/cidade/email: filtro exato, ignorando maiúsculas e acentos.
    idade: filtro exato.
    email=None: não filtra email.
    email="": somente usuários sem email.
    Não suporta comparação de idade, intervalos ou filtros aproximados.
    """
    params = {
        chave: valor
        for chave, valor in {
            "nome": nome,
            "cidade": cidade,
            "idade": idade,
            "email": email
        }.items()
        if valor is not None
    }

    response = requests.get(f"{API_URL}/usuarios", params=params)
    response.raise_for_status()
    return response.json()


def contar_usuarios(
    nome: str | None = None,
    cidade: str | None = None,
    idade: int | None = None,
    email: str | None = None
) -> int:
    """
    Conta usuários que correspondem aos filtros.
    nome/cidade/email: filtro exato, ignorando maiúsculas e acentos.
    idade: filtro exato.
    email=None: não filtra email.
    email="": somente usuários sem email.
    Não suporta comparação de idade, intervalos ou filtros aproximados.
    """
    params = {
        chave: valor
        for chave, valor in {
            "nome": nome,
            "cidade": cidade,
            "idade": idade,
            "email": email
        }.items()
        if valor is not None
    }

    response = requests.get(f"{API_URL}/usuarios/contagem", params=params)
    response.raise_for_status()
    return response.json()["quantidade"]


def buscar_usuario(usuario_id: int) -> dict:
    """
    Busca um usuário pelo ID exato.
    """
    response = requests.get(f"{API_URL}/usuarios/{usuario_id}")
    response.raise_for_status()
    return response.json()


def atualizar_usuario(usuario_id: int, dados: dict) -> dict:
    """
    Atualiza usuário existente pelo ID.
    dados contém somente os campos a alterar.
    Nunca invente valores.
    """
    response = requests.put(f"{API_URL}/usuarios/{usuario_id}", json=dados)
    response.raise_for_status()
    return response.json()


def deletar_usuario(usuario_id: int) -> dict:
    """
    Exclui usuário existente pelo ID.
    """
    response = requests.delete(f"{API_URL}/usuarios/{usuario_id}")
    response.raise_for_status()
    return response.json()