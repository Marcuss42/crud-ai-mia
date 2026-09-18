# CRUD AI — Mia

Projeto de **estudo pessoal** desenvolvido para explorar a integração entre uma API CRUD em Python e um agente de IA capaz de interagir com essa API por meio de ferramentas (*tool calling*).

A aplicação permite gerenciar usuários através de uma interface de terminal, utilizando linguagem natural.

## 🤖 Mia

**Mia** é a agente de IA responsável por interpretar as mensagens do usuário e decidir quais operações da API devem ser executadas.

Ela foi desenvolvida para:

* Criar usuários
* Listar usuários
* Buscar usuários
* Contar usuários
* Atualizar usuários
* Excluir usuários
* Solicitar confirmação antes de operações de criação, alteração e exclusão
* Coletar dados obrigatórios durante uma operação
* Manter o contexto da conversa

A Mia utiliza um modelo da **Groq** para interpretar a linguagem natural e decidir quando utilizar cada ferramenta disponível.

A execução das operações, entretanto, não fica sob responsabilidade direta do modelo. As operações são executadas pelo código Python após a chamada da ferramenta.

## Arquitetura

```text
Usuário
   ↓
Terminal
   ↓
Mia / Agente
   ↓
Groq
   ↓
Tool Calling
   ↓
API Client
   ↓ HTTP
FastAPI
   ↓
usuarios.json
```

O projeto é dividido principalmente em duas partes:

### Agente

```text
ai/
├── agent/
│   ├── agent.py
│   ├── rules.py
│   ├── state.py
│   └── rules/
├── api/
│   ├── api_client.py
│   └── tools.py
├── conversation/
│   ├── confirmation.py
│   ├── queries.py
│   └── user_flow.py
├── config/
└── terminal.py
```

Responsável pela interação com o modelo, regras de comportamento, estado da conversa, confirmação de operações e utilização das ferramentas.

### API

```text
api/
├── main.py
└── test.py
```

API REST desenvolvida com **FastAPI**.

Os dados são armazenados localmente no arquivo:

```text
usuarios.json
```

## Tecnologias

* Python
* FastAPI
* Uvicorn
* Groq API
* Requests
* Pydantic
* python-dotenv
* JSON
* Tool Calling

## Funcionalidades da API

A API disponibiliza operações para:

```text
GET    /usuarios
GET    /usuarios/contagem
GET    /usuarios/{id}
POST   /usuarios
PUT    /usuarios/{id}
DELETE /usuarios/{id}
```

Também permite filtros por:

* Nome
* Idade
* Cidade
* Email

Os filtros de texto consideram diferenças de maiúsculas/minúsculas e acentuação.

## Como executar

### 1. Clone o projeto

```bash
git clone <URL_DO_REPOSITORIO>
cd crud-ai
```

### 2. Crie o ambiente virtual

Windows:

```powershell
python -m venv .venv
```

Ative:

```powershell
.venv\Scripts\activate
```

### 3. Instale as dependências

```powershell
pip install -r requirements.txt
```

### 4. Configure a API da Groq

Crie um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua_chave_aqui
```

A chave da API é necessária para que a Mia possa utilizar o modelo de linguagem.

### 5. Inicie a API

A API precisa estar rodando **antes de iniciar a Mia**.

Entre na pasta `api`:

```powershell
cd api
```

Execute:

```powershell
uvicorn main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

Exemplo:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

### 6. Em outro terminal, inicie a Mia

Volte para a raiz do projeto:

```powershell
cd ..
```

Com o ambiente virtual ativo:

```powershell
python -m ai.terminal
```

A partir desse momento, é possível conversar com a Mia pelo terminal.

## Exemplos

### Criar usuário

```text
Você: crie a Mariana, 30, São Paulo

Mia:
Nome: Mariana
Idade: 30
Cidade: São Paulo

Confirmar?
```

Após a confirmação:

```text
Você: sim

Mia:
Usuário criado.
```

### Listar usuários

```text
Você: liste os usuários
```

### Buscar usuário

```text
Você: busque o usuário 4
```

### Contar usuários

```text
Você: quantos usuários existem em Jandira?
```

### Atualizar

```text
Você: atualize o usuário 4, coloque a idade para 25
```

A Mia solicita confirmação antes de executar a alteração.

### Excluir

```text
Você: exclua o usuário 4
```

A exclusão também exige confirmação.

## Confirmações

Operações que alteram os dados exigem confirmação explícita:

* Criar
* Atualizar
* Excluir

A Mia não deve executar essas operações apenas porque o modelo decidiu utilizar uma ferramenta.

O fluxo é:

```text
Solicitação
    ↓
Coleta dos dados
    ↓
Confirmação
    ↓
Execução da operação
```

## Objetivo do projeto

O projeto foi desenvolvido principalmente para **estudo pessoal** e experimentação com:

* Agentes de IA
* LLMs
* Tool Calling
* Integração entre IA e APIs
* Controle de estado de conversação
* Validação de dados
* Separação entre decisão do modelo e execução do código
* Desenvolvimento de APIs REST com Python


Espero que gostem :)