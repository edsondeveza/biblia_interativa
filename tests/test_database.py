"""
Testes para o módulo src.database.

Os testes utilizam um banco SQLite em memória para validar
as principais funções de acesso e busca.

Autor: Edson Deveza
Data: 2024
"""

import sqlite3

import pandas as pd
import pytest

from src.database import (
    carregar_testamentos,
    carregar_livros_testamento,
    carregar_todos_livros,
    carregar_capitulos,
    carregar_versiculos,
    buscar_versiculos,
    buscar_versiculos_avancada,
    comparar_versoes,
    obter_info_livro,
)


def criar_banco_teste() -> sqlite3.Connection:
    """
    Cria um banco de dados em memória com dados mínimos
    para os testes.
    """
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE testament (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE book (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            testament_reference_id INTEGER NOT NULL,
            FOREIGN KEY (testament_reference_id) REFERENCES testament(id)
        );

        CREATE TABLE verse (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES book(id)
        );
        """
    )

    # Testamentos
    cur.executemany(
        "INSERT INTO testament (id, name) VALUES (?, ?)",
        [(1, "Velho Testamento"), (2, "Novo Testamento")],
    )

    # Livros
    cur.executemany(
        "INSERT INTO book (id, name, testament_reference_id) VALUES (?, ?, ?)",
        [
            (1, "Gênesis", 1),
            (2, "João", 2),
        ],
    )

    # Versículos
    cur.executemany(
        "INSERT INTO verse (book_id, chapter, verse, text) VALUES (?, ?, ?, ?)",
        [
            (1, 1, 1, "No princípio criou Deus os céus e a terra."),
            (1, 1, 2, "A terra era sem forma e vazia."),
            (2, 3, 16, "Porque Deus amou o mundo de tal maneira."),
            (2, 3, 17, "Porque Deus enviou seu Filho ao mundo."),
        ],
    )

    conn.commit()
    return conn


@pytest.fixture
def conexao():
    conn = criar_banco_teste()
    try:
        yield conn
    finally:
        conn.close()


def test_carregar_testamentos(conexao):
    df = carregar_testamentos(conexao)
    assert not df.empty
    assert set(df["name"]) == {"Velho Testamento", "Novo Testamento"}


def test_carregar_livros_e_capitulos(conexao):
    livros_vt = carregar_livros_testamento(conexao, 1)
    assert len(livros_vt) == 1
    assert livros_vt["name"].iloc[0] == "Gênesis"

    capitulos_genesis = carregar_capitulos(conexao, 1)
    assert list(capitulos_genesis["chapter"]) == [1]


def test_carregar_todos_livros(conexao):
    df = carregar_todos_livros(conexao)
    assert len(df) == 2
    assert set(df["name"]) == {"Gênesis", "João"}


def test_carregar_versiculos(conexao):
    df = carregar_versiculos(conexao, livro_id=2, capitulo=3)
    assert len(df) == 2
    assert 16 in df["Versículo"].values


def test_buscar_versiculos_palavra_inteira(conexao):
    # Deve encontrar "amou" apenas como palavra inteira
    df = buscar_versiculos(conexao, termo="amou")
    assert not df.empty
    assert all("amou" in t.lower() for t in df["Texto"].tolist())


def test_buscar_versiculos_avancada_and(conexao):
    df = buscar_versiculos_avancada(
        conexao=conexao,
        termos=["Deus", "mundo"],
        operador="E",
        testamento_id=None,
        livro_id=2,
        busca_exata=False,
    )
    # João 3:16 contém "Deus" e "mundo"
    assert not df.empty
    ref_list = [
        (r["Livro"], r["Capítulo"], r["Versículo"]) for _, r in df.iterrows()
    ]
    assert ("João", 3, 16) in ref_list


def test_buscar_versiculos_avancada_or(conexao):
    df = buscar_versiculos_avancada(
        conexao=conexao,
        termos=["amou", "enviou"],
        operador="OU",
        testamento_id=None,
        livro_id=2,
        busca_exata=False,
    )
    # Deve trazer João 3:16 e 3:17
    refs = {
        (r["Livro"], r["Capítulo"], r["Versículo"])
        for _, r in df.iterrows()
    }
    assert ("João", 3, 16) in refs
    assert ("João", 3, 17) in refs


def test_comparar_versoes(conexao):
    """
    Testa comparar_versoes usando o mesmo banco como se fossem 2 versões.
    """
    conexoes = {"V1": conexao, "V2": conexao}
    df = comparar_versoes(
        conexoes_dict=conexoes,
        livro_id=2,
        capitulo=3,
        versiculo=16,
    )
    assert not df.empty
    assert "V1" in df.columns
    assert "V2" in df.columns
    assert df["Versículo"].iloc[0] == 16


def test_obter_info_livro(conexao):
    info = obter_info_livro(conexao, livro_id=2)
    assert info["nome"] == "João"
    assert info["testamento"] == "Novo Testamento"
    assert info["total_capitulos"] >= 1
    assert info["total_versiculos"] >= 2
