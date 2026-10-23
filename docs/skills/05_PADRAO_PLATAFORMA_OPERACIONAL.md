# Padrão de mensagem — Plataforma operacional

## Produtos associados

BRADESCO, FCA FIAT, MOVIDA, RESOLVE ASSIST, TATO ASSIST, YOUSE.

## Indicadores

Protocolo, Ordem de Serviço, Item de Cobertura, Dados do atendimento, Percurso Total, Tarifas, Endereço de Acionamento, Origem, Destino.

## Procedimento

1. Identificar o produto pelo nome da empresa.
2. Selecionar identificador principal conforme regra do produto.
3. Classificar o tipo de serviço.
4. Extrair somente cidades de origem/destino.
5. Usar KM somente quando representar claramente o percurso do serviço.
6. Usar VALOR somente quando explícito.
7. Ignorar prestadores, motoristas, taxistas, viaturas, placas, status.

## Prioridade de quilometragem

1. Regra específica do produto;
2. Percurso Total;
3. KM Total;
4. Soma de tarifas de deslocamento, apenas se inequívoco;
5. Caso contrário, vazio + ANALISE MANUAL.

## Valor

Preencher somente com valor total explícito.

## Ignorar

Chassi, Segurador/Beneficiário, Solicitante, Veículo, Placa, Colaborador, Status, Data de agendamento, Previsão, Viatura, Distância da viatura.