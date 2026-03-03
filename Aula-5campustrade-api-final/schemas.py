from pydantic import BaseModel, Field
from datetime import datetime


class ProdutoCreate(BaseModel):
    """
    Schema para CRIAR um produto.
    Estes são os campos que o cliente envia no POST.
    O Field() define validações automáticas.
    """
    titulo: str = Field(
        ...,
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
        gt=0,
        le=50000,
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
    Inclui campos gerados pelo servidor (id, data_criacao).
    Usado como response_model nos endpoints.
    """
    id: int
    titulo: str
    descricao: str
    preco: float
    categoria: str
    vendedor: str
    data_criacao: datetime
