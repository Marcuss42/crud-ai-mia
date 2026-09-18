import requests

from .agent.agent import executar_agente


def iniciar():
    print(
        "Agente iniciado. "
        "Digite 'sair' para encerrar."
    )

    while True:

        mensagem = input("\nVocê: ")

        if mensagem.strip().lower() == "sair":
            break

        try:

            resposta = executar_agente(mensagem)

            print(f"\nMia: {resposta}")

        except requests.RequestException as erro:

            print(f"\nErro na API: {erro}")

        except Exception as erro:

            print(f"\nErro: {erro}")


if __name__ == "__main__":
    iniciar()