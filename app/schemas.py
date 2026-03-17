from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────────
# Schemas de CATEGORIA
# ─────────────────────────────────────────────

class CategoriaCreate(BaseModel):
    """Schema para CRIAR uma categoria (POST /categorias)."""
    nome: str = Field(..., min_length=2, max_length=50, description="Nome único da categoria")
    descricao: Optional[str] = Field(None, max_length=200, description="Descrição opcional")


class CategoriaResponse(BaseModel):
    """Schema de RESPOSTA para categoria."""
    id: int
    nome: str
    descricao: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# Schemas de PRODUTO
# ─────────────────────────────────────────────

class ProdutoCreate(BaseModel):
    """Schema para CRIAR produto (POST /produtos)."""
    titulo: str = Field(..., min_length=3, max_length=100)
    descricao: str = Field(..., min_length=10, max_length=500)
    preco: float = Field(..., gt=0, le=50000)
    vendedor: str = Field(..., min_length=2, max_length=50)
    categoria_id: Optional[int] = Field(None, description="ID da categoria (opcional)")


class ProdutoUpdate(BaseModel):
    """
    Schema para ATUALIZAR produto (PUT /produtos/{id}).
    Todos os campos são opcionais — só atualiza o que for enviado.
    """
    titulo: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = Field(None, min_length=10, max_length=500)
    preco: Optional[float] = Field(None, gt=0, le=50000)
    vendedor: Optional[str] = Field(None, min_length=2, max_length=50)
    categoria_id: Optional[int] = None


class ProdutoResponse(BaseModel):
    """Schema de RESPOSTA — o que a API retorna ao consultar produtos."""
    id: int
    titulo: str
    descricao: str
    preco: float
    vendedor: str
    criado_em: datetime
    categoria_id: Optional[int]
    categoria_rel: Optional[CategoriaResponse] = None  # Retorna os dados da categoria

    model_config = ConfigDict(from_attributes=True)
