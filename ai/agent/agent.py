# ai/agent.py

import json
import unicodedata
from typing import get_args
from time import perf_counter

from ai.config.config import client, MODEL
from ai.agent.rules import carregar_regras
from ai.agent.state import EstadoAgente
from ai.api.tools import obter_todas_tools
from ai.api.api_client import (listar_usuarios, contar_usuarios, buscar_usuario)
from ai.conversation.confirmation import verificar_confirmacao
from ai.conversation.user_flow import (preparar_criacao, preparar_atualizacao, preparar_exclusao, executar_operacao)
from ai.conversation.queries import formatar_usuarios

from ai.agent.logger import (debug, info, warning, error, separador)

SYSTEM_PROMPT = carregar_regras()
MAX_MENSAGENS_HISTORICO = 10
estado = EstadoAgente()

def normalizar_texto(texto: str) -> str:
    return "".join( c for c in unicodedata.normalize("NFD", texto.casefold()) if unicodedata.category(c) != "Mn")

def tipo_para_schema(tipo) -> dict:
    tipos = get_args(tipo)

    if tipos:
        schemas = []

        for argumento in tipos:
            if argumento is type(None):
                schemas.append({"type": "null"})
            else:
                schemas.append(tipo_para_schema(argumento))

        if len(schemas) == 1:
            return schemas[0]

        return {"anyOf": schemas}

    if hasattr(tipo, "model_json_schema"):
        return tipo.model_json_schema()

    if tipo is int:
        return {"type": "integer"}

    if tipo is float:
        return {"type": "number"}

    if tipo is bool:
        return {"type": "boolean"}

    if tipo is str:
        return {"type": "string"}

    if tipo is dict:
        return {"type": "object"}

    if tipo is list:
        return {"type": "array"}

    return {"type": "string"}


def criar_definicoes_tools() -> list[dict]:
    definicoes = []

    for tool in obter_todas_tools():
        assinatura = tool["assinatura"]
        annotations = tool["annotations"]
        properties = {}

        for nome, parametro in assinatura.parameters.items():
            if nome == "self":
                continue

            tipo = annotations.get(nome)

            if (
                tool["funcao"].__name__ == "criar_usuario"
                and nome == "usuario"
            ):
                properties[nome] = {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string"},
                        "idade": {"type": "integer"},
                        "cidade": {"type": "string"},
                        "email": {"type": "string"}
                    },
                    "additionalProperties": False
                }
                continue

            properties[nome] = tipo_para_schema(tipo)

        definicoes.append({
            "type": "function",
            "function": {
                "name": tool["funcao"].__name__,
                "description": tool["docstring"] or "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": [],
                    "additionalProperties": False
                }
            }
        })

    return definicoes

def processar_confirmacao(mensagem: str) -> str | None:
    if not estado.operacao_pendente:
        return None

    confirmacao = verificar_confirmacao(mensagem)

    if confirmacao is True:
        operacao = estado.operacao_pendente
        info(f"CONFIRMAÇÃO ACEITA | executando: {operacao!r}")

        estado.operacao_pendente = None
        estado.usuario_em_criacao = None
        estado.dados_informados.clear()

        try:
            resposta = executar_operacao(operacao)
        except Exception as erro:
            error(f"Erro ao executar operação: {erro}")
            resposta = "Não foi possível executar a operação."

        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    if confirmacao is False:
        info("CONFIRMAÇÃO NEGADA | cancelando operação")

        estado.operacao_pendente = None
        estado.usuario_em_criacao = None
        estado.dados_informados.clear()

        resposta = "Operação cancelada."
        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    return None

def processar_tool(nome: str, argumentos: dict) -> str | None:
    debug(f"Tool recebida: {nome!r}")

    if nome == "criar_usuario":
        novos = argumentos.get("usuario", {})
        usuario = estado.usuario_em_criacao or {}

        campos_validos = {
            "nome",
            "idade",
            "cidade",
            "email"
        }

        mensagem_usuario = normalizar_texto(" ".join(
            m["content"]
            for m in estado.mensagens
            if m["role"] == "user"
        ))

        for campo, valor in novos.items():
            if campo not in campos_validos:
                continue

            if valor in (None, "", "?"):
                continue

            if campo == "idade":
                if not isinstance(valor, int) or valor <= 0:
                    continue

                if str(valor) not in mensagem_usuario:
                    continue

            else:
                valor_normalizado = normalizar_texto(str(valor).strip())

                if valor_normalizado not in mensagem_usuario:
                    continue

            usuario[campo] = valor
            estado.dados_informados[campo] = valor

        estado.usuario_em_criacao = usuario

        resposta, operacao = preparar_criacao(usuario)

        if operacao:
            info(f"OPERAÇÃO PENDENTE: {operacao!r}")
            estado.operacao_pendente = operacao

        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    if nome == "listar_usuarios":
        usuarios = listar_usuarios(
            nome=argumentos.get("nome"),
            cidade=argumentos.get("cidade"),
            idade=argumentos.get("idade"),
            email=argumentos.get("email")
        )

        resposta = formatar_usuarios(usuarios)

        if len(usuarios) == 1:
            estado.usuario_em_contexto = usuarios[0]
        else:
            estado.usuario_em_contexto = None

        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    if nome == "contar_usuarios":
        quantidade = contar_usuarios(
            nome=argumentos.get("nome"),
            cidade=argumentos.get("cidade"),
            idade=argumentos.get("idade"),
            email=argumentos.get("email")
        )

        resposta = f"Há {quantidade} usuários cadastrados."

        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    if nome == "buscar_usuario":
        usuario_id = argumentos.get("usuario_id")

        if usuario_id is None:
            resposta = "Qual o ID do usuário?"
        else:
            try:
                usuario = buscar_usuario(usuario_id)
            except Exception:
                resposta = "Usuário não encontrado."
            else:
                estado.usuario_em_contexto = usuario
                resposta = formatar_usuarios([usuario])

        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    if nome == "atualizar_usuario":
        usuario_id = argumentos.get("usuario_id")
        dados = argumentos.get("dados")

        if usuario_id is None or not dados:
            resposta = "Quais dados deseja atualizar?"
        else:
            try:
                usuario = buscar_usuario(usuario_id)
            except Exception:
                resposta = "Usuário não encontrado."
            else:
                estado.usuario_em_contexto = usuario

                resposta, operacao = preparar_atualizacao(usuario_id, dados)
                estado.operacao_pendente = operacao
                info(f"OPERAÇÃO PENDENTE UPDATE: {operacao!r}")

        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    if nome == "deletar_usuario":
        usuario_id = argumentos.get("usuario_id")

        if usuario_id is None:
            resposta = "Qual o ID do usuário?"
        else:
            try:
                usuario = buscar_usuario(usuario_id)
            except Exception:
                resposta = "Usuário não encontrado."
            else:
                estado.usuario_em_contexto = usuario
                resposta, operacao = preparar_exclusao(usuario)
                estado.operacao_pendente = operacao
                info(f"OPERAÇÃO PENDENTE DELETE: {operacao!r}")

        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    warning(f"Tool desconhecida: {nome!r}")
    return None

def executar_agente(mensagem: str) -> str:
    inicio_total = perf_counter()
    separador("NOVA INTERAÇÃO")
    info(f"Usuário: {mensagem!r}")
    estado.adicionar_mensagem("user", mensagem)

    if estado.operacao_pendente:
        resposta = processar_confirmacao(mensagem)
        if resposta is not None:
            info(f"Confirmação: {resposta}")
            return resposta

    tools = criar_definicoes_tools()
    historico = estado.mensagens[-10:]

    inicio_api = perf_counter()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *historico],
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False,
            reasoning_effort="low",
            max_completion_tokens=256
        )
    except Exception as erro:
        error(f"Erro no modelo após {(perf_counter() - inicio_api) * 1000:.0f} ms: {erro}")
        resposta = "Limite da API atingido. Tente novamente mais tarde." if "429" in str(erro) and "rate_limit" in str(erro) else "Não consegui entender essa informação. Pode explicar de outra forma?"
        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    debug(f"Modelo respondeu em {(perf_counter() - inicio_api) * 1000:.0f} ms")
    message = response.choices[0].message

    if not message.tool_calls:
        resposta = (message.content or "").strip()
        info(f"Resposta: {resposta}")
        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    tool_call = message.tool_calls[0]
    nome_tool = tool_call.function.name
    info(f"Tool: {nome_tool}")

    try:
        argumentos = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError as erro:
        error(f"Argumentos inválidos da tool: {erro}")
        resposta = "Não consegui entender os dados informados. Pode tentar novamente?"
        estado.adicionar_mensagem("assistant", resposta)
        return resposta

    if nome_tool in {"criar_usuario", "atualizar_usuario", "deletar_usuario"} and not estado.operacao_pendente:
        analise = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Analise TODO o histórico da conversa.\n"
                        "A operação representada pela tool recebida já foi explicitamente confirmada pelo usuário?\n"
                        "Considere a sequência completa da conversa.\n"
                        "Não execute nenhuma operação.\n"
                        "Responda SOMENTE SIM ou NAO."
                    )
                },
                *historico
            ],
            tools=tools,
            tool_choice="none",
            reasoning_effort="low",
            max_completion_tokens=256
        )

        confirmado = (analise.choices[0].message.content or "").strip().casefold() == "sim"

        if confirmado:
            operacao = {"nome": nome_tool, "argumentos": argumentos}
            info(f"CONFIRMAÇÃO DETECTADA NO HISTÓRICO | executando: {operacao!r}")

            try:
                resposta = executar_operacao(operacao)
            except Exception as erro:
                error(f"Erro ao executar operação: {erro}")
                resposta = "Não foi possível executar a operação."

            estado.usuario_em_criacao = None
            estado.dados_informados.clear()
            estado.adicionar_mensagem("assistant", resposta)
            info(f"Resposta: {resposta}")
            return resposta

    resposta = processar_tool(nome_tool, argumentos)
    debug(f"Interação concluída em {(perf_counter() - inicio_total) * 1000:.0f} ms")
    return resposta