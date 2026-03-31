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