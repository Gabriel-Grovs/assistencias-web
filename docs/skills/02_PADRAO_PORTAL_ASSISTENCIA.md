# Padrão de mensagem — Portal de assistência

## Produtos associados

ALLIANZ, CAOA CHERY, SUHAI, SURA (campos: Assistência, Solicitação, Produto, Serviço, Local, Destino).

## Indicadores

Assistência, Solicitação, Produto, Aceito em, Serviço, Prazo, Local, Cidade, Estado, Destino, Problema, Segurado, Solicitante.

## Procedimento

1. Identificar o produto.
2. Extrair o primeiro valor do campo Assistência.
3. Identificar categoria pelo campo Serviço.
4. Extrair cidade do campo Cidade associado ao local.
5. Extrair cidade do campo Cidade associado ao destino.
6. Extrair KM conforme regra específica do produto.
7. Ignorar segurado, solicitante, telefone, veículo, placa.
8. Usar data do WhatsApp, não a data de "Aceito em".

## Mapeamentos

- REBOQUE/LEVE → LEVE
- REBOQUE/PLATAFORMA → LEVE
- REBOQUE/UTILITÁRIO → UTILITARIO
- GUINCHO/GUINCHO LEVE → LEVE
- GUINCHO/GUINCHO UTILITÁRIOS → UTILITARIO
- REBOQUE/PESADO → PESADO
- TAXI → TAXI
- CHAVEIRO → CHAVEIRO

Se houver só REBOQUE sem porte claro: ANALISE MANUAL.

## Conflitos

Usar a primeira Assistência associada ao cabeçalho do serviço. Múltiplos blocos = múltiplas linhas.