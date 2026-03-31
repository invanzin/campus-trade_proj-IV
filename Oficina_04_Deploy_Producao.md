# 🚀 Oficina 4: Deploy em Produção com Azure SQL

**Disciplina:** IBM8942 — Projeto em Ciência de Dados IV  
**Aula 09** — Oficina 4  
**Duração estimada:** ~100 minutos

---

## 📋 O que vamos fazer hoje

Até agora, a API CampusTrade roda local com SQLite. Hoje vamos colocá-la em produção na nuvem:

- Criar o **Azure SQL Database** no portal
- Configurar **firewall** e **connection string**
- Fazer **deploy** no Azure App Service
- Testar o **CRUD completo em produção** com dados persistentes

Ao final da aula, sua API estará rodando na nuvem com banco de dados real.

> ⚠️ **Importante:** ao final desta oficina será distribuída uma **atividade avaliativa (AC)** que usa como base tudo o que fizemos hoje.

---

## ✅ Pré-requisitos

- [ ] **API da Oficina 3 funcionando** com SQLite local (main.py, schemas.py, models.py, database.py)
- [ ] **Conta Azure for Students** ativa
- [ ] **App Service** criado (da Oficina 2)
- [ ] **VS Code** com extensão Azure App Service

---

## Parte 1: Criar Azure SQL Database

### Passo 1 — Criar o banco no portal

1. Acesse o [Portal Azure](https://portal.azure.com)
2. Busque **SQL databases** → clique **Create**
3. Preencha:

| Campo                  | Valor                                                   |
| ---------------------- | ------------------------------------------------------- |
| **Subscription**       | Azure for Students                                      |
| **Resource Group**     | rg-campustrade (o mesmo do App Service)                 |
| **Database name**      | campustrade-db                                          |
| **Server**             | Create new → nome único (ex: `campustrade-srv-seunome`) |
| **Server admin login** | sqladmin                                                |
| **Password**           | Senha forte (anote!)                                    |
| **Location**           | Brazil South                                            |
| **Compute**            | Free tier (ou Basic se Free não disponível)             |
| **Backup**             | Locally-redundant                                       |

4. Clique **Review + Create** → **Create**
5. Aguarde 2-3 minutos

> ⚠️ **Anote a senha!** Se esquecer, terá que resetar pelo portal (Server → Reset password).

### Passo 2 — Configurar Firewall

1. Vá para o **SQL Server** (não o database) que acabou de criar
2. Clique em **Networking** (menu lateral)
3. Marque: **"Allow Azure services and resources to access this server"**
4. Clique **Save**

Não precisa adicionar o IP da faculdade — só o App Service vai acessar o banco. Lembre-se: a rede da faculdade bloqueia conexões diretas ao Azure SQL, mas o App Service está na mesma rede interna do Azure e conecta sem restrições.

### Passo 3 — Copiar Connection String

1. Vá para o **SQL Database** (campustrade-db)
2. Clique em **Connection strings** (menu lateral)
3. Copie a string **ODBC** e monte a URL no formato:

```
mssql+pyodbc://ivan:@server-campustrade-ivan-centralus.database.windows.net/campustrade-db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes
```

Substitua `sqladmin`, `SuaSenhaAqui` e `seuserver` pelos valores reais.

Driver={ODBC Driver 18 for SQL Server};Server=tcp:server-campustrade-ivan-centralus.database.windows.net,1433;Database=db-campustrade-ivan;Uid=ivan;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;

---

## Parte 2: Configurar App Service

### Passo 4 — Configurar variável de ambiente

1. Vá para o **App Service** (campustrade-seunome)
2. Clique em **Configuration** → **Application settings**
3. Clique **+ New application setting**:
   - **Name:** `DATABASE_URL`
   - **Value:** a connection string do passo 3
4. Clique **OK** → **Save**

O App Service reinicia automaticamente.

**Como funciona no código:**

- No seu computador: `DATABASE_URL` não existe → `database.py` usa `sqlite:///./local.db`
- No Azure: `DATABASE_URL` existe (App Settings) → `database.py` conecta ao Azure SQL
- Nenhuma alteração no código. A variável de ambiente decide o banco.

### Passo 5 — Atualizar requirements.txt

Adicione `pyodbc` ao `requirements.txt`. O arquivo completo:

```txt
fastapi
uvicorn[standard]
sqlalchemy
alembic
pyodbc
```

O `pyodbc` é o driver que conecta Python ao Azure SQL (SQL Server). O Azure App Service Linux já tem o ODBC Driver 18 pré-instalado.

---

## Parte 3: Deploy

### Passo 6 — Fazer deploy

1. No VS Code: `Ctrl+Shift+P` → **Azure App Service: Deploy to Web App**
2. Selecione seu App Service
3. Confirme e aguarde (3-5 minutos)
4. Verifique se o startup command está como: `python startup.py`
   - App Service → Configuration → General Settings → Startup Command

As tabelas serão criadas automaticamente pelo `Base.metadata.create_all()` quando a app iniciar pela primeira vez no Azure.

---

## Parte 4: Testar em Produção

### Passo 7 — Criar arquivo de testes para Azure

Crie ou atualize o arquivo `test_azure.http` (substitua a URL pela sua):

```http
### ==========================================
### TESTES API CAMPUSTRADE — AZURE PRODUÇÃO
### ==========================================

### SUBSTITUA pela sua URL real!
@azureUrl = https://campustrade-seunome.azurewebsites.net


### 1. Health check
GET {{azureUrl}}/health

### 2. Swagger (abra no navegador para ver)
GET {{azureUrl}}/docs

### 3. Listar produtos (vazio no primeiro acesso)
GET {{azureUrl}}/produtos

### 4. Criar primeiro produto
POST {{azureUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Livro de Algoritmos",
    "descricao": "Cormen et al., 3ª edição. Usado mas em ótimo estado.",
    "preco": 120.00,
    "categoria": "Livros",
    "vendedor": "Maria Santos"
}

### 5. Criar segundo produto
POST {{azureUrl}}/produtos
Content-Type: application/json

{
    "titulo": "Calculadora HP 12C",
    "descricao": "Calculadora financeira, funciona perfeitamente. Com capa.",
    "preco": 200.00,
    "categoria": "Eletrônicos",
    "vendedor": "Carlos Lima"
}

### 6. Listar produtos criados
GET {{azureUrl}}/produtos

### 7. Buscar por ID
GET {{azureUrl}}/produtos/1

### 8. Atualizar produto
PUT {{azureUrl}}/produtos/1
Content-Type: application/json

{
    "preco": 95.00
}

### 9. Verificar atualização
GET {{azureUrl}}/produtos/1

### 10. Deletar produto
DELETE {{azureUrl}}/produtos/2

### 11. Verificar lista final
GET {{azureUrl}}/produtos
```

### Passo 8 — Executar os testes

Execute os testes na ordem e verifique:

- Teste 1: Health check responde ✅
- Teste 3: Lista vazia (primeiro acesso, banco novo) ✅
- Testes 4-5: POST retorna 201 com id e criado_em ✅
- Teste 6: GET lista os produtos criados ✅
- Testes 8-9: PUT atualiza o preço ✅
- Testes 10-11: DELETE remove, lista reduzida ✅

Se tudo funciona, sua API está em produção com banco real! 🎉

> 💡 **Diferença importante:** na Oficina 3, se você parava o servidor os dados sumiam (SQLite era recriado). Agora os dados estão no Azure SQL — sobrevivem a restarts, redeploys e até recriação do App Service.

---

## 🔧 Troubleshooting

**"A API não responde no Azure"**

- Verifique se o deploy completou (3-5 min)
- Verifique o startup command: `python startup.py`
- No portal: App Service → Log Stream para ver logs em tempo real

**"pyodbc.OperationalError: Login failed"**

- Verifique se a senha na connection string está correta
- Verifique se o nome do servidor está certo (seuserver.database.windows.net)

**"Cannot open server requested by the login"**

- O database name na URL pode estar errado
- Verifique no portal: SQL Database → nome exato

**"Tabela não existe no Azure"**

- O `create_all()` no main.py cria automaticamente. Reinicie o App Service.
- Se não funcionar: App Service → SSH → `python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"`

**"Connection refused / timeout"**

- Verifique se o firewall tem "Allow Azure services" marcado
- Lembre: da rede da faculdade você NÃO consegue conectar direto — só o App Service acessa

**"ODBC Driver not found" (local, no Windows)**

- O App Service Linux já tem o driver pré-instalado
- Se quiser testar Azure SQL localmente (de casa): instale o driver de https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

---

## 📁 Estrutura Final do Projeto

```
campustrade-api/
├── venv/
├── migrations/
│   ├── versions/
│   │   └── xxxx_criar_tabela_produtos.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── database.py
├── models.py
├── main.py
├── schemas.py
├── startup.py
├── requirements.txt        ← ATUALIZADO (+ pyodbc)
├── test_api.http           ← testes locais
├── test_azure.http         ← testes Azure (NOVO)
├── local.db                ← banco local (no .gitignore)
└── .gitignore
```
