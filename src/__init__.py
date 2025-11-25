"""
Bíblia Interativa v2.0
Pacote principal da lógica de negócio.

Este pacote contém os módulos centrais da aplicação:

- database: Acesso e consultas ao banco SQLite da Bíblia
- annotations: Sistema de anotações de estudo bíblico
- export: Exportação de resultados em múltiplos formatos
- optimize: Criação de índices e otimizações de banco
- error_handler: Tratamento e validação de erros
- logger: Sistema de logging e métricas de uso
"""

from __future__ import annotations

from .database import (
    conectar_banco,
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
from .annotations import (
    salvar_anotacao,
    carregar_anotacao,
    listar_anotacoes,
    excluir_anotacao,
    exportar_anotacoes_json,
    importar_anotacoes_json,
    obter_estatisticas_anotacoes,
    buscar_anotacoes,
    obter_anotacoes_por_livro,
    obter_todas_tags,
    contar_anotacoes_por_testamento,
    limpar_todas_anotacoes,
)
from .export import (
    exportar_csv,
    exportar_xlsx,
    exportar_pdf,
    exportar_texto_simples,
    exportar_markdown,
    exportar_html,
)
from .optimize import (
    criar_indices,
    otimizar_todos_bancos,
    verificar_indices_existentes,
)
from .error_handler import (
    handle_database_error,
    handle_export_error,
    validate_search_input,
    validate_annotation_input,
    show_connection_error,
)
from .logger import (
    setup_logger,
    logger,
    log_busca,
    log_leitura,
    log_anotacao,
    log_exportacao,
    log_erro,
    log_inicio_aplicacao,
    log_estatisticas_sessao,
)

__version__ = "2.0.0"
__author__ = "Edson Deveza"
__email__ = "edsondeveza@hotmail.com"

__all__ = [
    # Database
    "conectar_banco",
    "carregar_testamentos",
    "carregar_livros_testamento",
    "carregar_todos_livros",
    "carregar_capitulos",
    "carregar_versiculos",
    "buscar_versiculos",
    "buscar_versiculos_avancada",
    "comparar_versoes",
    "obter_info_livro",
    # Annotations
    "salvar_anotacao",
    "carregar_anotacao",
    "listar_anotacoes",
    "excluir_anotacao",
    "exportar_anotacoes_json",
    "importar_anotacoes_json",
    "obter_estatisticas_anotacoes",
    "buscar_anotacoes",
    "obter_anotacoes_por_livro",
    "obter_todas_tags",
    "contar_anotacoes_por_testamento",
    "limpar_todas_anotacoes",
    # Export
    "exportar_csv",
    "exportar_xlsx",
    "exportar_pdf",
    "exportar_texto_simples",
    "exportar_markdown",
    "exportar_html",
    # Optimize
    "criar_indices",
    "otimizar_todos_bancos",
    "verificar_indices_existentes",
    # Error handler
    "handle_database_error",
    "handle_export_error",
    "validate_search_input",
    "validate_annotation_input",
    "show_connection_error",
    # Logger
    "setup_logger",
    "logger",
    "log_busca",
    "log_leitura",
    "log_anotacao",
    "log_exportacao",
    "log_erro",
    "log_inicio_aplicacao",
    "log_estatisticas_sessao",
]
