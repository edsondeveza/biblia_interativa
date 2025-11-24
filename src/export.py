"""
Módulo de Exportação
Funções para exportar dados em diferentes formatos
"""

import pandas as pd
import streamlit as st
import io
from fpdf import FPDF
from datetime import datetime

def exportar_csv(df, nome_arquivo="resultados"):
    """Exporta DataFrame para CSV"""
    csv = df.to_csv(index=False)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    st.download_button(
        label="📥 Exportar como CSV",
        data=csv,
        file_name=f"{nome_arquivo}_{timestamp}.csv",
        mime="text/csv",
        use_container_width=True
    )

def exportar_xlsx(df, nome_arquivo="resultados"):
    """Exporta DataFrame para Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    st.download_button(
        label="📥 Exportar como Excel",
        data=output.getvalue(),
        file_name=f"{nome_arquivo}_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

def exportar_pdf(df, titulo="Resultados da Busca", nome_arquivo="resultados"):
    """Exporta DataFrame para PDF"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Adicionar título
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=titulo.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C') # pyright: ignore[reportCallIssue]
    pdf.ln(5)
    
    # Adicionar data
    pdf.set_font("Arial", 'I', 8)
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    pdf.cell(0, 5, txt=f"Gerado em: {data_atual}", ln=True, align='C') # pyright: ignore[reportCallIssue]
    pdf.ln(10)

    # Adicionar dados
    pdf.set_font("Arial", size=9)
    for i, row in df.iterrows():
        try:
            # Referência
            ref = f"{row['Livro']} {row['Capítulo']}:{row['Versículo']}"
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 5, ref.encode('latin-1', 'replace').decode('latin-1'), ln=True)
            
            # Texto
            pdf.set_font("Arial", size=9)
            texto = row['Texto'].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, texto)
            pdf.ln(3)
        except Exception as e:
            st.error(f"Erro ao processar versículo: {e}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_output = pdf.output(dest='S').encode('latin-1', 'replace') # pyright: ignore[reportAttributeAccessIssue]
    
    st.download_button(
        label="📥 Exportar como PDF",
        data=pdf_output,
        file_name=f"{nome_arquivo}_{timestamp}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

def exportar_texto_simples(df, nome_arquivo="resultados"):
    """Exporta DataFrame como texto simples"""
    linhas = []
    
    for i, row in df.iterrows():
        ref = f"{row['Livro']} {row['Capítulo']}:{row['Versículo']}"
        texto = row['Texto']
        linhas.append(f"{ref}\n{texto}\n")
    
    conteudo = "\n".join(linhas)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    st.download_button(
        label="📥 Exportar como TXT",
        data=conteudo,
        file_name=f"{nome_arquivo}_{timestamp}.txt",
        mime="text/plain",
        use_container_width=True
    )

def exportar_markdown(df, nome_arquivo="resultados"):
    """Exporta DataFrame como Markdown"""
    linhas = ["# Resultados da Busca na Bíblia\n"]
    linhas.append(f"*Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}*\n\n")
    
    for i, row in df.iterrows():
        ref = f"**{row['Livro']} {row['Capítulo']}:{row['Versículo']}**"
        texto = row['Texto']
        linhas.append(f"{ref}\n\n{texto}\n\n---\n")
    
    conteudo = "\n".join(linhas)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    st.download_button(
        label="📥 Exportar como Markdown",
        data=conteudo,
        file_name=f"{nome_arquivo}_{timestamp}.md",
        mime="text/markdown",
        use_container_width=True
    )

def exportar_html(df, titulo="Resultados", nome_arquivo="resultados"):
    """Exporta DataFrame como HTML formatado"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: 'Georgia', serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                color: #667eea;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            .versiculo {{
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                border-radius: 5px;
            }}
            .referencia {{
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }}
            .texto {{
                font-size: 1.1em;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                color: #666;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <h1>{titulo}</h1>
        <p><em>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</em></p>
    """
    
    for i, row in df.iterrows():
        ref = f"{row['Livro']} {row['Capítulo']}:{row['Versículo']}"
        texto = row['Texto']
        
        html += f"""
        <div class="versiculo">
            <div class="referencia">{ref}</div>
            <div class="texto">{texto}</div>
        </div>
        """
    
    html += """
        <div class="footer">
            <p>Gerado pela Bíblia Interativa v2.0</p>
        </div>
    </body>
    </html>
    """
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    st.download_button(
        label="📥 Exportar como HTML",
        data=html,
        file_name=f"{nome_arquivo}_{timestamp}.html",
        mime="text/html",
        use_container_width=True
    )