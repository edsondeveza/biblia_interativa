# **Bíblia Interativa**

*Uma plataforma moderna para leitura, estudo e busca na Palavra de Deus.*

## **Índice**

1. [Descrição do Projeto](#descrição-do-projeto)
2. [Visão Geral do Projeto](#visão-geral-do-projeto)
3. [Funcionalidades Principais](#funcionalidades-principais)
4. [Público-Alvo](#público-alvo)
5. [Tecnologias Utilizadas](#tecnologias-utilizadas)
6. [Diferenciais do Projeto](#diferenciais-do-projeto)
7. [Estrutura Final do Projeto](#estrutura-final-do-projeto)

---

## **Descrição do Projeto**

**Nome do Projeto**: Bíblia Interativa  
**Objetivo**: Proporcionar aos usuários uma experiência moderna, acessível e personalizada para leitura, estudo e busca na Palavra de Deus, por meio de uma ferramenta interativa e fácil de usar.

---

## Visão Geral do Projeto

A Bíblia Interativa é uma ferramenta digital inovadora, projetada para transformar a leitura e o estudo da Palavra de Deus. Com uma interface amigável e ferramentas poderosas, o sistema permite que os usuários naveguem por diferentes versões bíblicas, explorem livros, capítulos e versículos, além de realizar buscas temáticas aprofundadas. Também oferece funcionalidades para exportação de dados e impressão, sendo útil tanto para estudos individuais quanto em grupo.

---

## **Funcionalidades Principais**

1. **Leitura da Bíblia**:
   - Navegação intuitiva por testamento, livro, capítulo e versículo.
   - Exibição clara e organizada do texto bíblico, sem sobrecarga de índices.

2. **Busca Avançada**:
   - Pesquisa por palavras-chave com filtros por Velho ou Novo Testamento.
   - Resultados detalhados com referências específicas de livro, capítulo e versículo.

3. **Exportação de Resultados**:
   - Exportação dos resultados da busca para formatos CSV, XLSX e PDF.
   - Impressão direta da tabela de resultados.

4. **Interface Amigável**:
   - Navegação intuitiva com um menu lateral fácil de usar.
   - Página inicial com uma mensagem de boas-vindas e imagem inspiradora.

---

## **Público-Alvo**

- Cristãos que buscam aprofundar o estudo da Bíblia de maneira prática e moderna.
- Professores de Escola Dominical e líderes religiosos.
- Pessoas interessadas em uma experiência dinâmica e interativa de leitura bíblica.

---

## **Tecnologias Utilizadas**

- **Linguagem de Programação**: Python.
- **Framework**: Streamlit (para interface de usuário interativa).
- **Banco de Dados**: SQLite (para armazenamento dos textos bíblicos).
- **Bibliotecas Complementares**:
  - **Pandas**: Manipulação de dados e análise.
  - **FPDF**: Geração de relatórios em formato PDF.
  - **XlsxWriter**: Criação e exportação de arquivos Excel.

---

## **Diferenciais do Projeto**

- **Suporte a múltiplas versões da Bíblia**: ACF, ARC, NVI e outras.
- **Exportação personalizável**: Exportação fácil e rápida dos resultados da busca.
- **Busca rápida e precisa**: Ideal para estudos bíblicos e pesquisas temáticas.
- **Design responsivo e minimalista**: Foco na leitura bíblica, com um layout simples e intuitivo.

---

## **Estrutura Final do Projeto**

```plaintext
bible_project/
├── .streamlit/             # Configurações do Streamlit
│   ├── config.toml
├── data/                   # Bancos de dados SQLite
│   ├── ACF.sqlite
│   ├── ARA.sqlite
│   └── ...
├── app.py                  # Arquivo principal da aplicação
├── busca.py                # Lógica da página de busca
├── leitura.py              # Lógica da página de leitura
├── utils.py                # Funções auxiliares (manipulação de dados, SQL)
├── poetry.lock             # Arquivo gerado pelo Poetry
├── pyproject.toml          # Configuração do Poetry
├── README.md               # Documentação do projeto
├── requirements.txt        # Dependências do projeto
└── .gitignore              # Arquivos ignorados pelo Git

---




