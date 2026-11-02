import os
import google.generativeai as genai
from src.tools import buscar_produtos, buscar_promocoes, consultar_pedido, consultar_politicas

# Configura a chave da API do Gemini obtida da variável de ambiente
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """
Você é o assistente virtual oficial da 'Empório da Música', uma loja especializada em instrumentos musicais localizada em Campo Grande/MS (fundada em 2008).
Sua persona: informal mas profissional, acolhedor, como um amigo que entende muito de música. Evite linguagem excessivamente robotizada.

Diretrizes obrigatórias:
1. Escopo de produtos: Trabalhamos EXCLUSIVAMENTE com instrumentos musicais (guitarras, baixos, violões, baterias, teclados, sopros, cordas orquestrais e ukuleles). NÃO comercializamos acessórios (cordas, palhetas, cabos, cases, pedais, amplificadores). Se o cliente pedir acessórios, redirecione educadamente informando que focamos apenas em instrumentos.
2. Precisão de dados: Nunca invente preços, estoque, status de pedidos ou regras. Sempre utilize as informações reais das ferramentas ou do manual de políticas da loja.
3. Formas de pagamento e políticas: Consulte o manual de políticas para responder dúvidas sobre prazos de troca, garantia, frete e formas de pagamento (PIX com 5% de desconto, parcelamento em até 12x no cartão, etc.).
"""

class EmporioAgente:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="models/gemini-3.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        self.chat = self.model.start_chat(history=[])
        self.politicas_texto = consultar_politicas()

    def responder(self, mensagem_usuario: str) -> str:
        """Função que processa a mensagem do cliente injetando dados formatados do catálogo, promoções e políticas."""
        contexto_extra = ""
        msg_lower = mensagem_usuario.lower()
        
        # Injeta produtos se houver menção a instrumentos ou preços
        if any(termo in msg_lower for termo in ["violao", "violão", "guitarra", "baixo", "bateria", "teclado", "preco", "preço", "custa", "quanto", "disponivel", "disponível", "opcao", "opção", "catalogo", "catálogo"]):
            produtos = buscar_produtos()
            if isinstance(produtos, list):
                lista_prod = "\n".join([
                    f"- ID {p.get('product_id')}: {p.get('name', 'Item')} | R$ {p.get('price_brl', 'N/A')} (Estoque: {p.get('stock_quantity', 'N/A')})" 
                    for p in produtos
                ])
                contexto_extra += f"\n[Catálogo de Produtos Disponíveis:\n{lista_prod}\n]\n"

        # Injeta promoções se houver menção a desconto ou oferta
        if any(termo in msg_lower for termo in ["promocao", "promoção", "desconto", "oferta", "liquidacao", "liquidação", "black friday"]):
            promocoes = buscar_promocoes()
            contexto_extra += f"\n[Promoções e Descontos Ativos:\n{str(promocoes)}\n]\n"

        # Injeta pedidos se houver menção a status ou rastreio
        if any(termo in msg_lower for termo in ["pedido", "status", "entrega", "rastreio", "@"]):
            # Extrai termos que pareçam e-mail ou ID para consulta na ferramenta
            palavras = mensagem_usuario.split()
            for palavra in palavras:
                if "@" in palavra or palavra.isdigit():
                    res_pedido = consultar_pedido(palavra)
                    contexto_extra += f"\n[Dados do Pedido Consultado ({palavra}):\n{str(res_pedido)}\n]\n"
                    break

        # Injeta políticas se houver menção a regras da loja
        if any(termo in msg_lower for termo in ["troca", "devolucao", "devolução", "garantia", "frete", "pagamento", "horario", "horário", "endereco", "endereço", "parcela"]):
            contexto_extra += f"\n[Trecho das Políticas da Loja:\n{self.politicas_texto[:2500]}\n]\n"

        prompt_final = f"{contexto_extra}\nMensagem do Cliente: {mensagem_usuario}"

        try:
            response = self.chat.send_message(prompt_final)
            return response.text
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"