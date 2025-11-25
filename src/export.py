"""
Módulo de Exportação de Dados.

Funções para exportar dados bíblicos e anotações em múltiplos
formatos (CSV, Excel, PDF, TXT, Markdown, HTML).

Autor: Edson Deveza
Data: 2024
Versão: 2.1
Compatível: Python 3.12
"""

from datetime import datetime
from typing import Optional
import io

import pandas as pd
import streamlit as st
from fpdf import FPDF

from .logger import log_exportacao, log_erro
from .error_handler import handle_export_error


def _validar_df(df: pd.DataFrame) -> bool:
    """Validação simples para evitar export de DF vazio."""
    return not df.empty


# ============================================================
# CSV
# ============================================================
def exportar_csv(df: pd.DataFrame, nome_arquivo: str = "resultados") -> None:
    """
    Exporta DataFrame para CSV com encoding UTF-8.
    Exibe botão de download no Streamlit.
    """
    if not _validar_df(df):
        st.warning("⚠️ Não há dados para exportar em CSV.")
        return

    try:
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="📥 Exportar como CSV",
            data=csv,
            file_name=f"{nome_arquivo}_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Formato compatível com Excel, Google Sheets, etc.",
        )

        log_exportacao("CSV", len(df), sucesso=True)

    except Exception as e:
        log_erro("exportar_csv", e)
        log_exportacao("CSV", len(df), sucesso=False)
        handle_export_error(e, "CSV")


# ============================================================
# Excel (XLSX)
# ============================================================
def exportar_xlsx(df: pd.DataFrame, nome_arquivo: str = "resultados") -> None:
    """
    Exporta DataFrame para Excel (.xlsx) com formatação.
    Exibe botão de download no Streamlit.
    """
    if not _validar_df(df):
        st.warning("⚠️ Não há dados para exportar em Excel.")
        return

    try:
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Resultados")

            workbook = writer.book
            worksheet = writer.sheets["Resultados"]

            header_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#667eea",
                    "font_color": "white",
                    "align": "center",
                    "valign": "vcenter",
                    "border": 1,
                }
            )

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).apply(len).max(),
                    len(col),
                )
                worksheet.set_column(i, i, min(max_len + 2, 50))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="📥 Exportar como Excel",
            data=output.getvalue(),
            file_name=f"{nome_arquivo}_{timestamp}.xlsx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            use_container_width=True,
            help="Formato Excel com formatação",
        )

        log_exportacao("XLSX", len(df), sucesso=True)

    except Exception as e:
        log_erro("exportar_xlsx", e)
        log_exportacao("XLSX", len(df), sucesso=False)
        handle_export_error(e, "Excel")


# ============================================================
# PDF
# ============================================================
def exportar_pdf(
    df: pd.DataFrame,
    titulo: str = "Resultados da Busca",
    nome_arquivo: str = "resultados",
) -> None:
    """
    Exporta DataFrame para PDF com formatação básica.
    """
    if not _validar_df(df):
        st.warning("⚠️ Não há dados para exportar em PDF.")
        return

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Título
        pdf.set_font("Arial", "B", 16)
        titulo_encoded = titulo.encode("latin-1", "replace").decode("latin-1")
        pdf.cell(0, 10, txt=titulo_encoded, ln=True, align="C")
        pdf.ln(5)

        # Data
        pdf.set_font("Arial", "I", 9)
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(0, 5, txt=f"Gerado em: {data_atual}", ln=True, align="C")
        pdf.ln(10)

        # Contador
        pdf.set_font("Arial", "", 10)
        pdf.cell(
            0,
            5,
            txt=f"Total de versículos: {len(df)}",
            ln=True,
        )
        pdf.ln(5)

        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        for idx, row in df.iterrows():
            try:
                referencia = (
                    f"{row['Livro']} "
                    f"{row['Capítulo']}:{row['Versículo']}"
                )
                pdf.set_font("Arial", "B", 11)
                pdf.cell(
                    0,
                    6,
                    referencia.encode("latin-1", "replace").decode(
                        "latin-1"
                    ),
                    ln=True,
                )

                pdf.set_font("Arial", "", 10)
                texto = row["Texto"].encode("latin-1", "replace").decode(
                    "latin-1"
                )
                pdf.multi_cell(0, 6, texto)
                pdf.ln(3)

                if (idx + 1) % 5 == 0:
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(2)

            except Exception as e_verso:
                # Loga erro, mas continua
                log_erro(
                    "exportar_pdf/versiculo",
                    e_verso,
                    detalhes=f"idx={idx}",
                )
                continue

        pdf.set_y(-20)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(
            0,
            10,
            "Gerado pela Bíblia Interativa v2.0",
            0,
            0,
            "C",
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_output = pdf.output(dest="S").encode("latin-1", "replace")

        st.download_button(
            label="📥 Exportar como PDF",
            data=pdf_output,
            file_name=f"{nome_arquivo}_{timestamp}.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Formato PDF (pode ter limitações com acentuação).",
        )

        log_exportacao("PDF", len(df), sucesso=True)

    except Exception as e:
        log_erro("exportar_pdf", e)
        log_exportacao("PDF", len(df), sucesso=False)
        handle_export_error(e, "PDF")


# ============================================================
# TXT
# ============================================================
def exportar_texto_simples(
    df: pd.DataFrame,
    nome_arquivo: str = "resultados",
) -> None:
    """
    Exporta DataFrame como arquivo de texto simples (.txt).
    """
    if not _validar_df(df):
        st.warning("⚠️ Não há dados para exportar em TXT.")
        return

    try:
        linhas = [
            "=" * 60,
            "BÍBLIA INTERATIVA - RESULTADOS DA BUSCA",
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Total de versículos: {len(df)}",
            "=" * 60,
            "",
        ]

        for _, row in df.iterrows():
            referencia = (
                f"{row['Livro']} "
                f"{row['Capítulo']}:{row['Versículo']}"
            )
            texto = row["Texto"]

            linhas.append(f"{referencia}")
            linhas.append(f"{texto}")
            linhas.append("-" * 60)
            linhas.append("")

        conteudo = "\n".join(linhas)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="📥 Exportar como TXT",
            data=conteudo,
            file_name=f"{nome_arquivo}_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True,
            help="Formato de texto simples.",
        )

        log_exportacao("TXT", len(df), sucesso=True)

    except Exception as e:
        log_erro("exportar_texto_simples", e)
        log_exportacao("TXT", len(df), sucesso=False)
        handle_export_error(e, "TXT")


# ============================================================
# Markdown
# ============================================================
def exportar_markdown(
    df: pd.DataFrame,
    nome_arquivo: str = "resultados",
) -> None:
    """
    Exporta DataFrame como Markdown (.md).
    """
    if not _validar_df(df):
        st.warning("⚠️ Não há dados para exportar em Markdown.")
        return

    try:
        linhas = [
            "# 📖 Resultados da Busca na Bíblia",
            "",
            f"*Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}*",
            f"*Total de versículos: {len(df)}*",
            "",
            "---",
            "",
        ]

        for _, row in df.iterrows():
            referencia = (
                f"{row['Livro']} "
                f"{row['Capítulo']}:{row['Versículo']}"
            )
            texto = row["Texto"]

            linhas.append(f"### **{referencia}**")
            linhas.append("")
            linhas.append(f"> {texto}")
            linhas.append("")
            linhas.append("---")
            linhas.append("")

        linhas.extend(
            [
                "",
                "---",
                "*Gerado pela Bíblia Interativa v2.0*",
            ]
        )

        conteudo = "\n".join(linhas)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="📥 Exportar como Markdown",
            data=conteudo,
            file_name=f"{nome_arquivo}_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True,
            help=(
                "Formato Markdown (compatível com GitHub, "
                "Notion, etc.)."
            ),
        )

        log_exportacao("MARKDOWN", len(df), sucesso=True)

    except Exception as e:
        log_erro("exportar_markdown", e)
        log_exportacao("MARKDOWN", len(df), sucesso=False)
        handle_export_error(e, "Markdown")


# ============================================================
# HTML
# ============================================================
def exportar_html(
    df: pd.DataFrame,
    titulo: str = "Resultados",
    nome_arquivo: str = "resultados",
) -> None:
    """
    Exporta DataFrame como HTML formatado e responsivo.
    """
    if not _validar_df(df):
        st.warning("⚠️ Não há dados para exportar em HTML.")
        return

    try:
        # Blocos de versículos
        blocos_versiculos = []
        for _, row in df.iterrows():
            referencia = (
                f"{row['Livro']} "
                f"{row['Capítulo']}:{row['Versículo']}"
            )
            texto = row["Texto"]
            blocos_versiculos.append(
                f"""
                <div class="versiculo">
                    <div class="referencia">{referencia}</div>
                    <div class="texto">{texto}</div>
                </div>
                """
            )

        html_versiculos = "\n".join(blocos_versiculos)

        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            line-height: 1.8;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 10px;
            font-size: 2em;
        }}
        
        .metadata {{
            color: #666;
            font-style: italic;
            margin-bottom: 30px;
            font-size: 0.95em;
        }}
        
        .versiculo {{
            margin: 25px 0;
            padding: 20px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 0 5px 5px 0;
            transition: all 0.3s ease;
        }}
        
        .versiculo:hover {{
            background: #e9ecef;
            border-left-width: 6px;
            transform: translateX(2px);
        }}
    
        .referencia {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .texto {{
            font-size: 1.05em;
            color: #2c3e50;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .stats {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
            .versiculo {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>{titulo}</h1>
    <div class="metadata">
        Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
    </div>
    
    <div class="stats">
        📊 Total de versículos encontrados: {len(df)}
    </div>

    {html_versiculos}

    <div class="footer">
        <p>📖 Gerado pela <strong>Bíblia Interativa v2.0</strong></p>
        <p>Uma ferramenta moderna para estudo da Palavra de Deus</p>
    </div>
</div>
</body>
</html>
"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="📥 Exportar como HTML",
            data=html,
            file_name=f"{nome_arquivo}_{timestamp}.html",
            mime="text/html",
            use_container_width=True,
            help="Página HTML formatada e responsiva.",
        )

        log_exportacao("HTML", len(df), sucesso=True)

    except Exception as e:
        log_erro("exportar_html", e)
        log_exportacao("HTML", len(df), sucesso=False)
        handle_export_error(e, "HTML")
