"""
Página de Busca Avançada
Busca com múltiplas palavras, operadores lógicos e filtros
"""

import streamlit as st
import sys
import os

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import conectar_banco, buscar_versiculos_avancada, carregar_todos_livros
from src.export import exportar_csv, exportar_xlsx, exportar_pdf, exportar_html

st.set_page_config(page_title="Busca Avançada", page_icon="🔍", layout="wide")
# =========================
# SELETOR DE VERSÃO GLOBAL
# =========================

with st.sidebar:
    st.markdown("### 📖 Versão da Bíblia")

    # Descobrir versões disponíveis (arquivos .sqlite da pasta data)
    raiz_projeto = os.path.dirname(os.path.dirname(__file__))  # .../biblia_interativa
    pasta_biblias = os.path.join(raiz_projeto, "data")         # .../biblia_interativa/data

    if not os.path.isdir(pasta_biblias):
        st.error(f"❌ Pasta de bíblias não encontrada: {pasta_biblias}")
    else:
        versoes_disponiveis = [
            f.replace(".sqlite", "")
            for f in os.listdir(pasta_biblias)
            if f.endswith(".sqlite")
        ]

        if not versoes_disponiveis:
            st.error("❌ Nenhuma versão (.sqlite) encontrada na pasta data.")
        else:
            # Valor atual (se ainda não existir, usa a primeira versão)
            versao_atual = st.session_state.get("versao_selecionada", versoes_disponiveis[0])

            versao_escolhida = st.selectbox(
                "Versão:",
                versoes_disponiveis,
                index=versoes_disponiveis.index(versao_atual),
                key="versao_global_selector",
            )

            if versao_escolhida != versao_atual:
                st.session_state.versao_selecionada = versao_escolhida
                st.session_state.caminho_banco = os.path.join(
                    pasta_biblias, versao_escolhida + ".sqlite"
                )
                st.rerun()


st.title("🔍+ Busca Avançada")

# Verificar se a versão foi selecionada
if 'caminho_banco' not in st.session_state:
    st.warning("⚠️ Por favor, selecione uma versão da Bíblia na página inicial.")
    if st.button("← Voltar para Home"):
        st.switch_page("Home.py")
    st.stop()

# Conectar ao banco
try:
    conexao = conectar_banco(st.session_state.caminho_banco)
    livros = carregar_todos_livros(conexao)
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco de dados: {e}")
    st.stop()

# Interface
st.markdown(f"**Versão atual:** {st.session_state.versao_selecionada}")
st.info("💡 **Busca Avançada:** Use múltiplas palavras, operadores lógicos e filtros precisos para encontrar exatamente o que procura.")

# Layout em duas colunas
col_esquerda, col_direita = st.columns([2, 1])

with col_esquerda:
    st.markdown("### 🔤 Termos de Busca")
    
    # Campo de busca
    termo_busca = st.text_input(
        "Digite as palavras para buscar:",
        placeholder="Ex: amor fé esperança",
        help="Separe múltiplas palavras com espaço",
        key="input_busca_avancada"
    )
    
    # Tipo de busca
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_busca = st.radio(
            "Tipo de busca:",
            ["Palavras individuais", "Frase exata"],
            help="Palavras individuais: busca cada palavra separadamente\nFrase exata: busca a frase completa"
        )
    
    with col2:
        # Operador lógico (só para palavras individuais)
        if tipo_busca == "Palavras individuais":
            operador = st.radio(
                "Operador lógico:",
                ["E (AND)", "OU (OR)"],
                help="E: todas as palavras devem aparecer\nOU: qualquer palavra pode aparecer"
            )
            operador_logico = "E" if operador == "E (AND)" else "OU"
        else:
            operador_logico = "E"
            st.info("💡 Na busca por frase exata, as palavras devem aparecer na ordem digitada.")

with col_direita:
    st.markdown("### 🎯 Filtros")
    
    # Filtro de testamento
    filtro_testamento = st.selectbox(
        "Testamento:",
        ["Ambos", "Velho Testamento", "Novo Testamento"],
        help="Limitar busca a um testamento específico"
    )
    
    testamento_id = None
    if filtro_testamento == "Velho Testamento":
        testamento_id = 1
    elif filtro_testamento == "Novo Testamento":
        testamento_id = 2
    
    # Filtro de livro
    usar_filtro_livro = st.checkbox("Buscar em livro específico")
    
    livro_id = None
    if usar_filtro_livro:
        livro_selecionado = st.selectbox(
            "Livro:",
            livros["name"],
            help="Buscar apenas neste livro"
        )
        livro_id = livros[livros["name"] == livro_selecionado]["id"].values[0]

# Botão de busca centralizado
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    buscar = st.button("🔍 Buscar", type="primary", use_container_width=True)

if buscar:
    if not termo_busca:
        st.warning("⚠️ Por favor, digite algo para buscar.")
    else:
        # Preparar termos
        if tipo_busca == "Palavras individuais":
            termos = termo_busca.split()
        else:
            termos = termo_busca
        
        # Realizar busca
        with st.spinner(f"Buscando por '{termo_busca}'..."):
            resultados = buscar_versiculos_avancada(
                conexao,
                termos,
                operador=operador_logico,
                testamento_id=testamento_id,
                livro_id=livro_id,
                busca_exata=(tipo_busca == "Frase exata")
            )
        
        if not resultados.empty:
            # Salvar no histórico
            if 'historico_buscas' not in st.session_state:
                st.session_state.historico_buscas = []
            
            st.session_state.historico_buscas.insert(0, {
                'termo': termo_busca,
                'resultados': len(resultados),
                'tipo': 'Busca Avançada',
                'operador': operador_logico if tipo_busca == "Palavras individuais" else "Frase",
                'testamento': filtro_testamento,
                'livro': livro_selecionado if usar_filtro_livro else "Todos"
            })
            
            st.session_state.historico_buscas = st.session_state.historico_buscas[:10]
            
            # Exibir resultados
            st.success(f"✅ Encontrados **{len(resultados)}** versículo(s)")
            
            # Estatísticas detalhadas
            st.markdown("### 📊 Estatísticas da Busca")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Versículos", len(resultados))
            
            with col2:
                livros_unicos = resultados['Livro'].nunique()
                st.metric("Livros Diferentes", livros_unicos)
            
            with col3:
                capitulos_unicos = len(resultados.groupby(['Livro', 'Capítulo']))
                st.metric("Capítulos Diferentes", capitulos_unicos)
            
            with col4:
                palavras_termo = len(termo_busca.split())
                st.metric("Palavras Buscadas", palavras_termo)
            
            # Top 5 livros com mais resultados
            with st.expander("📚 Top 5 Livros com Mais Resultados"):
                top_livros = resultados['Livro'].value_counts().head(5)
                for livro, count in top_livros.items():
                    st.write(f"**{livro}:** {count} versículo(s)")
            
            st.markdown("---")
            
            # Tabs para visualização
            tab1, tab2, tab3 = st.tabs(["📊 Tabela Completa", "📋 Lista Formatada", "📈 Análise"])
            
            with tab1:
                st.dataframe(
                    resultados,
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )
            
            with tab2:
                # Agrupar por livro
                agrupar = st.checkbox("Agrupar por livro", value=False)
                
                if agrupar:
                    for livro in resultados['Livro'].unique():
                        with st.expander(f"📖 {livro}"):
                            livro_resultados = resultados[resultados['Livro'] == livro]
                            for idx, row in livro_resultados.iterrows():
                                st.markdown(
                                    f"""
                                    <div style='padding: 8px; margin-bottom: 8px; 
                                                background-color: #f8f9fa; 
                                                border-left: 3px solid #667eea;'>
                                        <strong style='color: #667eea;'>
                                            {row['Capítulo']}:{row['Versículo']}
                                        </strong> - {row['Texto']}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                else:
                    for idx, row in resultados.iterrows():
                        col1, col2 = st.columns([1, 11])
                        
                        with col1:
                            if st.button("📝", key=f"anot_av_{idx}", help="Adicionar anotação"):
                                st.session_state.anotacao_livro = row['Livro']
                                st.session_state.anotacao_capitulo = row['Capítulo']
                                st.session_state.anotacao_versiculo = row['Versículo']
                                st.switch_page("pages/5_📝_Anotações.py")
                        
                        with col2:
                            st.markdown(
                                f"""
                                <div style='padding: 10px; background-color: #f8f9fa; 
                                            border-left: 4px solid #764ba2; border-radius: 5px; 
                                            margin-bottom: 10px;'>
                                    <strong style='color: #764ba2;'>
                                        {row['Livro']} {row['Capítulo']}:{row['Versículo']}
                                    </strong><br>
                                    <span style='font-size: 1.05em;'>{row['Texto']}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
            
            with tab3:
                st.markdown("#### 📈 Distribuição dos Resultados")
                
                # Gráfico de distribuição por livro
                import pandas as pd
                livros_count = resultados['Livro'].value_counts().head(10)
                
                st.bar_chart(livros_count)
                
                # Distribuição VT vs NT
                st.markdown("#### 📊 Testamentos")
                col1, col2 = st.columns(2)
                
                # Lista simplificada de livros do VT
                livros_vt = ['Gênesis', 'Êxodo', 'Levítico', 'Números', 'Deuteronômio',
                             'Josué', 'Juízes', 'Rute', 'I Samuel', 'II Samuel',
                             'I Reis', 'II Reis', 'I Crônicas', 'II Crônicas',
                             'Esdras', 'Neemias', 'Ester', 'Jó', 'Salmos', 'Provérbios',
                             'Eclesiastes', 'Cantares', 'Isaías', 'Jeremias', 'Lamentações',
                             'Ezequiel', 'Daniel', 'Oséias', 'Joel', 'Amós', 'Obadias',
                             'Jonas', 'Miquéias', 'Naum', 'Habacuque', 'Sofonias',
                             'Ageu', 'Zacarias', 'Malaquias']
                
                vt_count = len(resultados[resultados['Livro'].isin(livros_vt)])
                nt_count = len(resultados) - vt_count
                
                with col1:
                    st.metric("Velho Testamento", vt_count, 
                             f"{vt_count/len(resultados)*100:.1f}%")
                
                with col2:
                    st.metric("Novo Testamento", nt_count,
                             f"{nt_count/len(resultados)*100:.1f}%")
            
            # Exportação
            st.markdown("---")
            st.subheader("📥 Exportar Resultados")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                exportar_csv(resultados, f"busca_avancada_{termo_busca}")
            
            with col2:
                exportar_xlsx(resultados, f"busca_avancada_{termo_busca}")
            
            with col3:
                exportar_pdf(resultados, f"Busca Avançada: {termo_busca}", f"busca_avancada_{termo_busca}")
            
            with col4:
                exportar_html(resultados, f"Busca Avançada: {termo_busca}", f"busca_avancada_{termo_busca}")
        
        else:
            st.warning(f"⚠️ Nenhum versículo encontrado.")
            
            with st.expander("💡 Sugestões para melhorar sua busca"):
                st.markdown("""
                **Tente:**
                
                1. **Verificar ortografia** - Confira se as palavras estão corretas
                2. **Usar sinônimos** - Ex: "alegria" em vez de "felicidade"
                3. **Remover filtros** - Busque em "Ambos" os testamentos
                4. **Operador OU** - Encontre versículos com qualquer uma das palavras
                5. **Palavras-chave gerais** - Use termos mais abrangentes
                6. **Busca Simples** - Tente a busca simples primeiro
                """)

# Sidebar - Histórico e Dicas
with st.sidebar:
    st.markdown("### 📜 Histórico de Buscas Avançadas")
    
    if 'historico_buscas' in st.session_state and st.session_state.historico_buscas:
        buscas_avancadas = [b for b in st.session_state.historico_buscas if b['tipo'] == 'Busca Avançada']
        
        if buscas_avancadas:
            for i, busca in enumerate(buscas_avancadas[:5]):
                with st.expander(f"🔍 '{busca['termo']}'"):
                    st.write(f"**Resultados:** {busca['resultados']}")
                    st.write(f"**Operador:** {busca['operador']}")
                    st.write(f"**Testamento:** {busca['testamento']}")
                    st.write(f"**Livro:** {busca['livro']}")
        else:
            st.info("Nenhuma busca avançada no histórico.")
    else:
        st.info("Nenhuma busca realizada ainda.")
    
    st.markdown("---")
    
    # Exemplos de busca
    with st.expander("📚 Exemplos de Busca"):
        st.markdown("""
        **Busca com E (AND):**
        - `amor fé` → Versículos com ambas
        
        **Busca com OU (OR):**
        - `paz alegria` → Versículos com qualquer uma
        
        **Frase Exata:**
        - `o amor de Deus` → Frase completa
        
        **Com Filtros:**
        - Termo: `salvação`
        - Livro: `João`
        - Resultado: Salvação apenas em João
        """)
    
    # Atalhos
    st.markdown("---")
    st.markdown("### ⚡ Atalhos")
    
    if st.button("🔍 Busca Simples", use_container_width=True):
        st.switch_page("pages/2_🔍_Busca_Simples.py")
    
    if st.button("⚖️ Comparar Versões", use_container_width=True):
        st.switch_page("pages/4_⚖️_Comparação.py")

conexao.close()