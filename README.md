# <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnZqZHNscWsxb3MzcmxkdGVuMGUxMWFwNnpodHczYWQ3eTY3OWJqMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/YnUcQkUvPdHMmkLBZn/giphy.gif" alt="dados_1" width="50" height="50" /> SQUAD: LegoDados - Projeto de Inteligência Legislativa & Engenharia de dados

![logo](readme/identidade/legodadosbanner.png)


Este repositório contém o Projeto Integrador da pós-graduação em Engenharia de Dados e Inteligência Artificial. O objetivo é desenvolver um pipeline de dados completo (ETL) que automatiza a captura, organização e análise de dados da API de Dados Abertos da Câmara dos Deputados.

## <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmVuYTBwNnoxMWt3MnE1MHduNGk1anh4a3Jyc202dW0xNm8xeGJveiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/riAbhlrWv6dSFutbOj/giphy.gif" alt="dados_2" width="30" height="30" /> Propósito do Projeto:

Transformar o [oceano de dados brutos do legislativo brasileiro](https://dadosabertos.camara.leg.br/swagger/api.html) em sinais acionáveis para consultorias de relações governamentais e empresas reguladas. O projeto visa substituir processos manuais e inconsistentes por uma arquitetura escalável que utiliza IA Generativa para classificação temática e resumos executivos.

## <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExejRkbmF2OHhtNDNnejFtcDRqaW11cTY3Z3Bubm1vbHJ5ZGp6MWtwZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/nRiEzx0joBH6JECMkD/giphy.gif" alt="dados_3" width="30" height="30" /> Stack Tecnológica:

<div align="center" style="display: inline_block">
  <img align="center" alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img align="center" alt="Poetry" src="https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white" />
  <img align="center" alt="Pandas" src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />
  <img align="center" alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img align="center" alt="Supabase" src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" />
  <img align="center" alt="OpenAI" src="https://img.shields.io/badge/OpenAI_GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img align="center" alt="n8n" src="https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white" />
  <img align="center" alt="Power BI" src="https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" />
  <img align="center" alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</div>


## <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdHdwMnFrc2V2cHM2aGltMHJ5cXcxaXlhNGJneHNkOHl3d3JpNWdqcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/9LZSPFwk4UkeVUvJRV/giphy.gif" alt="dados_4" width="30" height="30" /> Arquitetura e Roadmap de Desenvolvimento:

![roadmap](readme/diagrama_pipeline.svg)

O projeto está estruturado em etapas principais. Abaixo está o status atual de desenvolvimento do que já foi mapeado e implementado:

1. **Exploração e Extração (Ingestão)** `[CONCLUÍDO]`

* Desenvolvimento de scripts Python em src/extraction.py para consumo estruturado da API de Dados Abertos.
* Extração modularizada através de extratores específicos: DeputadosExtractor, PartidosExtractor, ProposicoesExtractor e VotacoesExtractor.
* Tratamento de paginação, resiliência contra erros de timeout e persistência do JSON bruto no diretório local data_raw/ (Camada Bronze).

2. **Diagnóstico e Configuração** `[CONCLUÍDO]`

* Implementação de rotinas de validação inicial (src/diagnostico.py) disparadas antes da execução principal para garantir a integridade dos diretórios e conexões.
* Centralização das configurações e segurança através de variáveis de ambiente gerenciadas em src/config.py e .env.

3. **Transformação e Carga (ETL)** `[CONCLUÍDO]`

* Limpeza, padronização e processamento dos dados brutos utilizando Pandas (src/transformers.py).
* Modelagem relacional transformando arquivos JSON em estruturas adequadas para tabelas Fato e Dimensão (ex: fato_proposicoes_autores, fato_votacoes, fato_votos).
* Orquestração e execução da carga incremental (UPSERT por chave + delete/insert escopado nas associativas) em banco de dados PostgreSQL via SQLAlchemy (src/transformation.py), preservando `created_at` e os enriquecimentos de IA entre execuções.

4. **Camada de Inteligência Artificial** `[CONCLUÍDO]`

* **Caminho B — Resumo Executivo** (`src/ai_layer.py`, classe `PipelineEtapa4`): para cada proposição pendente, gera um resumo de até 3 frases em linguagem executiva via **GPT-4o-mini**, gravado em `fato_proposicoes.resumo_executivo` / `data_resumo`.
* **Caminho A — Classificação Temática por Embeddings** (`src/classificacao_tematica.py`, classe `PipelineEtapa5`): gera o embedding (**text-embedding-3-small**) da ementa de cada proposição e de um catálogo de ~11 temas de negócio (Tecnologia e IA, Tributário, Saúde, Trabalho e Previdência, Meio Ambiente, Economia e Finanças, Educação, Segurança Pública, Agronegócio, Infraestrutura e Transporte, Direitos e Cidadania), calcula a **similaridade de cosseno** entre eles e grava o tema de maior similaridade (ou `"Outros"` quando abaixo do limiar `LIMIAR_TEMA`) em `fato_proposicoes.tema` / `tema_score` / `data_tema`.
* **Modo de Simulação (Dry Run)**: ambas as etapas calculam e exibem a estimativa de custo (USD/BRL, tokens) antes de qualquer chamada real à API — controlado por `DRY_RUN` no `.env`.
* O `tema` classificado alimenta diretamente o digest e os alertas do workflow n8n da Etapa 5 — a IA não é decoração, ela muda o conteúdo do e-mail enviado.

5. **Automação e Monitoramento** `[CONCLUÍDO]`

* Workflow no **n8n** (`n8n/bussola_publica_ingestao_diaria.json`) agendado para rodar **diariamente às 06h** (cron `0 6 * * *`, timezone `America/Sao_Paulo`), executando `main.py`/`main2.py` via *Execute Command*.
* **Digest diário por e-mail** com as proposições mais relevantes das últimas 24h, já com **tema (embeddings)** e **resumo executivo (GPT)**.
* **Alerta de falha**: ramo dedicado que envia e-mail com o `stderr` caso o pipeline quebre.
* Guia completo de importação e configuração de credenciais em [`n8n/GUIA_IMPORTACAO_n8n.md`](n8n/GUIA_IMPORTACAO_n8n.md).

6. **Visualização de Dados e Analytics (Power BI)** `[CONCLUÍDO]`

* Criação do layout e prototipagem de alta fidelidade das telas utilizando o **Figma**.
* Conexão nativa do Power BI Desktop ao data warehouse (PostgreSQL) hospedado no **Supabase**.
* Modelagem e relacionamentos Star Schema replicados no Power BI, com criação de medidas em DAX para contadores e distribuições.
* Publicação do relatório no Power BI Service e disponibilização de link público (modo leitura) para consumo.


## <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGRxeDNjenpocXN6M2lsdzZ2Z2toYzIwNHM0ODJ4MjJxdXliaGR6eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/1ZIoSmnkIP0ghBiiAw/giphy.gif" alt="dados_5" width="30" height="30" />  Motivo das decisões técnicas:

![roadmap](readme/arquitetura/roadmap.png)

1. **Por que orquestrar `main.py` no n8n (Execute Command) em vez de reimplementar a ingestão em nós nativos?**

* A lógica de paginação, retry, validação e carga já está testada em Python. Reescrevê-la em nós HTTP do n8n duplicaria código e criaria duas fontes de verdade. O n8n entra como **orquestrador e camada de notificação**, não como ETL paralelo. O custo dessa escolha é que o n8n precisa rodar no mesmo host do repositório (VPS/Docker/local self-hosted) — documentado no guia.

2. **Por que classificação por embeddings (Caminho A) e não pedir o tema direto à LLM?**

* **Três motivos**:
  * **custo** — 1 embedding por ementa com `text-embedding-3-small` custa frações de centavo, muito abaixo de uma chamada de chat por proposição;
  * **consistência** — a lista de ~11 temas é um catálogo fechado, então a similaridade de cosseno sempre escolhe um rótulo válido, enquanto a LLM poderia inventar categorias novas;
  * **auditabilidade** — guardamos o `tema_score`, deixando a classificação transparente e com limiar ajustável (`LIMIAR_TEMA`).

3. **Por que e-mail e não Telegram (nesta entrega)?**

* E-mail é o canal mais simples de configurar, demonstrar e printar para a avaliação, e é o formato que o cliente corporativo da Bússola Pública já consome. O workflow é trivialmente extensível para Telegram (basta um nó `Telegram` em paralelo ao e-mail de sucesso).

4. **Por que o digest mostra tema + resumo?**

* Para a IA não ser decoração. O e-mail das 06h traz, para cada proposição priorizada, **o tema (embeddings)** e **o resumo executivo (GPT)**. A IA aparece no produto final que chega ao cliente — exatamente o que o desafio cobra.

5. **Controle de custo de IA:**

* Tanto o resumo (Caminho B) quanto o tema (Caminho A) sobem em `DRY_RUN=true` por padrão: estimam tokens e custo (USD/BRL) **antes** de gastar. Só com `DRY_RUN=false` há chamada real e gravação. O processamento é idempotente — pula o que já tem `resumo_executivo`/`tema`.

6. **Por que o deploy público do Power BI não atualiza em tempo real com o n8n?**

* O link de compartilhamento web público (`Embed to website`) no plano gratuito do Power BI Service possui restrições de atualização automática para fontes cloud diretas via DirectQuery sem Gateway corporativo. Portanto, o painel online reflete os dados históricos estáticos da última publicação manual do arquivo `.pbix`. O pipeline no n8n popula o banco Supabase em tempo real, mas o painel público web exige um reenvio do arquivo para refletir o estado mais recente.

7. **Resolução de problema crítico: conexão Power BI ↔ Supabase (erro de SSL):**

* Durante a configuração inicial, o Power BI Desktop rejeitou a conexão criptografada com o PostgreSQL do Supabase, retornando um erro de handshake SSL.
* **Solução:** Foi necessário baixar o certificado raiz do Supabase (`prod-ca-2021.crt`) e instalá-lo no Windows na pasta de **Autoridades de Certificação Raiz Confiáveis** (via `certlm.msc`). Isso permitiu que o driver ODBC/PostgreSQL do Power BI validasse a identidade do servidor e estabelecesse a conexão segura.


## <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2FuanM5OHhoYTZzZDU3ODlqbmQ4YjNxdm9qd2pxcDZmNmkza2VoNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/0sUBW0QZExZ1HJrmyr/giphy.gif" alt="dados_5" width="30" height="30" /> Modelo de Dados (DWH / Camada Relacional):

Para suportar as análises legislativas e o enriquecimento com Inteligência Artificial, os dados transformados foram estruturados em um modelo relacional (Fatos e Dimensões).

![schema](readme/arquitetura/schema.png)

> 📊 **Diagrama/dicionário completo do modelo:** veja [`docs/modelo_dados.md`](docs/modelo_dados.md) — modelo estrela com todas as dimensões, fatos e colunas adicionadas pela IA.

### <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3cxYXpwZm00OW9ocDA5a3NrczMwM284Y2Mya3E3cmhyNnRldmk3ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/9NDxo04budFf554AWO/giphy.gif" alt="dados_5_1" width="20" height="20" /> Tabelas de Dimensão (Dim):

`dim_deputados`
* Armazena os dados cadastrais e identificadores únicos dos deputados federais.

| Campo             | Tipo  | Restrição   | Descrição |
|-------------------|-------|------------|------------|
| id_deputado       | int8  | Primary Key | Identificador único do deputado na API da Câmara. |
| nome              | text  | Nullable    | Nome parlamentar do deputado. |
| sigla_partido     | text  | Nullable    | Sigla do partido político atual. |
| sigla_uf          | text  | Nullable    | Estado (Unidade da Federação) pelo qual foi eleito. |
| id_legislatura    | int8  | Nullable    | Identificador da legislatura atual. |
| url_foto          | text  | Nullable    | Link para a foto oficial do parlamentar. |
| uri               | text  | Nullable    | Link do endpoint oficial do deputado na API. |


`dim_partidos`
* Dicionário de partidos políticos mapeados no pipeline.

| Campo      | Tipo | Restrição   | Descrição |
|------------|------|------------|------------|
| id_partido | int8 | Primary Key | Identificador único do partido na API. |
| sigla      | text | Nullable    | Sigla oficial do partido político. |
| nome       | text | Nullable    | Nome completo do partido político. |
| uri        | text | Nullable    | Link do endpoint oficial do partido na API. |

### <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3cxYXpwZm00OW9ocDA5a3NrczMwM284Y2Mya3E3cmhyNnRldmk3ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/9NDxo04budFf554AWO/giphy.gif" alt="dados_5_2" width="20" height="20" />  Tabelas de Fato (Fact):

`fato_proposicoes`
* Entidade central de análise que armazena os textos, metadados e os enriquecimentos de IA (resumo executivo + classificação temática).

| Campo              | Tipo        | Restrição   | Descrição |
|--------------------|------------|------------|------------|
| id_proposicao      | int8       | Primary Key | Identificador único da proposição (projeto de lei, PEC, etc). |
| sigla_tipo         | text       | Nullable    | Tipo da proposição (ex: PL, PEC, MPV). |
| numero             | int8       | Nullable    | Número oficial da proposição no ano. |
| ano                | int8       | Nullable    | Ano de apresentação da matéria legislativa. |
| ementa             | text       | Nullable    | Texto original da ementa detalhando o objetivo do projeto. |
| data_apresentacao  | timestamptz | Nullable   | Data e hora em que a matéria foi protocolada. |
| created_at         | timestamptz | Nullable   | Data/hora da **primeira ingestão** do registro (não muda em re-execuções graças ao UPSERT). |
| resumo_executivo   | text       | **[IA · Etapa 4]** | Resumo analítico simplificado gerado via GPT-4o-mini (Caminho B). |
| data_resumo        | timestamptz | **[IA · Etapa 4]** | Timestamp de quando o resumo de IA foi gerado. |
| tema               | text       | **[IA · Etapa 5]** | Tema classificado por similaridade de cosseno entre embeddings (Caminho A). Alimenta o digest/alertas do n8n. |
| tema_score         | float8     | **[IA · Etapa 5]** | Similaridade de cosseno (0–1) entre a ementa e o tema escolhido. |
| data_tema          | timestamptz | **[IA · Etapa 5]** | Timestamp de quando a classificação temática foi gerada. |

> **Nota sobre `tema_score`:** `classificacao_tematica.py` calcula e grava `tema`, `tema_score` e `data_tema` juntos no mesmo `UPDATE`. Na carga atual do banco, `tema` está preenchido para as proposições já classificadas, mas `tema_score` ficou `NULL` em parte das linhas — indício de execuções feitas com uma versão anterior do script (antes da gravação do score). Isso não bloqueia o uso de `tema` no digest/alertas do n8n; é um ponto de atenção para a próxima reexecução da classificação temática.

`fato_proposicoes_autores`
* Tabela associativa que mapeia a autoria ou coautoria de cada proposição legislativa.

| Campo          | Tipo | Restrição | Descrição |
|----------------|------|-----------|------------|
| id_proposicao  | int8 | Nullable  | ID da proposição (chave estrangeira para fato_proposicoes). |
| nome_autor     | text | Nullable  | Nome do parlamentar ou órgão autor da matéria. |
| tipo_autor     | text | Nullable  | Categoria do autor (ex: Deputado, Órgão Executivo). |
| uri_autor      | text | Nullable  | Link do endpoint do autor na API. |


`fato_votacoes`
* Registra as sessões de votações ocorridas na Câmara para deliberação das matérias.

| Campo                | Tipo        | Restrição   | Descrição |
|----------------------|------------|------------|------------|
| id_votacao           | text       | Primary Key | Identificador alfanumérico único da votação. |
| descricao            | text       | Nullable    | Detalhamento do que está sendo votado em plenário ou comissão. |
| data_hora_registro   | timestamptz | Nullable   | Data e hora exata da sessão de votação. |
| aprovacao            | int2       | Nullable    | Indicador binário/status se a matéria foi aprovada (1) ou não (0). |
| proposicao_objeto    | text       | Nullable    | Descrição ou link da matéria que originou a votação. |
| created_at           | timestamptz | Nullable   | Data/hora da **primeira ingestão** do registro (não muda em re-execuções graças ao UPSERT). |

`fato_votos`
* Contém o posicionamento individual e nominal de cada parlamentar em uma votação específica.

| Campo       | Tipo        | Restrição       | Descrição |
|------------|------------|----------------|------------|
| id         | int4       | PK / Identity   | Chave primária sequencial auto-incremental da tabela. |
| id_votacao | varchar    | Non-Nullable    | ID da votação correspondente (Relaciona-se com fato_votacoes). |
| tipo_voto  | varchar    | Nullable        | O voto computado do deputado (ex: Sim, Não, Abstenção, Obstrução). |
| id_deputado| int4       | Nullable        | ID do parlamentar que votou (Relaciona-se com dim_deputados). |
| created_at | timestamptz | Nullable       | Data de inserção do registro de voto (carga incremental delete+insert escopada por `id_votacao`). |

**Relacionamentos:**

- `fato_proposicoes` 1—N `fato_proposicoes_autores` (por `id_proposicao`).
- `fato_votacoes` 1—N `fato_votos` (por `id_votacao`).
- `fato_votos` N—1 `dim_deputados` (por `id_deputado`).
- `dim_deputados` N—1 `dim_partidos` (por `sigla_partido` / `sigla`).
- `fato_proposicoes.tema` alimenta os alertas/digest do workflow n8n da Etapa de automação.

**Estratégia de carga (Etapa 3 — `src/transformation.py`):**

| Tabela | Modo | Por quê |
|---|---|---|
| `dim_deputados`, `dim_partidos` | TRUNCATE + reload | Catálogos completos devolvidos do zero pela API em toda execução — não há histórico a preservar. |
| `fato_proposicoes`, `fato_votacoes` | **UPSERT** (`INSERT ... ON CONFLICT (pk) DO UPDATE`) | Registro novo → `INSERT` com `created_at = now()`. Registro existente → `UPDATE` dos campos da API **sem tocar** em `created_at` nem nas colunas de IA (`resumo_executivo`, `tema`, `tema_score`, `data_tema`). A constraint UNIQUE/PK necessária para o `ON CONFLICT` é garantida de forma idempotente (`ALTER TABLE ... ADD CONSTRAINT ... UNIQUE`) caso ainda não exista. |
| `fato_proposicoes_autores`, `fato_votos` | **DELETE + INSERT escopado** (`carregar_incremental_assoc`) | Sem PK própria. Apaga só os registros associados aos `id_proposicao`/`id_votacao` do lote atual e reinsere — preserva associações de execuções anteriores. |

Essa estratégia torna a carga **idempotente e cumulativa**: rodar o pipeline diariamente faz o banco crescer, e `created_at` reflete a data real da primeira ingestão — o que sustenta o filtro `created_at >= NOW() - INTERVAL '24h'` usado no digest do n8n.


## Prompts e lógica utilizados na Camada de IA

### Caminho B — Resumo Executivo (`src/ai_layer.py`)

Modelo: **gpt-4o-mini** (10x mais barato que o gpt-4o, qualidade adequada para resumos de 3 frases).

**System prompt:**
```
Você é um analista legislativo sênior da consultoria Bússola Pública.
Sua função é transformar ementas técnicas de proposições da Câmara dos Deputados
em resumos claros e acionáveis para executivos e áreas de relações governamentais.

Regras para o resumo:
- Máximo 3 frases objetivas
- Linguagem direta, sem jargão jurídico
- Estrutura: (1) O que propõe, (2) Quem/o que é impactado, (3) Ponto de atenção para empresas
- Se a ementa for muito técnica ou vaga, informe isso claramente
- Responda APENAS com o resumo, sem introduções como 'O resumo é:' ou 'Esta proposição...'
```

**User prompt (template):**
```
Proposição: {sigla_tipo} {numero}/{ano}

Ementa oficial:
{ementa}

Gere o resumo executivo:
```

O resumo gerado é gravado em `fato_proposicoes.resumo_executivo` (+ `data_resumo`), e um backup local em JSON é salvo em `data/processed/`.

### Caminho A — Classificação Temática por Embeddings (`src/classificacao_tematica.py`)

Modelo: **text-embedding-3-small** (~$0.00002 / 1K tokens).

1. Gera o embedding da `ementa` de cada proposição pendente (`tema IS NULL`).
2. Gera, uma única vez por execução (com cache em memória), o embedding de cada um dos ~11 temas do catálogo de negócio — cada tema é descrito por uma frase rica em vocabulário, não só uma palavra:

   | Tema | Descrição (texto embedado) |
   |---|---|
   | Tecnologia e IA | Tecnologia, inteligência artificial, dados pessoais, internet, telecomunicações, inovação, startups, software, plataformas digitais e regulação de algoritmos. |
   | Tributário | Tributos, impostos, reforma tributária, carga fiscal, ICMS, IRPF, isenções, incentivos fiscais e arrecadação. |
   | Saúde | Saúde pública, SUS, medicamentos, planos de saúde, vigilância sanitária, hospitais, vacinas e profissionais de saúde. |
   | Trabalho e Previdência | Direitos trabalhistas, CLT, emprego, salário mínimo, sindicatos, previdência social, aposentadoria e relações de trabalho. |
   | Meio Ambiente | Meio ambiente, clima, licenciamento ambiental, desmatamento, saneamento, energia renovável, resíduos e sustentabilidade. |
   | Economia e Finanças | Economia, mercado financeiro, bancos, crédito, juros, inflação, câmbio, investimentos e orçamento público. |
   | Educação | Educação básica e superior, escolas, universidades, FIES, professores, currículo, financiamento educacional e ensino. |
   | Segurança Pública | Segurança pública, polícia, crime, armas, código penal, sistema prisional e combate ao tráfico. |
   | Agronegócio | Agronegócio, agricultura, pecuária, crédito rural, defensivos, exportação de commodities e produção no campo. |
   | Infraestrutura e Transporte | Infraestrutura, rodovias, portos, aeroportos, mobilidade urbana, concessões, obras públicas e transporte. |
   | Direitos e Cidadania | Direitos humanos, igualdade, direitos do consumidor, família, minorias, acesso à justiça e cidadania. |

3. Calcula a **similaridade de cosseno** entre o embedding da ementa e o embedding de cada tema.
4. O tema de maior similaridade é a classificação; se o melhor score ficar abaixo do limiar `LIMIAR_TEMA` (padrão `0.20`), a proposição recebe o tema `"Outros"`.
5. Grava `tema`, `tema_score` e `data_tema` em `fato_proposicoes` e salva backup local em JSON.

**Por que cosseno em vez de pedir o tema direto ao LLM?**
* **Custo**: 1 embedding por ementa é ordens de magnitude mais barato que uma chamada de chat por proposição.
* **Consistência**: a lista de temas é fixa; um LLM generativo poderia inventar rótulos novos a cada execução. O cosseno sempre escolhe um tema do catálogo controlado.
* **Auditabilidade**: o score fica salvo em `tema_score`, dando transparência à classificação.

> 📄 Detalhamento completo das decisões técnicas e prompts da camada de IA em [`docs/Etapa5_Documentacao_Tecnica.md`](docs/Etapa5_Documentacao_Tecnica.md) e [`docs/Etapa4_Camada_IA.pdf`](docs/Etapa4_Camada_IA.pdf).


## Automação com n8n e evidências

### Banco de dados (Supabase)

* **Projeto**: `bussola-publica` — Reference ID `thtdslaojkzbnzvbfjvu`
* **URL**: https://thtdslaojkzbnzvbfjvu.supabase.co

> O Table Editor/SQL Editor do Supabase exige login (não há link público de visualização no plano Free). Como evidência de que o banco está populado com ≥ 30 dias de dados e a camada de IA está gravando `tema`/`resumo_executivo`, seguem os prints abaixo, extraídos do Table Editor e SQL Editor do projeto acima.

### Workflow n8n

```
[Agendamento 06h]  →  [Rodar Pipeline (main.py)]  →  [Pipeline OK?]
                                                         ├─ SIM → [Consultar Proposições do Dia] → [Montar Digest HTML] → [Enviar Digest]
                                                         └─ NÃO → [Alerta de Falha]
```

* Workflow exportado em [`n8n/bussola_publica_ingestao_diaria.json`](n8n/bussola_publica_ingestao_diaria.json) (variante para Windows em [`n8n/bussola_publica_ingestao_diaria_WINDOWS.json`](n8n/bussola_publica_ingestao_diaria_WINDOWS.json)).
* Cron `0 6 * * *` (06h, timezone `America/Sao_Paulo`).
* Consulta as proposições das últimas 24h já com `tema` e `resumo_executivo` e monta um digest HTML por e-mail.
* Ramo de alerta dedicado envia o `stderr` por e-mail caso o pipeline falhe.
* Passo a passo de importação e configuração de credenciais (Postgres/Supabase via Session Pooler + SMTP) em [`n8n/GUIA_IMPORTACAO_n8n.md`](n8n/GUIA_IMPORTACAO_n8n.md).

### Evidências (prints)

| Execução do workflow n8n (todos os nós verdes) | Digest diário por e-mail (tema + resumo IA) |
|---|---|
| ![Execução n8n com sucesso (todos os nós verdes)](readme/prints/supabase_30dias.jpg) | ![E-mail digest Bússola Pública](readme/prints/email_digest.jpg) |

| `fato_proposicoes` no Supabase com `tema`/`resumo_executivo` | Cobertura de dados ≥ 30 dias (`data_apresentacao`) |
|---|---|
| ![Tabela fato_proposicoes com tema e resumo](readme/prints/supabase_tema.jpg) | ![Range de data_apresentacao no Supabase](readme/prints/n8n_execucao_sucesso.jpg) |

### Dashboard de BI (link público, modo leitura)

Como o Table Editor do Supabase não oferece link público no plano Free, a
visualização dos dados (≥ 30 dias, já enriquecidos com `tema` e `resumo_executivo`)
é publicada como um **dashboard de BI somente-leitura**, que o avaliador pode abrir
diretamente, sem login:

🔗 **Dashboard ao vivo (Power BI):** https://app.powerbi.com/view?r=eyJrIjoiMDQwMjE3NDQtMjExMi00MWExLWFhNTAtNWM3ODAyYzk5M2NlIiwidCI6IjUxZGQ3ZDM4LTYwNzctNDgzNy1hYTE0LWFlNDNmZThiM2ViMCJ9

![Dashboard Bússola Pública (Power BI sobre o Supabase)](readme/prints/Dashboard_Bussola_Publica.png)


## <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3PsZHg2Nmxhejc2eHc3bHB6N3lxaGt4cXJiOXNubmR3Ym1zYTMxdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/TKcnPuNL3VdTah6ymA/giphy.gif" alt="dados_7" width="30" height="30" /> Insights Extraídos do Dashboard (LegoDados)

<div align="center">
  <p align="center"><b>Visualização das Telas do Painel</b></p>
  <img src="readme/powerBI/CAPA.png" width="32%" alt="Tela de Início" />
  <img src="readme/powerBI/TELA1.png" width="32%" alt="Relatório Principal" />
  <img src="readme/powerBI/TELA2.png" width="32%" alt="Equipe e BI" />
</div>

<br />

A análise do painel legislativo consolidado (com dados mapeados entre **01/06/2026 e 12/06/2026**) gera diagnósticos acionáveis para consultorias de relações governamentais:

*   **Predomínio Temático de "Segurança Pública" e "Saúde":** Das 200 proposições classificadas por IA, o tema *Saúde* desponta com 39 projetos. Isso indica uma forte janela de oportunidade (ou risco regulatório) para empresas do setor monitorarem o Plenário.
*   **Eficiência da IA no Filtro de Ruído:** O alto volume de proposições em "Outros" (115) demonstra a precisão do modelo em isolar matérias administrativas ou protocolares, focando o esforço humano apenas no que é estratégico.
*   **Concentração Política:** A visualização por partido mostra que **PL** e **PT** dominam o volume de proposições, sendo os stakeholders centrais para qualquer estratégia de advocacy.
*   **Detalhamento Executivo:** O cruzamento direto entre o resumo gerado pela IA e a ementa original permite uma tomada de decisão rápida sem a necessidade de ler o documento íntegro da Câmara.

> **Observação sobre Atualização:** O link de deploy (Power BI Web) reflete os dados da última publicação manual do arquivo `.pbix`. Embora o pipeline (Python + n8n) atualize o banco de dados diariamente, o painel público só apresentará os novos dados após o reenvio do arquivo para o Power BI Service.

### <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjlyMG1wb3dkcXRjeG9pcWlsZGNkYWVwN2NlNDd5MmIzZTA4cms0byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/spuwPuxfMgN6OkcVMy/giphy.gif" alt="dados_7_1" width="20" height="20" /> Links do Painel

*   **Protótipo do Layout (Figma):** download dos [layouts](docs/figma/)
*   **Painel Interativo (Power BI Web):** [Acesse o Dashboard Publicado](https://app.powerbi.com/view?r=eyJrIjoiMDQwMjE3NDQtMjExMi00MWExLWFhNTAtNWM3ODAyYzk5M2NlIiwidCI6IjUxZGQ3ZDM4LTYwNzctNDgzNy1hYTE0LWFlNDNmZThiM2ViMCJ9)
*   **Arquivo Fonte do Projeto:** download do arquivo [`legislativoProjeto.pbix`](docs/power-BI/legislativoProjeto.pbix)


## <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExNmR4MWd6cGF0ZDlteHVhajZnczMweDAzcnMxOHQ4cHE5dXM3eXZuMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/qaHWmNBTKPo1uljTIZ/giphy.gif" alt="dados_pitch" width="30" height="30" /> Relatório Técnico e Pitch do Projeto:

<div align="center">
  <table>
    <tr>
      <td>
        <b>
          <a href="https://canva.link/asl0640ohoj05h6">Pitch - Negócios (CLIQUE)</a>
        </b>
      </td>
      <td>
        <b>
          <a href="https://gamma.app/docs/SQUAD-LegoDados-s83lzb6w7v4a9kh">Relatório Técnico (CLIQUE)</a>
        </b>
      </td>
    </tr>
    <tr>
      <td>
        <img src="readme/identidade/pitch.png" width="250px" height="250px">
      </td>
      <td>
        <img src="readme/identidade/relatorio.png" width="250px" height="250px">
      </td>
    </tr>
  </table>
</div>


## Decisões de escopo

* **Tabela fato `despesas` (cota parlamentar):** não implementada. O desafio cita `despesas` como exemplo de tabela fato, mas o produto da Bússola Pública foca em **proposições, votações e temas** — a cota parlamentar não alimenta o digest nem os alertas atuais. É uma decisão de escopo (não um item pendente) e pode ser adicionada em uma iteração futura sem impacto no modelo atual (bastaria uma nova tabela fato `despesas` ligada a `dim_deputados`, carregada com a mesma estratégia de UPSERT).
* **Alerta via Telegram:** não implementado. O desafio sugere e-mail OU Telegram para alertas; o workflow n8n já cobre o mesmo objetivo via **e-mail** — digest diário com as proposições de tema crítico + ramo dedicado de alerta em caso de falha do pipeline (`stderr`). Telegram ficaria redundante com a solução de e-mail entregue.


## <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDY4OGlpMW9yZ3JvcHAzamw3NnU3ZHZ3MHBjZDRyOHdtNG16cHRqMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/Op1ku9feTAxo1zA8ff/giphy.gif" alt="dados_6" width="30" height="30" /> Como Executar o Projeto:

Siga os passos abaixo para clonar o repositório, configurar o ambiente virtual com o Poetry, definir as variáveis de ambiente e executar o pipeline de inteligência legislativa.

### <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTV4ZGFjc3VoZnJvbWs0YW00dXowMGk2OG0wcmVxcWtudmFxbm8xbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/dv7sW46M17UQ36WVBT/giphy.gif" alt="dados_6_1" width="20" height="20" /> **Pré-requisitos**:

Antes de começar, certifique-se de ter instalado em sua máquina:
* **Python** (versão ^3.11 requisitada pelo projeto)
* **Poetry** (gerenciador de pacotes e ambientes virtuais)
* **Git**
* **Docker** (opcional — apenas se for orquestrar o pipeline pelo n8n em container)

### <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTV4ZGFjc3VoZnJvbWs0YW00dXowMGk2OG0wcmVxcWtudmFxbm8xbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/dv7sW46M17UQ36WVBT/giphy.gif" alt="dados_6_2" width="20" height="20" /> **Passo a Passo (execução local com Poetry)**:

1. **Clonar o Repositório e Acessar a Pasta**:
Abra o seu terminal e execute os comandos abaixo para clonar o projeto e entrar no diretório raiz:

```
git clone https://github.com/Mssvargas/bussola-publica_Etapa_Final.git
cd bussola-publica_Etapa_Final
```


2. **Instalar as Dependências com o Poetry**:

O projeto utiliza o Poetry para isolar o ambiente e gerenciar as bibliotecas estruturadas no pyproject.toml (como pandas, sqlalchemy, openai, entre outras). Instale todas as dependências executando:

```
poetry install
```

Este comando criará o ambiente virtual automaticamente e instalará os pacotes nas versões exatas necessárias.

3. **Configurar as Variáveis de Ambiente (.env)**:

O pipeline precisa de credenciais do banco de dados e da API da OpenAI para funcionar.

* Duplique o arquivo de exemplo para criar o seu arquivo .env definitivo:
```
cp .env.example .env
```

* Abra o arquivo .env recém-criado no seu editor (como o VS Code) e preencha os campos com as suas credenciais reais conforme o modelo abaixo:

```
# =============================================================================
# BUSSOLA PUBLICA - Variáveis de Ambiente
# =============================================================================

# --- PostgreSQL (Supabase / Neon / Railway) ---
# No Supabase: Settings > Database > Connection string > URI
DATABASE_URL=postgresql://usuario:senha@host:5432/banco

# --- OpenAI API ---
# Obtenha em: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-SUA_CHAVE_REAL_AQUI

# --- Configurações do Pipeline de IA (Etapas 4 e 5) ---
# DRY_RUN=true  -> Modo Simulação: apenas estima custos de tokens, não consome API e não grava no banco.
# DRY_RUN=false -> Modo Produção: executa o enriquecimento real e salva os dados.
DRY_RUN=true

# Quantidade de proposições pendentes a processar por lote/execução
BATCH_SIZE=10

# Modelo OpenAI escolhido (gpt-4o-mini é ~10x mais barato e ideal para os resumos)
MODELO_IA=gpt-4o-mini

# --- Classificação Temática por Embeddings (Etapa 5 - Caminho A) ---
# Modelo de embedding usado para calcular a similaridade de cosseno entre a
# ementa da proposição e cada tema (Tecnologia, Tributário, Saúde, etc.)
MODELO_EMBEDDING=text-embedding-3-small

# Limiar mínimo de similaridade de cosseno (0 a 1) para aceitar a classificação
# de um tema. Abaixo desse valor, a proposição recebe o tema padrão "Outros".
LIMIAR_TEMA=0.20
```


4. **Executar o Pipeline**:

Com o ambiente configurado e as credenciais prontas, você pode rodar o pipeline através do Poetry:

* **Pipeline completo (extração + carga + IA)**:

```
poetry run python main.py
```

* **Pipeline rápido (sem nova extração — carga + IA sobre o `data/raw` já existente)**:

```
poetry run python main2.py
```

Ambos os pontos de entrada executam, em sequência: Etapa 3 (carga incremental no Supabase) → Etapa 4 (resumo executivo via GPT) → Etapa 5 (classificação temática via embeddings). Se o `DRY_RUN` estiver definido como `true`, você verá no console o diagnóstico de custos e o volume de proposições prontas para processamento, garantindo total controle financeiro antes de consumir os créditos da API.

### <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTV4ZGFjc3VoZnJvbWs0YW00dXowMGk2OG0wcmVxcWtudmFxbm8xbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/dv7sW46M17UQ36WVBT/giphy.gif" alt="dados_6_3" width="20" height="20" /> **(Opcional) Orquestração via n8n em Docker**:

Caso queira reproduzir a automação diária completa (cron 06h + digest por e-mail) em container, com o Docker Desktop aberto e exibindo **Engine Running**:

```bash
docker compose up -d --build
```

Instale as dependências Python dentro do container do n8n:

```bash
docker compose exec -T n8n sh -c "cd /opt/bussola-publica && pip3 install --no-cache-dir --break-system-packages -r requirements.txt"
```

Acesse a interface do n8n em `http://localhost:5678`, crie a conta de administrador, importe o workflow (`n8n/bussola_publica_ingestao_diaria.json` — ou a variante `_WINDOWS.json`), configure as credenciais de PostgreSQL/Supabase e SMTP, e execute o fluxo. Para encerrar:

```bash
docker compose down
```

O passo a passo detalhado de importação e credenciais está em [`n8n/GUIA_IMPORTACAO_n8n.md`](n8n/GUIA_IMPORTACAO_n8n.md).


## <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGU3cXhzeHF5YmhsdmtxdzA1bGg1dWRwMWF6MmZjYWM5MjN2dTg1dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/AvSbLuJ4mVgpl4sG4M/giphy.gif" alt="dados_estrutura" width="30" height="30" />  Estrutura de Pastas e Arquivos:

Abaixo está a arquitetura modular implementada no projeto para garantir a separação de responsabilidades em cada etapa do pipeline:

```
├── .venv/                         # Ambiente virtual local
├── data_raw/                      # Data Lake - Camada Bronze (Arquivos JSON brutos)
│   ├── deputados/                 # JSONs de deputados com timestamp
│   ├── partidos/                  # JSONs de partidos
│   ├── proposicoes/               # JSONs de proposições e autores
│   └── votacoes/                  # JSONs de votações e votos
├── docs/                          # Documentações e relatórios das etapas
│   ├── apresentacoes/             # Pitch e relatório técnico (.pptx)
│   ├── figma/                     # Protótipos de interface (.svg)
│   ├── power-BI/                  # Arquivo fonte do dashboard (.pbix)
│   ├── Etapa4_Camada_IA.pdf       # Relatório de especificação da camada de IA
│   ├── Etapa5_Documentacao_Tecnica.md # Decisões técnicas + prompts da IA
│   └── modelo_dados.md            # Modelo dimensional (tabelas e relacionamentos)
├── logs/                          # Logs de execução do pipeline
├── n8n/                           # Automação (workflow + guia)
│   ├── bussola_publica_ingestao_diaria.json          # Workflow exportado (cron 06h + digest + alerta)
│   ├── bussola_publica_ingestao_diaria_WINDOWS.json  # Variante para ambiente Windows
│   └── GUIA_IMPORTACAO_n8n.md     # Passo a passo de importação e credenciais
├── readme/                        # Imagens e prints usados neste README
│   ├── arquitetura/               # Diagramas, roadmap e schema
│   ├── identidade/                # Logos e capas do squad
│   ├── powerBI/                   # Prints das telas do painel Power BI
│   ├── prints/                    # Evidências (n8n, digest, Supabase, dashboard)
│   ├── team/                      # Fotos dos integrantes do squad
│   └── diagrama_pipeline.svg      # Diagrama da arquitetura do pipeline
├── src/                           # Código-fonte principal do projeto
│   ├── __init__.py
│   ├── ai_layer.py                # Etapa 4: Integração com OpenAI (Resumo Executivo - Caminho B)
│   ├── classificacao_tematica.py  # Etapa 5: Classificação temática via embeddings (Caminho A)
│   ├── config.py                  # Configurações globais e variáveis de ambiente
│   ├── diagnostico.py             # Script de validação e saúde do ambiente
│   ├── extraction.py              # Etapa 1: Scripts de extração/ingestão da API
│   ├── transformation.py          # Etapa 3: Classe PipelineEtapa3 (Orquestrador de carga)
│   └── transformers.py            # Funções de transformação e limpeza com Pandas
├── .env                           # Variáveis de ambiente locais (Credenciais - não versionado)
├── .env.example                   # Modelo de configuração das variáveis de ambiente
├── .gitignore                     # Arquivos ignorados pelo Git
├── LICENSE                        # Licença do projeto
├── main.py                        # Ponto de entrada do pipeline completo (extração + carga + IA)
├── main2.py                       # Ponto de entrada rápido (carga + IA, sem nova extração)
├── poetry.lock                    # Trava de versões das dependências
├── pyproject.toml                 # Configurações do projeto e dependências (Poetry)
└── README.md                      # Documentação do projeto
```


## Segurança

* O arquivo `.env` (com `DATABASE_URL` e `OPENAI_API_KEY` reais) **não é versionado** — está no `.gitignore`. Use sempre o `.env.example` como modelo.
* O workflow do n8n usa **placeholders** de credencial (`REPLACE_POSTGRES_CRED_ID`, `REPLACE_SMTP_CRED_ID`); as credenciais reais ficam apenas na sua instância local do n8n.


## <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExb20yN2Q3NG0wZDJ3bnpjYjIxb2JieWN5dnI0aXNrbzAzc2NqdndybCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/CmeI2Ndgz1B5JWJDbt/giphy.gif" alt="dados_criterios" width="30" height="30" /> Critérios de avaliação atendidos

- **Funcionamento:** pipeline roda do início ao fim (extração → carga → IA → notificação).
- **Modelagem:** modelo estrela preservado; IA adiciona colunas, não quebra o schema.
- **IA aplicada:** tema (embeddings) e resumo (GPT) chegam ao e-mail do cliente — não é decoração.
- **Automação:** workflow n8n agendado, com sucesso e falha tratados.
- **Comunicação:** diagrama, doc técnica, prompts e pitch executivo.


## <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGgzd21kbXZjNWVucm5mcGd4M2VhcmtxNnhyanRuM2JuZXE2eTV2bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/VIWyDnerbiT4wfVTtt/giphy.gif" alt="dados_11" width="30" height="30" /> Equipe (Squad LegoDados):

<div align="center">
  <table>
    <tr>
      <td align="center" valign="top" width="25%">
        <img src="readme/team/Micael.png" width="120px" style="border-radius: 30%;" alt="Micael Lima"/><br />
        <b>Micael Lima</b><br />
        <sup>Data Analytics & AI Engineer</sup><br />
        <small>Python • SQL • Power BI • AI Automation</small><br /><br />
        <a href="https://github.com/micaellimaj" target="_blank">
          <img src="https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub" />
        </a>
        <a href="https://www.linkedin.com/in/micael-lima-data-analytics-ia-engineer/" target="_blank">
          <img src="https://img.shields.io/badge/-LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" />
        </a>
      </td>
      <td align="center" valign="top" width="25%">
        <img src="readme/team/Guilherme.png" width="120px" style="border-radius: 30%;" alt="Guilherme Sobral"/><br />
        <b>Guilherme Sobral</b><br />
        <sup>Analista de Dados / BI</sup><br />
        <small>Power BI • SQL • Excel • BI</small><br /><br />
        <a href="https://github.com/Sobral-git" target="_blank">
          <img src="https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub" />
        </a>
        <a href="https://www.linkedin.com/in/guilherme-sobral-santos/" target="_blank">
          <img src="https://img.shields.io/badge/-LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" />
        </a>
      </td>
      <td align="center" valign="top" width="25%">
        <img src="readme/team/Heitor.png" width="120px" style="border-radius: 30%;" alt="Heitor Nogueira"/><br />
        <b>Heitor Nogueira</b><br />
        <sup>Inteligência de Negócios</sup><br />
        <small>BI • SQL • Excel • MIS</small><br /><br />
        <a href="https://github.com/heitorgraciani" target="_blank">
          <img src="https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub" />
        </a>
        <a href="https://www.linkedin.com/in/heitor-graciani-nogueira-35201b10a/" target="_blank">
          <img src="https://img.shields.io/badge/-LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" />
        </a>
      </td>
      <td align="center" valign="top" width="25%">
        <img src="readme/team/Marlom.png" width="120px" style="border-radius: 30%;" alt="Marlon Vargas"/><br />
        <b>Marlon Vargas</b><br />
        <sup>Power BI Specialist</sup><br />
        <small>Data Analyst • Data Engineer • Power Apps</small><br /><br />
        <a href="https://github.com/Mssvargas" target="_blank">
          <img src="https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub" />
        </a>
        <a href="https://www.linkedin.com/in/marlonssv/" target="_blank">
          <img src="https://img.shields.io/badge/-LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" />
        </a>
      </td>
    </tr>
  </table>
</div>


## <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNzl5enFiZ2FsY2c2YmEyNnNyNWgyYmw4dTR3MzFyYTJqajYycXpvNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/U7P5euFXYtCOFNCbmY/giphy.gif" alt="dados_14" width="30" height="30" /> Conclusão e Aprendizados:

Este projeto marca a consolidação prática dos conhecimentos adquiridos ao longo da **Fase 1 (Fundamentos e Primeiros Pipelines)** da pós-graduação em Engenharia de Dados e Inteligência Artificial da **Xperiun (XP Educação)**. A construção desta esteira de inteligência legislativa permitiu aplicar de ponta a ponta as seguintes disciplinas e competências modulares:

* **Modelagem Relacional & DWH:** Estruturação lógica e física de tabelas Fato e Dimensão utilizando PostgreSQL (Supabase) via SQLAlchemy, garantindo o armazenamento de dados históricos por mais de 30 dias.
* **Manipulação e Limpeza de Dados:** Desenvolvimento de rotinas robustas em Python com a biblioteca Pandas para tratamento de paginação da API da Câmara, saneamento de strings e normalização de payloads brutos (Camada Bronze para Silver).
* **Automação e Orquestração Low-Code:** Integração de scripts nativos em Python dentro do ecossistema n8n através de containers Docker, programando cronjobs diários e gerenciando fluxos alternativos de alertas e falhas (notificações automatizadas).
* **Engenharia de Prompt e IA Generativa:** Implementação prática de LLMs (`gpt-4o-mini`) para geração de resumos executivos acionáveis e enriquecimento de dados por meio de embeddings (`text-embedding-3-small`) combinados com similaridade de cosseno.
* **Colaboração e DevOps:** Controle de versão profissional via Git/GitHub, organização de branches, documentação técnica clara e isolamento de ambientes virtuais com o Poetry.

---

### <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2lsMWwyYzRmdDFwYXhibHNteW9nYTg2cnltZXU1cmhvYzB5NHlneCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/qwYmEIimWmePXLRPKG/giphy.gif" alt="dados_14_1" width="20" height="20" /> Agradecimentos:

Agradecemos primeiramente à **Xperiun / XP Educação** e ao corpo docente (Ítalo Mesquita, Leon Solón, César Germano, Iago Braz) por fornecerem a base teórica e os insights práticos que viabilizaram o desenvolvimento de arquiteturas modernas e integradas.

Expressamos também nosso sincero agradecimento a cada integrante do **Squad LegoDados**. A sinergia, dedicação técnica e o esforço mútuo durante as madrugadas de código, testes de API e refinamento do dashboard no Power BI foram os verdadeiros pilares para transformar dados legislativos complexos em um produto final de alto valor estratégico.

Por fim, um agradecimento pessoal do **Marlon** à sua família — em especial à sua esposa, que segurou todas as pontas com os dois filhos pequenos enquanto as madrugadas de código rolavam soltas. Sem esse apoio em casa, nenhuma linha desse pipeline teria saído do papel. 😂

<br />
<p align="center">
  <kbd>
    <b>🧱 Assim como cada bloco de LEGO se encaixa perfeitamente para dar vida a grandes estruturas, nossa arquitetura une dados, IA e orquestração para construir uma visão legislativa sólida, transparente e indestrutível. 🧱</b>
  </kbd>
</p>
