"""
Página de Leitura da Bíblia.

Navegação intuitiva por testamento, livro e capítulo
com opções de visualização personalizáveis.

Autor: Edson Deveza
Data: 2025
Versão: 2.1
"""

from __future__ import annotations
from src.ui_utils import garantir_versao_selecionada
from src.logger import log_leitura, log_erro
from src.error_handler import handle_database_error, show_connection_error
from src.database import (
    conectar_banco,
    carregar_testamentos,
    carregar_livros_testamento,
    carregar_capitulos,
    carregar_versiculos,
)

import sys
from pathlib import Path

import streamlit as st

# Ajuste de path para permitir imports "src.*"
RAIZ_PROJETO = Path(__file__).parent.parent.absolute()
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


# Configuração da página
st.set_page_config(
    page_title="Leitura da Bíblia",
    page_icon="📖",
    layout="wide",
)

st.title("📖 Leitura da Bíblia")

# Garante versão selecionada (se não tiver, mostra seletor aqui mesmo)
caminho_banco = garantir_versao_selecionada()

# Conectar ao banco
try:
    conexao = conectar_banco(str(caminho_banco))
except Exception as e:
    log_erro("leitura_conexao", e)
    show_connection_error()
    st.stop()

versao_atual = (
    st.session_state.get("versao_biblia")
    or st.session_state.get("versao_selecionada", "N/D")
)
st.markdown(f"**Versão atual:** {versao_atual}")

# === SELEÇÃO DE TESTAMENTO E LIVRO ===
col1, col2 = st.columns(2)

try:
    with col1:
        testamentos = carregar_testamentos(conexao)
        if testamentos.empty:
            st.error("Nenhum testamento encontrado.")
            conexao.close()
            st.stop()

        testamento = st.selectbox(
            "📜 Testamento",
            testamentos["name"],
            key="sel_testamento",
        )

        # Mapeamento explícito 1 = VT, 2 = NT
        if "ntigo" in testamento:  # "Antigo Testamento"
            testamento_id = 1
        elif "Novo" in testamento:
            testamento_id = 2
        else:
            testamento_id = int(
                testamentos.loc[testamentos["name"]
                                == testamento, "id"].iloc[0]
            )

    with col2:
        livros = carregar_livros_testamento(conexao, testamento_id)

        if livros.empty:
            st.error(
                "Nenhum livro encontrado para o testamento selecionado.\n\n"
                "Isso normalmente acontece quando os códigos de testamento "
                "(1=VT e 2=NT) não batem com a tabela `testament` do banco."
            )
            conexao.close()
            st.stop()

        livro = st.selectbox(
            "📚 Livro",
            livros["name"],
            key="sel_livro",
        )
        livro_id = int(livros.loc[livros["name"] == livro, "id"].iloc[0])

except Exception as e:
    log_erro("leitura_navegacao", e)
    handle_database_error(e, "navegação")
    conexao.close()
    st.stop()

# === LISTA DE CAPÍTULOS ===
try:
    capitulos = carregar_capitulos(conexao, livro_id)
    if capitulos.empty:
        st.warning("Nenhum capítulo encontrado.")
        conexao.close()
        st.stop()

    lista_caps = sorted(list(capitulos["chapter"]))

except Exception as e:
    log_erro("leitura_capitulos", e)
    handle_database_error(e, "carregamento de capítulos")
    conexao.close()
    st.stop()

# Inicializar capítulo atual no session_state
if "capitulo_atual" not in st.session_state:
    st.session_state.capitulo_atual = lista_caps[0]
else:
    if st.session_state.capitulo_atual not in lista_caps:
        st.session_state.capitulo_atual = lista_caps[0]

capitulo_atual = st.session_state.capitulo_atual

# === NAVEGAÇÃO RÁPIDA ===
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
            st.session_state.capitulo_atual = lista_caps[novo_idx]
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
            st.session_state.capitulo_atual = lista_caps[novo_idx]
            st.rerun()

with nav_col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")

# === SELECTBOX DO CAPÍTULO ===
st.markdown("---")
capitulo = st.selectbox(
    "📖 Capítulo",
    lista_caps,
    index=lista_caps.index(capitulo_atual),
    key="sel_capitulo",
)

if capitulo != capitulo_atual:
    st.session_state.capitulo_atual = capitulo
    st.rerun()

# === OPÇÕES DE FORMATAÇÃO ===
with st.expander("⚙️ Opções de visualização", expanded=False):
    col_fmt1, col_fmt2, col_fmt3 = st.columns(3)

    with col_fmt1:
        tamanho_fonte = st.select_slider(
            "Tamanho da fonte",
            options=["Pequeno", "Médio", "Grande"],
            value="Médio",
        )

    with col_fmt2:
        mostrar_numeros = st.checkbox(
            "Mostrar números dos versículos", value=True)

    with col_fmt3:
        espacamento = st.select_slider(
            "Espaçamento",
            options=["Compacto", "Normal", "Amplo"],
            value="Normal",
        )

tamanhos = {"Pequeno": "14px", "Médio": "16px", "Grande": "18px"}
espacamentos = {"Compacto": "5px", "Normal": "10px", "Amplo": "15px"}

# === EXIBIÇÃO DOS VERSÍCULOS ===
st.markdown(f"## {livro} {capitulo}")

try:
    versiculos = carregar_versiculos(conexao, livro_id, capitulo)
    log_leitura(livro, capitulo, versao_atual)
except Exception as e:
    log_erro("leitura_versiculos", e, f"{livro} {capitulo}")
    handle_database_error(e, "carregamento de versículos")
    conexao.close()
    st.stop()

if versiculos.empty:
    st.warning("⚠️ Nenhum versículo encontrado.")
else:
    for _, row in versiculos.iterrows():
        versiculo_num = row["Versículo"]
        texto = row["Texto"]

        col_texto, col_acoes = st.columns([5, 1])

        with col_texto:
            if mostrar_numeros:
                st.markdown(
                    f"""
                    <div style='margin-bottom: {espacamentos[espacamento]};'>
                        <span style='font-weight: bold; margin-right: 5px;'>
                            {versiculo_num}
                        </span>
                        <span style='font-size: {tamanhos[tamanho_fonte]};'>
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

        with col_acoes:
            if st.button(
                "📝",
                key=f"anot_{livro_id}_{capitulo}_{versiculo_num}",
                help="Adicionar anotação",
            ):
                st.session_state["versiculo_anotacao"] = {
                    "livro": livro,
                    "capitulo": capitulo,
                    "versiculo": versiculo_num,
                    "texto": texto,
                }
                st.switch_page("pages/5_📝_Anotações.py")

# === RESUMO DO CAPÍTULO (placeholder) ===
st.markdown("---")
st.markdown("### 📌 Resumo do capítulo (em desenvolvimento)")
st.info(
    "No futuro, esta seção poderá trazer:\n"
    "- Palavras-chave do capítulo\n"
    "- Temas teológicos principais\n"
    "- Conexões com outros textos bíblicos\n"
)

# === RODAPÉ COM INFORMAÇÕES DO LIVRO ===
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Livro", livro)

with col2:
    total_versiculos = len(versiculos) if not versiculos.empty else 0
    st.metric("Versículos no capítulo", total_versiculos)

with col3:
    anotacoes_capitulo = [
        a
        for a in st.session_state.get("anotacoes", {}).values()
        if a["livro"] == livro and a["capitulo"] == capitulo
    ]
    st.metric("Anotações", len(anotacoes_capitulo))

conexao.close()
