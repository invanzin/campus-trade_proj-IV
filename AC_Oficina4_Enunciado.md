# 📝 Atividade Avaliativa (AC) — Oficina 4

**Disciplina:** IBM8942 — Projeto em Ciência de Dados IV  
**Tipo:** Individual ou em dupla  
**Prazo de entrega:** Final da Oficina 4 (12/03)  
**Valor:** Nota de AC (média aritmética com demais atividades)  

---

## Objetivo

Demonstrar que você consegue:

1. Colocar uma aplicação FastAPI em produção no Azure com banco de dados real
2. Evoluir o modelo de dados adicionando uma tabela com relacionamento (FK)

---

## Parte 1: Deploy em Produção (60 pontos)

Coloque a API CampusTrade (da Oficina 3) em produção no Azure com Azure SQL Database.

**Requisitos:**

- API rodando no Azure App Service
- Azure SQL Database como banco de dados (não SQLite)
- CRUD completo funcionando em produção (GET, POST, PUT, DELETE)
- Dados persistentes (sobrevivem a restart do App Service)

**Evidências (3 screenshots):**

1. **POST** criando um produto na URL do Azure — mostrando status 201 e o JSON de resposta com `id` e `criado_em`
2. **GET** listando produtos na URL do Azure — mostrando pelo menos 2 produtos cadastrados
3. **PUT ou DELETE** funcionando na URL do Azure — mostrando a operação e o resultado

> Os screenshots devem mostrar claramente a URL do Azure (https://...azurewebsites.net) na requisição.

---

## Parte 2: Tabela de Categorias (40 pontos)

Hoje, o campo `categoria` no produto é texto livre — o usuário pode digitar qualquer coisa. Sua tarefa é criar uma tabela separada de categorias e vincular aos produtos com chave estrangeira.

**O que fazer:**

1. **Criar a tabela `categorias`** no `models.py` com os campos:
   - `id` — INTEGER, PK, auto-increment
   - `nome` — VARCHAR(50), UNIQUE, NOT NULL
   - `descricao` — VARCHAR(200), nullable

2. **Atualizar a tabela `produtos`**:
   - Remover o campo `categoria` (String)
   - Adicionar `categoria_id` — INTEGER, FK → categorias.id, nullable (para não quebrar dados existentes)
   - Adicionar `relationship()` entre Produto e Categoria

3. **Gerar migration** com Alembic para aplicar as mudanças

4. **Criar pelo menos 2 endpoints novos**:
   - `GET /categorias` — listar todas as categorias
   - `POST /categorias` — criar nova categoria (validar nome duplicado)

5. **Atualizar os endpoints de produtos** para usar `categoria_id` em vez de `categoria`

6. **Atualizar os schemas Pydantic** (ProdutoCreate, ProdutoUpdate, ProdutoResponse) para refletir a mudança

7. **Deploy da versão atualizada** no Azure

**Evidências (2 screenshots):**

4. **Swagger** (/docs) mostrando os endpoints de categorias na lista
5. **POST** criando um produto com `categoria_id` — mostrando os dados da categoria na resposta

---

## Dicas de Implementação

**Model da Categoria:**
```python
class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(200), nullable=True)
    produtos = relationship("Produto", back_populates="categoria_rel")
```

**Atualização no Model de Produto:**
```python
# Trocar isto:
categoria = Column(String(50), nullable=False)

# Por isto:
categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
categoria_rel = relationship("Categoria", back_populates="produtos")
```

**No ProdutoResponse, para retornar os dados da categoria:**
```python
class ProdutoResponse(BaseModel):
    # ... campos existentes ...
    categoria_id: Optional[int]
    categoria_rel: Optional[CategoriaResponse] = None

    class Config:
        from_attributes = True
```

**Gerar e aplicar migration:**
```bash
alembic revision --autogenerate -m "adicionar tabela categorias e FK"
alembic upgrade head
```

---

## Formato de Entrega

Um documento (PDF ou Word) ou e-mail contendo:

1. **URL do App Service** (ex: https://campustrade-seunome.azurewebsites.net)
2. **5 screenshots** numerados conforme descrito acima:
   - Screenshot 1: POST produto em produção (201)
   - Screenshot 2: GET lista de produtos em produção
   - Screenshot 3: PUT ou DELETE em produção
   - Screenshot 4: Swagger com endpoints de categorias
   - Screenshot 5: POST produto com categoria_id

---

## Critérios de Avaliação

| Critério | Pontos |
|---|---|
| API online no Azure (URL responde, /docs abre) | 10 |
| Azure SQL configurado (DATABASE_URL em App Settings) | 10 |
| POST funcional em produção (status 201, dados corretos) | 15 |
| GET/PUT/DELETE funcionando em produção | 15 |
| Persistência (dados sobrevivem a restart) | 10 |
| Tabela categorias criada (migration + model + GET e POST) | 15 |
| FK categoria_id em produtos (relacionamento funcional) | 15 |
| Swagger documentado (endpoints aparecem com descrições) | 10 |
| **Total** | **100** |

---

## Perguntas Frequentes

**Posso fazer em dupla?**
Sim, mas cada membro deve ter seu próprio App Service deployado. A entrega pode ser conjunta com as duas URLs.

**E se meu deploy não funcionar a tempo?**
Entregue o que conseguiu com os screenshots parciais. Deploy incompleto com categorias locais funcionando vale nota parcial.

**O campo categoria antigo dos produtos existentes vai quebrar?**
Não, porque `categoria_id` é `nullable=True`. Produtos antigos ficam com `categoria_id = None` até serem atualizados.

**Preciso criar as categorias antes dos produtos?**
Sim. Primeiro crie as categorias (POST /categorias), depois crie produtos referenciando o `categoria_id`.

**Posso adicionar mais endpoints além do pedido?**
Sim! Endpoints extras (GET /categorias/{id}, DELETE /categorias/{id}, GET /produtos?categoria_id=1) demonstram domínio e são valorizados.
