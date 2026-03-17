from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class Categoria(Base):
    """
    Model SQLAlchemy — representa a tabela 'categorias' no banco.
    Cada categoria pode ter vários produtos vinculados.
    """
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(200), nullable=True)

    # Relacionamento: uma categoria possui muitos produtos
    produtos = relationship("Produto", back_populates="categoria_rel")


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
    vendedor = Column(String(50), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # FK para categorias — nullable para não quebrar dados existentes
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    # Relacionamento: produto pertence a uma categoria
    categoria_rel = relationship("Categoria", back_populates="produtos")
