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