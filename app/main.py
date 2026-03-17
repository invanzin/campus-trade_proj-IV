from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (
    ProdutoCreate, ProdutoResponse, ProdutoUpdate,
    CategoriaCreate, CategoriaResponse
)
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from .database import engine, get_db, Base
from .models import Produto, Categoria


# --- Criar tabelas automaticamente na primeira execução ---
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


# ─────────────────────────────────────────────
# Endpoints Gerais
# ─────────────────────────────────────────────

@app.get("/health", tags=["Geral"])
def health_check():
    """Endpoint de saúde — o Azure usa para verificar se a app está viva."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/", tags=["Geral"])
def root():
    """Página inicial da API."""
    return {
        "aplicacao": "CampusTrade API",
        "versao": "2.0.0",
        "documentacao": "/docs"
    }


# ─────────────────────────────────────────────
# Endpoints de CATEGORIAS
# ─────────────────────────────────────────────

@app.get("/categorias", response_model=List[CategoriaResponse], tags=["Categorias"])
def listar_categorias(db: Session = Depends(get_db)):
    """Lista todas as categorias cadastradas."""
    return db.query(Categoria).all()


@app.post("/categorias", response_model=CategoriaResponse, status_code=201, tags=["Categorias"])
def criar_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova categoria.
    Valida se o nome já existe (UNIQUE) — retorna 409 se duplicado.
    """
    existente = db.query(Categoria).filter(Categoria.nome == categoria.nome).first()
    if existente:
        raise HTTPException(status_code=409, detail=f"Categoria '{categoria.nome}' já existe")

    nova_categoria = Categoria(
        nome=categoria.nome,
        descricao=categoria.descricao
    )
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return nova_categoria


@app.get("/categorias/{categoria_id}", response_model=CategoriaResponse, tags=["Categorias"])
def buscar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Busca uma categoria pelo ID."""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@app.delete("/categorias/{categoria_id}", tags=["Categorias"])
def deletar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Remove uma categoria. Produtos vinculados ficam com categoria_id = NULL."""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    db.delete(categoria)
    db.commit()
    return {"message": "Categoria removida com sucesso", "id": categoria_id}


# ─────────────────────────────────────────────
# Endpoints de PRODUTOS
# ─────────────────────────────────────────────

@app.get("/produtos", response_model=List[ProdutoResponse], tags=["Produtos"])
def listar_produtos(categoria_id: int = None, db: Session = Depends(get_db)):
    """
    Lista todos os produtos cadastrados.
    Aceita filtro opcional por categoria: GET /produtos?categoria_id=1
    """
    query = db.query(Produto)
    if categoria_id is not None:
        query = query.filter(Produto.categoria_id == categoria_id)
    return query.all()


@app.post("/produtos", response_model=ProdutoResponse, status_code=201, tags=["Produtos"])
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo produto no banco.
    Se informado categoria_id, valida se a categoria existe.
    """
    if produto.categoria_id is not None:
        categoria = db.query(Categoria).filter(Categoria.id == produto.categoria_id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail=f"Categoria com id={produto.categoria_id} não encontrada")

    novo_produto = Produto(
        titulo=produto.titulo,
        descricao=produto.descricao,
        preco=produto.preco,
        vendedor=produto.vendedor,
        categoria_id=produto.categoria_id
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@app.get("/produtos/{produto_id}", response_model=ProdutoResponse, tags=["Produtos"])
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Busca um produto pelo ID."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.put("/produtos/{produto_id}", response_model=ProdutoResponse, tags=["Produtos"])
def atualizar_produto(produto_id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
    """
    Atualiza um produto existente.
    Só altera os campos que foram enviados (não-nulos).
    """
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Valida categoria_id se foi enviado
    if dados.categoria_id is not None:
        categoria = db.query(Categoria).filter(Categoria.id == dados.categoria_id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail=f"Categoria com id={dados.categoria_id} não encontrada")

    dados_dict = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_dict.items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto


@app.delete("/produtos/{produto_id}", tags=["Produtos"])
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Remove um produto do banco."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(produto)
    db.commit()
    return {"message": "Produto removido com sucesso", "id": produto_id}


# --- Ponto de entrada para execução direta ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
