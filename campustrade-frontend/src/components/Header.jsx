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