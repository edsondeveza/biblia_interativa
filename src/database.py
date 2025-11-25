"""
Módulo de Banco de Dados.

Centraliza todas as operações com SQLite para acesso aos dados bíblicos.
Implementa cache para otimizar performance de consultas frequentes.

Autor: Edson Deveza
Data: 2025
Versão: 2.1
Compatível: Python 3.12
"""

import sqlite3
import re
from time import perf_counter
from typing import Optional, Dict

import pandas as pd
import streamlit as st

from .logger import log_busca, log_leitura, log_erro


# ============================================================
# Conexão com o banco
# ============================================================
def conectar_banco(caminho: str) -> sqlite3.Connection:
    """
    Conecta ao banco de dados SQLite.

    Args:
        caminho: Caminho completo para o arquivo .sqlite

    Returns:
        sqlite3.Connection: Conexão ativa com o banco

    Raises:
        sqlite3.Error: Se não conseguir conectar ao banco
    """
    try:
        conexao = sqlite3.connect(caminho)
        # Otimização básica do SQLite
        conexao.execute("PRAGMA foreign_keys = ON;")
        conexao.execute("PRAGMA journal_mode = WAL;")
        return conexao
    except sqlite3.Error as e:
        log_erro("conectar_banco", e, detalhes=f"caminho={caminho}")
        raise


# ============================================================
# Consultas básicas (com cache)
# ============================================================
@st.cache_data(ttl=3600)
def carregar_testamentos(_conexao: sqlite3.Connection) -> pd.DataFrame:
    """
    Carrega lista de testamentos do banco (com cache de 1 hora).

    Args:
        _conexao: Conexão com o banco (prefixo _ ignora no cache)

    Returns:
        pd.DataFrame: DataFrame com colunas 'id' e 'name'
    """
    query = "SELECT id, name FROM testament"
    try:
        return pd.read_sql_query(query, _conexao)
    except Exception as e:
        log_erro("carregar_testamentos", e)
        raise


@st.cache_data(ttl=3600)
def carregar_livros_testamento(
    _conexao: sqlite3.Connection,
    testamento_id: int,
) -> pd.DataFrame:
    """
    Carrega livros de um testamento específico (com cache).

    Args:
        _conexao: Conexão com o banco
        testamento_id: ID do testamento (1=VT, 2=NT)

    Returns:
        pd.DataFrame: DataFrame com colunas 'id' e 'name'
    """
    query = """
        SELECT id, name
        FROM book
        WHERE testament_reference_id = ?
        ORDER BY id
    """
    try:
        return pd.read_sql_query(query, _conexao, params=(testamento_id,))
    except Exception as e:
        log_erro(
            "carregar_livros_testamento",
            e,
            detalhes=f"testamento_id={testamento_id}",
        )
        raise


@st.cache_data(ttl=3600)
def carregar_todos_livros(_conexao: sqlite3.Connection) -> pd.DataFrame:
    """
    Carrega todos os livros da Bíblia (com cache).

    Args:
        _conexao: Conexão com o banco

    Returns:
        pd.DataFrame: DataFrame com todos os livros ordenados
    """
    query = "SELECT id, name FROM book ORDER BY id"
    try:
        return pd.read_sql_query(query, _conexao)
    except Exception as e:
        log_erro("carregar_todos_livros", e)
        raise


@st.cache_data(ttl=3600)
def carregar_capitulos(
    _conexao: sqlite3.Connection,
    livro_id: int,
) -> pd.DataFrame:
    """
    Carrega capítulos de um livro específico (com cache).

    Args:
        _conexao: Conexão com o banco
        livro_id: ID do livro

    Returns:
        pd.DataFrame: DataFrame com números dos capítulos
    """
    query = """
        SELECT DISTINCT chapter
        FROM verse
        WHERE book_id = ?
        ORDER BY chapter
    """
    try:
        return pd.read_sql_query(query, _conexao, params=(livro_id,))
    except Exception as e:
        log_erro("carregar_capitulos", e, detalhes=f"livro_id={livro_id}")
        raise


# ============================================================
# Leitura de versículos
# ============================================================
def carregar_versiculos(
    conexao: sqlite3.Connection,
    livro_id: int,
    capitulo: int,
) -> pd.DataFrame:
    """
    Carrega versículos de um capítulo específico.

    Note:
        Esta função NÃO usa cache pois o usuário pode querer
        ver diferentes capítulos rapidamente.

    Args:
        conexao: Conexão com o banco
        livro_id: ID do livro
        capitulo: Número do capítulo

    Returns:
        pd.DataFrame: DataFrame com colunas 'Versículo' e 'Texto'

    Raises:
        ValueError: Se livro_id ou capitulo forem inválidos
    """
    if livro_id is None or capitulo is None:
        raise ValueError("livro_id e capitulo não podem ser nulos.")

    try:
        livro_id_int = int(livro_id)
        capitulo_int = int(capitulo)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"livro_id e capitulo devem ser inteiros. Erro: {e}"
        )

    query = """
        SELECT verse AS Versículo, text AS Texto
        FROM verse
        WHERE book_id = ? AND chapter = ?
        ORDER BY verse
    """

    try:
        df = pd.read_sql_query(
            query,
            conexao,
            params=(livro_id_int, capitulo_int),
        )
        # Logging de leitura (nome do livro é tratado na camada de UI)
        log_leitura(f"ID_{livro_id_int}", capitulo_int, "DESCONHECIDA")
        return df
    except Exception as e:
        log_erro(
            "carregar_versiculos",
            e,
            detalhes=f"livro_id={livro_id_int}, capitulo={capitulo_int}",
        )
        raise


# ============================================================
# Busca simples
# ============================================================
def buscar_versiculos(
    conexao: sqlite3.Connection,
    termo: str,
    testamento_id: Optional[int] = None,
) -> pd.DataFrame:
    """
    Busca simples por termo com filtro de palavra inteira.

    Strategy:
        1. SQL LIKE reduz o conjunto inicial (rápido)
        2. Regex em Python garante palavra inteira (preciso)

    Note:
        Se o termo contém espaço, busca como frase sem word boundary.
        Exemplo: "amor de Deus" busca a frase completa.

    Args:
        conexao: Conexão com o banco
        termo: Termo para buscar
        testamento_id: ID do testamento (opcional, None = ambos)

    Returns:
        pd.DataFrame: DataFrame com colunas:
                     ['Livro', 'Capítulo', 'Versículo', 'Texto']
    """
    inicio = perf_counter()

    termo = (termo or "").strip()
    if not termo:
        return pd.DataFrame(
            columns=["Livro", "Capítulo", "Versículo", "Texto"]
        )

    base_query = """
        SELECT
            book.name AS Livro,
            verse.chapter AS Capítulo,
            verse.verse AS Versículo,
            verse.text AS Texto
        FROM verse
        JOIN book ON verse.book_id = book.id
    """

    filtros = ["verse.text LIKE ?"]
    params = [f"%{termo}%"]

    if testamento_id:
        filtros.append("book.testament_reference_id = ?")
        params.append(testamento_id)

    if filtros:
        base_query += " WHERE " + " AND ".join(filtros)

    try:
        df = pd.read_sql_query(
            base_query,
            conexao,
            params=params,
        ).reset_index(drop=True)
    except Exception as e:
        log_erro("buscar_versiculos/SQL", e, detalhes=f"termo={termo}")
        raise

    # Se o termo tem espaço, trata como frase (sem word boundary)
    if " " in termo:
        termo_lower = termo.lower()
        mascara = df["Texto"].astype(str).str.lower().str.contains(
            termo_lower,
            case=False,
            regex=False,
        )
        resultados = df[mascara].reset_index(drop=True)
    else:
        # Caso contrário, aplica regex com word boundary
        padrao = re.compile(
            rf"\b{re.escape(termo.lower())}\b",
            flags=re.IGNORECASE,
        )
        mascara = df["Texto"].astype(str).str.lower().apply(
            lambda texto: bool(padrao.search(texto))
        )
        resultados = df[mascara].reset_index(drop=True)

    fim = perf_counter()
    tempo_ms = int((fim - inicio) * 1000)
    log_busca(termo, len(resultados), tempo_ms, tipo="simples")

    return resultados


# ============================================================
# Busca avançada
# ============================================================
def buscar_versiculos_avancada(
    conexao: sqlite3.Connection,
    termos,
    operador: str = "E",
    testamento_id: Optional[int] = None,
    livro_id: Optional[int] = None,
    busca_exata: bool = False,
) -> pd.DataFrame:
    """
    Busca avançada com múltiplas palavras e operadores lógicos.

    Strategy:
        1. SQL LIKE reduz conjunto inicial
        2. Python aplica AND/OR com word boundary
        3. Busca exata funciona como frase completa

    Args:
        conexao: Conexão com o banco
        termos: String ou lista de termos para buscar
        operador: "E" (AND) ou "OU" (OR)
        testamento_id: Filtrar por testamento (opcional)
        livro_id: Filtrar por livro (opcional)
        busca_exata: Se True, busca frase completa

    Returns:
        pd.DataFrame: DataFrame com resultados da busca
    """
    inicio = perf_counter()

    # Normalizar termos
    if isinstance(termos, str):
        termos = [termos.strip()]
    else:
        termos = [t.strip() for t in termos if t and t.strip()]

    if not termos:
        return pd.DataFrame(
            columns=["Livro", "Capítulo", "Versículo", "Texto"]
        )

    base_query = """
        SELECT 
            book.name AS Livro, 
            verse.chapter AS Capítulo, 
            verse.verse AS Versículo, 
            verse.text AS Texto
        FROM verse
        JOIN book ON verse.book_id = book.id
    """

    filtros = []
    params: list = []

    # Redução inicial com LIKE
    if busca_exata:
        frase = " ".join(termos)
        filtros.append("verse.text LIKE ?")
        params.append(f"%{frase}%")
    else:
        condicoes = []
        for termo in termos:
            condicoes.append("verse.text LIKE ?")
            params.append(f"%{termo}%")
        operador_sql = " AND " if operador.upper() == "E" else " OR "
        filtros.append("(" + operador_sql.join(condicoes) + ")")

    if testamento_id:
        filtros.append("book.testament_reference_id = ?")
        params.append(testamento_id)

    if livro_id:
        filtros.append("book.id = ?")
        params.append(livro_id)

    if filtros:
        base_query += " WHERE " + " AND ".join(filtros)

    try:
        df = pd.read_sql_query(
            base_query,
            conexao,
            params=params,
        ).reset_index(drop=True)
    except Exception as e:
        log_erro(
            "buscar_versiculos_avancada/SQL",
            e,
            detalhes=f"termos={termos}, operador={operador}",
        )
        raise

    # Busca exata: o filtro do SQL já é suficiente
    if busca_exata:
        resultados = df
    else:
        # Filtros AND/OR com word boundary em Python
        termos_norm = [t.lower() for t in termos]

        def combina_and(texto: str) -> bool:
            texto_lower = texto.lower()
            return all(
                re.search(rf"\b{re.escape(t)}\b", texto_lower)
                for t in termos_norm
            )

        def combina_or(texto: str) -> bool:
            texto_lower = texto.lower()
            return any(
                re.search(rf"\b{re.escape(t)}\b", texto_lower)
                for t in termos_norm
            )

        if operador.upper() == "E":
            mask = df["Texto"].astype(str).apply(combina_and)
        else:
            mask = df["Texto"].astype(str).apply(combina_or)

        resultados = df[mask].reset_index(drop=True)

    fim = perf_counter()
    tempo_ms = int((fim - inicio) * 1000)
    log_busca(" / ".join(termos), len(resultados), tempo_ms, tipo="avancada")

    return resultados


# ============================================================
# Comparação entre versões
# ============================================================
def comparar_versoes(
    conexoes_dict: Dict[str, sqlite3.Connection],
    livro_id: int,
    capitulo: int,
    versiculo: Optional[int] = None,
) -> pd.DataFrame:
    """
    Compara o mesmo versículo/capítulo em diferentes versões.

    Args:
        conexoes_dict: Dict {"ACF": conexao1, "NVI": conexao2, ...}
        livro_id: ID do livro
        capitulo: Número do capítulo
        versiculo: Número do versículo (None = capítulo completo)

    Returns:
        pd.DataFrame: DataFrame com colunas:
                    ['Versículo', 'Versão1', 'Versão2', ...]
    """
    resultado: Dict[str, pd.Series] = {}

    for versao, conexao in conexoes_dict.items():
        if versiculo:
            query = """
                SELECT verse, text 
                FROM verse 
                WHERE book_id = ? 
                  AND chapter = ? 
                  AND verse = ?
            """
            params = (livro_id, capitulo, versiculo)
        else:
            query = """
                SELECT verse, text 
                FROM verse 
                WHERE book_id = ? 
                  AND chapter = ?
                ORDER BY verse
            """
            params = (livro_id, capitulo)

        try:
            df = pd.read_sql_query(query, conexao, params=params)
        except Exception as e:
            log_erro(
                "comparar_versoes",
                e,
                detalhes=f"versao={versao}, livro_id={livro_id}, cap={capitulo}, "
                         f"vers={versiculo}",
            )
            raise

        resultado[versao] = df.set_index("verse")["text"]

    df_comparacao = pd.DataFrame(resultado)
    df_comparacao.index.name = "Versículo"

    return df_comparacao.reset_index()


# ============================================================
# Informações sobre o livro
# ============================================================
def obter_info_livro(
    conexao: sqlite3.Connection,
    livro_id: int,
) -> Dict:
    """
    Obtém informações estatísticas sobre um livro.

    Args:
        conexao: Conexão com o banco
        livro_id: ID do livro

    Returns:
        dict: {
            'nome': str,
            'testamento': str,
            'total_capitulos': int,
            'total_versiculos': int
        }
    """
    query = """
        SELECT 
            book.name as nome,
            testament.name as testamento,
            COUNT(DISTINCT verse.chapter) as total_capitulos,
            COUNT(verse.id) as total_versiculos
        FROM book
        JOIN testament ON book.testament_reference_id = testament.id
        LEFT JOIN verse ON verse.book_id = book.id
        WHERE book.id = ?
        GROUP BY book.id
    """

    try:
        df = pd.read_sql_query(query, conexao, params=(livro_id,))
    except Exception as e:
        log_erro("obter_info_livro", e, detalhes=f"livro_id={livro_id}")
        raise

    if df.empty:
        return {
            "nome": "",
            "testamento": "",
            "total_capitulos": 0,
            "total_versiculos": 0,
        }

    return df.iloc[0].to_dict()
