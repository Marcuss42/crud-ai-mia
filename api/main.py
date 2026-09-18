import json
import re
import unicodedata
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator


app = FastAPI(title="User API")
ARQUIVO_USUARIOS = Path("usuarios.json")


def normalizar_texto(valor: str) -> str:
    valor = " ".join(valor.strip().split())
    return valor.title()


def normalizar_nome(valor: str) -> str:
    return normalizar_texto(valor)


def normalizar_cidade(valor: str) -> str:
    return normalizar_texto(valor)


def normalizar_email(valor: str | None) -> str | None:
    if valor is None:
        return None

    valor = valor.strip().lower()
    return valor or None


class Usuario(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=1)
    idade: int = Field(gt=0)
    cidade: str = Field(min_length=1)
    email: str | None = None

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        return normalizar_nome(valor)

    @field_validator("cidade")
    @classmethod
    def validar_cidade(cls, valor: str) -> str:
        return normalizar_cidade(valor)

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str | None) -> str | None:
        return normalizar_email(valor)


class UsuarioResponse(Usuario):
    id: int


def carregar_usuarios() -> list[dict]:
    if not ARQUIVO_USUARIOS.exists():
        return []

    with ARQUIVO_USUARIOS.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_usuarios(usuarios: list[dict]) -> None:
    with ARQUIVO_USUARIOS.open("w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=4)


def obter_proximo_id(usuarios: list[dict]) -> int:
    if not usuarios:
        return 1

    return max(usuario["id"] for usuario in usuarios) + 1


def normalizar_usuario_existente(usuario: dict) -> dict:
    usuario["nome"] = normalizar_nome(usuario["nome"])
    usuario["cidade"] = normalizar_cidade(usuario["cidade"])
    usuario["email"] = normalizar_email(usuario.get("email"))
    return usuario


def normalizar_todos_usuarios(usuarios: list[dict]) -> list[dict]:
    alterado = False

    for usuario in usuarios:
        original = usuario.copy()
        normalizar_usuario_existente(usuario)

        if usuario != original:
            alterado = True

    if alterado:
        salvar_usuarios(usuarios)

    return usuarios


def remover_acentos(valor: str) -> str:
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", valor)
        if unicodedata.category(caractere) != "Mn"
    )


def comparar_texto(valor: str) -> str:
    return remover_acentos(valor).strip().casefold()


@app.post("/usuarios", response_model=UsuarioResponse, status_code=201)
def criar_usuario(usuario: Usuario) -> dict:
    usuarios = carregar_usuarios()

    novo_usuario = {
        "id": obter_proximo_id(usuarios),
        **usuario.model_dump()
    }

    usuarios.append(novo_usuario)
    salvar_usuarios(usuarios)

    return novo_usuario

@app.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(
    nome: str | None = Query(default=None),
    cidade: str | None = Query(default=None),
    idade: int | None = Query(default=None, gt=0),
    email: str | None = Query(default=None)
) -> list[dict]:
    usuarios = normalizar_todos_usuarios(carregar_usuarios())

    if nome:
        nome_busca = comparar_texto(nome)
        usuarios = [
            usuario for usuario in usuarios
            if comparar_texto(usuario["nome"]) == nome_busca
        ]

    if cidade:
        cidade_busca = comparar_texto(cidade)
        usuarios = [
            usuario for usuario in usuarios
            if comparar_texto(usuario["cidade"]) == cidade_busca
        ]

    if idade is not None:
        usuarios = [
            usuario for usuario in usuarios
            if usuario["idade"] == idade
        ]

    if email is not None:
        if email == "":
            usuarios = [
                usuario for usuario in usuarios
                if not usuario.get("email")
            ]
        else:
            email_busca = comparar_texto(email)
            usuarios = [
                usuario for usuario in usuarios
                if comparar_texto(
                    usuario.get("email") or ""
                ) == email_busca
            ]

    return usuarios


@app.get("/usuarios/contagem")
def contar_usuarios(
    nome: str | None = Query(default=None),
    cidade: str | None = Query(default=None),
    idade: int | None = Query(default=None, gt=0),
    email: str | None = Query(default=None)
) -> dict:
    usuarios = listar_usuarios(
        nome=nome,
        cidade=cidade,
        idade=idade,
        email=email
    )

    return {
        "quantidade": len(usuarios),
        "filtros": {
            "nome": nome,
            "cidade": cidade,
            "idade": idade,
            "email": email
        }
    }

@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: int) -> dict:
    usuarios = normalizar_todos_usuarios(carregar_usuarios())

    for usuario in usuarios:
        if usuario["id"] == usuario_id:
            return usuario

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )


@app.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, dados: Usuario) -> dict:
    usuarios = normalizar_todos_usuarios(carregar_usuarios())

    for usuario in usuarios:
        if usuario["id"] == usuario_id:
            usuario.update(dados.model_dump())
            salvar_usuarios(usuarios)
            return usuario

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )


@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int) -> dict:
    usuarios = normalizar_todos_usuarios(carregar_usuarios())

    for usuario in usuarios:
        if usuario["id"] == usuario_id:
            usuarios.remove(usuario)
            salvar_usuarios(usuarios)

            return {
                "message": "Usuário removido com sucesso",
                "id": usuario_id
            }

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )