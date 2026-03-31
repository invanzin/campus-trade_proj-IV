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