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