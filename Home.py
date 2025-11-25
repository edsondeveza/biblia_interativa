"""
Bíblia Interativa v2.0 - Página Principal

Página inicial da aplicação com:
- Seleção da versão da Bíblia (arquivos .sqlite em ./data)
- Exibição de métricas rápidas (livros, capítulos, versículos)
- Navegação para as páginas principais (Leitura, Busca, Anotações, Estatísticas)

Compatível com: Python 3.12.x
Autor: Edson Deveza
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st


# ============================================================
# Configurações gerais
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Mapeamento opcional: código da versão → nome amigável
BIBLE_VERSION_NAMES: Dict[str, str] = {
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


# ============================================================
# Funções auxiliares
# ============================================================


def listar_bancos_disponiveis(data_dir: Path) -> List[Path]:
    """Retorna a lista de arquivos .sqlite disponíveis na pasta data."""
    if not data_dir.exists():
        return []
    return sorted(data_dir.glob("*.sqlite"))


def nome_amigavel_versao(stem: str) -> str:
    """
    Converte o nome do arquivo (stem) em um nome mais amigável.

    Ex.: "ACF" -> "ACF - Almeida Corrigida e Fiel"
    """
    base = stem.upper()
    descricao = BIBLE_VERSION_NAMES.get(base)
    if descricao:
        return f"{base} – {descricao}"
    return base


def carregar_metricas_biblia(caminho_banco: Path) -> Tuple[int, int, int]:
    """
    Calcula métricas básicas da Bíblia:

    - quantidade de livros
    - quantidade de capítulos
    - quantidade de versículos

    Pressupõe uma tabela `verse` com colunas:
    - book_id
    - chapter
    - verse (ou equivalente)

    Se algo der errado, retorna (0, 0, 0).
    """
    try:
        conn = sqlite3.connect(caminho_banco)
        cur = conn.cursor()

        # n_livros
        cur.execute("SELECT COUNT(DISTINCT book_id) FROM verse;")
        n_livros = cur.fetchone()[0] or 0

        # n_capitulos (combinação livro + capítulo)
        cur.execute(
            """
            SELECT COUNT(DISTINCT book_id || '-' || chapter)
            FROM verse;
            """
        )
        n_capitulos = cur.fetchone()[0] or 0

        # n_versiculos
        cur.execute("SELECT COUNT(*) FROM verse;")
        n_versiculos = cur.fetchone()[0] or 0

        conn.close()
        return int(n_livros), int(n_capitulos), int(n_versiculos)
    except Exception:
        # Se quiser, aqui você pode integrar com seu sistema de logger
        # (ex.: log_erro("carregar_metricas_biblia", e, ...))
        return 0, 0, 0


def inicializar_estado() -> None:
    """Garante chaves básicas no session_state."""
    if "caminho_banco" not in st.session_state:
        st.session_state.caminho_banco = None
    if "versao_biblia" not in st.session_state:
        st.session_state.versao_biblia = None


# ============================================================
# Layout da página
# ============================================================


def mostrar_header() -> None:
    """Cabeçalho principal da aplicação."""
    st.set_page_config(
        page_title="Bíblia Interativa",
        page_icon="📖",
        layout="wide",
    )

    st.title("📖 Bíblia Interativa")
    st.caption("Estudo bíblico com múltiplas versões, buscas avançadas e anotações.")


def selecionar_versao(bancos: List[Path]) -> Path | None:
    """
    Exibe o seletor de versões disponíveis.

    Atualiza:
    - st.session_state.caminho_banco
    - st.session_state.versao_biblia
    """
    if not bancos:
        st.error("❌ Nenhuma versão encontrada na pasta `data/`.")
        st.info(
            "Coloque os arquivos `.sqlite` na pasta `data/` "
            "(ex.: `ACF.sqlite`, `ARA.sqlite`, etc.)."
        )
        return None

    # Mapeia nome exibido → Path
    opcoes = {nome_amigavel_versao(b.stem): b for b in bancos}

    # Define valor padrão (se já tiver no estado, tenta reaproveitar)
    default_label = None
    if st.session_state.caminho_banco:
        atual = Path(st.session_state.caminho_banco)
        for label, path in opcoes.items():
            if path == atual:
                default_label = label
                break

    st.subheader("📚 Selecione a versão da Bíblia")
    label_escolhida = st.selectbox(
        "Versão disponível (arquivos .sqlite detectados em `./data`):",
        options=list(opcoes.keys()),
        index=(
            list(opcoes.keys()).index(default_label)
            if default_label in opcoes
            else 0
        ),
    )

    caminho_escolhido = opcoes[label_escolhida]

    # Atualiza session_state
    st.session_state.caminho_banco = str(caminho_escolhido)
    st.session_state.versao_biblia = Path(caminho_escolhido).stem.upper()

    st.success(f"✅ Usando: **{label_escolhida}**")
    return caminho_escolhido


def mostrar_metricas(caminho_banco: Path | None) -> None:
    """Mostra métricas rápidas da Bíblia selecionada."""
    st.subheader("📊 Visão geral da Bíblia")

    if caminho_banco is None:
        st.info("Selecione uma versão para ver as estatísticas.")
        return

    n_livros, n_capitulos, n_versiculos = carregar_metricas_biblia(caminho_banco)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Livros", f"{n_livros:,}".replace(",", "."))
    with col2:
        st.metric("Capítulos", f"{n_capitulos:,}".replace(",", "."))
    with col3:
        st.metric("Versículos", f"{n_versiculos:,}".replace(",", "."))


def mostrar_navegacao() -> None:
    """Bloco com atalhos para as páginas principais."""
    st.subheader("🚀 Acesse as funcionalidades")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Leitura")
        st.write("Leia capítulos, altere versão e acompanhe a leitura de forma contínua.")
        st.page_link(
            "pages/1_📖_Leitura.py",
            label="Ir para Leitura",
        )

    with col2:
        st.markdown("### Buscas e Comparação")
        st.write(
            "- Busca simples por palavra ou expressão\n"
            "- Busca avançada com filtros\n"
            "- Comparação de versões lado a lado"
        )
        st.page_link(
            "pages/2_🔍_Busca_Simples.py",
            label="Busca Simples",
        )
        st.page_link(
            "pages/3_🔍+_Busca_Avançada.py",
            label="Busca Avançada",
        )
        st.page_link(
            "pages/4_⚖️_Comparação.py",
            label="Comparação de Versões",
        )

    with col3:
        st.markdown("### Anotações & Estatísticas")
        st.write(
            "- Anotações por versículo\n"
            "- Histórico de estudos\n"
            "- Estatísticas de uso"
        )
        st.page_link(
            "pages/5_📝_Anotações.py",
            label="Anotações",
        )
        st.page_link(
            "pages/6_📊_Estatísticas.py",
            label="Estatísticas",
        )


def mostrar_rodape() -> None:
    """Rodapé com informações gerais."""
    st.markdown("---")
    st.caption(
        "Bíblia Interativa v2.0 · Desenvolvido em Python 3.12 + Streamlit · "
        "Projeto pessoal de estudo bíblico e tecnologia."
    )


# ============================================================
# Função principal (entrypoint)
# ============================================================


def main() -> None:
    inicializar_estado()
    mostrar_header()

    bancos = listar_bancos_disponiveis(DATA_DIR)
    caminho_banco = selecionar_versao(bancos)

    mostrar_metricas(caminho_banco)
    mostrar_navegacao()
    mostrar_rodape()


if __name__ == "__main__":
    main()
