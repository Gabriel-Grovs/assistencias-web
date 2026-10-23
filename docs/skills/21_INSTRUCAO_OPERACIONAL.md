# Instrução operacional de processamento

Ao receber mensagens do WhatsApp:

1. Identifique a data real de envio de cada mensagem.
2. Agrupe mensagens consecutivas que pertençam à mesma assistência.
3. Ignore conversas sem dados de assistência.
4. Identifique o cliente/produto pelo padrão da mensagem.
5. Identifique o modelo de mensagem utilizado.
6. Extraia a assistência conforme a regra específica do produto.
7. Classifique o serviço em uma categoria permitida.
8. Extraia somente a cidade de origem.
9. Extraia somente a cidade de destino, quando existir.
10. Calcule KM TOTAL somente pelas regras específicas.
11. Preencha VALOR somente quando permitido e explícito.
12. Nunca copie placa, nome do segurado, motorista ou taxista.
13. Preserve serviços aparentemente duplicados.
14. Em duplicidades, adicione "Possivel duplicação".
15. Em incerteza relevante, adicione "ANALISE MANUAL".
16. Gere uma linha independente para cada assistência.
17. Retorne somente as colunas nesta ordem:

DATA;CLIENTE;ASSISTENCIA;CATEGORIA;ORIGEM;DESTINO;KM TOTAL;VALOR;OBS