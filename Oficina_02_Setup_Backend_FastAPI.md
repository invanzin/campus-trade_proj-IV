# 🚀 Oficina 2: Setup Inicial do Backend e Primeiras APIs

**Disciplina:** IBM8942 — Projeto em Ciência de Dados IV  
**Aula:** Oficina 2 — Desenvolvimento Backend Moderno  
**Duração estimada:** ~100 minutos  

---

## 📋 O que vamos fazer hoje

Nesta oficina, vamos colocar em prática tudo o que vimos na Aula 4. Ao final, você terá:

- Uma API REST funcional escrita em **FastAPI**
- Endpoints **GET** e **POST** com validação automática
- Documentação **Swagger** gerada do código
- A API rodando **localmente** e **deployada no Azure App Service**

> 💡 Esta é a base do projeto do semestre. Nas próximas oficinas, vamos adicionar banco de dados, upload de arquivos, autenticação e frontend.

---

## ✅ Pré-requisitos

Antes de começar, confirme que você tem:

- [ ] **Python 3.11+** instalado (`python --version` no terminal)
- [ ] **VS Code** instalado
- [ ] **Conta Azure for Students** ativa (ou trial gratuito)
- [ ] **Git** instalado (opcional, mas recomendado)

### Extensões do VS Code

Abra o VS Code, vá em **Extensions** (`Ctrl+Shift+X`) e instale:

- **Python** (Microsoft)
- **Azure App Service** (Microsoft)
- **REST Client** (Huachao Mao) — vamos usar para testar a API

---

## Parte 1: Criando o Projeto

### Passo 1 — Criar a pasta do projeto

Crie uma pasta para o projeto. O nome deve refletir o tema que seu grupo escolheu, mas para este guia usaremos um exemplo genérico:

```
campustrade-api
```

Abra essa pasta no VS Code: `File` → `Open Folder` → selecione a pasta.

Abra o terminal integrado: `Terminal` → `New Terminal` (ou `` Ctrl+` ``).

### Passo 2 — Criar e ativar o ambiente virtual

O ambiente virtual isola as dependências do seu projeto. Isso é fundamental para que o deploy no Azure funcione corretamente.

```bash
python -m venv venv
```

Ative o ambiente virtual:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

Você deve ver `(venv)` no início da linha do terminal. Isso confirma que o ambiente está ativo.

> ⚠️ **Importante:** Sempre que abrir o terminal para trabalhar no projeto, ative o ambiente virtual primeiro.

### Passo 3 — Instalar as dependências

Crie o arquivo `requirements.txt` na raiz do projeto com o seguinte conteúdo:

```txt
fastapi
uvicorn[standard]
```

Agora instale:

```bash
pip install -r requirements.txt
```

O `fastapi` é o framework da API. O `uvicorn` é o servidor que roda a aplicação.

---

## Parte 2: Implementando a API

Vamos criar dois arquivos: `schemas.py` (modelos de dados) e `main.py` (a aplicação). 

Na Aula 4, vimos que é boa prática separar os schemas Pydantic do código da aplicação. Isso mantém o projeto organizado desde o início.

### Passo 4 — Criar `schemas.py`

Este arquivo define a **forma dos dados** que a API aceita e retorna. O Pydantic valida tudo automaticamente — se alguém enviar um preço negativo ou esquecer um campo obrigatório, a API retorna erro 422 sem que você precise escrever uma linha de validação.

Crie o arquivo `schemas.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProdutoCreate(BaseModel):
    """
    Schema para CRIAR um produto.
    Estes são os campos que o cliente envia no POST.
    O Field() define validações automáticas.
    """
    titulo: str = Field(
        ...,                    # ... significa obrigatório
        min_length=3,
        max_length=100,
        description="Título do produto"
    )
    descricao: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Descrição detalhada do produto"
    )
    preco: float = Field(
        ...,
        gt=0,                   # gt = greater than (maior que)
        le=50000,               # le = less or equal (menor ou igual)
        description="Preço em reais"
    )
    categoria: str = Field(
        ...,
        description="Categoria do produto"
    )
    vendedor: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nome do vendedor"
    )


class ProdutoResponse(BaseModel):
    """
    Schema de RESPOSTA.
    Inclui os campos que o servidor adiciona (id, data).
    Usado como response_model nos endpoints.
    """
    id: int
    titulo: str
    descricao: str
    preco: float
    categoria: str
    vendedor: str
    data_criacao: datetime
```

**O que cada parte faz:**

- `ProdutoCreate` → define o que o cliente envia quando cria um produto. Campos com `Field(...)` são obrigatórios e têm validações (tamanho mínimo/máximo, valor positivo etc.)
- `ProdutoResponse` → define o que a API retorna. Inclui `id` e `data_criacao`, que são gerados pelo servidor (o cliente não envia esses campos)
- A separação entre Create e Response é a boa prática que vimos na Aula 4: nunca exponha a estrutura interna direto na API

### Passo 5 — Criar `main.py`

Este é o coração da aplicação. Aqui configuramos o FastAPI, definimos os endpoints e a lógica de negócio.

Crie o arquivo `main.py`:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import ProdutoCreate, ProdutoResponse
from datetime import datetime
from typing import List


# --- Configuração do App ---

app = FastAPI(
    title="CampusTrade API",
    description="Marketplace universitário — Projeto de Cloud IBMEC",
    version="1.0.0"
)

# CORS: permite que o frontend (React) acesse esta API.
# Sem isso, o navegador bloqueia as requisições.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Em produção, restrinja ao domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- "Banco de dados" em memória (temporário) ---
# Na próxima oficina, substituiremos por Azure SQL Database.

produtos_db: list = []
next_id: int = 1


# --- Endpoints ---

@app.get("/health")
def health_check():
    """
    Endpoint de saúde — o Azure usa para verificar se a app está viva.
    Se este endpoint parar de responder, o Azure reinicia a aplicação.
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/")
def root():
    """Página inicial da API."""
    return {
        "aplicacao": "CampusTrade API",
        "versao": "1.0.0",
        "documentacao": "/docs"
    }


@app.get("/produtos", response_model=List[ProdutoResponse])
def listar_produtos():
    """
    Lista todos os produtos cadastrados.
    O response_model garante que a resposta segue o schema ProdutoResponse.
    """
    return produtos_db


@app.post("/produtos", response_model=ProdutoResponse, status_code=201)
def criar_produto(produto: ProdutoCreate):
    """
    Cria um novo produto.
    - O Pydantic valida os dados automaticamente (tipo, tamanho, valor).
    - Se algo estiver errado, retorna 422 com detalhes do erro.
    - status_code=201 indica que um recurso foi criado (boa prática REST).
    """
    global next_id

    novo_produto = {
        "id": next_id,
        "titulo": produto.titulo,
        "descricao": produto.descricao,
        "preco": produto.preco,
        "categoria": produto.categoria,
        "vendedor": produto.vendedor,
        "data_criacao": datetime.now()
    }

    produtos_db.append(novo_produto)
    next_id += 1
    return novo_produto


@app.get("/produtos/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: int):
    """
    Busca um produto pelo ID.
    - {produto_id} é um path parameter — FastAPI converte para int automaticamente.
    - Se não encontrar, retorna 404 (Not Found).
    """
    for produto in produtos_db:
        if produto["id"] == produto_id:
            return produto

    raise HTTPException(status_code=404, detail="Produto não encontrado")


# --- Ponto de entrada para execução direta ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Conceitos da Aula 4 aplicados aqui:**

- **CORS** configurado desde o início (slide 20 da Aula 4)
- **Health check** em `/health` (slide 21 — boas práticas)
- **response_model** filtra a resposta (slide 21 — nunca exponha dados internos)
- **status_code=201** no POST (slide 8 — status codes semânticos)
- **HTTPException** para erros (slide 8 — 404 Not Found)
- **Schemas separados** do main.py (slides 10-11 — estrutura de projeto)

---

## Parte 3: Testando Localmente

### Passo 6 — Executar a API

No terminal (com o venv ativo), execute:

```bash
uvicorn main:app --reload
```

O `--reload` faz o servidor reiniciar automaticamente quando você salvar alterações no código. Muito útil durante o desenvolvimento.

Você deve ver algo como:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

Agora abra no navegador:

- **http://localhost:8000** → página inicial da API
- **http://localhost:8000/docs** → documentação Swagger interativa
- **http://localhost:8000/health** → health check

> 🎉 Se você viu o Swagger, parabéns! Sua API está rodando. A documentação foi gerada automaticamente do código — é isso que o FastAPI faz por você.

### Passo 7 — Testar com REST Client

Vamos testar a API de forma mais completa. O REST Client permite enviar requisições HTTP direto do VS Code.

Crie o arquivo `test_api.http`:

```http
### ===================================
### TESTES API CAMPUSTRADE — LOCAL
### ===================================

@baseUrl = http://localhost:8000


### 1. Health check
GET {{baseUrl}}/health

### 2. Página inicial
GET {{baseUrl}}/

### 3. Listar produtos (deve retornar lista vazia)
GET {{baseUrl}}/produtos

### 4. Criar primeiro produto
POST {{baseUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Livro de Algoritmos",
    "descricao": "Cormen et al., 3ª edição. Usado mas em ótimo estado.",
    "preco": 120.00,
    "categoria": "Livros",
    "vendedor": "Maria Santos"
}

### 5. Criar segundo produto
POST {{baseUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Calculadora HP 12C",
    "descricao": "Calculadora financeira, funciona perfeitamente. Com capa.",
    "preco": 200.00,
    "categoria": "Eletrônicos",
    "vendedor": "Carlos Lima"
}

### 6. Criar terceiro produto
POST {{baseUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Mesa de Estudos Compacta",
    "descricao": "Mesa de madeira, 1,20m x 60cm, perfeita para quarto pequeno.",
    "preco": 150.00,
    "categoria": "Móveis",
    "vendedor": "Ana Costa"
}

### 7. Listar todos os produtos (agora com 3)
GET {{baseUrl}}/produtos

### 8. Buscar produto por ID
GET {{baseUrl}}/produtos/1

### 9. Buscar produto inexistente (deve retornar 404)
GET {{baseUrl}}/produtos/999

### 10. Testar validação — preço negativo (deve retornar 422)
POST {{baseUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Produto Inválido",
    "descricao": "Testando validação de preço negativo no Pydantic.",
    "preco": -50.00,
    "categoria": "Teste",
    "vendedor": "Teste"
}

### 11. Testar validação — título muito curto (deve retornar 422)
POST {{baseUrl}}/produtos
Content-Type: application/json

{
    "titulo": "AB",
    "descricao": "Testando validação de título com menos de 3 caracteres.",
    "preco": 10.00,
    "categoria": "Teste",
    "vendedor": "Teste"
}
```

**Como usar:**

1. Abra o arquivo `test_api.http` no VS Code
2. Clique no texto **"Send Request"** que aparece acima de cada requisição (ou `Ctrl+Alt+R`)
3. A resposta abre em uma aba ao lado

**Execute na ordem e observe:**

- Testes 1-3: API respondendo, lista vazia ✅
- Testes 4-6: Criando 3 produtos, resposta com `id` e `data_criacao` ✅
- Teste 7: Lista com os 3 produtos ✅
- Teste 8: Busca retorna produto com id=1 ✅
- Teste 9: Erro 404 com mensagem "Produto não encontrado" ✅
- Testes 10-11: Erro 422 com detalhes da validação ✅

> 💡 Observe como o Pydantic gera mensagens de erro detalhadas sem você escrever uma linha de validação. É o poder do `Field()`.

---

## Parte 4: Deploy no Azure App Service

Agora vamos colocar a API na nuvem. O Azure App Service é um PaaS — você faz deploy do código e o Azure cuida do resto (servidor, OS, SSL, load balancing).

### Passo 8 — Criar o arquivo de startup

O Azure precisa saber como iniciar sua aplicação. Crie o arquivo `startup.py`:

```python
import subprocess
import sys

def main():
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

if __name__ == "__main__":
    main()
```

### Passo 9 — Login no Azure pelo VS Code

1. Pressione `Ctrl+Shift+P` (Command Palette)
2. Digite e selecione: **Azure: Sign In**
3. Faça login com sua conta Azure for Students
4. Aguarde a confirmação no canto inferior do VS Code

### Passo 10 — Criar o App Service

1. Pressione `Ctrl+Shift+P`
2. Digite e selecione: **Azure App Service: Create New Web App... (Advanced)**
3. Preencha:

| Campo | Valor |
|---|---|
| **Nome** | `campustrade-[seunome]` (deve ser único) |
| **Subscription** | Azure for Students |
| **Resource Group** | Criar novo → `rg-campustrade` |
| **Runtime** | Python 3.11 |
| **OS** | Linux |
| **Location** | Brazil South |
| **Pricing tier** | Free (F1) |

> ⚠️ O nome se torna parte da URL: `https://campustrade-[seunome].azurewebsites.net`. Use algo único como seu nome ou matrícula.

### Passo 11 — Fazer o deploy

1. Pressione `Ctrl+Shift+P`
2. Digite: **Azure App Service: Deploy to Web App**
3. Selecione o App Service que você criou
4. Selecione a pasta atual do projeto
5. Confirme e aguarde (3-5 minutos)

### Passo 12 — Configurar o comando de startup

1. Na barra lateral do VS Code, clique no ícone do **Azure**
2. Expanda **App Service** → clique com botão direito no seu app → **Open in Portal**
3. No Portal Azure:
   - Vá em **Configuration** → **General Settings**
   - Em **Startup Command**, digite: `python startup.py`
   - Clique em **Save**
   - Aguarde 1-2 minutos para reiniciar

### Passo 13 — Testar no Azure

Descubra a URL do seu app: na aba Azure do VS Code, clique com botão direito no app → **Browse Website**.

Crie o arquivo `test_azure.http` (substitua a URL pela sua):

```http
### ===================================
### TESTES API CAMPUSTRADE — AZURE
### ===================================

### SUBSTITUA pela sua URL real!
@azureUrl = https://campustrade-seunome.azurewebsites.net


### 1. Health check no Azure
GET {{azureUrl}}/health

### 2. Página inicial
GET {{azureUrl}}/

### 3. Acessar documentação Swagger
GET {{azureUrl}}/docs

### 4. Listar produtos (vazio — é uma nova instância)
GET {{azureUrl}}/produtos

### 5. Criar produto no Azure
POST {{azureUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Livro de Cálculo I",
    "descricao": "Stewart, 7ª edição. Algumas anotações a lápis, bom estado.",
    "preco": 90.00,
    "categoria": "Livros",
    "vendedor": "Pedro Oliveira"
}

### 6. Criar segundo produto no Azure
POST {{azureUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Notebook Dell Inspiron",
    "descricao": "i5 11ª geração, 8GB RAM, SSD 256GB. Ótimo para estudos.",
    "preco": 1500.00,
    "categoria": "Eletrônicos",
    "vendedor": "Lucas Santos"
}

### 7. Listar produtos criados
GET {{azureUrl}}/produtos

### 8. Buscar por ID
GET {{azureUrl}}/produtos/1
```

Execute os testes na ordem. Se todos responderem corretamente, sua API está rodando na nuvem! 🎉

---

## 🔧 Troubleshooting

**"A API não responde no Azure"**
- Verifique se o Startup Command está configurado como `python startup.py`
- No Portal Azure, vá em **Log Stream** para ver os logs em tempo real
- Verifique se o `requirements.txt` está na raiz do projeto

**"Erro 422 quando tento criar produto"**
- Confira se o `Content-Type: application/json` está no header
- Verifique se todos os campos obrigatórios estão no JSON
- Leia a mensagem de erro — o Pydantic diz exatamente o que está errado

**"ModuleNotFoundError: No module named 'schemas'"**
- Verifique se o arquivo se chama `schemas.py` (não `schema.py`)
- Verifique se está na mesma pasta que `main.py`

**"O ambiente virtual não ativa"**
- Windows: tente `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` no PowerShell
- macOS/Linux: use `source venv/bin/activate` (não `./venv/bin/activate`)

---

## 📁 Estrutura Final do Projeto

Ao final da oficina, sua pasta deve ter esta estrutura:

```
campustrade-api/
├── venv/               ← ambiente virtual (NÃO vai para o Azure)
├── main.py             ← aplicação FastAPI
├── schemas.py          ← modelos Pydantic (validação)
├── startup.py          ← script de inicialização do Azure
├── requirements.txt    ← dependências do projeto
├── test_api.http       ← testes locais
└── test_azure.http     ← testes no Azure
```

---

## 🔮 Próxima Oficina

Na **Oficina 3**, vamos integrar com o **Azure SQL Database**: modelagem de tabelas, conexão com SQLAlchemy, e migrar os dados em memória para persistência real. Traga a API desta oficina funcionando — vamos construir em cima dela.
