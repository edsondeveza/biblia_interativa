import streamlit as st
import pandas as pd
from utils import carregar_testamentos, carregar_livros_testamento, carregar_capitulos, carregar_versiculos

def pagina_leitura(conexao):
    st.subheader("Seleção de Testamento, Livro e Capítulo")

    # Seleção de testamento
    testamentos = carregar_testamentos(conexao)
    if testamentos.empty:
        st.warning("Nenhum testamento encontrado no banco de dados.")
        return
    
    # Seleção de testamento
    testamento = st.selectbox("Selecione o Testamento", testamentos["name"])
    testamento_id = testamentos[testamentos["name"] == testamento]["id"].values[0]

    # Seleção de livro
    livros = carregar_livros_testamento(conexao, testamento_id)
    if livros.empty:
        st.warning("Nenhum livro encontrado no banco de dados.")
        return
    
    livro = st.selectbox("Selecione o Livro", livros["name"])
    livro_id = livros[livros["name"] == livro]["id"].values[0]

    # Seleção de capítulo
    capitulos = carregar_capitulos(conexao, livro_id)
    if capitulos.empty:
        st.warning("Nenhum capítulo encontrado para o livro selecionado.")
        return
    
    capitulo = st.selectbox("Selecione o Capítulo", capitulos["chapter"])

    # Exibição dos versículos
    versiculos = carregar_versiculos(conexao, livro_id, capitulo)
    if versiculos.empty:
        st.warning("Nenhum versículo encontrado para o capítulo selecionado.")
        
    else:
        # Gera a tabela HTML sem o índice
        tabela_html = versiculos.to_html(index=False, justify="center", border=2.5)
        st.markdown(tabela_html, unsafe_allow_html=True)
    
