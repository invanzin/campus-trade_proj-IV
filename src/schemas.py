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
