from operator import index
import pandas as pd
import sqlite3
from fpdf import FPDF
import streamlit as st
import io



# Função para conexão com o banco de dados
def conectar_banco(caminho):
    return sqlite3.connect(caminho)

# Função para carregar os Testamentos
def carregar_testamentos(conexao):
    return pd.read_sql_query("SELECT id, name FROM testament", conexao)

# Função para carregar os livros de um testamento específico
def carregar_livros_testamento(conexao, testamento_id):
    return pd.read_sql_query(f"SELECT id, name FROM book WHERE testament_reference_id = {testamento_id}", conexao)

# Função para carregar os capítulos de um livro específico
def carregar_capitulos(conexao, livro_id):
    return pd.read_sql_query(f"SELECT DISTINCT chapter FROM verse WHERE book_id = {livro_id}", conexao)

# Função para carregar os versículos de um capítulo específico de um livro
def carregar_versiculos(conexao, livro_id, capitulo):
    # Validações para evitar valores inválidos
    if livro_id is None or capitulo is None:
        raise ValueError("livro_id s capitulo não pedem ser nulos.")
    if isinstance(livro_id, int) or not isinstance(capitulo, int):
        raise ValueError("livro_id e capitulo devem ser do tipo inteiro.")
    # Construção da query como uma string válida
    query = f"""
        SELECT verse AS Versículo, text AS Texto 
        FROM verse 
        WHERE book_id = {livro_id} AND chapter = {capitulo}
        
    """
    
    # Executa a consulta e retorna o DataFrame
    return pd.read_sql_query(query, conexao).reset_index(drop=True)

# Função para buscar versículos no banco de dados
def buscar_versiculos(conexao, termo, testamento_id=None):
    # Consulta SQL base
    query = """
        SELECT book.name AS Livro, chapter AS Capítulo, verse AS Versículo, text AS Texto
        FROM verse
        JOIN book ON verse.book_id = book.id   
    """
    # Filtro para buscar pelo termo no texto do versículo
    filtros =[f"text LIKE '%{termo}%'"]
    if testamento_id:
        filtros.append(f"book.testament_reference_id = {testamento_id}") # Adiciona filtro pelo testamento, se necessário
    if filtros:
        query += " WHERE " + " AND ".join(filtros) # Adiciona os filtros à consulta
    return pd.read_sql_query(query, conexao).reset_index(drop=True) # Executa a consulta e retorna um DataFrame

    
# Função para exportar pesquisa para CSV
def exportar_csv(df):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Exportar como CSV",
        data = csv,
        file_name="resultados.csv",
        mime="text/csv"
    )
    return
# Função para exportar pesquisa para Excel
def exportar_xlsx(df):
    # Cria um arquivo Excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
        
    # Prepara o arquivo para download
    st.download_button(
        label="Exportar como Excel",
        data = output.getvalue(),
        file_name="resultados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    return
    
# Função para exportar pesquisa para PDF
def exportar_pdf(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Adicionar título
    pdf.cell(200, 10, txt="Resultados da Busca na Bíblia", ln=True, align='C') # pyright: ignore[reportCallIssue]
    pdf.ln(10)

    # Adicionar dados
    for i, row in df.iterrows():
        # Usa o método encode() para lidar com caracteres especiais
        linha = f"{row['Livro']} {row['Capítulo']}:{row['Versículo']} - {row['Texto']}"
        try:
            pdf.multi_cell(0, 10, linha.encode('latin-1', 'replace').decode('latin-1'))
        except UnicodeEncodeError:
            st.error("Erro ao codificar caracteres Unicode no PDF.")

    # Salva o PDF em memória e disponibiliza para download
    pdf_output = pdf.output(dest='S').encode('latin-1', 'replace') # pyright: ignore[reportAttributeAccessIssue]
    st.download_button(
        label="Exportar como PDF",
        data=pdf_output,
        file_name="resultados.pdf",
        mime="application/pdf"
    )
