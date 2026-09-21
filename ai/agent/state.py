from dataclasses import dataclass, field


@dataclass
class EstadoAgente:
    mensagens: list[dict] = field(default_factory=list)
    operacao_pendente: dict | None = None
    usuario_em_criacao: dict | None = None
    usuario_em_contexto: dict | None = None
    dados_informados: dict = field(default_factory=dict)

    def adicionar_mensagem(self, role: str, content: str) -> None:
        self.mensagens.append({"role": role, "content": content})