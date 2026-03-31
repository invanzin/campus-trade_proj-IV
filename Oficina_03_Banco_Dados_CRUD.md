# 🚀 Oficina 3: Integração com Banco de Dados e CRUD Completo

**Disciplina:** IBM8942 — Projeto em Ciência de Dados IV  
**Aula:** Oficina 3 — Banco de Dados + CRUD  
**Duração estimada:** ~100 minutos  

---

## 📋 O que vamos fazer hoje

Na Oficina 2, criamos uma API com dados em memória — toda vez que o servidor reiniciava, os dados sumiam. Hoje vamos resolver isso:

- Conectar a API a um **banco de dados real** (SQLite local)
- Configurar o **SQLAlchemy** como ORM
- Rodar a primeira **migration** com Alembic
- Expandir o CRUD com **PUT** e **DELETE** (antes só tínhamos GET e POST)
- Verificar que os dados **persistem** mesmo reiniciando o servidor

> 💡 Usamos SQLite local para desenvolvimento. Na Aula 5, vimos que o mesmo código funciona com Azure SQL em produção — basta trocar a variável de ambiente.

---

## ✅ Pré-requisitos

- [ ] **API da Oficina 2 funcionando** (main.py + schemas.py + requirements.txt)
- [ ] **VS Code** com extensões Python e REST Client
- [ ] **Ambiente virtual** ativo (`(venv)` no terminal)

Se você não completou a Oficina 2, baixe o código base fornecido pelo professor antes de continuar.

---

## Parte 1: Instalando as Dependências

### Passo 1 — Atualizar requirements.txt

Abra o `requirements.txt` e adicione as novas dependências. O arquivo completo fica:

```txt
fastapi
uvicorn[standard]
sqlalchemy
alembic
```

- `sqlalchemy` — o ORM que conecta Python ao banco de dados
- `alembic` — ferramenta de migrations (versionamento do schema)

### Passo 2 — Instalar

No terminal (com venv ativo):

```bash
pip install -r requirements.txt
```

---

## Parte 2: Criando a Camada de Banco de Dados

Vamos criar dois arquivos novos: `database.py` (conexão) e `models.py` (tabelas).

### Passo 3 — Criar `database.py`

Este arquivo configura a conexão com o banco. O truque está no `os.getenv()`: se a variável `DATABASE_URL` existir (como no Azure), usa ela. Se não existir (seu computador), usa SQLite local.

Crie o arquivo `database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Lê a URL do banco da variável de ambiente.
# Se não existir, usa SQLite local (desenvolvimento).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

# Configuração do engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite: precisa de check_same_thread para FastAPI
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Azure SQL ou outro banco: usa connection pool
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        pool_recycle=3600,
        pool_pre_ping=True
    )

# Fábrica de sessões — cada request usa uma sessão isolada
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os models
Base = declarative_base()


def get_db():
    """
    Dependency injection para FastAPI.
    Cria uma sessão de banco por request e fecha ao final,
    mesmo se acontecer um erro no meio.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**O que cada parte faz:**

- `os.getenv("DATABASE_URL", "sqlite:///./local.db")` — tenta ler a variável de ambiente. Se não achar, usa SQLite. Isso permite que o mesmo código rode local e no Azure.
- `check_same_thread=False` — necessário para SQLite funcionar com FastAPI (que usa múltiplas threads).
- `pool_size=5` — para Azure SQL, mantém 5 conexões abertas e reutiliza entre requests.
- `get_db()` — função geradora que cria uma sessão, entrega para o endpoint (yield), e garante o fechamento (finally). Usamos com `Depends()` nos endpoints.

### Passo 4 — Criar `models.py`

Este arquivo define a tabela `produtos` como uma classe Python. Cada atributo `Column()` vira uma coluna no banco.

Crie o arquivo `models.py`:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime


class Produto(Base):
    """
    Model SQLAlchemy — representa a tabela 'produtos' no banco.
    Cada instância desta classe = uma linha na tabela.
    """
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=False)
    preco = Column(Float, nullable=False)
    categoria = Column(String(50), nullable=False)
    vendedor = Column(String(50), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
```

**Conexão com a Aula 5:**

- `Base` — herdamos da classe base declarada em `database.py`. O Alembic usa isso para descobrir quais tabelas existem.
- `__tablename__ = "produtos"` — nome da tabela no banco. Convenção: plural, snake_case.
- `Column(Integer, primary_key=True, index=True)` — cria coluna com auto-increment e índice.
- `Column(String(100), nullable=False)` — VARCHAR(100), obrigatório. O SQLAlchemy traduz para o tipo correto de cada banco.
- `Column(DateTime, default=datetime.utcnow)` — preenchido automaticamente na criação.

> 💡 **Importante:** `models.py` (SQLAlchemy) define a estrutura no banco. `schemas.py` (Pydantic) define a validação na API. São camadas diferentes com responsabilidades diferentes.

### Passo 5 — Atualizar `schemas.py`

Precisamos adicionar um schema para UPDATE (PUT) e configurar o `ProdutoResponse` para funcionar com objetos SQLAlchemy.

Substitua o conteúdo de `schemas.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProdutoCreate(BaseModel):
    """Schema para CRIAR produto (POST)."""
    titulo: str = Field(..., min_length=3, max_length=100)
    descricao: str = Field(..., min_length=10, max_length=500)
    preco: float = Field(..., gt=0, le=50000)
    categoria: str = Field(...)
    vendedor: str = Field(..., min_length=2, max_length=50)


class ProdutoUpdate(BaseModel):
    """
    Schema para ATUALIZAR produto (PUT).
    Todos os campos são opcionais — só atualiza o que for enviado.
    """
    titulo: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = Field(None, min_length=10, max_length=500)
    preco: Optional[float] = Field(None, gt=0, le=50000)
    categoria: Optional[str] = None
    vendedor: Optional[str] = Field(None, min_length=2, max_length=50)


class ProdutoResponse(BaseModel):
    """Schema de RESPOSTA — o que a API retorna."""
    id: int
    titulo: str
    descricao: str
    preco: float
    categoria: str
    vendedor: str
    criado_em: datetime

    class Config:
        from_attributes = True  # Permite converter objetos SQLAlchemy → Pydantic
```

**O que mudou:**

- Adicionamos `ProdutoUpdate` — todos os campos opcionais para atualização parcial.
- Adicionamos `class Config: from_attributes = True` no Response — isso permite que o Pydantic converta um objeto SQLAlchemy (que vem do banco) em JSON automaticamente. Sem isso, dá erro.

---

## Parte 3: Configurando Migrations com Alembic

Agora vamos configurar o Alembic para versionar o schema do banco. Na Aula 5 vimos a teoria — agora é a prática.

### Passo 6 — Inicializar o Alembic

No terminal:

```bash
alembic init migrations
```

Isso cria uma pasta `migrations/` com arquivos de configuração. Vamos ajustar dois deles.

### Passo 7 — Configurar alembic.ini

Abra o arquivo `alembic.ini` na raiz do projeto. Encontre a linha:

```
sqlalchemy.url = driver://user:pass@localhost/dbname
```

E substitua por:

```
sqlalchemy.url = sqlite:///./local.db
```

> ⚠️ Em produção, essa URL será substituída pela variável de ambiente. Por enquanto, estamos configurando para desenvolvimento local.

### Passo 8 — Configurar env.py

Abra `migrations/env.py`. Precisamos importar nossos models para que o Alembic saiba quais tabelas criar.

Encontre a linha (perto do início):

```python
target_metadata = None
```

E substitua por:

```python
from models import Base
target_metadata = Base.metadata
```

Isso diz ao Alembic: "olhe para os models que herdam de Base e descubra quais tabelas precisam existir".

### Passo 9 — Gerar a primeira migration

Agora o Alembic vai comparar os models com o banco (que ainda não existe) e gerar um script de criação:

```bash
alembic revision --autogenerate -m "criar tabela produtos"
```

Você verá algo como:

```
Generating migrations/versions/xxxx_criar_tabela_produtos.py ... done
```

Abra o arquivo gerado em `migrations/versions/`. Ele deve conter algo como:

```python
def upgrade():
    op.create_table('produtos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=100), nullable=False),
        # ... outras colunas
    )

def downgrade():
    op.drop_table('produtos')
```

- `upgrade()` — cria a tabela. Executado com `alembic upgrade`.
- `downgrade()` — desfaz a criação. Executado com `alembic downgrade`.

### Passo 10 — Aplicar a migration

```bash
alembic upgrade head
```

Você verá:

```
Running upgrade  -> xxxx, criar tabela produtos
```

Pronto! O banco `local.db` foi criado na pasta do projeto com a tabela `produtos`. Você pode confirmar olhando no explorador de arquivos — o arquivo `local.db` apareceu.

> 🎉 Se você chegou aqui, o banco está criado e pronto para receber dados.

---

## Parte 4: Refatorando a API para Usar o Banco

Agora vem a parte principal: conectar os endpoints ao banco real.

### Passo 11 — Reescrever `main.py`

Vamos substituir a lista em memória por queries ao banco. O `main.py` completo fica:

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import Produto
from schemas import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from datetime import datetime
from typing import List


# --- Criar tabelas (fallback se não usar migrations) ---
Base.metadata.create_all(bind=engine)

# --- Configuração do App ---
app = FastAPI(
    title="CampusTrade API",
    description="Marketplace universitário — Projeto de Cloud IBMEC",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoints ---

@app.get("/health")
def health_check():
    """Health check — Azure usa para verificar se a app está viva."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/")
def root():
    """Página inicial."""
    return {
        "aplicacao": "CampusTrade API",
        "versao": "2.0.0",
        "documentacao": "/docs"
    }


@app.get("/produtos", response_model=List[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    """
    Lista todos os produtos.
    O Depends(get_db) injeta uma sessão de banco automaticamente.
    """
    return db.query(Produto).all()


@app.post("/produtos", response_model=ProdutoResponse, status_code=201)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo produto no banco.
    1. Pydantic valida os dados (ProdutoCreate)
    2. Criamos o objeto SQLAlchemy (Produto)
    3. Salvamos no banco (add + commit)
    4. Refresh carrega o id e criado_em gerados pelo banco
    """
    novo_produto = Produto(
        titulo=produto.titulo,
        descricao=produto.descricao,
        preco=produto.preco,
        categoria=produto.categoria,
        vendedor=produto.vendedor
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@app.get("/produtos/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Busca produto por ID."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.put("/produtos/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza um produto existente.
    Só altera os campos que foram enviados (não-nulos).
    """
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Atualiza apenas campos enviados
    dados_dict = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_dict.items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto


@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Remove um produto do banco."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(produto)
    db.commit()
    return {"message": "Produto removido com sucesso", "id": produto_id}


# --- Ponto de entrada ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**O que mudou da Oficina 2:**

- `db: Session = Depends(get_db)` — cada endpoint recebe uma sessão de banco automaticamente. O FastAPI chama `get_db()`, entrega a sessão, e fecha ao final.
- `db.query(Produto).all()` — busca todos os produtos do banco (antes era `return produtos_db`).
- `db.add()` + `db.commit()` — salva no banco (antes era `produtos_db.append()`).
- `db.refresh()` — recarrega o objeto com os dados gerados pelo banco (id, criado_em).
- `db.query(Produto).filter(Produto.id == produto_id).first()` — busca por ID com query SQL.
- `setattr(produto, campo, valor)` — atualiza cada campo dinamicamente no PUT.
- `db.delete()` — remove do banco no DELETE.
- `Base.metadata.create_all(bind=engine)` — cria tabelas se não existirem (fallback para quem não usar Alembic).

---

## Parte 5: Testando o CRUD Completo

### Passo 12 — Executar a API

```bash
uvicorn main:app --reload
```

Abra http://localhost:8000/docs — a documentação Swagger agora mostra todos os 5 endpoints (GET lista, POST, GET por ID, PUT, DELETE).

### Passo 13 — Testar com REST Client

Substitua o conteúdo do `test_api.http`:

```http
### ======================================
### TESTES API CAMPUSTRADE — OFICINA 3
### CRUD completo com banco de dados
### ======================================

@baseUrl = http://localhost:8000


### 1. Health check
GET {{baseUrl}}/health

### 2. Página inicial
GET {{baseUrl}}/

### 3. Listar produtos (pode ter dados de execuções anteriores!)
GET {{baseUrl}}/produtos

### ---- CRIAR (POST) ----

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

### ---- LER (GET) ----

### 7. Listar todos (agora com 3 produtos)
GET {{baseUrl}}/produtos

### 8. Buscar por ID
GET {{baseUrl}}/produtos/1

### 9. Buscar produto inexistente (deve retornar 404)
GET {{baseUrl}}/produtos/999

### ---- ATUALIZAR (PUT) ----

### 10. Atualizar preço e descrição do produto 1
PUT {{baseUrl}}/produtos/1
Content-Type: application/json

{
    "preco": 95.00,
    "descricao": "Cormen et al., 3ª edição. Com anotações a lápis, bom estado."
}

### 11. Verificar que atualizou
GET {{baseUrl}}/produtos/1

### 12. Tentar atualizar produto inexistente (deve retornar 404)
PUT {{baseUrl}}/produtos/999
Content-Type: application/json

{
    "preco": 50.00
}

### ---- DELETAR (DELETE) ----

### 13. Deletar produto 3
DELETE {{baseUrl}}/produtos/3

### 14. Verificar que deletou (lista deve ter 2 produtos)
GET {{baseUrl}}/produtos

### 15. Tentar deletar novamente (deve retornar 404)
DELETE {{baseUrl}}/produtos/3

### ---- VALIDAÇÕES ----

### 16. Preço negativo (deve retornar 422)
POST {{baseUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Produto Inválido",
    "descricao": "Testando validação de preço negativo.",
    "preco": -50.00,
    "categoria": "Teste",
    "vendedor": "Teste"
}

### 17. Título muito curto (deve retornar 422)
POST {{baseUrl}}/produtos
Content-Type: application/json

{
    "titulo": "AB",
    "descricao": "Testando validação de título com menos de 3 caracteres.",
    "preco": 10.00,
    "categoria": "Teste",
    "vendedor": "Teste"
}

### ---- TESTE DE PERSISTÊNCIA ----
### Pare o servidor (Ctrl+C), reinicie (uvicorn main:app --reload)
### e execute o teste abaixo. Os dados devem continuar lá!

### 18. Listar produtos após reiniciar servidor
GET {{baseUrl}}/produtos
```

**Execute na ordem e observe:**

- Testes 1-3: API online, lista pode ter dados de execuções anteriores (dados persistem!) ✅
- Testes 4-6: Criar 3 produtos, resposta com id e criado_em do banco ✅
- Testes 7-9: Listar e buscar funcionando, 404 para inexistente ✅
- Testes 10-12: PUT atualiza campos parcialmente, 404 para inexistente ✅
- Testes 13-15: DELETE remove, não encontra de novo, lista reduzida ✅
- Testes 16-17: Validação Pydantic continua funcionando (422) ✅
- Teste 18: **Teste crucial** — pare o servidor, reinicie, e os dados continuam! 🎉

---

## 🔧 Troubleshooting

**"ImportError: cannot import name 'Base' from 'database'"**
- Verifique se `database.py` está na mesma pasta que `main.py`
- Verifique se o nome é `database.py` (não `db.py`)

**"sqlalchemy.exc.OperationalError: no such table: produtos"**
- Rode `alembic upgrade head` para criar a tabela
- Ou reinicie o servidor — o `Base.metadata.create_all()` no main.py cria como fallback

**"AttributeError: 'Produto' object has no attribute..." no response**
- Verifique se o `ProdutoResponse` tem `class Config: from_attributes = True`
- Sem isso, o Pydantic não consegue converter objetos SQLAlchemy

**"alembic.util.exc.CommandError: Can't locate revision"**
- Delete a pasta `migrations/versions/` e o arquivo `local.db`
- Rode novamente: `alembic revision --autogenerate -m "criar tabela produtos"`
- Depois: `alembic upgrade head`

**"O PUT não atualiza nada"**
- Verifique se está enviando o Content-Type: application/json
- Verifique se os campos no JSON coincidem com os nomes do schema (titulo, descricao, preco...)

---

## 📁 Estrutura Final do Projeto

```
campustrade-api/
├── venv/                   ← ambiente virtual
├── migrations/             ← pasta do Alembic (NOVA)
│   ├── versions/           ← scripts de migration
│   │   └── xxxx_criar_tabela_produtos.py
│   ├── env.py              ← configuração do Alembic
│   └── script.py.mako      ← template de migration
├── alembic.ini             ← configuração principal do Alembic (NOVO)
├── database.py             ← conexão com banco (NOVO)
├── models.py               ← tabelas SQLAlchemy (NOVO)
├── main.py                 ← aplicação FastAPI (ATUALIZADO)
├── schemas.py              ← validação Pydantic (ATUALIZADO)
├── startup.py              ← script para Azure
├── requirements.txt        ← dependências (ATUALIZADO)
├── test_api.http           ← testes CRUD completo (ATUALIZADO)
├── local.db                ← banco SQLite local (GERADO, no .gitignore)
└── test_azure.http         ← testes Azure (da Oficina 2)
```

> ⚠️ **Lembre-se:** adicione `local.db` ao `.gitignore` se usar Git. O banco local é só para desenvolvimento.

---

## 🔮 Próxima Aula

Na próxima aula, vamos **colocar o projeto em produção**: criar o Azure SQL Database, configurar o deploy, rodar migrations na nuvem e testar o CRUD funcionando com banco real. Traga a API desta oficina funcionando com o banco de dados — vamos construir em cima dela.
