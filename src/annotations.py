"""
Módulo de Anotações
Gerencia anotações de estudo bíblico
"""

import json
from datetime import datetime
import streamlit as st

def salvar_anotacao(livro, capitulo, versiculo, texto_anotacao, tags=None):
    """
    Salva uma anotação
    
    Args:
        livro: Nome do livro
        capitulo: Número do capítulo
        versiculo: Número do versículo
        texto_anotacao: Conteúdo da anotação
        tags: Lista de tags (opcional)
    """
    chave = f"anotacao:{livro}:{capitulo}:{versiculo}"
    
    anotacao = {
        "livro": livro,
        "capitulo": capitulo,
        "versiculo": versiculo,
        "texto": texto_anotacao,
        "tags": tags or [],
        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_modificacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Salvar no session state
    if 'anotacoes' not in st.session_state:
        st.session_state.anotacoes = {}
    
    st.session_state.anotacoes[chave] = anotacao
    
    return True

def carregar_anotacao(livro, capitulo, versiculo):
    """Carrega uma anotação específica"""
    chave = f"anotacao:{livro}:{capitulo}:{versiculo}"
    
    if 'anotacoes' in st.session_state:
        return st.session_state.anotacoes.get(chave)
    
    return None

def listar_anotacoes(filtro_tag=None):
    """
    Lista todas as anotações
    
    Args:
        filtro_tag: Tag opcional para filtrar
    
    Returns:
        Lista de anotações
    """
    if 'anotacoes' not in st.session_state:
        return []
    
    anotacoes = list(st.session_state.anotacoes.values())
    
    if filtro_tag:
        anotacoes = [a for a in anotacoes if filtro_tag in a.get('tags', [])]
    
    return anotacoes

def excluir_anotacao(livro, capitulo, versiculo):
    """Exclui uma anotação"""
    chave = f"anotacao:{livro}:{capitulo}:{versiculo}"
    
    if 'anotacoes' in st.session_state and chave in st.session_state.anotacoes:
        del st.session_state.anotacoes[chave]
        return True
    
    return False

def exportar_anotacoes_json():
    """Exporta todas as anotações para JSON"""
    if 'anotacoes' not in st.session_state:
        return json.dumps({}, indent=2, ensure_ascii=False)
    
    return json.dumps(st.session_state.anotacoes, indent=2, ensure_ascii=False)

def importar_anotacoes_json(json_string):
    """Importa anotações de um JSON"""
    try:
        anotacoes = json.loads(json_string)
        if 'anotacoes' not in st.session_state:
            st.session_state.anotacoes = {}
        
        st.session_state.anotacoes.update(anotacoes)
        return True
    except Exception as e:
        return False

def obter_estatisticas_anotacoes():
    """Obtém estatísticas das anotações"""
    if 'anotacoes' not in st.session_state:
        return {
            'total': 0,
            'total_tags': 0,
            'livro_mais_anotado': 'N/A',
            'tags_mais_usadas': []
        }
    
    anotacoes = list(st.session_state.anotacoes.values())
    
    # Contar livros
    livros_count = {}
    tags_count = {}
    
    for anot in anotacoes:
        livro = anot['livro']
        livros_count[livro] = livros_count.get(livro, 0) + 1
        
        for tag in anot.get('tags', []):
            tags_count[tag] = tags_count.get(tag, 0) + 1
    
    # Livro mais anotado
    livro_top = max(livros_count, key=livros_count.get) if livros_count else 'N/A' # pyright: ignore[reportCallIssue, reportArgumentType]
    
    # Tags mais usadas
    tags_ordenadas = sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'total': len(anotacoes),
        'total_tags': len(tags_count),
        'livro_mais_anotado': livro_top,
        'tags_mais_usadas': tags_ordenadas
    }

def buscar_anotacoes(termo):
    """
    Busca anotações por texto
    
    Args:
        termo: Termo para buscar no texto das anotações
    
    Returns:
        Lista de anotações que contêm o termo
    """
    if 'anotacoes' not in st.session_state:
        return []
    
    termo_lower = termo.lower()
    anotacoes_encontradas = []
    
    for anot in st.session_state.anotacoes.values():
        if termo_lower in anot['texto'].lower():
            anotacoes_encontradas.append(anot)
    
    return anotacoes_encontradas

def obter_anotacoes_por_livro(livro):
    """Obtém todas as anotações de um livro específico"""
    if 'anotacoes' not in st.session_state:
        return []
    
    return [
        a for a in st.session_state.anotacoes.values()
        if a['livro'] == livro
    ]

def obter_todas_tags():
    """Obtém lista de todas as tags únicas"""
    if 'anotacoes' not in st.session_state:
        return []
    
    tags = set()
    for anot in st.session_state.anotacoes.values():
        tags.update(anot.get('tags', []))
    
    return sorted(list(tags))