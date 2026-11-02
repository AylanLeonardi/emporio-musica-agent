import os
import pandas as pd
from pypdf import PdfReader

# Caminho absoluto para a pasta data na raiz do projeto
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

def buscar_produtos(termo_busca: str = None):
    """Função para buscar produtos no catálogo nome, marca ou categoria"""
    try:
        # Encontra o arquivo correto do produto independentemente do prefixo exato
        prod_file = [f for f in os.listdir(DATA_DIR) if 'products.csv' in f][0]
        df = pd.read_csv(os.path.join(DATA_DIR, prod_file))
        
        if termo_busca:
            # Filtra por nome ignorando maiúsculas/minúsculas
            res = df[df['name'].str.contains(termo_busca, case=False, na=False)]
            if res.empty:
                return "Nenhum instrumento encontrado com esse termo."
            return res.to_dict(orient='records')
        return df.to_dict(orient='records')
    except Exception as e:
        return {"erro": str(e)}

def consultar_pedido(order_id: str):
    """Função para consultar o status de um pedido específico pelo ID"""
    try:
        orders_file = [f for f in os.listdir(DATA_DIR) if 'orders.csv' in f][0]
        df = pd.read_csv(os.path.join(DATA_DIR, orders_file))
        
        pedido = df[df['order_id'].astype(str) == str(order_id)]
        if pedido.empty:
            return {"erro": "Pedido não encontrado no sistema."}
        return pedido.to_dict(orient='records')[0]
    except Exception as e:
        return {"erro": str(e)}

def consultar_politicas():
    """Função para extrair o texto completo do manual de políticas e procedimentos da loja em PDF"""
    try:
        pdf_path = os.path.join(DATA_DIR, 'políticas_da_loja.pdf')
        reader = PdfReader(pdf_path)
        txt_pol = ""
        for page in reader.pages:
            txt_pol += page.extract_text() + "\n"
        return txt_pol
    except Exception as e:
        return f"Erro ao ler políticas: {str(e)}"