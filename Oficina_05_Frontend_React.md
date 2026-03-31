# Oficina 5: Frontend React — Consumindo a API CampusTrade

**Disciplina:** IBM8942 — Projeto em Ciência de Dados IV  
**Aula:** Oficina 5 — Frontend e Integração  

---

## O que vamos construir hoje

Um frontend React que consome a API CampusTrade. Ao final, você terá:

- Listagem de produtos em cards visuais
- Formulário para cadastrar novos produtos (com select de categorias)
- Botões para deletar produtos
- Tudo conectado à API via fetch

> Vamos rodar dois servidores simultâneos: a API FastAPI (porta 8000) e o React (porta 5173). O React faz fetch para a API.

---

## Pré-requisitos

- [ ] **Node.js 18+** instalado (`node --version`)
- [ ] **npm** funcional (`npm --version`)
- [ ] **API CampusTrade** rodando local (`uvicorn main:app --reload` na porta 8000)
- [ ] Pelo menos **2 categorias criadas** na API (via Swagger ou REST Client)

Se não tem categorias criadas, abra http://localhost:8000/docs e crie pelo menos:
- Livros (POST /categorias com `{"nome": "Livros", "descricao": "Livros didáticos"}`)
- Eletrônicos (POST /categorias com `{"nome": "Eletrônicos", "descricao": "Gadgets e periféricos"}`)

---

## Parte 1: Criando o Projeto React

### Passo 1 — Criar o projeto com Vite

Abra um **novo terminal** (não feche o da API!) e execute:

```bash
npm create vite@latest campustrade-frontend -- --template react
```

Entre na pasta e instale as dependências:

```bash
cd campustrade-frontend
npm install
```

Teste se funciona:

```bash
npm run dev
```

Abra http://localhost:5173 no navegador. Você verá a página padrão do Vite com o logo do React girando.

Pare o servidor (`Ctrl+C`) — vamos substituir o conteúdo.

### Passo 2 — Limpar o projeto

Vamos remover o conteúdo padrão e começar do zero.

**Delete os seguintes arquivos:**
- `src/App.css`
- `src/assets/` (pasta inteira)

**Substitua o conteúdo de `src/index.css`** por:

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f7fa;
  color: #2c3e50;
}
```

Isso dá um reset básico e define a fonte e cores que vamos usar.

---

## Parte 2: Configurando a Conexão com a API

### Passo 3 — Criar o arquivo de configuração da API

Crie o arquivo `src/api.js`:

```javascript
// URL base da API — mude para a URL do Azure em produção
const API_URL = "http://localhost:8000";

// --- Categorias ---

export async function listarCategorias() {
  const response = await fetch(`${API_URL}/categorias`);
  if (!response.ok) throw new Error("Erro ao buscar categorias");
  return response.json();
}

export async function criarCategoria(dados) {
  const response = await fetch(`${API_URL}/categorias`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });
  if (!response.ok) {
    const erro = await response.json();
    throw new Error(erro.detail || "Erro ao criar categoria");
  }
  return response.json();
}

// --- Produtos ---

export async function listarProdutos() {
  const response = await fetch(`${API_URL}/produtos`);
  if (!response.ok) throw new Error("Erro ao buscar produtos");
  return response.json();
}

export async function criarProduto(dados) {
  const response = await fetch(`${API_URL}/produtos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });
  if (!response.ok) {
    const erro = await response.json();
    throw new Error(erro.detail || "Erro ao criar produto");
  }
  return response.json();
}

export async function deletarProduto(id) {
  const response = await fetch(`${API_URL}/produtos/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Erro ao deletar produto");
  return response.json();
}
```

**Por que separar em um arquivo?**

- Se a URL da API mudar (ex: ir para Azure), você muda em **um lugar só**
- Os componentes ficam mais limpos — só chamam `listarProdutos()`, sem saber os detalhes do fetch
- Tratamento de erros centralizado

---

## Parte 3: Criando os Componentes

### Passo 4 — Criar a pasta de componentes

```bash
mkdir src/components
```

### Passo 5 — Componente Header

Crie `src/components/Header.jsx`:

```jsx
function Header({ totalProdutos }) {
  return (
    <header style={{
      backgroundColor: "#003366",
      color: "white",
      padding: "20px 40px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
    }}>
      <div>
        <h1 style={{ margin: 0, fontSize: "24px" }}>CampusTrade</h1>
        <p style={{ margin: 0, fontSize: "14px", color: "#F2A900" }}>
          Marketplace Universitário
        </p>
      </div>
      <div style={{
        backgroundColor: "#F2A900",
        color: "#003366",
        padding: "8px 16px",
        borderRadius: "20px",
        fontWeight: "bold",
        fontSize: "14px",
      }}>
        {totalProdutos} produto{totalProdutos !== 1 ? "s" : ""}
      </div>
    </header>
  );
}

export default Header;
```

**Conceitos aplicados:**
- Recebe `totalProdutos` via props
- Estilos inline com objetos JavaScript (padrão React)
- Expressão ternária para plural: "1 produto" vs "2 produtos"

### Passo 6 — Componente CardProduto

Crie `src/components/CardProduto.jsx`:

```jsx
function CardProduto({ produto, onDeletar }) {
  return (
    <div style={{
      backgroundColor: "white",
      borderRadius: "8px",
      padding: "20px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
      display: "flex",
      flexDirection: "column",
      gap: "8px",
    }}>
      {/* Categoria badge */}
      {produto.categoria_rel && (
        <span style={{
          backgroundColor: "#e8f4f8",
          color: "#1a5276",
          padding: "4px 10px",
          borderRadius: "12px",
          fontSize: "12px",
          fontWeight: "bold",
          alignSelf: "flex-start",
        }}>
          {produto.categoria_rel.nome}
        </span>
      )}

      <h3 style={{ margin: 0, color: "#003366" }}>{produto.titulo}</h3>
      <p style={{ color: "#5d6d7e", fontSize: "14px", margin: 0 }}>
        {produto.descricao}
      </p>

      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginTop: "8px",
      }}>
        <span style={{
          fontSize: "20px",
          fontWeight: "bold",
          color: "#F2A900",
        }}>
          R$ {produto.preco.toFixed(2)}
        </span>
        <span style={{ fontSize: "13px", color: "#6b7b8d" }}>
          por {produto.vendedor}
        </span>
      </div>

      <button
        onClick={() => onDeletar(produto.id)}
        style={{
          marginTop: "8px",
          padding: "8px",
          backgroundColor: "#fadbd8",
          color: "#e74c3c",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          fontSize: "13px",
        }}
      >
        Remover
      </button>
    </div>
  );
}

export default CardProduto;
```

**Conceitos aplicados:**
- Recebe `produto` (dados) e `onDeletar` (função callback) via props
- Renderização condicional: `{produto.categoria_rel && ...}` — só mostra badge se tiver categoria
- `onClick` chama a função do pai com o ID do produto

### Passo 7 — Componente FormularioProduto

Crie `src/components/FormularioProduto.jsx`:

```jsx
import { useState } from "react";

function FormularioProduto({ categorias, onProdutoCriado }) {
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [preco, setPreco] = useState("");
  const [categoriaId, setCategoriaId] = useState("");
  const [vendedor, setVendedor] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setEnviando(true);

    try {
      const dados = {
        titulo,
        descricao,
        preco: parseFloat(preco),
        categoria_id: categoriaId ? parseInt(categoriaId) : null,
        vendedor,
      };

      await onProdutoCriado(dados);

      // Limpar formulário após sucesso
      setTitulo("");
      setDescricao("");
      setPreco("");
      setCategoriaId("");
      setVendedor("");
    } catch (error) {
      setErro(error.message);
    } finally {
      setEnviando(false);
    }
  }

  const inputStyle = {
    width: "100%",
    padding: "10px",
    border: "1px solid #e8ecf0",
    borderRadius: "4px",
    fontSize: "14px",
  };

  return (
    <div style={{
      backgroundColor: "white",
      borderRadius: "8px",
      padding: "24px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
    }}>
      <h2 style={{ margin: "0 0 16px 0", color: "#003366", fontSize: "18px" }}>
        Novo Produto
      </h2>

      {erro && (
        <div style={{
          backgroundColor: "#fadbd8",
          color: "#e74c3c",
          padding: "10px",
          borderRadius: "4px",
          marginBottom: "12px",
          fontSize: "14px",
        }}>
          {erro}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <input
          style={inputStyle}
          placeholder="Título do produto"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          required
          minLength={3}
        />

        <textarea
          style={{ ...inputStyle, minHeight: "60px", resize: "vertical" }}
          placeholder="Descrição detalhada (mínimo 10 caracteres)"
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          required
          minLength={10}
        />

        <div style={{ display: "flex", gap: "12px" }}>
          <input
            style={{ ...inputStyle, flex: 1 }}
            placeholder="Preço (R$)"
            type="number"
            step="0.01"
            min="0.01"
            value={preco}
            onChange={(e) => setPreco(e.target.value)}
            required
          />
          <select
            style={{ ...inputStyle, flex: 1 }}
            value={categoriaId}
            onChange={(e) => setCategoriaId(e.target.value)}
          >
            <option value="">Sem categoria</option>
            {categorias.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.nome}
              </option>
            ))}
          </select>
        </div>

        <input
          style={inputStyle}
          placeholder="Nome do vendedor"
          value={vendedor}
          onChange={(e) => setVendedor(e.target.value)}
          required
          minLength={2}
        />

        <button
          type="submit"
          disabled={enviando}
          style={{
            padding: "12px",
            backgroundColor: enviando ? "#b0b0b0" : "#003366",
            color: "white",
            border: "none",
            borderRadius: "4px",
            fontSize: "15px",
            fontWeight: "bold",
            cursor: enviando ? "not-allowed" : "pointer",
          }}
        >
          {enviando ? "Cadastrando..." : "Cadastrar Produto"}
        </button>
      </form>
    </div>
  );
}

export default FormularioProduto;
```

**Conceitos aplicados:**
- Um `useState` para cada campo do formulário (controlled components)
- `handleSubmit` com `e.preventDefault()` (evita recarregar a página)
- Tratamento de erro com `try/catch`
- Estado `enviando` para desabilitar o botão enquanto processa
- Select populado com categorias recebidas via props
- Limpa campos após sucesso

---

## Parte 4: Montando o App Principal

### Passo 8 — Reescrever App.jsx

Substitua o conteúdo de `src/App.jsx`:

```jsx
import { useState, useEffect } from "react";
import Header from "./components/Header";
import CardProduto from "./components/CardProduto";
import FormularioProduto from "./components/FormularioProduto";
import {
  listarProdutos,
  listarCategorias,
  criarProduto,
  deletarProduto,
} from "./api";

function App() {
  const [produtos, setProdutos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState("");

  // Carregar dados ao montar o componente
  useEffect(() => {
    carregarDados();
  }, []);

  async function carregarDados() {
    try {
      setLoading(true);
      const [prods, cats] = await Promise.all([
        listarProdutos(),
        listarCategorias(),
      ]);
      setProdutos(prods);
      setCategorias(cats);
      setErro("");
    } catch (error) {
      setErro("Erro ao carregar dados. Verifique se a API está rodando.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCriarProduto(dados) {
    const novo = await criarProduto(dados);
    // Recarrega a lista para pegar o produto com categoria_rel populado
    await carregarDados();
  }

  async function handleDeletarProduto(id) {
    if (!window.confirm("Tem certeza que deseja remover este produto?")) return;
    try {
      await deletarProduto(id);
      setProdutos(produtos.filter((p) => p.id !== id));
    } catch (error) {
      setErro("Erro ao deletar produto.");
    }
  }

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <p style={{ fontSize: "18px", color: "#6b7b8d" }}>Carregando CampusTrade...</p>
      </div>
    );
  }

  return (
    <div>
      <Header totalProdutos={produtos.length} />

      {erro && (
        <div style={{
          backgroundColor: "#fadbd8",
          color: "#e74c3c",
          padding: "12px 40px",
          textAlign: "center",
        }}>
          {erro}
        </div>
      )}

      <main style={{
        maxWidth: "1100px",
        margin: "24px auto",
        padding: "0 24px",
        display: "grid",
        gridTemplateColumns: "1fr 2fr",
        gap: "24px",
        alignItems: "start",
      }}>
        {/* Coluna esquerda: formulário */}
        <FormularioProduto
          categorias={categorias}
          onProdutoCriado={handleCriarProduto}
        />

        {/* Coluna direita: lista de produtos */}
        <div>
          <h2 style={{ margin: "0 0 16px 0", color: "#003366" }}>
            Produtos Disponíveis
          </h2>

          {produtos.length === 0 ? (
            <div style={{
              backgroundColor: "white",
              borderRadius: "8px",
              padding: "40px",
              textAlign: "center",
              color: "#6b7b8d",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            }}>
              <p style={{ fontSize: "40px", marginBottom: "8px" }}>📦</p>
              <p>Nenhum produto cadastrado ainda.</p>
              <p style={{ fontSize: "14px" }}>Use o formulário ao lado para criar o primeiro!</p>
            </div>
          ) : (
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
              gap: "16px",
            }}>
              {produtos.map((produto) => (
                <CardProduto
                  key={produto.id}
                  produto={produto}
                  onDeletar={handleDeletarProduto}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
```

**Conceitos aplicados:**
- `useEffect` com `[]` para carregar dados ao montar
- `Promise.all` para buscar produtos e categorias em paralelo
- Estado `loading` para tela de carregamento
- `handleCriarProduto` recarrega a lista após criar (para pegar o `categoria_rel`)
- `handleDeletarProduto` com confirmação e atualização otimista (remove do array local)
- CSS Grid para layout responsivo em duas colunas
- Estado vazio tratado com mensagem visual

---

## Parte 5: Testando

### Passo 9 — Rodar tudo junto

Você precisa de **dois terminais abertos**:

**Terminal 1 — API:**
```bash
cd campustrade-api
uvicorn main:app --reload
```

**Terminal 2 — React:**
```bash
cd campustrade-frontend
npm run dev
```

Abra http://localhost:5173 no navegador.

### Passo 10 — Testar o fluxo completo

1. A página deve carregar e mostrar "Nenhum produto cadastrado" (ou produtos existentes)
2. Preencha o formulário e clique "Cadastrar Produto"
3. O produto deve aparecer na lista com o badge da categoria
4. Clique em "Remover" em um produto e confirme
5. O produto desaparece da lista

> Abra o DevTools do navegador (F12) → aba Network para ver as requisições fetch saindo para a API.

---

## Troubleshooting

**"Erro ao carregar dados. Verifique se a API está rodando."**
- Confirme que a API está rodando em http://localhost:8000
- Teste: abra http://localhost:8000/health no navegador

**Erro de CORS no console do navegador**
- Verifique se o `main.py` da API tem o CORSMiddleware configurado
- O `allow_origins=["*"]` deve estar presente

**"Categorias não aparecem no select"**
- Crie categorias via Swagger (http://localhost:8000/docs) antes de usar o frontend
- POST /categorias com `{"nome": "Livros"}`

**"npm create vite" dá erro**
- Atualize o npm: `npm install -g npm@latest`
- Ou tente: `npx create-vite@latest campustrade-frontend --template react`

**A página não atualiza ao mudar código**
- O Vite tem hot reload. Se não funcionar, pare e rode `npm run dev` novamente

---

## Estrutura Final

```
campustrade-frontend/
├── node_modules/           ← dependências (gerado pelo npm)
├── public/
├── src/
│   ├── components/
│   │   ├── Header.jsx      ← cabeçalho com contador
│   │   ├── CardProduto.jsx  ← card individual de produto
│   │   └── FormularioProduto.jsx  ← formulário de cadastro
│   ├── api.js               ← funções de fetch (centralizado)
│   ├── App.jsx              ← componente principal
│   ├── main.jsx             ← ponto de entrada (não alterar)
│   └── index.css            ← estilos globais
├── index.html
├── package.json
└── vite.config.js
```
