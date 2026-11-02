import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env se existir
load_dotenv()

# Garante que o diretório raiz esteja no path do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import EmporioAgente

def main():
    print("=" * 60)
    print("    🎸 EMPÓRIO DA MÚSICA - ATENDIMENTO VIRTUAL (CLI) 🥁    ")
    print("=" * 60)
    print("Digite 'sair' ou 'exit' a qualquer momento para encerrar.\n")

    # Verifica se a chave da API está configurada
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ ALERTA: A variável de ambiente GEMINI_API_KEY não foi encontrada!")
        print("Defina a variável no seu sistema ou num arquivo .env na raiz do projeto.\n")

    try:
        agnt = EmporioAgente()
        print("Atendente inicializado com sucesso. Como posso ajudar você hoje?\n")
    except Exception as e:
        print(f"Erro ao inicializar o agente: {e}")
        return

    while True:
        try:
            entrada_usuario = input("Cliente: ")
            if entrada_usuario.strip().lower() in ["sair", "exit"]:
                print("\nAtendente: Valeu por conversar com a Empório da Música! Qualquer coisa estamos por aqui. Boas notas! 🎵")
                break
            
            if not entrada_usuario.strip():
                continue

            resposta = agnt.responder(entrada_usuario)
            print(f"\nAtendente: {resposta}\n" + "-" * 50)
            
        except KeyboardInterrupt:
            print("\n\nAtendimento encerrado.")
            break

if __name__ == "__main__":
    main()