import sys
import subprocess
import os

if __name__ == "__main__":
    # Garante que estamos rodando a partir do diretório onde o arquivo app.py reside
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")
    
    print("=" * 60)
    print("🧠 Inicializando o Sistema de Pensamentos Automáticos (RPA) 🧠")
    print(f"Diretório: {current_dir}")
    print(f"Executando: {app_path}")
    print("=" * 60)
    
    try:
        # Executa: python -m streamlit run app.py no diretorio correto
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], cwd=current_dir)
    except KeyboardInterrupt:
        print("\n[!] Aplicativo encerrado pelo usuário.")
    except Exception as e:
        print(f"\n[X] Erro ao iniciar o aplicativo: {e}")
        print("Certifique-se de que o streamlit está instalado rodando: pip install -r requirements.txt")
