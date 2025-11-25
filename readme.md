# 📖 Bíblia Interativa

_Uma ferramenta moderna para leitura, estudo e busca na Palavra de Deus._  

**Este projeto é fornecido apenas para fins educacionais e de estudo. Não possui finalidade comercial e não se destina, sob qualquer forma, à venda, monetização ou exploração comercial.**

---

## 📚 Índice

1. [Descrição do Projeto](#-descrição-do-projeto)
2. [Estrutura do Projeto](#-estrutura-do-projeto)
3. [Como Executar (Python 312--venv)](#-como-executar-python-312--venv)
4. [Capturas de Tela](#-capturas-de-tela)
5. [Funcionalidades](#-funcionalidades)
6. [Guia de Contribuição](#-guia-de-contribuição)
7. [Requisitos do Sistema](#-requisitos-do-sistema)
8. [Roadmap Futuro](#-roadmap-futuro)

---

## 📝 Descrição do Projeto

A **Bíblia Interativa** é uma aplicação web construída com **Python 3.12** e **Streamlit** para:

- Ler a Bíblia com navegação por **testamento → livro → capítulo → versículo**  
- Realizar **buscas simples e avançadas** por palavras, trechos ou temas  
- Comparar **diferentes versões/traduções** lado a lado  
- Criar e organizar **anotações pessoais** ligadas a versículos específicos  
- Visualizar **estatísticas de leitura, anotações e buscas**  

O foco é ser uma ferramenta de estudo **leve, simples de usar** e com base em **arquivos SQLite** contendo diferentes traduções bíblicas.

---

## 🧱 Estrutura do Projeto

Estrutura sugerida do repositório (pode haver pequenas variações locais):

```bash
biblia_interativa/
├── Home.py                    # Arquivo inicial do Streamlit (menu principal)
├── pages/                     # Páginas adicionais da aplicação (multipage)
│   ├── 1_📖_Leitura.py        # Leitura da Bíblia
│   ├── 2_🔍_Busca_Simples.py  # Busca simples
│   ├── 3_🔍+_Busca_Avançada.py# Busca avançada
│   ├── 4_⚖️_Comparação.py     # Comparação de versões
│   ├── 5_📝_Anotações.py      # Anotações de estudo
│   └── 6_📊_Estatísticas.py   # Estatísticas de uso e da Bíblia
│
├── src/                       # Módulos internos (lógica e serviços)
│   ├── __init__.py
│   ├── database.py            # Conexão e consultas ao SQLite
│   ├── logger.py              # Registro de logs de uso/erros
│   ├── export.py              # Exportação (CSV, XLSX, PDF, HTML)
│   ├── error_handler.py       # Tratamento padronizado de erros
│   ├── annotations.py         # (Opcional) Camada de anotações persistentes
│   └── ui_utils.py            # Utilidades de UI (ex.: seletor global de versão)
│
├── data/                      # Arquivos de banco de dados SQLite (não versionados)
│   ├── ACF.sqlite             # Almeida Corrigida e Fiel
│   ├── ARA.sqlite             # Almeida Revista e Atualizada
│   ├── ARC.sqlite             # Almeida Revista e Corrigida
│   ├── NAA.sqlite             # Nova Almeida Atualizada
│   ├── NVI.sqlite             # Nova Versão Internacional
│   └── ...                    # Demais versões suportadas
│
├── tests/                     # Testes automatizados
│   └── test_database.py       # Testes básicos para o módulo database
│
├── .gitignore                 # Arquivos/pastas ignorados pelo Git
├── README.md                  # Este arquivo
├── requirements.txt           # Dependências do projeto (pip)
└── config.toml                # (Opcional) Configurações extras
```

> 💡 A pasta `data/` normalmente _não_ é versionada no Git (por conter arquivos grandes `.sqlite`).  
> Utilize amostras pequenas ou scripts de criação/população do banco, se quiser distribuir junto.

---

## ▶️ Como Executar (Python 3.12 + venv)

A aplicação foi pensada para rodar com **Python 3.12** e ambiente virtual local (`venv`).  
Abaixo um passo a passo padrão para Windows; as variações para Linux/macOS estão indicadas.

### 1. Clonar o repositório (ou copiar os arquivos)

```bash
git https://github.com/edsondeveza/biblia_interativa
cd biblia_interativa
```

Ou simplesmente copie os arquivos para uma pasta, por exemplo:

```bash
C:\estudos\biblia_interativa
```

### 2. Criar o ambiente virtual (`venv`)

```bash
python -m venv .venv
```

- Isso criará uma pasta `.venv` dentro do projeto.

### 3. Ativar o ambiente virtual

**No Windows (PowerShell ou CMD):**

```bash
.\.venv\Scriptsctivate
```

**No Linux/macOS:**

```bash
source .venv/bin/activate
```

Você deve ver algo como `(.venv)` no início da linha do terminal.

### 4. Instalar dependências

Se existir um arquivo `requirements.txt`, use:

```bash
pip install -r requirements.txt
```

Caso ainda não exista, o mínimo para rodar é:

```bash
pip install streamlit pandas
```

(Dependendo das funcionalidades, podem ser usados também `reportlab` ou outra lib de PDF, etc.)

### 5. Colocar os arquivos da Bíblia na pasta `data/`

Crie a pasta `data/` na raiz do projeto (se ainda não existir) e copie para dentro dela os arquivos `.sqlite` das traduções que você possui, como:

```bash
data/
├── ACF.sqlite
├── ARA.sqlite
├── ARC.sqlite
└── ...
```

### 6. Rodar a aplicação

Com o ambiente virtual **ativo**, execute:

```bash
streamlit run Home.py
```

O navegador abrirá (ou você poderá acessar manualmente) em algo como:

```text
http://localhost:8501
```

A partir daí, você navega pelas páginas usando a barra lateral do Streamlit.

---

## ⚙️ Funcionalidades

### 🔹 Seletor Global de Versão da Bíblia

- Disponível em todas as páginas (graças ao utilitário `src/ui_utils.py`)  
- Permite escolher rapidamente entre as versões disponíveis em `data/`  
- Atualiza a aplicação inteira para usar o `.sqlite` correspondente

### 🔹 Home (`Home.py`)

- Apresenta a visão geral do projeto
- Explica as principais funcionalidades
- Oferece botões de navegação para as demais páginas

### 🔹 Leitura da Bíblia (`pages/1_📖_Leitura.py`)

- Navegação por: **Testamento → Livro → Capítulo**
- Exibição dos versículos com:
  - Opção de mostrar/ocultar números de versículos
  - Ajuste de tamanho de fonte
  - Ajuste de espaçamento entre linhas
- Botão em cada versículo para criar anotações ligadas àquele texto

### 🔹 Busca Simples (`pages/2_🔍_Busca_Simples.py`)

- Campo de busca por **palavra ou trecho**
- Filtro por **testamento (VT / NT / Todos)**
- Exibe:
  - Total de versículos encontrados
  - Quantidade por testamento
  - Lista em tabela (`Livro`, `Capítulo`, `Versículo`, `Texto`)
- Exportação de resultados em:
  - CSV
  - XLSX
  - PDF
  - HTML
- Histórico de buscas recentes (com tempo de execução)

### 🔹 Busca Avançada (`pages/3_🔍+_Busca_Avançada.py`)

- Permite combinar **múltiplas palavras** com operador lógico:
  - `E` (todas as palavras)
  - `OU` (qualquer palavra)
- Opção de **“frase exata”**
- Filtros por:
  - Testamento
  - Livro específico
- Exibe métricas avançadas:
  - Quantidade de livros encontrados
  - Quantidade de capítulos distintos
  - Total de versículos
- Exportação de resultados (CSV, XLSX, PDF, HTML)
- Histórico compartilhado com a busca simples

### 🔹 Comparação de Versões (`pages/4_⚖️_Comparação.py`)

- Seleção de **um texto base** (Testamento → Livro → Capítulo → Versículo opcional)
- Escolha de até **3 versões** diferentes (arquivos `.sqlite`)
- Exibe os versículos lado a lado em uma tabela, cada coluna sendo uma versão
- Ideal para estudo comparativo de traduções

### 🔹 Anotações (`pages/5_📝_Anotações.py`)

- Criação de anotações ligadas a:
  - Livro
  - Capítulo
  - Versículo
- Possibilidade de registrar também:
  - Trecho do versículo
  - Texto livre de reflexão/estudo
  - Tags (fé, graça, promessa, oração, etc.)
- Listagem de anotações com filtros por livro e por tag
- Botões para:
  - Editar anotação existente
  - Excluir anotação
- Integração com a página de Leitura (botão 📝 em cada versículo)

> Atualmente as anotações são mantidas em `st.session_state`.  
> Futuramente, podem ser persistidas em SQLite ou outro armazenamento.

### 🔹 Estatísticas (`pages/6_📊_Estatísticas.py`)

Dividida em três abas:

1. **Bíblia**
   - Número total de livros, capítulos e versículos
   - Distribuição de versículos entre Antigo e Novo Testamento
   - Top 10 livros com mais versículos (tabela e gráfico)
2. **Anotações**
   - Quantidade de anotações
   - Quantidade de livros anotados
   - Distribuição de anotações por livro
   - Tags mais usadas
3. **Buscas**
   - Total de buscas realizadas na sessão
   - Tipos de busca (simples x avançada)
   - Média de resultados por busca
   - Termos mais buscados

---

## 🤝 Guia de Contribuição

Se você quiser contribuir com o projeto (ou apenas manter padrão na sua própria cópia), seguem algumas sugestões:

### 1. Organização de Branches (opcional, se usar Git)

- `main` ou `master`: versão estável
- `develop`: desenvolvimento contínuo
- `feature/<nome>`: novas funcionalidades
- `fix/<nome>`: correções pontuais

### 2. Estilo de Código

- Utilize **Python 3.12**
- Siga o máximo possível o padrão **PEP8**
- Use **type hints** quando possível:
  - `def funcao(x: int) -> str:`
- Funções e módulos com **docstrings** claras:
  - O que fazem
  - Principais parâmetros
  - Valor de retorno

### 3. Dependências

- Sempre que adicionar uma nova biblioteca, inclua no `requirements.txt`
- Evite dependências desnecessárias (principalmente pesadas)

### 4. Testes

- Centralizar testes em `tests/`
- Exemplo de execução (com venv ativo):

```bash
pytest -v
```

- O arquivo `tests/test_database.py` já serve como base para novos testes

### 5. Padrão de Commits (sugestão)

- `feat: descrição da nova funcionalidade`
- `fix: correção de algum bug`
- `refactor: melhoria interna de código`
- `docs: ajustes em documentação`
- `test: inclusão/melhoria de testes`

### 6. Sugestões de Melhorias

Antes de implementar algo maior, é interessante registrar (como issue ou TODO) ideias como:

- Persistência das anotações em banco de dados
- Sistema de usuários/perfis
- Exportação de planos de leitura
- Integração com APIs externas (quando houver Bíblias de domínio público)

---

## 🖥️ Requisitos do Sistema

- **Python**: 3.12.x  
- **Sistema Operacional**:
  - Windows 10/11
  - Linux
  - macOS
- **Bibliotecas principais**:
  - `streamlit`
  - `pandas`
  - (Opcional) libs de exportação como `openpyxl`, `reportlab`, etc.

Hardware mínimo:

- CPU dual-core
- 4 GB de RAM
- Navegador moderno (Chrome, Edge, Firefox, etc.)

---

## 🚀 Roadmap Futuro

Algumas ideias de evolução para próximas versões:

- 🔍 **Highlight** das palavras buscadas nos resultados
- 🎨 **Tema claro/escuro** com seletor global
- 🧾 **Exportação temática de PDF** (layout mais elegante para impressão)
- 📊 **Gráficos adicionais** em Estatísticas (radar, séries temporais, etc.)
- 📚 **Buscas por tema** (no estilo de concordância bíblica)
- ⭐ **Favoritos** (livros, capítulos, versículos ou buscas favoritas)
- 🔐 Persistência de anotações e favoritos em banco de dados

---

> Se você estiver lendo este README dentro do próprio projeto local, parabéns:  
> a maior parte da fundamentação já está pronta. Agora é aprofundar o código, as funcionalidades e, claro, o estudo da Palavra. 🙏
