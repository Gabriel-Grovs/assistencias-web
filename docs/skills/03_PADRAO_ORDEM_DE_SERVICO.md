# Padrão de mensagem — Ordem de Serviço

## Produtos associados

TOKIO e plataformas com Ordem de Serviço, Número da Assistência, Tipo de Evento, Origem, Serviços.

## Indicadores

"Ordem de Serviço: OS...", "Numero da Assistência:", Tipo de Serviço, Tipo de Evento, Status, Dados Cliente, Serviços, Origem:.

## Procedimento

1. ASSISTENCIA = valor iniciado por OS.
2. CLIENTE identificado pela plataforma/contexto.
3. Usar Tipo de Evento para categoria.
4. Extrair cidade após Origem.
5. Sem bloco de destino: deixar DESTINO vazio.
6. Ignorar valor do serviço quando a regra do produto determinar.
7. Ignorar Base/Viatura, prestador, placa, nome do contato, status, valor SOS.

## Classificação

- PNEUS FURADOS / TROCA DE PNEU → TROCA PNEU
- PANE MECÂNICA / PANE ELÉTRICA → SOCORRO MECANICO
- REBOQUE LEVE → LEVE
- REBOQUE UTILITÁRIO → UTILITARIO
- REBOQUE PESADO → PESADO

## Data

Sempre a data de envio no grupo do WhatsApp.