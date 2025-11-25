"""
Módulo de Tratamento de Erros.

Centraliza o tratamento de erros da aplicação, proporcionando
mensagens amigáveis ao usuário e logging adequado de exceções.

Autor: Edson Deveza
Data: 2024
Versão: 2.1
"""

import streamlit as st
import traceback
import re
from typing import Tuple


def handle_database_error(error: Exception, context: str = "operação") -> None:
    """
    Exibe erro de banco de dados de forma amigável ao usuário.
    """
    st.error(f"❌ Erro ao realizar {context}")

    with st.expander("🔍 Detalhes Técnicos (para desenvolvedores)"):
        st.code(str(error))
        st.code(traceback.format_exc())

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Tentar Novamente", use_container_width=True):
            st.rerun()

    with col2:
        # OBS: dependendo da versão do Streamlit, pode ser "Home" ao invés de "Home.py"
        if st.button("🏠 Voltar ao Início", use_container_width=True):
            st.switch_page("Home.py")


def handle_export_error(error: Exception, formato: str = "arquivo") -> None:
    """
    Exibe erro de exportação de forma amigável ao usuário.
    """
    st.error(f"❌ Erro ao exportar {formato}")

    st.warning(
        "💡 **Sugestões:**\n"
        "- Tente exportar em outro formato (CSV ou Excel)\n"
        "- Reduza a quantidade de dados (use filtros)\n"
        "- Verifique se há espaço em disco suficiente"
    )

    with st.expander("🔍 Detalhes do Erro"):
        st.code(str(error))
        st.code(traceback.format_exc())


def validate_search_input(termo: str) -> Tuple[bool, str]:
    """
    Valida entrada de busca antes de consultar o banco.
    """
    termo = termo.strip()

    # Comprimento mínimo
    if not termo or len(termo) < 2:
        return False, "⚠️ Digite pelo menos 2 caracteres para buscar."

    # Comprimento máximo
    if len(termo) > 100:
        return False, "⚠️ Termo de busca muito longo (máximo 100 caracteres)."

    # Caracteres potencialmente perigosos de forma direta
    caracteres_perigosos = ["'", '"', ";", "--", "/*", "*/"]

    for char in caracteres_perigosos:
        if char in termo:
            return False, "⚠️ O termo contém caracteres não permitidos."

    # Palavras SQL perigosas (DROP, DELETE) como tokens, não como substring
    termo_upper = termo.upper()
    sql_keywords = {"DROP", "DELETE"}
    tokens = re.findall(r"[A-Z]+", termo_upper)

    if any(token in sql_keywords for token in tokens):
        return False, "⚠️ O termo contém palavras reservadas não permitidas."

    # Caracteres válidos (inclui acentos e alguma pontuação útil em referências bíblicas)
    caracteres_validos_extra = (
        "áéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ"
        ":,.-!?()"
    )

    if not all(c.isalnum() or c.isspace() or c in caracteres_validos_extra for c in termo):
        return False, "⚠️ O termo contém caracteres especiais não permitidos."

    return True, ""


def validate_annotation_input(texto: str, min_length: int = 5) -> Tuple[bool, str]:
    """
    Valida entrada de anotação antes de salvar.
    """
    texto = texto.strip()

    if not texto:
        return False, "⚠️ A anotação não pode estar vazia."

    if len(texto) < min_length:
        return False, f"⚠️ A anotação deve ter pelo menos {min_length} caracteres."

    if len(texto) > 5000:
        return False, "⚠️ A anotação é muito longa (máximo 5000 caracteres)."

    return True, ""


def show_connection_error() -> None:
    """
    Exibe erro de conexão com banco de dados.
    """
    st.error("❌ Não foi possível conectar ao banco de dados")

    st.warning(
        "💡 **Possíveis soluções:**\n"
        "1. Verifique se o arquivo .sqlite existe na pasta `data/`\n"
        "2. Tente selecionar outra versão da Bíblia\n"
        "3. Reinicie a aplicação\n"
        "4. Verifique as permissões do arquivo"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏠 Voltar ao Início", use_container_width=True):
            st.switch_page("Home.py")

    with col2:
        if st.button("🔄 Recarregar Página", use_container_width=True):
            st.rerun()
