import os
import sys

from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import EmporioAgente  # noqa: E402


def main():
    print("=" * 60)
    print("    🎸 EMPÓRIO DA MÚSICA - ATENDIMENTO VIRTUAL (CLI) 🥁    ")
    print("=" * 60)
    print("Digite 'sair' para encerrar.\n")

    try:
        agente = EmporioAgente()
    except Exception as e:  # noqa: BLE001
        print(f"Erro ao inicializar o agente: {e}")
        return

    print("Atendente: Fala! Aqui é o assistente da Empório da Música. Como posso ajudar? 🎵\n")
    while True:
        try:
            entrada = input("Cliente: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nAtendimento encerrado.")
            break
        if entrada.lower() in ("sair", "exit"):
            print("\nAtendente: Valeu por passar aqui! Boas notas! 🎵")
            break
        if not entrada:
            continue
        print(f"\nAtendente: {agente.responder(entrada)}\n" + "-" * 50)


if __name__ == "__main__":
    main()