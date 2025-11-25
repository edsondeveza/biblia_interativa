"""
Módulo de Gerenciamento de Anotações.

Gerencia anotações de estudo bíblico com suporte a tags,
busca, estatísticas e exportação/importação.

Autor: Edson Deveza
Data: 2024
Versão: 2.1
Compatível: Python 3.12
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import streamlit as st

from .logger import (
    log_anotacao,
    log_exportacao,
    log_erro,
    log_estatisticas_sessao,
)


# ============================================================
# Helpers internos
# ============================================================
def _init_storage() -> None:
    """Garante que st.session_state.anotacoes exista."""
    if "anotacoes" not in st.session_state:
        st.session_state.anotacoes = {}


def _make_key(livro: str, capitulo: int, versiculo: int) -> str:
    """Gera chave única para a anotação."""
    return f"anotacao:{livro}:{capitulo}:{versiculo}"


# ============================================================
# CRUD de anotações
# ============================================================
def salvar_anotacao(
    livro: str,
    capitulo: int,
    versiculo: int,
    texto_anotacao: str,
    tags: Optional[List[str]] = None,
) -> bool:
    """
    Salva uma anotação de estudo bíblico.

    Se já existir uma anotação para o mesmo versículo,
    ela será atualizada mantendo a data de criação original.
    """
    try:
        _init_storage()
        chave = _make_key(livro, capitulo, versiculo)

        anotacao_existente = carregar_anotacao(livro, capitulo, versiculo)
        data_criacao = (
            anotacao_existente["data_criacao"]
            if anotacao_existente
            else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Normalizar tags (sem espaços nas pontas)
        tags_norm = [t.strip() for t in (tags or []) if t.strip()]

        anotacao = {
            "livro": livro,
            "capitulo": capitulo,
            "versiculo": versiculo,
            "texto": texto_anotacao,
            "tags": tags_norm,
            "data_criacao": data_criacao,
            "data_modificacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        st.session_state.anotacoes[chave] = anotacao

        # Log: se já existia, é edição; senão, criação
        acao = "editada" if anotacao_existente else "criada"
        log_anotacao(acao, livro, capitulo, versiculo)

        return True

    except Exception as e:
        log_erro(
            "salvar_anotacao",
            e,
            detalhes=f"{livro} {capitulo}:{versiculo}",
        )
        return False


def carregar_anotacao(
    livro: str,
    capitulo: int,
    versiculo: int,
) -> Optional[Dict]:
    """
    Carrega uma anotação específica.
    """
    chave = _make_key(livro, capitulo, versiculo)
    if "anotacoes" in st.session_state:
        return st.session_state.anotacoes.get(chave)
    return None


def listar_anotacoes(filtro_tag: Optional[str] = None) -> List[Dict]:
    """
    Lista todas as anotações, opcionalmente filtradas por tag.
    """
    if "anotacoes" not in st.session_state:
        return []

    anotacoes = list(st.session_state.anotacoes.values())

    if filtro_tag:
        filtro_norm = filtro_tag.strip().lower()
        anotacoes = [
            a
            for a in anotacoes
            if any(
                t.lower() == filtro_norm
                for t in a.get("tags", [])
            )
        ]

    return anotacoes


def excluir_anotacao(
    livro: str,
    capitulo: int,
    versiculo: int,
) -> bool:
    """
    Exclui uma anotação permanentemente.
    """
    if "anotacoes" not in st.session_state:
        return False

    chave = _make_key(livro, capitulo, versiculo)

    if chave in st.session_state.anotacoes:
        del st.session_state.anotacoes[chave]
        log_anotacao("excluida", livro, capitulo, versiculo)
        return True

    return False


# ============================================================
# Importação / exportação
# ============================================================
def exportar_anotacoes_json() -> str:
    """
    Exporta todas as anotações para formato JSON.

    Útil para backup ou migração de dados.
    """
    if "anotacoes" not in st.session_state:
        json_vazio = json.dumps({}, indent=2, ensure_ascii=False)
        log_exportacao("JSON", 0, sucesso=True)
        return json_vazio

    total = len(st.session_state.anotacoes)
    json_data = json.dumps(
        st.session_state.anotacoes,
        indent=2,
        ensure_ascii=False,
    )

    log_exportacao("JSON", total, sucesso=True)
    return json_data


def importar_anotacoes_json(json_string: str) -> bool:
    """
    Importa anotações de uma string JSON.

    Anotações duplicadas serão substituídas pelas importadas.
    """
    try:
        data = json.loads(json_string)

        if not isinstance(data, dict):
            log_exportacao("JSON_IMPORT", 0, sucesso=False)
            return False

        _init_storage()

        # Mescla as anotações
        st.session_state.anotacoes.update(data)
        log_exportacao("JSON_IMPORT", len(data), sucesso=True)
        return True

    except json.JSONDecodeError as e:
        log_erro("importar_anotacoes_json/JSON", e)
        log_exportacao("JSON_IMPORT", 0, sucesso=False)
        return False
    except Exception as e:
        log_erro("importar_anotacoes_json", e)
        log_exportacao("JSON_IMPORT", 0, sucesso=False)
        return False


# ============================================================
# Estatísticas e buscas
# ============================================================
def obter_estatisticas_anotacoes() -> Dict:
    """
    Obtém estatísticas sobre as anotações do usuário.
    """
    if "anotacoes" not in st.session_state:
        return {
            "total": 0,
            "total_tags": 0,
            "livro_mais_anotado": "N/A",
            "tags_mais_usadas": [],
        }

    anotacoes = list(st.session_state.anotacoes.values())

    livros_count: Dict[str, int] = {}
    tags_count: Dict[str, int] = {}

    for anot in anotacoes:
        livro = anot["livro"]
        livros_count[livro] = livros_count.get(livro, 0) + 1

        for tag in anot.get("tags", []):
            tags_count[tag] = tags_count.get(tag, 0) + 1

    livro_top = (
        max(livros_count, key=livros_count.get)
        if livros_count
        else "N/A"
    )

    tags_ordenadas = sorted(
        tags_count.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:5]

    stats = {
        "total": len(anotacoes),
        "total_tags": len(tags_count),
        "livro_mais_anotado": livro_top,
        "tags_mais_usadas": tags_ordenadas,
    }

    # Log simples das estatísticas gerais
    log_estatisticas_sessao(
        total_buscas=0,  # aqui você pode ajustar depois se quiser
        total_anotacoes=stats["total"],
        tempo_sessao_min=0,
    )

    return stats


def buscar_anotacoes(termo: str) -> List[Dict]:
    """
    Busca anotações por texto (case-insensitive).
    """
    if "anotacoes" not in st.session_state:
        return []

    termo = (termo or "").strip()
    if not termo:
        return []

    termo_lower = termo.lower()
    encontrados: List[Dict] = []

    for anot in st.session_state.anotacoes.values():
        if termo_lower in anot["texto"].lower():
            encontrados.append(anot)

    return encontrados


def obter_anotacoes_por_livro(livro: str) -> List[Dict]:
    """
    Obtém todas as anotações de um livro específico.
    """
    if "anotacoes" not in st.session_state:
        return []

    return [
        a
        for a in st.session_state.anotacoes.values()
        if a["livro"] == livro
    ]


def obter_todas_tags() -> List[str]:
    """
    Obtém lista ordenada de todas as tags únicas.
    """
    if "anotacoes" not in st.session_state:
        return []

    tags = set()
    for anot in st.session_state.anotacoes.values():
        tags.update(anot.get("tags", []))

    return sorted(tags)


def contar_anotacoes_por_testamento() -> Tuple[int, int]:
    """
    Conta anotações por testamento (VT e NT).

    Retorna:
        (total_vt, total_nt)
    """
    if "anotacoes" not in st.session_state:
        return (0, 0)

    livros_vt = {
        "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio",
        "Josué", "Juízes", "Rute", "I Samuel", "II Samuel",
        "I Reis", "II Reis", "I Crônicas", "II Crônicas",
        "Esdras", "Neemias", "Ester", "Jó", "Salmos", "Provérbios",
        "Eclesiastes", "Cantares", "Isaías", "Jeremias", "Lamentações",
        "Ezequiel", "Daniel", "Oséias", "Joel", "Amós", "Obadias",
        "Jonas", "Miquéias", "Naum", "Habacuque", "Sofonias",
        "Ageu", "Zacarias", "Malaquias",
    }

    total_vt = 0
    total_nt = 0

    for anot in st.session_state.anotacoes.values():
        if anot["livro"] in livros_vt:
            total_vt += 1
        else:
            total_nt += 1

    return total_vt, total_nt


def limpar_todas_anotacoes() -> bool:
    """
    Remove TODAS as anotações permanentemente.

    ATENÇÃO: Esta ação não pode ser desfeita!
    """
    if "anotacoes" in st.session_state:
        total = len(st.session_state.anotacoes)
        st.session_state.anotacoes = {}
        log_exportacao("LIMPEZA_TOTAL_ANOTACOES", total, sucesso=True)
        return True
    return False
