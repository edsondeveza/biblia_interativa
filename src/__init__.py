"""
Bíblia Interativa v2.0
Módulo de Lógica de Negócio

Este pacote contém toda a lógica de negócio da aplicação,
separada da interface do usuário.

Módulos:
    - database: Operações com banco de dados SQLite
    - annotations: Sistema de anotações de estudo
    - export: Funções de exportação em múltiplos formatos
"""

__version__ = "2.0.0"
__author__ = "Edson Deveza"
__email__ = "edsondeveza@hotmail.com"

# Imports para facilitar uso
from .database import (
    conectar_banco,
    carregar_testamentos,
    carregar_livros_testamento,
    carregar_todos_livros,
    carregar_capitulos,
    carregar_versiculos,
    buscar_versiculos,
    buscar_versiculos_avancada,
    comparar_versoes
)

from .annotations import (
    salvar_anotacao,
    carregar_anotacao,
    listar_anotacoes,
    excluir_anotacao,
    exportar_anotacoes_json,
    importar_anotacoes_json,
    obter_estatisticas_anotacoes,
    buscar_anotacoes,
    obter_todas_tags
)

from .export import (
    exportar_csv,
    exportar_xlsx,
    exportar_pdf,
    exportar_texto_simples,
    exportar_markdown,
    exportar_html
)

__all__ = [
    # Database
    'conectar_banco',
    'carregar_testamentos',
    'carregar_livros_testamento',
    'carregar_todos_livros',
    'carregar_capitulos',
    'carregar_versiculos',
    'buscar_versiculos',
    'buscar_versiculos_avancada',
    'comparar_versoes',
    
    # Annotations
    'salvar_anotacao',
    'carregar_anotacao',
    'listar_anotacoes',
    'excluir_anotacao',
    'exportar_anotacoes_json',
    'importar_anotacoes_json',
    'obter_estatisticas_anotacoes',
    'buscar_anotacoes',
    'obter_todas_tags',
    
    # Export
    'exportar_csv',
    'exportar_xlsx',
    'exportar_pdf',
    'exportar_texto_simples',
    'exportar_markdown',
    'exportar_html',
]