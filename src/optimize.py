"""
Módulo de Otimização do Banco de Dados.

Este módulo contém funções para criar índices e otimizar
a performance das consultas SQL nos bancos de dados SQLite.

Autor: Edson Deveza
Data: 2024
Versão: 2.1
"""

import sqlite3
import os
from typing import Dict, List


# ============================================================
# 🔧 1. Criar índices otimizados
# ============================================================
def criar_indices(caminho_banco: str) -> bool:
    """
    Cria índices otimizados no banco de dados SQLite.

    Os índices melhoram significativamente a performance de:
    - Buscas por texto (em alguns casos)
    - Navegação por livro/capítulo
    - Filtros por testamento

    Args:
        caminho_banco: Caminho completo para o arquivo .sqlite

    Returns:
        bool: True se índices foram criados com sucesso, False caso contrário
    """
    try:
        conexao = sqlite3.connect(caminho_banco)
        cursor = conexao.cursor()

        indices_sql: List[str] = [
            """
            CREATE INDEX IF NOT EXISTS idx_verse_text 
            ON verse(text)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_verse_book_chapter 
            ON verse(book_id, chapter)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_book_testament 
            ON book(testament_reference_id)
            """
        ]

        for sql in indices_sql:
            try:
                cursor.execute(sql)
            except sqlite3.Error as e:
                print(f"⚠️ Erro ao criar índice em {caminho_banco}: {e}")

        # Melhora consultas internas do SQLite
        try:
            cursor.execute("PRAGMA optimize;")
        except:
            pass

        conexao.commit()
        return True

    except sqlite3.Error as e:
        print(f"❌ Erro ao otimizar banco {caminho_banco}: {e}")
        return False

    finally:
        try:
            conexao.close()
        except:
            pass


# ============================================================
# 🔧 2. Otimizar TODOS bancos da pasta /data
# ============================================================
def otimizar_todos_bancos(pasta_data: str) -> Dict[str, str]:
    """
    Otimiza todos os bancos de dados SQLite em uma pasta.

    Args:
        pasta_data: Caminho para a pasta contendo os arquivos .sqlite

    Returns:
        dict: {"ACF.sqlite": "✅ Otimizado", "NVI.sqlite": "❌ Erro"}
    """
    if not os.path.isdir(pasta_data):
        return {"erro": f"❌ Pasta não encontrada: {pasta_data}"}

    arquivos_sqlite = [
        f for f in os.listdir(pasta_data)
        if f.endswith(".sqlite")
    ]

    if not arquivos_sqlite:
        return {"aviso": "⚠️ Nenhum arquivo .sqlite encontrado"}

    resultados = {}

    for arquivo in arquivos_sqlite:
        caminho = os.path.join(pasta_data, arquivo)
        sucesso = criar_indices(caminho)
        resultados[arquivo] = "✅ Otimizado" if sucesso else "❌ Erro"

    return resultados


# ============================================================
# 🔧 3. Verificar índices existentes
# ============================================================
def verificar_indices_existentes(caminho_banco: str) -> Dict[str, bool]:
    """
    Verifica quais índices já existem no banco de dados.

    Args:
        caminho_banco: Caminho completo para o arquivo .sqlite

    Returns:
        dict: {"idx_verse_text": True/False, ...}
    """
    try:
        conexao = sqlite3.connect(caminho_banco)
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='index' 
            AND sql IS NOT NULL
        """)

        existentes = {row[0] for row in cursor.fetchall()}

        indices_esperados = [
            "idx_verse_text",
            "idx_verse_book_chapter",
            "idx_book_testament",
        ]

        return {
            indice: indice in existentes
            for indice in indices_esperados
        }

    except sqlite3.Error as e:
        print(f"Erro ao verificar índices: {e}")
        return {}

    finally:
        try:
            conexao.close()
        except:
            pass
