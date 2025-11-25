"""
Página de Busca Simples.

Busca rápida por palavras-chave com filtros básicos
e exportação de resultados.

Autor: Edson Deveza
Data: 2024
Versão: 2.1
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ajuste de path
RAIZ_PROJETO = Path(__file__).parent.parent.absolute()
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from src.database import conectar_banco, buscar_versiculos
from src.export import (
    exportar_csv,
    exportar_xlsx,
    exportar_pdf,
    exportar_html,
)
from src.error_handler import handle_database_error, show_connection_error
from src.logger import log_busca, log_erro
from src.ui_utils import garantir_versao_selecionada

# === Configuração da página ===
st.set_page_config(
    page_title="Busca Simples",
    page_icon="🔍",
    layout="wide",
)

# === Session State ===
if "sugestao_aplicada" not in st.session_state:
    st.session_state.sugestao_aplicada = None

if "disparar_busca" not in st.session_state:
    st.session_state.disparar_busca = False

if "historico_buscas" not in st.session_state:
    st.session_state.historico_buscas = []

# === Título ===
st.title("🔍 Busca Simples")

# Garante versão selecionada
caminho_banco = garantir_versao_selecionada()

# === Conectar ao banco ===
try:
    conexao = conectar_banco(str(caminho_banco))
except Exception as e:
    log_erro("busca_simples_conexao", e)
    show_connection_error()
    st.stop()

versao_atual = st.session_state.get("versao_biblia") or st.session_state.get(
    "versao_selecionada", "N/D"
)
st.markdown(f"**Versão atual:** {versao_atual}")

st.info(
    "💡 **Dica:** Digite uma palavra ou frase para buscar em toda a Bíblia. "
    "Para mais opções, use a **Busca Avançada**."
)

# === Preencher campo se veio de sugestões ===
if st.session_state.sugestao_aplicada:
    st.session_state.input_busca_simples = st.session_state.sugestao_aplicada
    st.session_state.sugestao_aplicada = None


# ==========================================================
# FUNÇÃO PRINCIPAL DA BUSCA
# ==========================================================
def executar_busca(termo: str, filtro_testamento: str, testamento_id: int | None):
    """
    Executa a busca simples no banco de dados.
    """
    import time

    if not termo.strip():
        st.warning("Digite um termo para buscar.")
        return None

    try:
        inicio = time.time()

        resultados = buscar_versiculos(
            conexao,
            termo=termo,
            testamento_id=testamento_id,
        )

        fim = time.time()
        tempo_ms = int((fim - inicio) * 1000)

        if resultados is None or resultados.empty:
            st.warning("Nenhum versículo encontrado para o termo informado.")
            return None

        # Registrar log
        log_busca(termo, len(resultados), tempo_ms, tipo="simples")

        # SALVAR NO HISTÓRICO
        st.session_state.historico_buscas.insert(
            0,
            {
                "termo": termo,
                "resultados": len(resultados),
                "tipo": "Busca Simples",
                "testamento": filtro_testamento,
                "tempo_ms": tempo_ms,
            },
        )
        st.session_state.historico_buscas = st.session_state.historico_buscas[:10]

        st.success(
            f"🔎 Encontrados **{len(resultados)}** versículos contendo "
            f"'{termo}' em **{tempo_ms}ms**"
        )

        # MÉTRICAS RÁPIDAS
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Livros Encontrados", resultados["Livro"].nunique())

        livros_vt = [
            "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio",
            "Josué", "Juízes", "Rute", "1 Samuel", "2 Samuel",
            "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas",
            "Esdras", "Neemias", "Ester", "Jó", "Salmos", "Provérbios",
            "Eclesiastes", "Cânticos", "Isaías", "Jeremias",
            "Lamentações", "Ezequiel", "Daniel", "Oséias", "Joel",
            "Amós", "Obadias", "Jonas", "Miquéias", "Naum",
            "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias",
        ]

        resultados["Testamento"] = resultados["Livro"].apply(
            lambda x: "VT" if x in livros_vt else "NT"
        )

        with col2:
            st.metric(
                "Versículos no VT",
                resultados[resultados["Testamento"] == "VT"].shape[0],
            )

        with col3:
            st.metric(
                "Versículos no NT",
                resultados[resultados["Testamento"] == "NT"].shape[0],
            )

        # LISTAGEM EM TABELA
        st.markdown("---")
        st.subheader("📋 Resultados da Busca")

        resultados = resultados.sort_values(
            by=["Testamento", "Livro", "Capítulo", "Versículo"]
        )

        st.dataframe(
            resultados[
                ["Testamento", "Livro", "Capítulo", "Versículo", "Texto"]
            ].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

        # EXPORTAÇÃO
        st.markdown("---")
        st.subheader("📥 Exportar Resultados")

        colE1, colE2, colE3, colE4 = st.columns(4)

        with colE1:
            exportar_csv(resultados, f"busca_simples_{termo}")

        with colE2:
            exportar_xlsx(resultados, f"busca_simples_{termo}")

        with colE3:
            exportar_pdf(
                resultados, f"Busca Simples: {termo}", f"busca_simples_{termo}"
            )

        with colE4:
            exportar_html(
                resultados, f"Busca Simples: {termo}", f"busca_simples_{termo}"
            )

    except Exception as e:
        log_erro("busca_simples_execucao", e, termo)
        handle_database_error(e, "busca")


# ==========================================================
# FORMULÁRIO DE BUSCA
# ==========================================================
st.markdown("---")

st.subheader("📝 Parâmetros da Busca")

with st.form("form_busca_simples"):
    colF1, colF2 = st.columns([3, 1])

    with colF1:
        termo_busca = st.text_input(
            "Termo de busca",
            key="input_busca_simples",
            value=st.session_state.get("input_busca_simples", ""),
            placeholder="Ex.: fé, graça, amor de Deus...",
        )

    with colF2:
        filtro_testamento = st.selectbox(
            "Testamento",
            ["Todos", "Antigo Testamento", "Novo Testamento"],
            index=0,
        )

    colFB1, colFB2 = st.columns([1, 4])
    with colFB1:
        disparar = st.form_submit_button("🔎 Buscar", use_container_width=True)

    with colFB2:
        st.write(
            "Use a busca simples para localizar rapidamente termos na Bíblia. "
            "Para filtros por livro, faixa de capítulos e outros critérios, "
            "use a **Busca Avançada**."
        )

testamento_id = None
if filtro_testamento == "Antigo Testamento":
    testamento_id = 1
elif filtro_testamento == "Novo Testamento":
    testamento_id = 2

if disparar:
    st.session_state.disparar_busca = True

if st.session_state.disparar_busca:
    st.session_state.disparar_busca = False
    executar_busca(termo_busca, filtro_testamento, testamento_id)


# ==========================================================
# HISTÓRICO DE BUSCAS
# ==========================================================
st.markdown("---")
st.subheader("🕒 Histórico recente de buscas")

if not st.session_state.historico_buscas:
    st.info("Nenhuma busca realizada nesta sessão.")
else:
    for item in st.session_state.historico_buscas:
        termo = item.get("termo", "")
        resultados = item.get("resultados", 0)
        testamento_hist = item.get("testamento")
        tempo_ms_hist = item.get("tempo_ms")

        titulo = f"{termo} • {resultados} resultados"

        if testamento_hist and testamento_hist not in ("", "Todos"):
            titulo += f" ({testamento_hist})"

        if tempo_ms_hist is not None:
            titulo += f" • {tempo_ms_hist}ms"

        with st.expander(titulo):
            st.write(f"Tipo: {item.get('tipo', 'N/D')}")
            if testamento_hist and testamento_hist != "Todos":
                st.write(f"Testamento: {testamento_hist}")
            if item.get("livro") and item["livro"] != "Todos":
                st.write(f"Livro: {item['livro']}")


# ==========================================================
# SUGESTÕES RÁPIDAS
# ==========================================================
st.markdown("---")
st.subheader("✨ Sugestões rápidas de busca")

colS1, colS2, colS3, colS4 = st.columns(4)

sugestoes = [
    ("🕊️ Espírito Santo", "Espírito Santo"),
    ("❤️ Amor de Deus", "amor de Deus"),
    ("🧭 Vontade de Deus", "vontade de Deus"),
    ("🕊️ Paz", "paz"),
    ("🙏 Oração", "oração"),
    ("🪨 Rocha", "rocha"),
    ("🌿 Graça", "graça"),
    ("🛡️ Fé", "fé"),
]

for i, (label, termo_sugerido) in enumerate(sugestoes):
    col = [colS1, colS2, colS3, colS4][i % 4]
    with col:
        if st.button(label, key=f"sug{i}"):
            st.session_state.sugestao_aplicada = termo_sugerido
            st.session_state.disparar_busca = True
            st.rerun()

# Fechar conexão
conexao.close()
