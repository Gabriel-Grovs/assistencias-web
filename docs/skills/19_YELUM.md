# Produto — YELUM

## Identificação

Produto: YELUM. CLIENTE = YELUM.

## Assistência

Primeira ocorrência do campo Assistência (não usar Solicitação).

## Categoria

- GUINCHO LEVE → LEVE
- GUINCHO - GUINCHO UTILITÁRIOS (PICK-UPS E SUV) → UTILITARIO
- GUINCHO UTILITÁRIO → UTILITARIO
- GUINCHO PLATAFORMA → LEVE
- REBOQUE LEVE → LEVE
- REBOQUE PESADO → PESADO
- TAXI → TAXI
- CHAVEIRO → CHAVEIRO

## Origem

Cidade do campo Cidade do bloco ORIGEM. Ex.: Itamogi → ITAMOGI.

## Destino

Cidade do campo Cidade do bloco DESTINO. Ex.: Ituverava → ITUVERAVA. Se não houver: vazio.

## KM TOTAL

Tabela SENHA/TARIFA/QUANTIDADE:

KM TOTAL = KM DESLOCAMENTO + KM EXCEDENTE + 40 (SAÍDA)

Exemplo: 83 + 290 + 40 = 413.

Não incluir pedágio, diária, senha, limite de KM.

## VALOR

Ignorar valores neste produto. Deixar vazio.

## Ignorar

Cliente/segurado, solicitante, telefone, veículo, placa, motorista, taxista, prestador, cidade do prestador, forma de pagamento, status.

## Duplicidades

Sufixos ou solicitação complementar: manter linha + "Possivel duplicação".

## Exemplo

DATA;CLIENTE;ASSISTENCIA;CATEGORIA;ORIGEM;DESTINO;KM TOTAL;VALOR;OBS
11/08/2026;YELUM;9887901;UTILITARIO;ITAMOGI;ITUVERAVA;413;;