# ai/api/tools.py

import inspect

from ai.api import api_client


def obter_tool(nome_funcao: str):
    """
    Obtém uma função da API e seus metadados para criação de uma tool.
    """

    funcao = getattr(api_client, nome_funcao)

    return {
        "funcao": funcao,
        "assinatura": inspect.signature(funcao),
        "annotations": funcao.__annotations__,
        "docstring": inspect.getdoc(funcao)
    }


def obter_todas_tools() -> list[dict]:
    """
    Obtém automaticamente todas as funções públicas do api_client.
    """

    nomes = [
        nome
        for nome, funcao in inspect.getmembers(
            api_client,
            inspect.isfunction
        )
        if funcao.__module__ == api_client.__name__
        and not nome.startswith("_")
    ]

    return [
        obter_tool(nome)
        for nome in nomes
    ]