# Padrão de mensagem — Laudo Digital

## Produtos associados

AZUL, PORTO.

## Indicadores

"SERVIÇO ...", SENHA DE ATENDIMENTO, Empresa, Tipo de Serviço, Data Abertura, Endereço Ocorrência, Cidade, Endereço Destino, Problema.

## Procedimento

1. ASSISTENCIA = número após SERVIÇO.
2. CLIENTE = empresa responsável, normalizada.
3. CATEGORIA por Tipo de Serviço + contexto.
4. ORIGEM = cidade de Endereço Ocorrência.
5. DESTINO = cidade de Endereço Destino, se houver.
6. Ignorar senha, cliente/segurado, responsável, socorrista, modelo, placa, situação, hora prevista, data interna.
7. Não usar Data Abertura como DATA.

## Classificação

- SOCORRO sem detalhe → SOCORRO MECANICO
- TRANSPORTE → TAXI
- CHAVEIRO → CHAVEIRO
- TROCA DE PNEU → TROCA PNEU
- REBOQUE LEVE → LEVE
- REBOQUE UTILITÁRIO → UTILITARIO

Se incerto: vazio + ANALISE MANUAL.