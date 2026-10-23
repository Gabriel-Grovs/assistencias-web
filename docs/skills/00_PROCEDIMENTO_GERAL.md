# Procedimento geral — Identificador de serviços de assistência

## Finalidade

Ler mensagens recebidas em grupos de WhatsApp e extrair serviços de assistência para posterior análise financeira.

As mensagens são enviadas por funcionários de atendimento e podem conter:

- Informações relevantes da assistência;
- Mensagens operacionais;
- Mensagens duplicadas;
- Correções;
- Atualizações de status;
- Dados de prestadores;
- Dados do segurado;
- Placas e informações do veículo;
- Valores;
- Informações conflitantes;
- Mensagens sem relação com o serviço.

O agente deve separar somente os dados necessários para a planilha final.

## Resultado esperado

O agente deve gerar um registro por assistência ou serviço identificado, utilizando as colunas:

- DATA
- CLIENTE
- ASSISTENCIA
- CATEGORIA
- ORIGEM
- DESTINO
- KM TOTAL
- VALOR
- OBS

## Regra de segurança

Nunca inventar, completar ou deduzir informações ausentes.

Quando uma informação não estiver claramente presente:

- Deixar o campo vazio; ou
- Registrar `ANALISE MANUAL` em OBS quando a ausência impedir uma classificação segura.

Não usar dados de outro serviço para preencher o serviço atual.

## Fonte da data

A DATA deve ser a data em que a mensagem foi enviada no grupo do WhatsApp.

Não utilizar automaticamente:

- Data de abertura;
- Data de aceite;
- Data de solicitação;
- Data combinada;
- Data de agendamento;
- Data de aceite do prestador;
- Data presente no corpo da assistência.

## Formato da data

Usar: `DD/MM/AAAA`

Respeitar a data real da mensagem:

- Mensagem às 23:59 pertence ao dia informado pelo WhatsApp;
- Mensagem às 00:00 pertence ao novo dia.

Se a data da mensagem não estiver disponível:

`DATA IMPOSSIVEL DE IDENTIFICAR` + `ANALISE MANUAL` em OBS.

## Identificação do cliente

CLIENTE representa a seguradora, montadora, locadora ou empresa responsável pela assistência.

Nunca preencher CLIENTE com nome do segurado, solicitante, motorista ou prestador.

## Padronização dos clientes

- ALLIANZ → ALLIANZ
- AZUL SEGUROS → AZUL
- BRADESCO AUTORE → BRADESCO
- CAOA MONTADORA → CAOA CHERY
- FCA FIAT CHRYSLER → FCA FIAT
- MOVIDA PARTICIPACOES → MOVIDA
- PORTO SERVIÇO / PORTO → PORTO
- RESOLVE ASSIST → RESOLVE ASSIST
- SANTANDER AUTO → SANTANDER
- SUHAI SEGURADORA → SUHAI
- SURA SEGUROS → SURA
- TATO ASSIST → TATO ASSIST
- TOKIO / TOKIO MARINE → TOKIO
- YELUM → YELUM
- YOUSE SEGUROS → YOUSE

Se houver mais de um cliente na conversa, usar o primeiro claramente associado ao serviço.

## Identificação da assistência

Podem ser usados: Assistência, Número da Assistência, OS, Ordem de Serviço, Serviço, Protocolo, Número do serviço.

Prioridades por padrão:

1. Tokio: número iniciado por OS.
2. Padrão com Número da Assistência: usar esse número.
3. Santander/Yelum: campo Assistência.
4. Azul/Porto: número de SERVIÇO.
5. Bradesco/FCA: número do campo # Serviço.
6. Resolve/Tato: campo Protocolo.
7. Youse: Ordem de Serviço.
8. Movida: identificador principal do atendimento.

## Serviços duplicados ou complementares

Identificadores como 9887901-1 / 9887901-2 devem ser mantidos como registros separados.

Adicionar em OBS: `Possivel duplicação`

## Mensagens irrelevantes

Ignorar saudações, conversas internas, mensagens sem número de assistência, atualizações sem identificação do serviço.

## Informações que devem ser ignoradas

Nome do segurado, solicitante, beneficiário, motorista, taxista, prestador, cidade do prestador, viatura, placa da viatura, forma de pagamento, status, placa do veículo, chassi, telefone, endereço completo, problema detalhado, SLA, prazo, número de lote.

## Informações conflitantes

1. Não escolher por intuição;
2. Priorizar campo explicitamente rotulado;
3. Se persistir conflito, manter vazio e usar ANALISE MANUAL.

## Extração de cidades

ORIGEM e DESTINO somente com nome da cidade, sem estado, bairro, rua, CEP, referência ou coordenadas.

## Origem

Prioridade: seção Origem > Município/Cidade da origem > endereço de acionamento.

Se só houver BASE DO PRESTADOR: usar "BASE DO PRESTADOR".

## Destino

Prioridade: seção Destino > segundo endereço do atendimento.

Se não houver destino: deixar vazio.

## Classificação da categoria

LEVE, UTILITARIO, PESADO, EXTRA PESADO, TAXI, CHAVEIRO, SOCORRO MECANICO, TROCA PNEU, CARGA DE BATERIA, RESIDENCIAL, ELETRICISTA.

- Plataforma/guincho plataforma → LEVE
- Reboque leve/guincho leve → LEVE
- Reboque/guincho utilitário → UTILITARIO
- Reboque pesado → PESADO
- Reboque extra pesado → EXTRA PESADO
- Táxi → TAXI
- Pneu furado/troca de pneu → TROCA PNEU
- Pane mecânica sem porte → SOCORRO MECANICO

Se não estiver claro: deixar vazio + ANALISE MANUAL.

## KM TOTAL

Não calcular por endereço, mapa ou distância estimada. Usar somente números explícitos.

SAÍDA = 40 km (regra padrão).

Ignorar: distância da base, do prestador, da viatura, KM de retorno, telefone, senha, pedágio, diária de pátio.

## VALOR

Preencher somente quando o total estiver explícito e a regra do produto permitir.

## OBS

Usar para: ANALISE MANUAL, Possivel duplicação, conflitos, categoria incerta, ausência de data.

## Regra de uma linha por serviço

Cada assistência gera uma linha independente.

## Formato de retorno

DATA;CLIENTE;ASSISTENCIA;CATEGORIA;ORIGEM;DESTINO;KM TOTAL;VALOR;OBS