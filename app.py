import streamlit as st
import os
import sqlite3
from leitura import pagina_leitura
from busca import pagina_busca

# Diretório dos bancos de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def conectar_banco(caminho):
    return sqlite3.connect(caminho)

def main():
    st.set_page_config(page_title="Bíblia Interativa", page_icon="📖", layout="wide")

    # Cabeçalho da aplicação
    st.title("📖 Bíblia Sagrada Interativa")
    st.sidebar.title("Navegação")

    # Escolha da versão
    versoes = ["ACF", "ARA", "ARC", "AS21", "JFAA", "KJA", "KJF", "NAA", "NBV", "NTLH", "NVI", "NVT", "TB"]
    versao = st.sidebar.selectbox("Escolha a Versão da Bíblia", versoes)
    caminho_banco = os.path.join(DATA_DIR, f"{versao}.sqlite")

    if not os.path.exists(caminho_banco):
        st.error(f"O banco de dados para a versão {versao} não foi encontrado!")
        return

    conexao = conectar_banco(caminho_banco)

    # Navegação personalizada
    menu = st.sidebar.radio("Menu", ["Página Inicial", "Leitura da Bíblia", "Busca na Bíblia"])

    if menu == "Página Inicial":
        st.write("### Bem-vindo à Bíblia Interativa!")
        st.write("Escolha uma opção no menu à esquerda para começar.")
        
        #st.image("static/bible_image.jpg", use_column_width=True)  # Exemplo de imagem estática na pasta 'static'
    elif menu == "Leitura da Bíblia":
        pagina_leitura(conexao)
    elif menu == "Busca na Bíblia":
        pagina_busca(conexao)

    conexao.close()

if __name__ == "__main__":
    main()
