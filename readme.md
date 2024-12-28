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
8. [Como Executar](#como-executar)
9. [Requisitos do Sistema](#requisitos-do-sistema)
10. [Agradecimentos](#agradecimentos)
11. [Contribuindo](#contribuindo)
12. [Licença](#licença)
13. [Mensagem Final](#mensagem-final)

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
```

---

## **Como Executar**

1. *Clone o repositório:*

   ```bash
   git clone https://github.com/edsondeveza/biblia_interativa.git
   cd biblia_interativa

2. *Crie um ambiente virtual (opcional, mas recomendado):*

   ```bash
   python -m venv venv
   source venv/bin/activate       # Linux/Mac
   venv\Scripts\activate          # Windows

3. *Instale as dependências:*

   ```bash

   pip install -r requirements.txt
4. *Execute o aplicativo:*

   ```bash
   streamlit run app.py 

5. *Acesse no navegador:*

- O Streamlit abrirá automaticamente uma janela no navegador. Caso isso não ocorra, acesse <http://localhost:8501>.

---

## **Requisitos do Sistema**

- **Python**: Versão 3.13 ou superior.
- **Streamlit**: Versão 1.41.1 ou superior.
- **Bibliotecas Necessárias**: Listadas em requirements.txt.
- **Sistema Operacional**: Compatível com Windows, macOS e Linux.

---

## **Agradecimentos**

Gostaria de expressar minha mais sincera gratidão:

- **A Deus**, por me capacitar e guiar na realização deste projeto, que tem como propósito levar Sua Palavra a mais pessoas.
- **Aos meus amigos e familiares**, pelo apoio incondicional e incentivo constante.
- **À comunidade de desenvolvedores**, que compartilha conhecimento e inspira a criação de soluções inovadoras.
- **Aos usuários desta ferramenta**, que dão vida e significado a este projeto.
- **Ao meu professor Vinícius Rocha Lima e à Empowerdata**, por serem fundamentais na minha capacitação e no desenvolvimento da minha trajetória com Python.

**Juntos, continuamos espalhando fé, conhecimento e esperança!**

---

## **Contribuindo**

Contribuições são muito bem-vindas!  

Se você deseja ajudar a melhorar este projeto, siga os passos abaixo:

1. Faça um fork deste repositório.
2. Crie uma branch para suas alterações:

   ```bash
   git checkout -b minha-nova-feature
3. Commit suas alterações:

   ```bash
   git commit -m 'Adiciona nova funcionalidade'
4. Envie para sua branch:

   ```bash
   git push origin minha-nova-feature
5. Abra um Pull Request

Vamos construir juntos uma plataforma ainda mais impactante!

---

## **Licença**

Este projeto está licenciado sob a Licença MIT. Sinta-se à vontade para usá-lo, modificá-lo e distribuí-lo, desde que os devidos créditos sejam mantidos.

## **Mensagem Final**

A Bíblia Interativa não é apenas uma ferramenta digital, mas um verdadeiro companheiro na jornada espiritual de cada usuário. Unindo tecnologia e fé, nossa missão é facilitar o acesso à Palavra de Deus, inspirar vidas e fortalecer a fé de milhares de pessoas, oferecendo uma experiência única e enriquecedora.
