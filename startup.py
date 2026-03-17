import subprocess
import sys

def main():
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",  # Mudança aqui: pasta.arquivo:variável_fastapi
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

if __name__ == "__main__":
    main()