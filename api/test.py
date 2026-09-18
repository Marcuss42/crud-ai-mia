import requests


BASE_URL = "http://127.0.0.1:8000"


def testar(nome: str, funcao, status_esperado: int):
    try:
        response = funcao()

        if response.status_code == status_esperado:
            print(f"[OK] {nome} -> {response.status_code}")
        else:
            print(
                f"[ERRO] {nome} -> "
                f"esperado {status_esperado}, "
                f"recebido {response.status_code}"
            )

        print(response.json())

        return response

    except requests.RequestException as erro:
        print(f"[FALHA] {nome}")
        print(erro)
        return None


# ==========================================
# 1. LISTAR USUÁRIOS
# ==========================================

testar(
    "Listar usuários",
    lambda: requests.get(f"{BASE_URL}/usuarios"),
    200
)


# ==========================================
# 2. CRIAR USUÁRIO
# ==========================================

response = testar(
    "Criar usuário",
    lambda: requests.post(
        f"{BASE_URL}/usuarios",
        json={
            "nome": "João",
            "idade": 25,
            "cidade": "Barueri",
            "email": "joao@email.com"
        }
    ),
    201
)

usuario_id = None

if response and response.status_code == 201:
    usuario_id = response.json()["id"]
    print(f"ID criado: {usuario_id}")


# ==========================================
# 3. TESTAR NORMALIZAÇÃO
# ==========================================

response = testar(
    "Criar usuário para testar normalização",
    lambda: requests.post(
        f"{BASE_URL}/usuarios",
        json={
            "nome": "   jOaO   ",
            "idade": 28,
            "cidade": "jAnDiRa",
            "email": "  TESTE@EMAIL.COM  "
        }
    ),
    201
)

usuario_normalizado_id = None

if response and response.status_code == 201:
    usuario_normalizado = response.json()
    usuario_normalizado_id = usuario_normalizado["id"]

    assert usuario_normalizado["nome"] == "Joao"
    assert usuario_normalizado["cidade"] == "Jandira"
    assert usuario_normalizado["email"] == "teste@email.com"

    print("[OK] Dados normalizados corretamente")


# ==========================================
# 4. FILTRAR POR NOME
# ==========================================

testar(
    "Filtrar usuários por nome",
    lambda: requests.get(
        f"{BASE_URL}/usuarios",
        params={"nome": "joao"}
    ),
    200
)


# ==========================================
# 5. FILTRAR POR CIDADE
# ==========================================

testar(
    "Filtrar usuários por cidade",
    lambda: requests.get(
        f"{BASE_URL}/usuarios",
        params={"cidade": "jandira"}
    ),
    200
)


# ==========================================
# 6. CONTAR POR NOME
# ==========================================

testar(
    "Contar usuários com nome Joao",
    lambda: requests.get(
        f"{BASE_URL}/usuarios/contagem",
        params={"nome": "joao"}
    ),
    200
)


# ==========================================
# 7. CONTAR POR CIDADE
# ==========================================

testar(
    "Contar usuários de Jandira",
    lambda: requests.get(
        f"{BASE_URL}/usuarios/contagem",
        params={"cidade": "jandira"}
    ),
    200
)

# ==========================================
# 3. BUSCAR USUÁRIO
# ==========================================

if usuario_id is not None:

    testar(
        "Buscar usuário criado",
        lambda: requests.get(
            f"{BASE_URL}/usuarios/{usuario_id}"
        ),
        200
    )


# ==========================================
# 4. ATUALIZAR USUÁRIO
# ==========================================

if usuario_id is not None:

    testar(
        "Atualizar usuário",
        lambda: requests.put(
            f"{BASE_URL}/usuarios/{usuario_id}",
            json={
                "nome": "João Silva",
                "idade": 26,
                "cidade": "Jandira",
                "email": "joao.silva@email.com"
            }
        ),
        200
    )


# ==========================================
# 5. TESTAR USUÁRIO INEXISTENTE
# ==========================================

testar(
    "Buscar usuário inexistente",
    lambda: requests.get(
        f"{BASE_URL}/usuarios/999999"
    ),
    404
)


# ==========================================
# 6. TESTAR VALIDAÇÃO
# ==========================================

testar(
    "Criar usuário com dados inválidos",
    lambda: requests.post(
        f"{BASE_URL}/usuarios",
        json={
            "nome": "Teste",
            "idade": "idade inválida",
            "cidade": "Jandira"
        }
    ),
    422
)


# ==========================================
# 7. DELETAR USUÁRIO
# ==========================================

if usuario_id is not None:

    testar(
        "Deletar usuário",
        lambda: requests.delete(
            f"{BASE_URL}/usuarios/{usuario_id}"
        ),
        200
    )


# ==========================================
# 8. CONFIRMAR QUE FOI DELETADO
# ==========================================

if usuario_id is not None:

    testar(
        "Buscar usuário depois da exclusão",
        lambda: requests.get(
            f"{BASE_URL}/usuarios/{usuario_id}"
        ),
        404
    )


print("\nTestes finalizados.")