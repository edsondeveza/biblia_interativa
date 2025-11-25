"""
Página de Estatísticas.

Mostra estatísticas da Bíblia selecionada, das anotações
e das buscas realizadas na sessão.

Autor: Edson Deveza
Versão: 2.1
Compatível: Python 3.12
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ajuste de path para permitir imports "src.*"
RAIZ_PROJETO = Path(__file__).parent.parent.absolute()
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from src.database import conectar_banco
from src.error_handler import handle_database_error, show_connection_error
from src.logger import log_erro
from src.ui_utils import garantir_versao_selecionada


st.set_page_config(
    page_title="Estatísticas",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Estatísticas de Uso e da Bíblia")

# Garante versão selecionada
caminho_banco = garantir_versao_selecionada()

versao_atual = st.session_state.get("versao_biblia") or st.session_state.get(
    "versao_selecionada", "N/D"
)
st.markdown(f"**Versão atual:** {versao_atual}")

try:
    conexao = conectar_banco(str(caminho_banco))
except Exception as e:
    log_erro("estatisticas_conexao", e)
    show_connection_error()
    st.stop()


def estatisticas_biblia():
    """Calcula estatísticas da Bíblia a partir do banco atual."""
    try:
        df_versos = pd.read_sql_query(
            """
            SELECT v.book_id,
                   v.chapter,
                   v.verse AS versiculo,
                   v.text AS texto,
                   b.name AS livro
            FROM verse v
            JOIN book b ON v.book_id = b.id
            """,
            conexao,
        )
    except Exception as e:
        log_erro("estatisticas_biblia_query", e)
        handle_database_error(e, "estatísticas da Bíblia")
        return

    if df_versos.empty:
        st.warning("Não foi possível carregar versículos para estatísticas.")
        return

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

    df_versos["testamento"] = df_versos["livro"].apply(
        lambda x: "Antigo Testamento" if x in livros_vt else "Novo Testamento"
    )

    n_livros = df_versos["livro"].nunique()
    n_capitulos = df_versos[["livro", "chapter"]].drop_duplicates().shape[0]
    n_versiculos = len(df_versos)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Livros", n_livros)
    with col2:
        st.metric("Capítulos", n_capitulos)
    with col3:
        st.metric("Versículos", n_versiculos)

    st.markdown("---")
    st.subheader("📚 Distribuição por Testamento")

    dist_test = (
        df_versos.groupby("testamento")["versiculo"]
        .count()
        .reset_index(name="qtde_versiculos")
    )
    st.dataframe(dist_test, use_container_width=True, hide_index=True)
    st.bar_chart(
        dist_test.set_index("testamento")["qtde_versiculos"],
    )

    st.markdown("---")
    st.subheader("🏆 Top 10 livros com mais versículos")

    top_livros = (
        df_versos.groupby("livro")["versiculo"]
        .count()
        .reset_index(name="qtde_versiculos")
        .sort_values("qtde_versiculos", ascending=False)
        .head(10)
    )

    st.dataframe(top_livros, use_container_width=True, hide_index=True)
    st.bar_chart(
        top_livros.set_index("livro")["qtde_versiculos"],
    )


def estatisticas_anotacoes():
    """Estatísticas das anotações armazenadas no session_state."""
    anot = st.session_state.get("anotacoes", {})
    if not anot:
        st.info("Nenhuma anotação registrada nesta sessão.")
        return

    df = pd.DataFrame(anot.values())

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de anotações", len(df))
    with col2:
        st.metric("Livros anotados", df["livro"].nunique())

    st.markdown("#### 📚 Anotações por livro")

    dist_livro = (
        df.groupby("livro")["anotacao"]
        .count()
        .reset_index(name="qtde_anotacoes")
        .sort_values("qtde_anotacoes", ascending=False)
    )

    st.dataframe(dist_livro, use_container_width=True, hide_index=True)

    if len(dist_livro) > 1:
        st.bar_chart(
            dist_livro.set_index("livro")["qtde_anotacoes"],
        )

    if "tags" in df.columns:
        st.markdown("#### 🏷️ Tags mais usadas")
        df_tags = df.explode("tags")
        df_tags = df_tags[df_tags["tags"].notna() & (df_tags["tags"] != "")]
        if not df_tags.empty:
            dist_tags = (
                df_tags.groupby("tags")["anotacao"]
                .count()
                .reset_index(name="qtde")
                .sort_values("qtde", ascending=False)
            )
            st.dataframe(dist_tags, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma tag cadastrada nas anotações.")


def estatisticas_buscas():
    """Estatísticas das buscas recentes (simples e avançada)."""
    hist = st.session_state.get("historico_buscas", [])
    if not hist:
        st.info("Nenhuma busca registrada nesta sessão.")
        return

    df = pd.DataFrame(hist)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de buscas", len(df))
    with col2:
        st.metric("Tipos de busca", df["tipo"].nunique())
    with col3:
        st.metric(
            "Média de resultados por busca",
            f"{df['resultados'].mean():.1f}",
        )

    st.markdown("#### 🔍 Buscas por tipo")
    dist_tipo = (
        df.groupby("tipo")["termo"]
        .count()
        .reset_index(name="qtde_buscas")
        .sort_values("qtde_buscas", ascending=False)
    )
    st.dataframe(dist_tipo, use_container_width=True, hide_index=True)
    st.bar_chart(
        dist_tipo.set_index("tipo")["qtde_buscas"],
    )

    st.markdown("#### 🏷️ Termos mais buscados")
    dist_termo = (
        df.groupby("termo")["resultados"]
        .count()
        .reset_index(name="qtde_buscas")
        .sort_values("qtde_buscas", ascending=False)
        .head(20)
    )
    st.dataframe(dist_termo, use_container_width=True, hide_index=True)


tab_biblia, tab_anot, tab_buscas = st.tabs(
    ["📖 Bíblia", "📝 Anotações", "🔍 Buscas"]
)

with tab_biblia:
    estatisticas_biblia()

with tab_anot:
    estatisticas_anotacoes()

with tab_buscas:
    estatisticas_buscas()

st.markdown("---")
st.markdown("### ⚡ Atalhos")

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📖 Leitura", use_container_width=True):
        st.switch_page("pages/1_📖_Leitura.py")
with c2:
    if st.button("🔍 Busca Simples", use_container_width=True):
        st.switch_page("pages/2_🔍_Busca_Simples.py")
with c3:
    if st.button("🔍+ Busca Avançada", use_container_width=True):
        st.switch_page("pages/3_🔍+_Busca_Avançada.py")
with c4:
    if st.button("📝 Anotações", use_container_width=True):
        st.switch_page("pages/5_📝_Anotações.py")

conexao.close()
