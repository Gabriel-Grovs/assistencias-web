# Produto — TOKIO

## Identificação

Ordem de Serviço / Numero da Assistência / Tokio Marine. CLIENTE = TOKIO.

## Assistência

Sempre o identificador iniciado por "OS". Ignorar "Numero da Assistência" como ASSISTENCIA quando houver OS.

## Categoria

- PNEUS FURADOS / TROCA DE PNEU → TROCA PNEU
- PANE MECÂNICA / PANE ELÉTRICA → SOCORRO MECANICO
- REBOQUE LEVE → LEVE
- REBOQUE UTILITÁRIO → UTILITARIO
- REBOQUE PESADO → PESADO

## Origem

Cidade após "Origem".

## Destino

Se não existir seção de destino: deixar vazio.

## KM

Não calcular por endereço. Não usar quantidade do serviço "TÉCNICO SOS SAÍDA". Se não explícito: vazio.

## Valor

Ignorar valor para este produto. VALOR vazio, salvo instrução posterior específica.

## Ignorar

Número da assistência secundário, Base/Viatura, prestador, status, nome do contato, telefone, veículo, placa, SLA, data de aceite do prestador.

## Data

Usar a data de envio no grupo do WhatsApp.