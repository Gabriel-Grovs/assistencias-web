# Schema final da planilha

## Colunas obrigatórias

| Coluna | Regra |
|---|---|
| DATA | Data de envio da mensagem no grupo, formato DD/MM/AAAA |
| CLIENTE | Seguradora, montadora ou empresa padronizada |
| ASSISTENCIA | Primeiro identificador principal da assistência |
| CATEGORIA | Categoria padronizada do serviço |
| ORIGEM | Somente cidade de origem |
| DESTINO | Somente cidade de destino |
| KM TOTAL | Quilometragem extraída ou calculada conforme o produto |
| VALOR | Valor total explícito, somente quando permitido |
| OBS | Incertezas, duplicidades e conflitos |

## Cabeçalho CSV

DATA;CLIENTE;ASSISTENCIA;CATEGORIA;ORIGEM;DESTINO;KM TOTAL;VALOR;OBS

## Exemplo

DATA;CLIENTE;ASSISTENCIA;CATEGORIA;ORIGEM;DESTINO;KM TOTAL;VALOR;OBS
11/08/2026;YELUM;9887901;UTILITARIO;ITAMOGI;ITUVERAVA;413;;

## Regras de formatação

- Separador: ponto e vírgula;
- Uma linha por assistência;
- Não inserir placa, nome do segurado, motorista, taxista, prestador, status;
- Campos ausentes permanecem vazios;
- Não usar "N/A" para substituir informação ausente.