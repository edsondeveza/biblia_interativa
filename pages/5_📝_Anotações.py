"""
Página de Anotações.

Permite criar, listar, editar e excluir anotações
associadas a versículos específicos.

Autor: Edson Deveza
Versão: 2.1
Compatível: Python 3.12
"""

from __future__ import annotations
from src.ui_utils import garantir_versao_selecionada
from src.logger import log_erro
from src.error_handler import show_connection_error

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import streamlit as st

# Ajuste de path para permitir imports "src.*"
RAIZ_PROJETO = Path(__file__).parent.parent.absolute()
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


st.set_page_config(
    page_title="Anotações",
    page_icon="📝",
    layout="wide",
)

st.title("📝 Anotações de Estudo")

# Garante versão selecionada (mesmo que a página não use o banco diretamente)
caminho_banco = garantir_versao_selecionada()

versao_atual = st.session_state.get("versao_biblia") or st.session_state.get(
    "versao_selecionada", "N/D"
)
st.markdown(f"**Versão atual:** {versao_atual}")

if "anotacoes" not in st.session_state:
    st.session_state.anotacoes: Dict[str, Dict[str, Any]] = {}

versiculo_ctx = st.session_state.get("versiculo_anotacao")


def _make_key(livro: str, capitulo: int, versiculo: int) -> str:
    return f"{livro}|{capitulo}|{versiculo}"


col_esq, col_dir = st.columns([2, 3])

with col_esq:
    st.subheader("✏️ Nova anotação / edição")

    if versiculo_ctx:
        livro_default = versiculo_ctx["livro"]
        cap_default = versiculo_ctx["capitulo"]
        ver_default = versiculo_ctx["versiculo"]
        texto_verso = versiculo_ctx["texto"]
    else:
        livro_default = ""
        cap_default = 1
        ver_default = 1
        texto_verso = ""

    livro = st.text_input("Livro", value=livro_default)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        capitulo = st.number_input(
            "Capítulo", min_value=1, value=int(cap_default))
    with col_c2:
        versiculo = st.number_input(
            "Versículo", min_value=1, value=int(ver_default))

    st.markdown("**Texto do versículo (opcional, para referência pessoal):**")
    texto_verso = st.text_area(
        "Texto do versículo",
        value=texto_verso,
        height=80,
        label_visibility="collapsed",
    )

    anotacao = st.text_area(
        "Anotação",
        value="",
        height=150,
        placeholder="Escreva aqui sua reflexão, aplicação prática, observações, etc.",
    )

    tags_raw = st.text_input(
        "Tags (opcional)",
        help="Separe tags por vírgula. Ex.: fé, graça, oração, promessa",
    )

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        salvar = st.button("💾 Salvar anotação",
                           type="primary", use_container_width=True)
    with col_b2:
        limpar = st.button("🧹 Limpar formulário", use_container_width=True)

    if limpar:
        if "versiculo_anotacao" in st.session_state:
            del st.session_state["versiculo_anotacao"]
        st.rerun()

    if salvar:
        try:
            if not livro.strip():
                st.warning("Informe o livro para salvar a anotação.")
            elif not anotacao.strip():
                st.warning("O campo de anotação está vazio.")
            else:
                key = _make_key(livro.strip(), int(capitulo), int(versiculo))
                st.session_state.anotacoes[key] = {
                    "livro": livro.strip(),
                    "capitulo": int(capitulo),
                    "versiculo": int(versiculo),
                    "texto_verso": texto_verso.strip(),
                    "anotacao": anotacao.strip(),
                    "tags": [
                        t.strip()
                        for t in tags_raw.split(",")
                        if t.strip()
                    ],
                    "versao": versao_atual,
                    "criado_em": datetime.now().isoformat(timespec="seconds"),
                }
                if "versiculo_anotacao" in st.session_state:
                    del st.session_state["versiculo_anotacao"]
                st.success("✅ Anotação salva/atualizada com sucesso!")
        except Exception as e:
            log_erro("anotacoes_salvar", e)
            st.error("❌ Erro ao salvar anotação.")

with col_dir:
    st.subheader("📚 Suas anotações")

    if not st.session_state.anotacoes:
        st.info("Nenhuma anotação registrada ainda.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_livro = st.text_input(
                "Filtrar por livro",
                placeholder="Ex.: Salmos, João...",
            )
        with col_f2:
            filtro_tag = st.text_input(
                "Filtrar por tag",
                placeholder="Ex.: fé, promessa...",
            )

        anot_list = list(st.session_state.anotacoes.values())

        if filtro_livro.strip():
            anot_list = [
                a
                for a in anot_list
                if filtro_livro.strip().lower() in a["livro"].lower()
            ]

        if filtro_tag.strip():
            anot_list = [
                a
                for a in anot_list
                if any(
                    filtro_tag.strip().lower() in t.lower()
                    for t in a.get("tags", [])
                )
            ]

        anot_list.sort(key=lambda x: x.get("criado_em", ""), reverse=True)

        for idx, a in enumerate(anot_list):
            header = f"{a['livro']} {a['capitulo']}:{a['versiculo']} • {a.get('versao', '')}"
            with st.expander(header, expanded=False):
                if a.get("texto_verso"):
                    st.markdown(f"> _{a['texto_verso']}_")
                    st.markdown("---")

                st.markdown(a["anotacao"])

                if a.get("tags"):
                    st.markdown(
                        "🏷️ **Tags:** "
                        + ", ".join(f"`{t}`" for t in a["tags"])
                    )

                st.caption(f"📅 Criado em: {a.get('criado_em', 'N/D')}")

                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button(
                        "✏️ Editar",
                        key=f"edit_{idx}",
                        use_container_width=True,
                    ):
                        st.session_state["versiculo_anotacao"] = {
                            "livro": a["livro"],
                            "capitulo": a["capitulo"],
                            "versiculo": a["versiculo"],
                            "texto": a.get("texto_verso", ""),
                        }
                        st.rerun()
                with col_a2:
                    if st.button(
                        "🗑️ Excluir",
                        key=f"del_{idx}",
                        use_container_width=True,
                    ):
                        try:
                            chave = _make_key(
                                a["livro"], a["capitulo"], a["versiculo"]
                            )
                            st.session_state.anotacoes.pop(chave, None)
                            st.success("Anotação excluída.")
                            st.rerun()
                        except Exception as e:
                            log_erro("anotacoes_excluir", e)
                            st.error("❌ Erro ao excluir anotação.")

st.markdown("---")
st.markdown("### ⚡ Atalhos")

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📖 Leitura", use_container_width=True):
        st.switch_page("pages/1_📖_Leitura.py")
with c2:
    if st.button("🔍 Busca Simples", use_container_width=True):
        st.switch_page("pages/2_🔍_Busca_Simples.py")
with c3:
    if st.button("🔍+ Busca Avançada", use_container_width=True):
        st.switch_page("pages/3_🔍+_Busca_Avançada.py")
