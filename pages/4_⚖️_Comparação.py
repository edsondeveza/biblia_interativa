"""
Página de Comparação de Versões.

Permite comparar até 3 traduções bíblicas lado a lado
para o mesmo capítulo ou versículo.

Autor: Edson Deveza
Versão: 2.0
Compatível: Python 3.12
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st

# Ajuste de path para permitir imports "src.*"
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
from src.error_handler import handle_database_error, show_connection_error
from src.logger import log_erro


# ============================================================
# Configuração da página
# ============================================================
st.set_page_config(
    page_title="Comparação de Versões",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Comparação de Versões")


# ============================================================
# Verificações iniciais
# ============================================================
if not st.session_state.get("caminho_banco"):
    st.warning("⚠️ Por favor, selecione uma versão da Bíblia na página inicial.")
    if st.button("← Voltar para Home"):
        st.switch_page("Home.py")
    st.stop()

versao_atual = st.session_state.get("versao_biblia") or st.session_state.get(
    "versao_selecionada", "N/D"
)
st.markdown(f"**Versão base:** {versao_atual}")

# Pasta data com as outras versões
DATA_DIR = RAIZ_PROJETO / "data"


def listar_bancos_disponiveis() -> Dict[str, Path]:
    """Retorna um dict {stem_upper: caminho} com arquivos .sqlite em ./data."""
    if not DATA_DIR.exists():
        return {}
    arquivos = sorted(DATA_DIR.glob("*.sqlite"))
    return {a.stem.upper(): a for a in arquivos}


bancos = listar_bancos_disponiveis()
if not bancos:
    st.error("❌ Nenhuma versão `.sqlite` encontrada na pasta `data/`.")
    st.stop()

# Garante que a versão atual esteja no dicionário (caso path seja diferente)
stem_atual = Path(st.session_state.caminho_banco).stem.upper()
if stem_atual not in bancos:
    bancos[stem_atual] = Path(st.session_state.caminho_banco)

# ============================================================
# Conexão com a versão base (para navegação)
# ============================================================
try:
    conexao_base = conectar_banco(st.session_state.caminho_banco)
except Exception as e:
    log_erro("comparacao_conexao_base", e)
    show_connection_error()
    st.stop()

# ============================================================
# Seleção da referência bíblica
# ============================================================
st.markdown("---")
st.subheader("📌 Selecione o texto para comparar")

try:
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        df_test = carregar_testamentos(conexao_base)
        if df_test.empty:
            st.error("Nenhum testamento encontrado no banco de dados.")
            conexao_base.close()
            st.stop()

        testamento_nome = st.selectbox(
            "Testamento",
            df_test["name"],
            key="cmp_testamento",
        )
        testamento_id = int(
            df_test.loc[df_test["name"] == testamento_nome, "id"].iloc[0]
        )

    with col_t2:
        df_livros = carregar_livros_testamento(conexao_base, testamento_id)

        if df_livros.empty:
            st.error("Nenhum livro encontrado para o testamento selecionado.")
            conexao_base.close()
            st.stop()

        livro_nome = st.selectbox(
            "Livro",
            df_livros["name"],
            key="cmp_livro",
        )

        # Garantir que o livro selecionado existe no DF
        mask = df_livros["name"] == livro_nome
        if not mask.any():
            st.error(
                "Não foi possível localizar o livro selecionado. "
                "Por favor, selecione novamente o testamento e o livro."
            )
            conexao_base.close()
            st.stop()

        livro_id = int(df_livros.loc[mask, "id"].iloc[0])

    df_caps = carregar_capitulos(conexao_base, livro_id)
    if df_caps.empty:
        st.error("Nenhum capítulo encontrado para o livro selecionado.")
        conexao_base.close()
        st.stop()

    lista_caps = sorted(df_caps["chapter"].tolist())

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        capitulo = st.selectbox(
            "Capítulo",
            lista_caps,
            key="cmp_capitulo",
        )

    with col_c2:
        tipo_comparacao = st.radio(
            "Comparar",
            options=["Capítulo inteiro", "Versículo específico"],
            horizontal=True,
        )

    versiculo_especifico = None
    if tipo_comparacao == "Versículo específico":
        df_versos_base = carregar_versiculos(conexao_base, livro_id, capitulo)
        if df_versos_base.empty:
            st.error("Nenhum versículo encontrado para o capítulo selecionado.")
            conexao_base.close()
            st.stop()

        lista_versos = sorted(df_versos_base["Versículo"].tolist())
        versiculo_especifico = st.selectbox(
            "Versículo",
            lista_versos,
            key="cmp_versiculo",
        )

except Exception as e:
    log_erro("comparacao_navegacao", e)
    handle_database_error(e, "navegação")
    conexao_base.close()
    st.stop()

# ============================================================
# Seleção das versões para comparar
# ============================================================
st.markdown("---")
st.subheader("📚 Versões para comparação")

todas_versoes = sorted(bancos.keys())
default_selecao: List[str] = [stem_atual]
outros = [v for v in todas_versoes if v != stem_atual]
default_selecao += outros[:2]  # até 3 no total

versoes_escolhidas = st.multiselect(
    "Escolha até 3 versões",
    options=todas_versoes,
    default=default_selecao[:3],
    max_selections=3,
)

if not versoes_escolhidas:
    st.info("Selecione pelo menos uma versão para comparar.")
    conexao_base.close()
    st.stop()

if st.button("⚖️ Comparar versões", type="primary"):
    st.session_state["cmp_disparar"] = True

if not st.session_state.get("cmp_disparar"):
    conexao_base.close()
    st.stop()

st.session_state["cmp_disparar"] = False

# ============================================================
# Execução da comparação
# ============================================================
st.markdown("---")
st.subheader("📖 Resultados da comparação")

comparacoes: Dict[str, pd.DataFrame] = {}

for versao in versoes_escolhidas:
    caminho = bancos[versao]
    try:
        conn = conectar_banco(str(caminho))
        df = carregar_versiculos(conn, livro_id, capitulo)

        if df.empty:
            st.warning(f"Nenhum versículo encontrado na versão {versao}.")
            conn.close()
            continue

        if tipo_comparacao == "Versículo específico":
            df = df[df["Versículo"] == versiculo_especifico]

        # Renomeia coluna de texto para o nome da versão
        df = df[["Versículo", "Texto"]].copy()
        df.rename(columns={"Texto": versao}, inplace=True)
        comparacoes[versao] = df

        conn.close()
    except Exception as e:
        log_erro("comparacao_versao", e, detalhes=versao)
        st.error(f"❌ Erro ao carregar dados da versão **{versao}**.")

if not comparacoes:
    st.error("Não foi possível montar a tabela de comparação.")
    conexao_base.close()
    st.stop()

# Merge por número de versículo
dfs = list(comparacoes.values())
df_merged = dfs[0]
for d in dfs[1:]:
    df_merged = df_merged.merge(on="Versículo", right=d, how="outer")

df_merged = df_merged.sort_values("Versículo").reset_index(drop=True)

titulo_ref = f"{livro_nome} {capitulo}"
if versiculo_especifico is not None:
    titulo_ref += f":{versiculo_especifico}"

st.markdown(f"### 📍 {titulo_ref}")

st.dataframe(
    df_merged,
    use_container_width=True,
    hide_index=True,
)

st.caption("Cada coluna representa uma versão da Bíblia para o mesmo texto.")

# Atalhos
st.markdown("---")
st.markdown("### ⚡ Atalhos")

c1, c2 = st.columns(2)
with c1:
    if st.button("📖 Ir para Leitura", use_container_width=True):
        st.switch_page("pages/1_📖_Leitura.py")
with c2:
    if st.button("🔍 Ir para Busca Avançada", use_container_width=True):
        st.switch_page("pages/3_🔍+_Busca_Avançada.py")

conexao_base.close()
