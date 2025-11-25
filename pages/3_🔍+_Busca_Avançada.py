"""
Página de Busca Avançada.

Busca com múltiplas palavras, operadores lógicos e filtros
por testamento, livro e frase exata.

Autor: Edson Deveza
Data: 2025
Versão: 2.1
"""

from __future__ import annotations
from src.ui_utils import garantir_versao_selecionada
from src.logger import log_erro
from src.error_handler import handle_database_error, show_connection_error
from src.export import exportar_csv, exportar_xlsx, exportar_pdf, exportar_html
from src.database import (
    conectar_banco,
    carregar_testamentos,
    carregar_livros_testamento,
    buscar_versiculos_avancada,
)

import sys
import time
from pathlib import Path
from typing import Optional

import streamlit as st

# Ajuste de path para permitir "from src...."
RAIZ_PROJETO = Path(__file__).parent.parent.absolute()
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


# ============================================================
# Configuração da página
# ============================================================
st.set_page_config(
    page_title="Busca Avançada",
    page_icon="🔍➕",
    layout="wide",
)

st.title("🔍➕ Busca Avançada")


# ============================================================
# Verificações iniciais de sessão
# ============================================================
if "historico_buscas" not in st.session_state:
    st.session_state.historico_buscas = []

# Garante versão selecionada
caminho_banco = garantir_versao_selecionada()

# ============================================================
# Conexão com o banco
# ============================================================
try:
    conexao = conectar_banco(str(caminho_banco))
except Exception as e:
    log_erro("busca_avancada_conexao", e)
    show_connection_error()
    st.stop()

versao_atual = st.session_state.get("versao_biblia") or st.session_state.get(
    "versao_selecionada", "N/D"
)
st.markdown(f"**Versão atual:** {versao_atual}")

st.info(
    "💡 **Use a busca avançada quando precisar combinar palavras, "
    "filtrar por testamento/livro ou buscar uma frase exata.**"
)


# ============================================================
# Carregamento de testamentos e livros
# ============================================================
try:
    df_test = carregar_testamentos(conexao)
except Exception as e:
    log_erro("busca_avancada_testamentos", e)
    handle_database_error(e, "carregamento de testamentos")
    conexao.close()
    st.stop()

if df_test.empty:
    st.error("Nenhum testamento encontrado no banco de dados.")
    conexao.close()
    st.stop()

map_test_id_nome = {int(r["id"]): r["name"] for _, r in df_test.iterrows()}
map_test_nome_id = {v: k for k, v in map_test_id_nome.items()}


# ============================================================
# Formulário da Busca Avançada
# ============================================================
st.markdown("---")
st.subheader("📝 Parâmetros da busca avançada")

with st.form("form_busca_avancada"):
    col_termo, col_frase = st.columns([3, 1])

    with col_termo:
        termos_raw = st.text_input(
            "Palavras ou frase para buscar",
            placeholder="Ex.: graça salvadora; fé; amor de Deus; justificação pela fé...",
        )

    with col_frase:
        busca_exata = st.checkbox(
            "Frase exata?",
            help="Se marcado, a busca será pela frase completa, na ordem digitada.",
            value=False,
        )

    col_op, col_test, col_livro = st.columns([1, 1.2, 2])

    with col_op:
        operador = st.selectbox(
            "Operador",
            options=["E", "OU"],
            index=0,
            help="E = todas as palavras devem aparecer; OU = qualquer uma das palavras.",
            disabled=busca_exata,
        )

    with col_test:
        filtro_testamento = st.selectbox(
            "Testamento",
            options=["Todos"] + list(map_test_nome_id.keys()),
            index=0,
        )

    livros_opcoes = ["Todos"]
    livros_dict: dict[str, int] = {}

    testamento_id: Optional[int]
    if filtro_testamento == "Todos":
        testamento_id = None
    else:
        testamento_id = int(map_test_nome_id[filtro_testamento])
        try:
            df_livros = carregar_livros_testamento(conexao, testamento_id)
            for _, row in df_livros.iterrows():
                nome_livro = row["name"]
                livros_opcoes.append(nome_livro)
                livros_dict[nome_livro] = int(row["id"])
        except Exception as e:
            log_erro("busca_avancada_livros", e)
            handle_database_error(e, "carregamento de livros")
            conexao.close()
            st.stop()

    with col_livro:
        livro_escolhido = st.selectbox(
            "Livro",
            options=livros_opcoes,
            index=0,
        )

    col_botao, col_hint = st.columns([1, 3])
    with col_botao:
        disparar = st.form_submit_button("🔍 Buscar", use_container_width=True)

    with col_hint:
        st.write(
            "- Separe múltiplas palavras por espaço (ex.: `graça fé salvação`).  \n"
            "- Use **Frase exata** para buscar uma expressão completa.  \n"
            "- Combine Testamento + Livro para refinar ainda mais a busca."
        )

livro_id: Optional[int]
if livro_escolhido == "Todos":
    livro_id = None
else:
    livro_id = livros_dict.get(livro_escolhido)


# ============================================================
# Execução da busca avançada
# ============================================================
def executar_busca_avancada():
    termo_limpo = termos_raw.strip()
    if not termo_limpo:
        st.warning("Digite pelo menos uma palavra ou frase para buscar.")
        return

    if busca_exata:
        termos = [termo_limpo]
    else:
        termos = [t for t in termo_limpo.split() if t]

    try:
        inicio = time.time()

        resultados = buscar_versiculos_avancada(
            conexao=conexao,
            termos=termos,
            operador=operador,
            testamento_id=testamento_id,
            livro_id=livro_id,
            busca_exata=busca_exata,
        )

        fim = time.time()
        tempo_ms = int((fim - inicio) * 1000)
    except Exception as e:
        log_erro(
            "busca_avancada_execucao",
            e,
            detalhes=f"termos={termos}, operador={operador}",
        )
        handle_database_error(e, "busca avançada")
        return

    if resultados is None or resultados.empty:
        st.warning(
            f"⚠️ Nenhum versículo encontrado com os termos '{termos_raw}'."
        )
        st.info(
            "💡 **Sugestões:**\n"
            "- Teste outro operador lógico (E/OU)\n"
            "- Reduza a quantidade de palavras\n"
            "- Tente apenas uma palavra-chave principal\n"
            "- Use a opção de busca por frase exata apenas quando necessário"
        )
        return

    st.session_state.historico_buscas.insert(
        0,
        {
            "termo": termos_raw,
            "resultados": len(resultados),
            "tipo": "Busca Avançada",
            "testamento": filtro_testamento,
            "livro": livro_escolhido,
            "tempo_ms": tempo_ms,
        },
    )
    st.session_state.historico_buscas = st.session_state.historico_buscas[:10]

    label_contexto: list[str] = []
    if filtro_testamento != "Todos":
        label_contexto.append(filtro_testamento)
    if livro_escolhido != "Todos":
        label_contexto.append(livro_escolhido)

    contexto_str = " / ".join(label_contexto) if label_contexto else "Toda a Bíblia"

    st.success(
        f"🔎 Encontrados **{len(resultados)}** versículos "
        f"para **'{termos_raw}'** em **{contexto_str}** "
        f"({tempo_ms}ms)."
    )

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Livros encontrados", resultados["Livro"].nunique())
    with col_m2:
        st.metric(
            "Capítulos distintos",
            resultados[["Livro", "Capítulo"]].drop_duplicates().shape[0],
        )
    with col_m3:
        st.metric("Total de versículos", len(resultados))

    st.markdown("---")
    st.subheader("📋 Resultados da busca")

    resultados_ord = resultados.sort_values(
        by=["Livro", "Capítulo", "Versículo"]
    ).reset_index(drop=True)

    st.dataframe(
        resultados_ord[["Livro", "Capítulo", "Versículo", "Texto"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("📥 Exportar resultados")

    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    base_nome = f"busca_avancada_{termos_raw.replace(' ', '_')}"

    with col_e1:
        exportar_csv(resultados_ord, base_nome)
    with col_e2:
        exportar_xlsx(resultados_ord, base_nome)
    with col_e3:
        exportar_pdf(resultados_ord,
                     f"Busca Avançada: {termos_raw}", base_nome)
    with col_e4:
        exportar_html(
            resultados_ord,
            f"Busca Avançada: {termos_raw}",
            base_nome,
        )


if disparar:
    executar_busca_avancada()


# ============================================================
# Histórico de buscas
# ============================================================
st.markdown("---")
st.subheader("🕒 Histórico recente de buscas")

if not st.session_state.historico_buscas:
    st.info("Nenhuma busca realizada nesta sessão.")
else:
    for item in st.session_state.historico_buscas:
        detalhes = f"{item.get('termo', '')} • {item.get('resultados', 0)} resultados"
        if item.get("livro") and item["livro"] != "Todos":
            detalhes += f" • {item['livro']}"
        elif item.get("testamento") and item["testamento"] not in (None, "", "Todos"):
            detalhes += f" • {item['testamento']}"
        if "tempo_ms" in item:
            detalhes += f" • {item['tempo_ms']}ms"

        with st.expander(detalhes):
            st.write(f"Tipo: {item.get('tipo', 'N/D')}")
            if item.get("testamento") and item["testamento"] != "Todos":
                st.write(f"Testamento: {item['testamento']}")
            if item.get("livro") and item["livro"] != "Todos":
                st.write(f"Livro: {item['livro']}")


# ============================================================
# Atalhos
# ============================================================
st.markdown("---")
st.markdown("### ⚡ Atalhos")

c_at1, c_at2 = st.columns(2)
with c_at1:
    if st.button("🔍 Busca Simples", use_container_width=True):
        st.switch_page("pages/2_🔍_Busca_Simples.py")
with c_at2:
    if st.button("📖 Leitura", use_container_width=True):
        st.switch_page("pages/1_📖_Leitura.py")

conexao.close()
