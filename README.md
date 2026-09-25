# Sistema de Assistências (assistencias-web)

Aplicação web Flask que lê textos copiados de portais de seguradoras, identifica
o produto, extrai os dados da assistência conforme regras documentadas e grava
uma linha no Google Sheets.

## Funcionalidades

- Login por senha (variável de ambiente `APP_PASSWORD`).
- Identificação automática do produto pelo conteúdo do texto (18 produtos).
- Extração de DATA, CLIENTE, ASSISTENCIA, CATEGORIA, ORIGEM, DESTINO, KM TOTAL,
  VALOR e OBS.
- Gravação no Google Sheets via Service Account (`gspread`).
- Exibição do resultado com destaque visual em ORIGEM e DESTINO.

## Estrutura

```
assistencias-web/
├── app.py                  # Flask principal (login + /processar)
├── extractor/
│   ├── identifier.py       # Identifica o produto pelo texto
│   ├── extractor.py        # Orquestra a extração
│   ├── km_calculator.py    # 3 modelos de KM
│   ├── category_mapper.py  # Normaliza categorias
│   ├── helpers.py          # Funções de parsing compartilhadas
│   └── products/           # Um módulo por produto
├── sheets/writer.py        # Grava linha no Google Sheets
├── templates/              # login.html e index.html
├── static/style.css
├── tests/test_extractor.py # Um teste por produto
├── requirements.txt
├── render.yaml
└── .env.example
```

## Schema da planilha (ordem das colunas)

```
DATA | CLIENTE | ASSISTENCIA | CATEGORIA | ORIGEM | DESTINO | KM TOTAL | VALOR | MOTORISTA | VEICULO | OBS
```

`MOTORISTA` e `VEICULO` são sempre gravados vazios (preenchimento manual).

## Configuração local

1. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

2. Copie `.env.example` para `.env` e preencha:

   ```bash
   copy .env.example .env
   ```

3. Rode a aplicação:

   ```bash
   python app.py
   ```

   Acesse `http://localhost:5000` e faça login com a senha definida em `APP_PASSWORD`.

## Configuração do Google Sheets

1. No [Google Cloud Console](https://console.cloud.google.com), crie um projeto e
   habilite as APIs **Google Sheets API** e **Google Drive API**.
2. Crie uma **Service Account** (IAM e Admin > Contas de serviço).
3. Baixe a chave JSON da Service Account.
4. Crie uma planilha no Google Sheets e **compartilhe** com o e-mail da Service
   Account (ex.: `minha-conta@projeto.iam.gserviceaccount.com`) com permissão de
   **Editor**.
5. Configure as variáveis de ambiente:
   - `GOOGLE_CREDENTIALS_JSON`: conteúdo da chave JSON em uma única linha
     (serialize com `json.dumps` / remova quebras de linha).
   - `GOOGLE_SHEET_ID`: o ID da planilha (trecho entre `/d/` e `/edit` no URL).
   - `GOOGLE_SHEET_TAB`: nome da aba (padrão `Assistencias`).

   A planilha já deve conter a linha de cabeçalho com as colunas do schema acima.

## Deploy no Render

1. Faça push do projeto para um repositório Git.
2. No [Render](https://render.com), crie um **Blueprint** apontando para o
   repositório (ele usa o `render.yaml`).
3. No painel do serviço, defina as variáveis de ambiente sensíveis:
   - `APP_PASSWORD`
   - `GOOGLE_CREDENTIALS_JSON`
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_SHEET_TAB` (opcional, padrão `Assistencias`)
   - `SECRET_KEY` (gerada automaticamente pelo blueprint)

O serviço será exposto em `https://assistencias-web.onrender.com`.

## Testes

```bash
python -m unittest discover -s tests
```

Há um caso de teste por produto com texto de exemplo fictício.

## Regras de extração

As regras completas estão documentadas em `F:\rules\`. Em resumo:

- **Nunca inventar** dados ausentes; usar `ANALISE MANUAL` em OBS quando houver
  incerteza.
- **DATA** = data da mensagem; nunca usar "Data Abertura"/"Aceito em".
- **KM** segue três modelos: A (só explícito), B (Percurso Total) e C
  (40 + deslocamento + excedente).
- **VALOR** é preenchido somente quando permitido e explícito por produto.
