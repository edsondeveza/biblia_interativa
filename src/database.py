"""
Módulo de Banco de Dados
Centraliza todas as operações com SQLite
"""

import sqlite3
import pandas as pd
import re


def conectar_banco(caminho):
    """Conecta ao banco de dados SQLite"""
    return sqlite3.connect(caminho)


def carregar_testamentos(conexao):
    """Carrega lista de testamentos"""
    return pd.read_sql_query("SELECT id, name FROM testament", conexao)


def carregar_livros_testamento(conexao, testamento_id):
    """Carrega livros de um testamento específico"""
    return pd.read_sql_query(
        f"SELECT id, name FROM book WHERE testament_reference_id = {testamento_id} ORDER BY id",
        conexao
    )


def carregar_todos_livros(conexao):
    """Carrega todos os livros"""
    return pd.read_sql_query("SELECT id, name FROM book ORDER BY id", conexao)


def carregar_capitulos(conexao, livro_id):
    """Carrega capítulos de um livro específico"""
    return pd.read_sql_query(
        f"SELECT DISTINCT chapter FROM verse WHERE book_id = {livro_id} ORDER BY chapter",
        conexao
    )


def carregar_versiculos(conexao, livro_id, capitulo):
    """Carrega versículos de um capítulo específico"""
    # Validações básicas
    if livro_id is None or capitulo is None:
        raise ValueError("livro_id e capitulo não podem ser nulos.")

    # Converte para int (aceita numpy.int64, strings numéricas etc.)
    try:
        livro_id_int = int(livro_id)
        capitulo_int = int(capitulo)
    except (TypeError, ValueError):
        raise ValueError("livro_id e capitulo devem ser valores inteiros.")

    query = f"""
        SELECT verse AS Versículo, text AS Texto 
        FROM verse 
        WHERE book_id = {livro_id_int} AND chapter = {capitulo_int}
        ORDER BY verse
    """

    return pd.read_sql_query(query, conexao)


def buscar_versiculos(conexao, termo, testamento_id=None):
    """
    Busca simples por termo.

    - Usa LIKE no SQLite para reduzir o universo de versículos
    - Em seguida, faz filtro por palavra inteira em Python
      (ex.: "amor" não casa com "amorreu")
    """
    termo = (termo or "").strip()
    if not termo:
        # Evita query vazia e devolve DataFrame vazio
        return pd.DataFrame(columns=["Livro", "Capítulo", "Versículo", "Texto"])

    base_query = """
        SELECT book.name AS Livro, chapter AS Capítulo, verse AS Versículo, text AS Texto
        FROM verse
        JOIN book ON verse.book_id = book.id
    """

    filtros = []
    params: list[object] = []

    # Primeiro filtro: LIKE para reduzir o conjunto
    filtros.append("text LIKE ?")
    params.append(f"%{termo}%")

    # Filtro por testamento, se houver
    if testamento_id:
        filtros.append("book.testament_reference_id = ?")
        params.append(testamento_id)

    if filtros:
        base_query += " WHERE " + " AND ".join(filtros)

    df = pd.read_sql_query(base_query, conexao,
                           params=params).reset_index(drop=True) # type: ignore

    # --- Filtro de palavra inteira em Python ---
    # Se o termo tiver espaço ("amor de Deus"), não aplico borda de palavra,
    # deixo funcionar como "frase" normal.
    if " " not in termo:
        padrao = re.compile(
            rf"\b{re.escape(termo.lower())}\b", flags=re.IGNORECASE)
        mascara = df["Texto"].astype(str).str.lower().apply(
            lambda t: bool(padrao.search(t))
        )
        df = df[mascara].reset_index(drop=True)

    return df


def buscar_versiculos_avancada(
    conexao,
    termos,
    operador="E",
    testamento_id=None,
    livro_id=None,
    busca_exata=False
):
    """
    Busca avançada com múltiplas palavras e operadores lógicos.

    - Usa LIKE no SQLite para reduzir o conjunto inicial
    - Depois filtra em Python garantindo:
        * Palavra inteira para buscas simples
        * AND / OR corretos
        * Busca exata funciona como frase
    """

    # Normaliza os termos
    if isinstance(termos, str):
        termos = [termos.strip()]
    else:
        termos = [t.strip() for t in termos if t.strip()]

    if not termos:
        return pd.DataFrame(columns=["Livro", "Capítulo", "Versículo", "Texto"])

    base_query = """
        SELECT book.name AS Livro, chapter AS Capítulo, verse AS Versículo, text AS Texto
        FROM verse
        JOIN book ON verse.book_id = book.id
    """

    filtros = []
    params = []

    # --------------------------------------------------
    # SQL: Redução inicial do conjunto com LIKE
    # --------------------------------------------------
    if busca_exata:
        frase = " ".join(termos)
        filtros.append("text LIKE ?")
        params.append(f"%{frase}%")
    else:
        # Cada termo vira um LIKE
        condicoes = []
        for termo in termos:
            condicoes.append("text LIKE ?")
            params.append(f"%{termo}%")

        operador_sql = " AND " if operador.upper() == "E" else " OR "
        filtros.append("(" + operador_sql.join(condicoes) + ")")

    # Filtro por testamento
    if testamento_id:
        filtros.append("book.testament_reference_id = ?")
        params.append(testamento_id)

    # Filtro por livro
    if livro_id:
        filtros.append("book.id = ?")
        params.append(livro_id)

    if filtros:
        base_query += " WHERE " + " AND ".join(filtros)

    df = pd.read_sql_query(base_query, conexao,
                           params=params).reset_index(drop=True)

    # --------------------------------------------------
    # Python: Filtro final preciso (palavra inteira)
    # --------------------------------------------------

    # Caso busca exata → já está filtrado no SQL
    if busca_exata:
        return df

    # Monta filtros AND/OR para palavra inteira
    def combina_AND(texto: str):
        texto = texto.lower()
        return all(re.search(rf"\b{re.escape(t.lower())}\b", texto) for t in termos)

    def combina_OR(texto: str):
        texto = texto.lower()
        return any(re.search(rf"\b{re.escape(t.lower())}\b", texto) for t in termos)

    if operador.upper() == "E":
        mask = df["Texto"].astype(str).apply(combina_AND)
    else:
        mask = df["Texto"].astype(str).apply(combina_OR)

    return df[mask].reset_index(drop=True)


def comparar_versoes(conexoes_dict, livro_id, capitulo, versiculo=None):
    """
    Compara o mesmo versículo/capítulo em diferentes versões

    Args:
        conexoes_dict: Dict {"ACF": conexao1, "NVI": conexao2}
        livro_id: ID do livro
        capitulo: Número do capítulo
        versiculo: Número do versículo (opcional)

    Returns:
        DataFrame com colunas: Versículo, Versão1, Versão2, ...
    """
    resultado = {}

    for versao, conexao in conexoes_dict.items():
        if versiculo:
            query = f"""
                SELECT verse, text 
                FROM verse 
                WHERE book_id = {livro_id} AND chapter = {capitulo} AND verse = {versiculo}
            """
        else:
            query = f"""
                SELECT verse, text 
                FROM verse 
                WHERE book_id = {livro_id} AND chapter = {capitulo}
                ORDER BY verse
            """

        df = pd.read_sql_query(query, conexao)
        resultado[versao] = df.set_index('verse')['text']

    # Combinar em um único DataFrame
    df_comparacao = pd.DataFrame(resultado)
    df_comparacao.index.name = 'Versículo'

    return df_comparacao.reset_index()


def obter_info_livro(conexao, livro_id):
    """Obtém informações sobre um livro"""
    query = f"""
        SELECT 
            book.name as nome,
            testament.name as testamento,
            COUNT(DISTINCT verse.chapter) as total_capitulos,
            COUNT(verse.id) as total_versiculos
        FROM book
        JOIN testament ON book.testament_reference_id = testament.id
        LEFT JOIN verse ON verse.book_id = book.id
        WHERE book.id = {livro_id}
        GROUP BY book.id
    """
    return pd.read_sql_query(query, conexao).iloc[0].to_dict()
