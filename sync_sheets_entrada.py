"""Sincronizador da aba Entrada_Bruta no Google Sheets (Opção 3).

Lê textos colados em massa na aba 'Entrada_Bruta' do Google Sheets,
processa cada acionamento com o extrator oficial (extract_record),
anexa as linhas estruturadas na aba 'Assistencias' e atualiza o status
na aba 'Entrada_Bruta'.

Uso:
    python sync_sheets_entrada.py
    python sync_sheets_entrada.py --criar-aba
"""

import argparse
from datetime import datetime
import os
import sys

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura encoding UTF-8 para o console do Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from extractor.extractor import extract_record
from sheets.writer import _authorized_client, append_rows

TAB_ENTRADA = "Entrada_Bruta"
TAB_DESTINO = os.environ.get("GOOGLE_SHEET_TAB") or "Assistencias"
HEADERS_ENTRADA = [
    "Texto Bruto do Acionamento",
    "Status",
    "Data Processamento",
    "Cliente Identificado",
    "Assistencia",
]


def setup_entrada_tab(sheet):
    """Garante que a aba Entrada_Bruta exista com os cabeçalhos corretos."""
    existing_titles = [ws.title for ws in sheet.worksheets()]
    if TAB_ENTRADA not in existing_titles:
        print(f"📄 Criando aba '{TAB_ENTRADA}' no Google Sheets...")
        ws = sheet.add_worksheet(title=TAB_ENTRADA, rows=1000, cols=10)
        ws.append_row(HEADERS_ENTRADA, value_input_option="USER_ENTERED")
        print(f"✅ Aba '{TAB_ENTRADA}' criada com sucesso com cabeçalhos.")
        return ws

    ws = sheet.worksheet(TAB_ENTRADA)
    rows = ws.get_all_values()
    if not rows or not rows[0]:
        ws.append_row(HEADERS_ENTRADA, value_input_option="USER_ENTERED")
    return ws


def sync_entrada():
    """Lê linhas não processadas em Entrada_Bruta e transfere para Assistencias."""
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("❌ Erro: GOOGLE_SHEET_ID não configurado no .env.")
        return

    print("=" * 70)
    print("🔄 SINCRONIZADOR GOOGLE SHEETS — ENTRADA BRUTA -> ASSISTÊNCIAS")
    print("=" * 70)

    client = _authorized_client()
    sheet = client.open_by_key(sheet_id)
    ws_entrada = setup_entrada_tab(sheet)

    rows = ws_entrada.get_all_values()
    if len(rows) <= 1:
        print(f"ℹ️ Nenhum dado para processar na aba '{TAB_ENTRADA}'. Cole textos na coluna A para sincronizar.")
        return

    novos_registros = []
    updates_status = []  # (linha, status, data, cliente, assistencia)

    print(f"📊 Analisando {len(rows) - 1} linha(s) em '{TAB_ENTRADA}'...")

    for idx, row in enumerate(rows[1:], start=2):
        texto = row[0].strip() if len(row) > 0 else ""
        status_atual = row[1].strip() if len(row) > 1 else ""

        # Pula linhas vazias ou já processadas
        if not texto or status_atual.startswith("Processado"):
            continue

        rec = extract_record(texto)
        prod = rec.get("PRODUTO", "unknown")
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")

        if prod == "unknown":
            status_desc = "Revisão Manual (Produto desconhecido)"
        else:
            status_desc = f"Processado ({prod.upper()})"
            novos_registros.append(rec)

        updates_status.append({
            "range": f"B{idx}:E{idx}",
            "values": [[
                status_desc,
                agora,
                rec.get("CLIENTE", ""),
                rec.get("ASSISTENCIA", ""),
            ]],
        })

    if not updates_status:
        print("✅ Todas as linhas de Entrada_Bruta já estão processadas.")
        return

    # Gravação em lote na aba Assistencias
    if novos_registros:
        print(f"🚀 Gravando {len(novos_registros)} nova(s) assistência(s) na aba '{TAB_DESTINO}'...")
        res = append_rows(novos_registros, tab=TAB_DESTINO)
        if res.get("ok"):
            print(f"✅ {res.get('total_inseridas')} linha(s) gravada(s) na aba '{TAB_DESTINO}' (Linha final: {res.get('linha_final')}).")
        else:
            print(f"❌ Erro ao gravar na aba '{TAB_DESTINO}': {res.get('erro')}")
            return

    # Atualiza os status na aba Entrada_Bruta em lote
    print("📝 Atualizando status na aba 'Entrada_Bruta'...")
    ws_entrada.batch_update(updates_status, value_input_option="USER_ENTERED")
    print(f"🎉 Sincronização concluída! {len(updates_status)} linha(s) atualizada(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincronizador de Entrada Bruta no Google Sheets.")
    parser.add_argument("--criar-aba", action="store_true", help="Cria a aba Entrada_Bruta se não existir.")
    args = parser.parse_args()

    sync_entrada()
