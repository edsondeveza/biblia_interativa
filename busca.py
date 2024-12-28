import streamlit as st
from utils import buscar_versiculos, exportar_csv, exportar_pdf, exportar_xlsx

def pagina_busca(conexao):
    st.subheader("Busca na Bíblia")

    # Seleção de testamento para busca
    filtro_testamento = st.radio("Escolha o Testamento para a Busca", ["Ambos", "Velho Testamento", "Novo Testamento"])
    testamento_id = None
    if filtro_testamento == "Velho Testamento":
        testamento_id = 1
    elif filtro_testamento == "Novo Testamento":
        testamento_id = 2

    # Termo de busca
    termo = st.text_input("Digite o termo para buscar:")

    if st.button("Buscar"):
        resultados = buscar_versiculos(conexao, termo, testamento_id)
        if not resultados.empty:
            # Gera a tabela HTML sem índice
            tabela_html = resultados.to_html(index=False, justify="center", border=1)
            st.markdown(tabela_html,unsafe_allow_html=True)
            
            # Opções de exportação
            exportar_xlsx(resultados)  # Botão para exportar CSV
            exportar_csv(resultados)  # Botão para exportar CSV
            exportar_pdf(resultados)  # Botão para exportar PDF
        else:
            st.warning("Nenhum resultado encontrado.")
