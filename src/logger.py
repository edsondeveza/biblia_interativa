"""
Sistema de Logging da Aplicação.

Registra eventos importantes, erros e métricas de uso da aplicação
em arquivos de log organizados por data.

Autor: Edson Deveza
Data: 2024
Versão: 2.1
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(name: str = 'BibliaInterativa') -> logging.Logger:
    """
    Configura e retorna um logger da aplicação.
    Evita recriação múltipla durante reruns do Streamlit.
    """
    logger = logging.getLogger(name)

    # ⚠️ Se já existir handler → retornar logger existente (evita duplicações)
    if logger.handlers:
        return logger

    # Criar pasta logs se não existir
    os.makedirs("logs", exist_ok=True)

    # Arquivo de log por dia
    hoje = datetime.now().strftime('%Y%m%d')
    log_file = f"logs/biblia_{hoje}.log"

    # Formatação padrão
    formato = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formato_data = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(formato, datefmt=formato_data)

    logger.setLevel(logging.INFO)

    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para console (apenas erros)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Logger global (singleton)
logger = setup_logger()


# ===================================================================
# Funções específicas de logging
# ===================================================================

def log_busca(termo: str, num_resultados: int, tempo_ms: int,
              tipo: str = "simples") -> None:
    logger.info(
        f"BUSCA_{tipo.upper()}: '{termo}' | "
        f"{num_resultados} resultados | {tempo_ms}ms"
    )


def log_leitura(livro: str, capitulo: int, versao: str) -> None:
    logger.info(f"LEITURA: {livro} {capitulo} ({versao})")


def log_anotacao(acao: str, livro: str, capitulo: int,
                 versiculo: int) -> None:
    logger.info(
        f"ANOTACAO_{acao.upper()}: {livro} {capitulo}:{versiculo}"
    )


def log_exportacao(formato: str, num_registros: int,
                   sucesso: bool = True) -> None:
    status = "SUCESSO" if sucesso else "ERRO"
    logger.info(
        f"EXPORTACAO_{status}: {formato} | {num_registros} registros"
    )


def log_erro(contexto: str, erro: Exception,
             detalhes: Optional[str] = None) -> None:
    mensagem = f"ERRO em {contexto}: {str(erro)}"
    if detalhes:
        mensagem += f" | Detalhes: {detalhes}"
    logger.error(mensagem, exc_info=True)


def log_inicio_aplicacao(versao: str = "2.0") -> None:
    logger.info("=" * 70)
    logger.info(f"APLICACAO INICIADA - Biblia Interativa v{versao}")
    logger.info(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 70)


def log_estatisticas_sessao(total_buscas: int, total_anotacoes: int,
                            tempo_sessao_min: int) -> None:
    logger.info(
        f"ESTATISTICAS_SESSAO: "
        f"{total_buscas} buscas | "
        f"{total_anotacoes} anotacoes | "
        f"{tempo_sessao_min} minutos"
    )
