# Produto — PIER

## Identificação

Produto: PIER. CLIENTE = PIER.

## Data

Usar a data extraída do campo "Aceito em" no formato DD/MM/AAAA (desconsiderar horário).

## Assistência

Primeiro valor do campo Assistência (ignorar campo Solicitação).

## Categoria

Classificar a partir do campo "Serviço":
- TÁXI / TÁXI VIAGEM → TAXI
- REBOQUE/LEVE ou REBOQUE LEVE → LEVE
- REBOQUE/UTILITÁRIO ou REBOQUE UTILITÁRIO → UTILITARIO
- REBOQUE/PESADO → PESADO
- REBOQUE PLATAFORMA → LEVE
- CHAVEIRO → CHAVEIRO
- TROCA DE PNEU → TROCA PNEU
- SOCORRO MECÂNICO / ELÉTRICO → SOCORRO MECANICO

## Origem

Cidade do campo "Cidade" associado ao bloco Local (primeiro endereço).

## Destino

Cidade do campo "Cidade" associado ao bloco Destino. Se não houver: vazio.

## KM TOTAL

Preencher apenas se houver quilometragem explícita. Nunca usar o campo "Prazo" como KM.

## VALOR

Preencher apenas se houver valor monetário total explícito. Caso contrário: vazio.

## Ignorar

Solicitação, Prazo, Problema, Importante, Segurado, Solicitante, Telefone, Veículo, Placa, Ano, Cor, Combustível, Bairro, CEP, Referências, dados cadastrais do veículo (Kit Gás, Ar Cond.).