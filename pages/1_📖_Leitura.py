"""
Página de Leitura da Bíblia
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Encontrar a raiz do projeto
RAIZ_PROJETO = Path(__file__).parent.parent.absolute()
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from src.database import (
    conectar_banco,
    carregar_testamentos,
    carregar_livros_testamento,
    carregar_capitulos,
    carregar_versiculos,
)

st.set_page_config(page_title="Leitura da Bíblia", page_icon="📖", layout="wide")

# =========================
# SELETOR DE VERSÃO GLOBAL
# =========================

with st.sidebar:
    st.markdown("### 📖 Versão da Bíblia")

    # Descobrir versões disponíveis (arquivos .sqlite da pasta data)
    raiz_projeto = os.path.dirname(os.path.dirname(__file__))  # .../biblia_interativa
    pasta_biblias = os.path.join(raiz_projeto, "data")         # .../biblia_interativa/data

    if not os.path.isdir(pasta_biblias):
        st.error(f"❌ Pasta de bíblias não encontrada: {pasta_biblias}")
    else:
        versoes_disponiveis = [
            f.replace(".sqlite", "")
            for f in os.listdir(pasta_biblias)
            if f.endswith(".sqlite")
        ]

        if not versoes_disponiveis:
            st.error("❌ Nenhuma versão (.sqlite) encontrada na pasta data.")
        else:
            # Valor atual (se ainda não existir, usa a primeira versão)
            versao_atual = st.session_state.get("versao_selecionada", versoes_disponiveis[0])

            versao_escolhida = st.selectbox(
                "Versão:",
                versoes_disponiveis,
                index=versoes_disponiveis.index(versao_atual),
                key="versao_global_selector",
            )

            if versao_escolhida != versao_atual:
                st.session_state.versao_selecionada = versao_escolhida
                st.session_state.caminho_banco = os.path.join(
                    pasta_biblias, versao_escolhida + ".sqlite"
                )
                st.rerun()


st.title("📖 Leitura da Bíblia")

# ---------------------------------------------------
# Verificar se a versão foi selecionada
# ---------------------------------------------------
if "caminho_banco" not in st.session_state:
    st.warning("⚠️ Por favor, selecione uma versão da Bíblia na página inicial.")
    if st.button("← Voltar para Home"):
        st.switch_page("Home.py")
    st.stop()

# ---------------------------------------------------
# Conectar ao banco
# ---------------------------------------------------
try:
    conexao = conectar_banco(st.session_state.caminho_banco)
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco de dados: {e}")
    st.stop()

st.markdown(f"**Versão atual:** {st.session_state.versao_selecionada}")

# ===================================================
# SELEÇÃO DE TESTAMENTO E LIVRO
# ===================================================
col1, col2 = st.columns(2)

with col1:
    testamentos = carregar_testamentos(conexao)
    if testamentos.empty:
        st.error("Nenhum testamento encontrado.")
        st.stop()

    testamento = st.selectbox(
        "📜 Testamento",
        testamentos["name"],
        key="sel_testamento",
    )
    testamento_id = testamentos.loc[
        testamentos["name"] == testamento, "id"
    ].values[0]  # pyright: ignore[reportAttributeAccessIssue]

with col2:
    livros = carregar_livros_testamento(conexao, testamento_id)
    if livros.empty:
        st.warning("Nenhum livro encontrado.")
        st.stop()

    livro = st.selectbox(
        "📚 Livro",
        livros["name"],
        key="sel_livro",
    )
    livro_id = livros.loc[livros["name"] == livro, "id"].values[0] # pyright: ignore[reportAttributeAccessIssue]

# ===================================================
# LISTA DE CAPÍTULOS E ESTADO sel_capitulo
# ===================================================
capitulos = carregar_capitulos(conexao, livro_id)
if capitulos.empty:
    st.warning("Nenhum capítulo encontrado.")
    st.stop()

lista_caps = sorted(list(capitulos["chapter"]))

# Inicializa o capítulo atual no session_state
if "sel_capitulo" not in st.session_state:
    st.session_state.sel_capitulo = lista_caps[0]
else:
    # Se mudou de livro e o capítulo não existe nesse livro, volta ao primeiro
    if st.session_state.sel_capitulo not in lista_caps:
        st.session_state.sel_capitulo = lista_caps[0]

capitulo_atual = st.session_state.sel_capitulo

# ===================================================
# NAVEGAÇÃO RÁPIDA (Anterior / Próximo / Home)
# ===================================================
st.markdown("---")
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    desabilitar_anterior = capitulo_atual == lista_caps[0]
    if st.button(
        "⬅️ Anterior",
        use_container_width=True,
        disabled=desabilitar_anterior,
    ):
        if not desabilitar_anterior:
            idx = lista_caps.index(capitulo_atual)
            novo_idx = max(0, idx - 1)
            st.session_state.sel_capitulo = lista_caps[novo_idx]
            st.rerun()

with nav_col2:
    desabilitar_proximo = capitulo_atual == lista_caps[-1]
    if st.button(
        "➡️ Próximo",
        use_container_width=True,
        disabled=desabilitar_proximo,
    ):
        if not desabilitar_proximo:
            idx = lista_caps.index(capitulo_atual)
            novo_idx = min(len(lista_caps) - 1, idx + 1)
            st.session_state.sel_capitulo = lista_caps[novo_idx]
            st.rerun()

with nav_col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")

# ===================================================
# SELECTBOX DO CAPÍTULO (usa o valor do session_state)
# ===================================================
st.markdown("---")
capitulo = st.selectbox(
    "📄 Capítulo",
    lista_caps,
    index=lista_caps.index(st.session_state.sel_capitulo),
    key="sel_capitulo",
)

# NÃO mexe em st.session_state.sel_capitulo aqui;
# o próprio selectbox já atualiza essa chave.

# ===================================================
# EXIBIÇÃO DOS VERSÍCULOS
# ===================================================
st.markdown(f"## {livro} {capitulo}")

versiculos = carregar_versiculos(conexao, livro_id, capitulo)

if versiculos.empty:
    st.warning("⚠️ Nenhum versículo encontrado.")
else:
    # Opções de visualização
    with st.expander("⚙️ Opções de Visualização"):
        col1, col2, col3 = st.columns(3)

        with col1:
            mostrar_numeros = st.checkbox("Mostrar números", value=True)
        with col2:
            tamanho_fonte = st.select_slider(
                "Tamanho da fonte",
                options=["Pequeno", "Médio", "Grande"],
                value="Médio",
            )
        with col3:
            espacamento = st.select_slider(
                "Espaçamento",
                options=["Compacto", "Normal", "Amplo"],
                value="Normal",
            )

    tamanhos = {"Pequeno": "14px", "Médio": "16px", "Grande": "18px"}
    espacamentos = {"Compacto": "5px", "Normal": "10px", "Amplo": "15px"}

    for _, row in versiculos.iterrows():
        versiculo_num = row["Versículo"]
        texto = row["Texto"]

        if mostrar_numeros:
            st.markdown(
                f"""
                <div style='margin-bottom: {espacamentos[espacamento]};'>
                    <span style='font-weight: bold; color: #667eea; font-size: {tamanhos[tamanho_fonte]};'>
                        {versiculo_num}
                    </span>
                    <span style='font-size: {tamanhos[tamanho_fonte]}; line-height: 1.6;'>
                        {texto}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style='margin-bottom: {espacamentos[espacamento]}; 
                            font-size: {tamanhos[tamanho_fonte]}; 
                            line-height: 1.6;'>
                    {texto}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Botão para adicionar anotação
        if st.button(f"📝 Anotar v.{versiculo_num}", key=f"anot_{versiculo_num}"):
            st.session_state.anotacao_livro = livro
            st.session_state.anotacao_capitulo = capitulo
            st.session_state.anotacao_versiculo = versiculo_num
            st.switch_page("pages/5_📝_Anotações.py")

# ===================================================
# ESTATÍSTICAS DO CAPÍTULO
# ===================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Versículos", len(versiculos))

with col2:
    palavras_total = sum(len(str(row["Texto"]).split()) for _, row in versiculos.iterrows())
    st.metric("Total de Palavras", palavras_total)

with col3:
    anotacoes_capitulo = [
        a
        for a in st.session_state.get("anotacoes", {}).values()
        if a["livro"] == livro and a["capitulo"] == capitulo
    ]
    st.metric("Anotações", len(anotacoes_capitulo))

conexao.close()
