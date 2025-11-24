"""
Página de Comparação de Versões
Compare até 3 traduções bíblicas lado a lado
"""

from src.export import exportar_csv, exportar_xlsx
from src.database import (
    conectar_banco,
    carregar_testamentos,
    carregar_livros_testamento,
    carregar_capitulos,
    comparar_versoes
)
import streamlit as st
import sys
import os

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


st.set_page_config(page_title="Comparação de Versões",
                   page_icon="⚖️", layout="wide")


st.title("⚖️ Comparação Entre Versões da Bíblia")

# Informação
st.info("📖 Compare o mesmo capítulo ou versículo em diferentes traduções da Bíblia lado a lado. Perfeito para estudos aprofundados!")

# Diretórios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Versões disponíveis
versoes_disponiveis = ["ACF", "ARA", "ARC", "AS21", "JFAA",
                       "KJA", "KJF", "NAA", "NBV", "NTLH", "NVI", "NVT", "TB"]
versoes_existentes = []

# Verificar quais versões existem
for versao in versoes_disponiveis:
    caminho = os.path.join(DATA_DIR, f"{versao}.sqlite")
    if os.path.exists(caminho):
        versoes_existentes.append(versao)

if len(versoes_existentes) < 2:
    st.error(
        "❌ É necessário ter pelo menos 2 versões da Bíblia para fazer comparações.")
    st.info("💡 Certifique-se de que os arquivos .sqlite estão na pasta 'data'")

    with st.expander("📋 Versões Disponíveis"):
        if versoes_existentes:
            for v in versoes_existentes:
                st.write(f"✅ {v}")
        else:
            st.write("❌ Nenhuma versão encontrada")

    if st.button("← Voltar para Home"):
        st.switch_page("Home.py")
    st.stop()

# Seleção de versões
st.markdown("### 📚 Selecione as Versões para Comparar")

col1, col2, col3 = st.columns(3)

with col1:
    versao1 = st.selectbox(
        "Primeira versão:",
        versoes_existentes,
        key="versao1_comp",
        help="Versão principal para comparação"
    )

with col2:
    versoes_disponiveis_v2 = [v for v in versoes_existentes if v != versao1]
    versao2 = st.selectbox(
        "Segunda versão:",
        versoes_disponiveis_v2,
        key="versao2_comp",
        help="Segunda versão para comparar"
    )

with col3:
    # Opção de terceira versão
    adicionar_terceira = st.checkbox(
        "Adicionar terceira versão", help="Compare até 3 versões simultaneamente")

    versao3 = None
    if adicionar_terceira:
        versoes_disponiveis_v3 = [
            v for v in versoes_existentes if v not in [versao1, versao2]]
        if versoes_disponiveis_v3:
            versao3 = st.selectbox(
                "Terceira versão:",
                versoes_disponiveis_v3,
                key="versao3_comp"
            )

# Conectar aos bancos de dados
try:
    conexoes = {
        versao1: conectar_banco(os.path.join(DATA_DIR, f"{versao1}.sqlite")),
        versao2: conectar_banco(os.path.join(DATA_DIR, f"{versao2}.sqlite"))
    }

    if versao3:
        conexoes[versao3] = conectar_banco(
            os.path.join(DATA_DIR, f"{versao3}.sqlite"))

    # Usar primeira conexão para navegação
    conexao_ref = conexoes[versao1]

except Exception as e:
    st.error(f"❌ Erro ao conectar aos bancos de dados: {e}")
    st.stop()

# Seleção de passagem bíblica
st.markdown("---")
st.markdown("### 📍 Selecione a Passagem para Comparar")

col1, col2, col3 = st.columns(3)

with col1:
    testamentos = carregar_testamentos(conexao_ref)
    testamento = st.selectbox(
        "Testamento:",
        testamentos["name"],
        key="test_comp"
    )
    testamento_id = testamentos[testamentos["name"]
                                == testamento]["id"].values[0]

with col2:
    livros = carregar_livros_testamento(conexao_ref, testamento_id)
    livro = st.selectbox(
        "Livro:",
        livros["name"],
        key="livro_comp"
    )
    livro_id = livros[livros["name"] == livro]["id"].values[0]

with col3:
    capitulos = carregar_capitulos(conexao_ref, livro_id)
    capitulo = st.selectbox(
        "Capítulo:",
        capitulos["chapter"],
        key="cap_comp"
    )

# Opções adicionais
col1, col2 = st.columns([1, 3])

with col1:
    comparar_versiculo_especifico = st.checkbox(
        "Comparar apenas um versículo",
        help="Marque para comparar um versículo específico"
    )

with col2:
    versiculo_especifico = None
    if comparar_versiculo_especifico:
        versiculo_especifico = st.number_input(
            "Número do versículo:",
            min_value=1,
            value=1,
            key="vers_comp"
        )

# Botão de comparação
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    comparar_btn = st.button(
        "⚖️ Comparar", type="primary", use_container_width=True)

if comparar_btn:
    with st.spinner("Carregando comparação..."):
        try:
            comparacao = comparar_versoes(
                conexoes,
                livro_id,
                capitulo,
                versiculo_especifico
            )
        except Exception as e:
            st.error(f"❌ Erro ao realizar comparação: {e}")
            st.stop()

    if not comparacao.empty:
        st.success("✅ Comparação carregada com sucesso!")

        # Cabeçalho da comparação
        st.markdown(f"## 📖 {livro} {capitulo}" +
                    (f":{versiculo_especifico}" if versiculo_especifico else ""))

        # Mostrar versões comparadas
        # pyright: ignore[reportArgumentType, reportCallIssue]
        versoes_comparadas = " vs. ".join(conexoes.keys()) # pyright: ignore[reportCallIssue, reportArgumentType]
        st.caption(f"Comparando: {versoes_comparadas}")

        st.markdown("---")

        # Tabs para diferentes visualizações
        tab1, tab2, tab3 = st.tabs(["📊 Tabela", "📋 Lado a Lado", "📈 Análise"])

        with tab1:
            # Visualização em tabela
            st.dataframe(
                comparacao,
                use_container_width=True,
                height=600,
                column_config={
                    "Versículo": st.column_config.NumberColumn("Ver.", width="small")
                }
            )

        with tab2:
            # Visualização lado a lado
            for idx, row in comparacao.iterrows():
                versiculo_num = row['Versículo']

                st.markdown(f"#### Versículo {versiculo_num}")

                # Criar colunas dinamicamente baseado no número de versões
                num_versoes = len(conexoes)
                cols = st.columns(num_versoes)

                for i, (versao, col) in enumerate(zip(conexoes.keys(), cols)):
                    with col:
                        # pyright: ignore[reportCallIssue, reportArgumentType]
                        texto = row[versao] if versao in row else "N/A" # pyright: ignore[reportCallIssue, reportArgumentType]

                        # Cores diferentes para cada versão
                        cores = ['#667eea', '#764ba2', '#f093fb']
                        cor = cores[i % len(cores)]

                        st.markdown(
                            f"""
                            <div style='padding: 15px; background-color: #f8f9fa; 
                                        border-left: 4px solid {cor}; 
                                        border-radius: 5px; height: 100%;'>
                                <strong style='color: {cor};'>{versao}</strong><br>
                                <span style='font-size: 0.95em; line-height: 1.6;'>{texto}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown("---")

        with tab3:
            # Análise de diferenças
            st.markdown("### 📊 Análise de Diferenças")

            if len(conexoes) == 2:
                versoes = list(conexoes.keys())
                diferencas = 0
                versiculos_diferentes = []

                for idx, row in comparacao.iterrows():
                    # pyright: ignore[reportCallIssue, reportArgumentType]
                    if row[versoes[0]] != row[versoes[1]]: # pyright: ignore[reportCallIssue, reportArgumentType]
                        diferencas += 1
                        versiculos_diferentes.append(row['Versículo'])

                total = len(comparacao)
                percentual = (diferencas / total * 100) if total > 0 else 0

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total de Versículos", total)

                with col2:
                    st.metric("Versículos Diferentes", diferencas)

                with col3:
                    st.metric("Percentual de Diferença", f"{percentual:.1f}%")

                # Gráfico de diferenças
                if versiculos_diferentes:
                    st.markdown("#### 📍 Versículos com Diferenças")
                    st.write(
                        f"Versículos: {', '.join(map(str, versiculos_diferentes[:20]))}")
                    if len(versiculos_diferentes) > 20:
                        st.caption(
                            f"... e mais {len(versiculos_diferentes) - 20} versículos")

                # Estatísticas de palavras
                st.markdown("#### 📝 Estatísticas de Palavras")

                for versao in versoes:
                    palavras_total = sum(len(str(row[versao]).split( # pyright: ignore[reportArgumentType] # type: ignore
                    )) for _, row in comparacao.iterrows())  # type: ignore
                    palavras_media = palavras_total / len(comparacao)
                    st.write(
                        f"**{versao}:** {palavras_total} palavras total | Média de {palavras_media:.1f} palavras/versículo")

            elif len(conexoes) == 3:
                st.info(
                    "💡 Análise detalhada disponível para comparação entre 2 versões.")

                # Estatísticas simples para 3 versões
                versoes = list(conexoes.keys())

                st.markdown("#### 📝 Estatísticas de Palavras")
                for versao in versoes:
                    # pyright: ignore[reportCallIssue, reportArgumentType]
                    palavras_total = sum(
                        len(str(row[versao]).split()) for _, row in comparacao.iterrows()) # pyright: ignore[reportCallIssue, reportArgumentType]
                    palavras_media = palavras_total / len(comparacao)
                    st.write(
                        f"**{versao}:** {palavras_total} palavras | Média: {palavras_media:.1f}")

        # Opções de exportação
        st.markdown("---")
        st.subheader("📥 Exportar Comparação")

        col1, col2 = st.columns(2)

        with col1:
            nome_arquivo = f"comparacao_{livro}_{capitulo}_{versoes_comparadas.replace(' vs. ', '_')}"
            exportar_csv(comparacao, nome_arquivo)

        with col2:
            exportar_xlsx(comparacao, nome_arquivo)

        # Opção de adicionar anotação
        st.markdown("---")
        if st.button("📝 Adicionar Anotação sobre esta Comparação"):
            st.session_state.anotacao_livro = livro
            st.session_state.anotacao_capitulo = capitulo
            st.session_state.anotacao_versiculo = versiculo_especifico if versiculo_especifico else 1
            st.switch_page("pages/5_📝_Anotações.py")

    else:
        st.warning("⚠️ Nenhum dado encontrado para comparação.")

# Sidebar - Dicas e Exemplos
with st.sidebar:
    st.markdown("### 💡 Dicas de Uso")

    with st.expander("📚 Quando Comparar"):
        st.markdown("""
        **A comparação é útil para:**
        
        - 📖 Estudo aprofundado
        - 🔍 Entender nuances
        - ✍️ Preparar sermões
        - 📝 Análise textual
        - 🎓 Pesquisa teológica
        """)

    with st.expander("⚖️ Escolhendo Versões"):
        st.markdown("""
        **Boas combinações:**
        
        - **ACF + NVI** - Tradicional vs Moderna
        - **ARA + NAA** - Almeida Antigas
        - **NTLH + NVT** - Linguagem Simples
        - **ACF + ARC + NVI** - Três perspectivas
        """)

    with st.expander("🎯 Foco da Comparação"):
        st.markdown("""
        **Para versículo específico:**
        - Análise palavra por palavra
        - Diferenças teológicas
        - Tradução de termos-chave
        
        **Para capítulo completo:**
        - Fluxo narrativo
        - Estilo literário
        - Consistência temática
        """)

    st.markdown("---")
    st.markdown("### ⚡ Atalhos")

    if st.button("📖 Leitura", use_container_width=True):
        st.switch_page("pages/1_📖_Leitura.py")

    if st.button("🔍 Buscar", use_container_width=True):
        st.switch_page("pages/3_🔍+_Busca_Avançada.py")

# Fechar conexões
for conexao in conexoes.values():
    conexao.close()
