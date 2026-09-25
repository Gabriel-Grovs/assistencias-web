"""Scanner e calibrador de assistências a partir do WhatsApp histórico."""
import os, sys, re, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractor.extractor import extract_record

caminho_zap = r"C:\Users\gabri\Downloads\Mensagens de maio de 2026 - Conversa WhatsApp Serviços JM.txt"
if not os.path.exists(caminho_zap):
    caminho_zap = r"C:\Users\gabri\Downloads\Mensagens de maio de 2026 - Conversa WhatsApp Serviços JM(1).txt"

with open(caminho_zap, "r", encoding="utf-8", errors="ignore") as f:
    linhas = f.readlines()

# Agrupa blocos de mensagens por horário/contexto que contenham assistências
blocos = []
bloco_atual = []
keywords = [
    "SERVIÇO", "SERVICO", "Assistência", "Assistencia", "Ordem de Serviço",
    "Ordem de Servico", "Protocolo", "PORTO", "ALLIANZ", "YELUM", "HDI",
    "TOKIO", "BRADESCO", "SUHAI", "SURA", "MOVIDA", "RESOLVE", "TATO",
    "UNIVERSO", "VELOX", "YOUSE", "CAOA", "FIAT"
]

for linha in linhas:
    # Nova mensagem do WhatsApp: formato "DD/MM/AAAA HH:MM - Nome:"
    m_msg = re.match(r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}) - (.*?): (.*)$", linha)
    if m_msg:
        data_hora, autor, conteudo = m_msg.groups()
        if any(k.lower() in conteudo.lower() for k in keywords):
            if bloco_atual:
                blocos.append("\n".join(bloco_atual))
                bloco_atual = []
            bloco_atual.append(conteudo)
        elif bloco_atual and not conteudo.startswith("<Mídia oculta>") and len(conteudo) > 10:
            bloco_atual.append(conteudo)
    else:
        if bloco_atual:
            bloco_atual.append(linha.strip())

if bloco_atual:
    blocos.append("\n".join(bloco_atual))

# Filtra blocos que realmente parecem solicitações completas
assistencias = []
for b in blocos:
    if len(b) > 80 and any(k.lower() in b.lower() for k in ["origem", "destino", "cidade", "local", "laudo", "serviço", "servico", "assistência"]):
        assistencias.append(b)

print(f"Total de mensagens examinadas: {len(linhas)}")
print(f"Total de blocos de assistência identificados: {len(assistencias)}")
print("=" * 60)

stats = {}
sucesso = 0
revisar = 0

for i, raw in enumerate(assistencias):
    rec = extract_record(raw)
    prod = rec.get("PRODUTO", "unknown")
    stats[prod] = stats.get(prod, 0) + 1
    
    # Critérios de sucesso: cliente, assistência e origem preenchidos
    tem_cliente = bool(rec.get("CLIENTE"))
    tem_assist = bool(rec.get("ASSISTENCIA"))
    tem_origem = bool(rec.get("ORIGEM"))
    
    if tem_cliente and tem_assist and tem_origem:
        sucesso += 1
    else:
        revisar += 1

print("\n--- DISTRIBUIÇÃO POR PRODUTO IDENTIFICADO ---")
for p, c in sorted(stats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {p.upper()}: {c} serviços")

print(f"\nResumo: {sucesso} completos | {revisar} para ajuste fino")
