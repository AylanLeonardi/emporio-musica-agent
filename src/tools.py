"""Ferramentas (function calling) e carregamento de dados do agente Empório da Música.

Todas as funções públicas retornam dicts/listas simples (JSON-serializáveis), pois
o SDK do Gemini as expõe ao modelo como ferramentas chamáveis.
"""
import glob
import json
import os
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import pandas as pd
from pypdf import PdfReader

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

STATUS_PEDIDO = {
    "pending": "Pendente (aguardando confirmação de pagamento)",
    "confirmed": "Confirmado (em preparação para envio)",
    "shipped": "Enviado (a caminho)",
    "delivered": "Entregue",
    "cancelled": "Cancelado",
}
STATUS_PRODUTO = {
    "active": "ativo",
    "discontinued": "descontinuado (fora do catálogo)",
    "coming_soon": "em breve (ainda não disponível para compra)",
}


###################################################### utilidades ######################################################
def _norm(texto) -> str:
    """minúsculas + sem acentos, para buscas tolerantes ('violao' acha 'Violão')."""
    t = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in t if not unicodedata.combining(c)).lower().strip()


def _arquivo(sufixo: str) -> str:
    achados = sorted(glob.glob(os.path.join(DATA_DIR, f"*{sufixo}")))
    if not achados:
        raise FileNotFoundError(f"Arquivo '*{sufixo}' não encontrado em {os.path.abspath(DATA_DIR)}")
    return achados[0]

@lru_cache(maxsize=1)
def _catalogo() -> pd.DataFrame:
    """Produtos + categoria + promoção ativa já cruzados, com preços finais calculados."""
    prod = pd.read_csv(_arquivo("products.csv"))
    cat = pd.read_csv(_arquivo("categories.csv")).rename(columns={"name": "categoria"})[["category_id", "categoria"]]
    promo = pd.read_csv(_arquivo("promotions.csv"))

    promo = promo[promo["is_active"] == 1]
    # Se houver mais de uma promoção ativa para o mesmo produto, vale a de maior desconto.
    promo = (promo.sort_values("discount_percent", ascending=False)
                  .drop_duplicates("product_id")
                  .rename(columns={"description": "promocao_nome"})
                  [["product_id", "promocao_nome", "discount_percent"]])

    df = prod.merge(cat, on="category_id", how="left").merge(promo, on="product_id", how="left")
    df["discount_percent"] = df["discount_percent"].fillna(0)
    df["preco_final"] = (df["price_brl"] * (1 - df["discount_percent"] / 100)).round(2)
    # Política 6.2: PIX (5%) não é cumulativo com preço promocional.
    df["preco_pix"] = df.apply(
        lambda r: r["preco_final"] if r["discount_percent"] > 0 else round(r["price_brl"] * 0.95, 2), axis=1)
    df["_busca"] = (df["name"] + " " + df["categoria"].fillna("") + " " + df["description"].fillna("")).map(_norm)
    return df


def _parcelas_max(valor: float) -> int:
    """Maior nº de parcelas sem juros respeitando a política 3.1 (parcela mínima por faixa)."""
    melhor = 1
    for n in range(1, 13):
        minimo = 0 if n <= 3 else (80 if n <= 6 else 100)
        if n <= 3 and valor < 50:
            continue
        if valor / n >= minimo:
            melhor = n
    return melhor


###################################################### ferramentas ######################################################
def buscar_produtos(termo: str = "", categoria: str = "", preco_max: float = 0, preco_min: float = 0,
                    apenas_disponiveis: bool = True) -> dict:
    try:
        df = _catalogo()
        if termo:
            tokens = [t for t in re.split(r"\s+", _norm(termo)) if t]
            for t in tokens:
                df = df[df["_busca"].str.contains(re.escape(t), na=False)]
        if categoria:
            df = df[df["categoria"].map(_norm).str.contains(re.escape(_norm(categoria)), na=False)]
        if preco_max and preco_max > 0:
            df = df[df["preco_final"] <= preco_max]
        if preco_min and preco_min > 0:
            df = df[df["preco_final"] >= preco_min]
        if apenas_disponiveis:
            df = df[(df["status"] == "active") & (df["stock_quantity"] > 0)]

        if df.empty:
            return {"encontrados": 0, "produtos": [],
                    "aviso": "Nenhum produto encontrado com esses filtros. Não invente produtos; "
                             "ofereça ajustar a busca (outro termo, faixa de preço ou categoria)."}

        df = df.sort_values("preco_final")
        total = len(df)
        itens = []
        for _, r in df.head(15).iterrows():
            itens.append({
                "id": int(r["product_id"]),
                "nome": r["name"],
                "categoria": r["categoria"],
                "descricao": r["description"],
                "status": STATUS_PRODUTO.get(r["status"], r["status"]),
                "estoque": int(r["stock_quantity"]),
                "preco_tabela_brl": float(r["price_brl"]),
                "em_promocao": bool(r["discount_percent"] > 0),
                "promocao": r["promocao_nome"] if r["discount_percent"] > 0 else None,
                "discount_percent": float(r["discount_percent"]),
                "preco_final_brl": float(r["preco_final"]),
                "preco_pix_brl": float(r["preco_pix"]),
                "parcelamento_max_sem_juros": _parcelas_max(float(r["preco_final"])),
                "specs": r["specs"],
            })
        return {"encontrados": total, "exibindo": len(itens), "produtos": itens}
    except Exception as e:  # noqa: BLE001
        return {"erro": f"Falha ao consultar o catálogo: {e}"}


def listar_promocoes() -> dict:
    try:
        df = _catalogo()
        df = df[(df["discount_percent"] > 0) & (df["status"] == "active")].sort_values("discount_percent", ascending=False)
        if df.empty:
            return {"promocoes": [], "aviso": "Não há promoções ativas no momento."}
        return {"promocoes": [{
            "id": int(r["product_id"]), "nome": r["name"], "promocao": r["promocao_nome"],
            "discount_percent": float(r["discount_percent"]), "preco_tabela_brl": float(r["price_brl"]),
            "preco_final_brl": float(r["preco_final"]), "estoque": int(r["stock_quantity"]),
        } for _, r in df.iterrows()]}
    except Exception as e:  # noqa: BLE001
        return {"erro": f"Falha ao consultar promoções: {e}"}


def consultar_pedidos(email: str, numero_pedido: int = 0) -> dict:
    try:
        email_n = str(email or "").strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email_n):
            return {"erro": "E-mail inválido. Peça ao cliente o e-mail cadastrado na compra."}

        clientes = pd.read_csv(_arquivo("customers.csv"))
        cli = clientes[clientes["email"].str.lower().str.strip() == email_n]
        if cli.empty:
            return {"erro": "Não encontramos cadastro com esse e-mail. Peça para conferir o e-mail usado na compra "
                            "ou sugira falar com a equipe pelo WhatsApp."}
        ids = set(cli["customer_id"])  # e-mail pode (raramente) repetir no cadastro

        pedidos = pd.read_csv(_arquivo("orders.csv"))
        pedidos = pedidos[pedidos["customer_id"].isin(ids)]
        if numero_pedido:
            pedidos = pedidos[pedidos["order_id"] == int(numero_pedido)]
        if pedidos.empty:
            return {"cliente": cli.iloc[0]["name"], "pedidos": [],
                    "aviso": "Nenhum pedido encontrado para este cliente" + (" com esse número." if numero_pedido else ".")}

        itens = pd.read_csv(_arquivo("order_items.csv")).merge(
            _catalogo()[["product_id", "name"]], on="product_id", how="left")

        saida = []
        for _, p in pedidos.sort_values("order_date", ascending=False).iterrows():
            its = itens[itens["order_id"] == p["order_id"]]
            saida.append({
                "numero_pedido": int(p["order_id"]),
                "data": p["order_date"],
                "status": STATUS_PEDIDO.get(p["status"], p["status"]),
                "total_brl": float(p["total_brl"]),
                "forma_pagamento": p["payment_method"],
                "codigo_rastreio": None if pd.isna(p["tracking_code"]) else p["tracking_code"],
                "previsao_entrega": None if pd.isna(p["estimated_delivery"]) else p["estimated_delivery"],
                "observacoes": None if pd.isna(p["notes"]) else p["notes"],
                "itens": [{"produto": r["name"], "quantidade": int(r["quantity"])} for _, r in its.iterrows()],
            })
        return {"cliente": cli.iloc[0]["name"], "pedidos": saida}
    except Exception as e:  # noqa: BLE001
        return {"erro": f"Falha ao consultar pedidos: {e}"}


@lru_cache(maxsize=1)
def carregar_politicas() -> str:
    try:
        pdfs = sorted(glob.glob(os.path.join(DATA_DIR, "*.pdf")))
        if not pdfs:
            return "(Manual de políticas não encontrado.)"
        reader = PdfReader(pdfs[0])
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception as e:  # noqa: BLE001
        return f"(Erro ao ler o manual de políticas: {e})"


FERRAMENTAS = [buscar_produtos, listar_promocoes, consultar_pedidos]