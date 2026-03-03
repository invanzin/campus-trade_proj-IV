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