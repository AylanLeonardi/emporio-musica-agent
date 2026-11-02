import os
import pandas as pd
from pypdf import PdfReader

# Caminho absoluto para a pasta data na raiz do projeto
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

def buscar_produtos(termo_busca: str = None):
    """Função para buscar produtos e cruza automaticamente com promocoes ativas"""
    try:
        prod_file = [f for f in os.listdir(DATA_DIR) if 'products.csv' in f][0]
        df_prod = pd.read_csv(os.path.join(DATA_DIR, prod_file))
        
        # Tenta carregar promocoes ativas
        try:
            promo_file = [f for f in os.listdir(DATA_DIR) if 'promotions.csv' in f][0]
            df_promo = pd.read_csv(os.path.join(DATA_DIR, promo_file))
            if 'is_active' in df_promo.columns:
                df_promo = df_promo[df_promo['is_active'] == 1]
            df_prod = df_prod.merge(df_promo[['product_id', 'discount_percent', 'description']], on='product_id', how='left')
        except Exception:
            pass

        if termo_busca:
            res = df_prod[df_prod['name'].str.contains(termo_busca, case=False, na=False)]
            if res.empty:
                return "Nenhum instrumento encontrado com esse termo."
            return res.to_dict(orient='records')
            
        return df_prod.to_dict(orient='records')
    except Exception as e:
        return {"erro": str(e)}

def buscar_promocoes():
    """Função para listar promoções e descontos ativos no sistema"""
    try:
        promo_file = [f for f in os.listdir(DATA_DIR) if 'promotions.csv' in f][0]
        df = pd.read_csv(os.path.join(DATA_DIR, promo_file))
        
        # Filtra apenas promoções ativas (is_active == 1) se houver a coluna, ou retorna todas
        if 'is_active' in df.columns:
            df_ativas = df[df['is_active'] == 1]
            if df_ativas.empty:
                return "Não há promoções ativas no momento."
            return df_ativas.to_dict(orient='records')
        return df.to_dict(orient='records')
    except Exception as e:
        return {"erro": str(e)}

def consultar_pedido(parametro_busca: str):
    """Função para consultar o status de um pedido pelo ID do pedido ou pelo e-mail do cliente"""
    try:
        orders_file = [f for f in os.listdir(DATA_DIR) if 'orders.csv' in f][0]
        df_orders = pd.read_csv(os.path.join(DATA_DIR, orders_file))
        
        param_str = str(parametro_busca).strip().lower()
        
        # Se for um e-mail, tenta cruzar com a tabela de clientes se existir
        if "@" in param_str:
            try:
                cust_file = [f for f in os.listdir(DATA_DIR) if 'customers.csv' in f][0]
                df_cust = pd.read_csv(os.path.join(DATA_DIR, cust_file))
                cliente = df_cust[df_cust['email'].str.lower() == param_str]
                if not cliente.empty:
                    cust_id = cliente.iloc[0]['customer_id']
                    pedidos = df_orders[df_orders['customer_id'].astype(str) == str(cust_id)]
                    if not pedidos.empty:
                        return pedidos.to_dict(orient='records')
            except Exception:
                pass
            return {"erro": "Nenhum pedido encontrado para este e-mail."}
            
        # Caso contrário, busca direto pelo order_id
        pedido = df_orders[df_orders['order_id'].astype(str) == param_str]
        if pedido.empty:
            return {"erro": "Pedido não encontrado no sistema."}
        return pedido.to_dict(orient='records')[0]
    except Exception as e:
        return {"erro": str(e)}

def consultar_politicas():
    """Função para extrair o texto completo do manual de políticas da loja em PDF"""
    try:
        pdf_path = os.path.join(DATA_DIR, 'políticas_da_loja.pdf')
        reader = PdfReader(pdf_path)
        txt_pol = ""
        for page in reader.pages:
            txt_pol += page.extract_text() + "\n"
        return txt_pol
    except Exception as e:
        return f"Erro ao ler políticas: {str(e)}"