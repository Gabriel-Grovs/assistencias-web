"""Script CLI de processamento em massa de planilhas de assistências.

Lê um arquivo Excel (.xlsx, .xls) ou CSV contendo textos de mensagens brutas,
aplica o pipeline modular de extração (extractor.extract_record), gera uma
planilha estruturada no schema oficial de 11 colunas e opcionalmente sincroniza
diretamente em lote com o Google Sheets.

Exemplo de uso:
    python processar_planilha.py "C:\\Users\\gabri\\Downloads\\plan to ia.xlsx"
    python processar_planilha.py "C:\\Users\\gabri\\Downloads\\plan to ia.xlsx" --sheet "seguradora"
    python processar_planilha.py "C:\\Users\\gabri\\Downloads\\plan to ia.xlsx" --sync-sheets
"""

import argparse
from datetime import datetime
import os
import sys

from dotenv import load_dotenv
import openpyxl
import pandas as pd

# Carrega variáveis de ambiente e garante visibilidade do projeto
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura encoding UTF-8 para o console do Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from extractor.extractor import extract_record
from extractor.helpers import COLUMNS
from sheets.writer import append_rows


def _find_message_column(df):
    """Localiza a coluna que mais provavelmente contém os textos dos acionamentos."""
    candidates = [
        "mensagens originais completas",
        "mensagens originais",
        "mensagem original",
        "mensagens",
        "mensagem",
        "texto do acionamento",
        "texto bruto",
        "texto",
        "conteudo",
        "raw",
    ]
    for cand in candidates:
        for col in df.columns:
            if cand in str(col).lower().strip():
                return col

    # Fallback: coluna de texto com maior média de caracteres
    best_col = None
    max_len = 0
    for col in df.columns:
        if df[col].dtype == object or isinstance(df[col].iloc[0], str):
            avg_len = df[col].astype(str).str.len().mean()
            if avg_len > max_len:
                max_len = avg_len
                best_col = col

    return best_col


def process_file(
    file_path,
    sheet_name=None,
    col_name=None,
    output_path=None,
    sync_sheets=False,
    include_unknown=True,
):
    """Executa o processamento em lote da planilha."""
    if not os.path.exists(file_path):
        print(f"❌ Erro: Arquivo não encontrado: {file_path}")
        return

    print("=" * 70)
    print("🚀 PROCESSADOR EM MASSA DE ASSISTÊNCIAS — JM ASSISTÊNCIAS")
    print("=" * 70)
    print(f"📂 Arquivo de entrada: {file_path}")

    # Leitura do arquivo
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        xl = pd.ExcelFile(file_path)
        selected_sheet = sheet_name or xl.sheet_names[0]
        print(f"📄 Aba selecionada: [{selected_sheet}] (Abas disponíveis: {xl.sheet_names})")
        df = pd.read_excel(file_path, sheet_name=selected_sheet)
    elif ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        print(f"❌ Erro: Formato {ext} não suportado. Use .xlsx, .xls ou .csv.")
        return

    print(f"📊 Total de linhas lidas: {len(df)}")

    # Identificação da coluna de mensagens
    target_col = col_name or _find_message_column(df)
    if not target_col or target_col not in df.columns:
        print(f"❌ Erro: Não foi possível identificar a coluna de mensagens. Colunas disponíveis: {list(df.columns)}")
        return

    print(f"🔍 Coluna de mensagens identificada: [{target_col}]")

    # Processamento linha a linha
    records = []
    product_stats = {}
    category_stats = {}
    start_time = datetime.now()

    for idx, row in df.iterrows():
        raw_text = str(row[target_col] or "").strip()
        if not raw_text or raw_text.lower() in ["nan", "none", "não informado", "nao informado"]:
            continue

        try:
            rec = extract_record(raw_text)
            prod = rec.get("PRODUTO", "unknown")

            if not include_unknown and prod == "unknown":
                continue

            # Preserva identificador ou índice original para rastreabilidade
            rec["_LINHA_ORIGINAL"] = idx + 2
            if "ID do pedido" in df.columns:
                rec["_ID_PEDIDO"] = row["ID do pedido"]

            records.append(rec)
            product_stats[prod] = product_stats.get(prod, 0) + 1

            cat = rec.get("CATEGORIA") or "A DEFINIR"
            category_stats[cat] = category_stats.get(cat, 0) + 1

        except Exception as exc:  # noqa: BLE001
            print(f"⚠️ Erro ao processar linha {idx + 2}: {exc}")

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⚡ Processamento concluído em {elapsed:.2f} segundos!")
    print(f"✅ Total de registros estruturados: {len(records)}")

    # Exibição de Estatísticas
    print("\n" + "-" * 50)
    print("📈 DISTRIBUIÇÃO POR PRODUTO / SEGURADORA:")
    print("-" * 50)
    for prod, count in sorted(product_stats.items(), key=lambda x: -x[1]):
        pct = (count / len(records)) * 100 if records else 0
        print(f"  • {prod.upper():<18}: {count:>4} ({pct:>5.1f}%)")

    print("\n" + "-" * 50)
    print("🚛 DISTRIBUIÇÃO POR CATEGORIA:")
    print("-" * 50)
    for cat, count in sorted(category_stats.items(), key=lambda x: -x[1]):
        pct = (count / len(records)) * 100 if records else 0
        print(f"  • {cat:<20}: {count:>4} ({pct:>5.1f}%)")

    # Geração do Arquivo de Saída Excel
    df_out = pd.DataFrame(records)

    # Reordena conforme schema oficial de 11 colunas + metadados
    final_cols = [c for c in COLUMNS if c in df_out.columns]
    extra_cols = [c for c in df_out.columns if c not in COLUMNS]
    df_out = df_out[final_cols + extra_cols]

    if not output_path:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        sheet_suffix = f"_{selected_sheet}" if ext in [".xlsx", ".xls"] else ""
        output_path = os.path.join(
            os.path.dirname(file_path),
            f"{base_name}{sheet_suffix}_estruturado.xlsx",
        )

    # Exporta com formatação limpa via openpyxl
    df_out.to_excel(output_path, index=False)
    print("\n" + "=" * 70)
    print(f"💾 Planilha estruturada salva com sucesso em:\n👉 {output_path}")
    print("=" * 70)

    # Sincronização direta com Google Sheets (opcional)
    if sync_sheets:
        print("\n☁️ Sincronizando registros em lote com o Google Sheets...")
        res = append_rows(records)
        if res.get("ok"):
            print(f"🎉 Sucesso! {res.get('total_inseridas')} linhas anexadas ao Google Sheets (Linha final: {res.get('linha_final')}).")
        else:
            print(f"❌ Falha na sincronização com Google Sheets: {res.get('erro')}")

    return output_path, records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processador em massa de assistências.")
    parser.add_argument("arquivo", help="Caminho do arquivo Excel ou CSV a processar.")
    parser.add_argument("--sheet", help="Nome da aba do Excel (opcional).", default=None)
    parser.add_argument("--col", help="Nome da coluna com o texto bruto (opcional).", default=None)
    parser.add_argument("--output", help="Caminho do arquivo de saída (opcional).", default=None)
    parser.add_argument("--sync-sheets", action="store_true", help="Grava os registros no Google Sheets em lote.")
    parser.add_argument("--ignorar-desconhecidos", action="store_true", help="Ignora mensagens não reconhecidas como seguradoras.")

    args = parser.parse_args()

    process_file(
        args.arquivo,
        sheet_name=args.sheet,
        col_name=args.col,
        output_path=args.output,
        sync_sheets=args.sync_sheets,
        include_unknown=not args.ignorar_desconhecidos,
    )
