from __future__ import annotations

from pathlib import Path
import streamlit as st

# Pasta onde estão as Bíblias .sqlite
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def listar_bancos_disponiveis(data_dir: Path) -> dict[str, Path]:
    """Lista todos os arquivos .sqlite da pasta data."""
    if not data_dir.exists():
        return {}
    arquivos = sorted(data_dir.glob("*.sqlite"))
    return {a.stem.upper(): a for a in arquivos}


def nome_amigavel_versao(stem: str) -> str:
    """Converte código da bíblia em nome exibível."""
    MAP = {
        "ACF": "Almeida Corrigida e Fiel",
        "ARA": "Almeida Revista e Atualizada",
        "ARC": "Almeida Revista e Corrigida",
        "AS21": "Almeida Século 21",
        "JFAA": "Almeida Atualizada (JFAA)",
        "KJA": "King James Atualizada",
        "KJF": "King James Fiel",
        "NAA": "Nova Almeida Atualizada",
        "NBV": "Nova Bíblia Viva",
        "NTLH": "Nova Tradução na Linguagem de Hoje",
        "NVI": "Nova Versão Internacional",
        "NVT": "Nova Versão Transformadora",
        "TB": "Tradução Brasileira",
    }
    return MAP.get(stem.upper(), stem)


def garantir_versao_selecionada() -> Path:
    """
    Exibe SEMPRE um seletor de versão da Bíblia no topo da página
    e garante que st.session_state.caminho_banco esteja definido.

    - Se já existe uma versão selecionada, ela vem marcada como padrão.
    - Se o usuário escolher outra versão, o estado é atualizado e a página recarrega.
    - Retorna o Path do arquivo .sqlite correspondente à versão atual.
    """
    bancos = listar_bancos_disponiveis(DATA_DIR)

    if not bancos:
        st.error("❌ Nenhum arquivo .sqlite encontrado na pasta `data/`.")
        st.stop()

    # Versão atualmente selecionada (se houver)
    caminho_atual = st.session_state.get("caminho_banco")
    stem_atual: str | None = None
    if caminho_atual:
        try:
            stem_atual = Path(caminho_atual).stem.upper()
        except Exception:
            stem_atual = None

    # Monta opções legíveis
    labels: list[str] = []
    stem_por_label: dict[str, str] = {}
    for stem, path in bancos.items():
        label = f"{stem} – {nome_amigavel_versao(stem)}"
        labels.append(label)
        stem_por_label[label] = stem

    # Determina índice padrão do selectbox
    if stem_atual and stem_atual in bancos:
        label_atual = next(
            (lbl for lbl, st_code in stem_por_label.items() if st_code == stem_atual),
            labels[0],
        )
        index_default = labels.index(label_atual)
    else:
        index_default = 0

    st.markdown("#### 📚 Versão da Bíblia")
    escolha_label = st.selectbox(
        "Selecione a versão (válido para todas as páginas):",
        labels,
        index=index_default,
        key="versao_global_select",
    )

    stem_escolhido = stem_por_label[escolha_label]
    caminho_escolhido = bancos[stem_escolhido]

    # Se ainda não havia versão, ou se o usuário trocou, atualiza e recarrega
    if (not caminho_atual) or (stem_atual != stem_escolhido):
        st.session_state["caminho_banco"] = str(caminho_escolhido)
        st.session_state["versao_biblia"] = stem_escolhido
        # Não faz loop infinito, porque na próxima execução stem_atual == stem_escolhido
        st.rerun()

    # Neste ponto, já temos estado consistente
    return caminho_escolhido
