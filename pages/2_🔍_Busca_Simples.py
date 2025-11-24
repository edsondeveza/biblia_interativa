"""
Página de Busca Simples
Busca rápida por palavras-chave na Bíblia
"""

import streamlit as st
import sys
import os


# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import conectar_banco, buscar_versiculos
from src.export import exportar_csv, exportar_xlsx, exportar_pdf, exportar_html


st.set_page_config(page_title="Busca Simples", page_icon="🔍", layout="wide")

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

# Flags de controle no session_state
if "sugestao_aplicada" not in st.session_state:
    st.session_state.sugestao_aplicada = None
if "disparar_busca" not in st.session_state:
    st.session_state.disparar_busca = False

st.title("🔍 Busca Simples")

# ---------------------------------------------------
# Verificar se a versão foi selecionada
# ---------------------------------------------------
if "caminho_banco" not in st.session_state:
    st.warning("⚠️ Por favor, selecione uma versão da Bíblia na página inicial.")
    if st.button("← Voltar para Home"):
        st.switch_page("Home.py")
    st.stop()

# ---------------------------------------------------
# Conectar ao banco
# ---------------------------------------------------
try:
    conexao = conectar_banco(st.session_state.caminho_banco)
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco de dados: {e}")
    st.stop()

st.markdown(f"**Versão atual:** {st.session_state.versao_selecionada}")
st.info(
    "💡 **Dica:** Digite uma palavra ou frase para buscar em toda a Bíblia. "
    "Para buscas mais avançadas, use a página de Busca Avançada."
)

# ---------------------------------------------------
# Se veio de sugestão / histórico, preencher o campo de busca
# ---------------------------------------------------
if st.session_state.sugestao_aplicada:
    # Aqui ainda não existe widget com key="input_busca_simples" neste ciclo,
    # então é seguro atualizar o session_state diretamente.
    st.session_state.input_busca_simples = st.session_state.sugestao_aplicada
    st.session_state.sugestao_aplicada = None

# ---------------------------------------------------
# Função para executar a busca e exibir resultados
# ---------------------------------------------------
def executar_busca(termo: str, filtro_testamento: str, testamento_id: int | None) -> None:
    if not termo:
        st.warning("⚠️ Por favor, digite algo para buscar.")
        return

    with st.spinner(f"Buscando por '{termo}'..."):
        resultados = buscar_versiculos(conexao, termo, testamento_id)

    if not resultados.empty:
        # Salvar no histórico
        if "historico_buscas" not in st.session_state:
            st.session_state.historico_buscas = []

        st.session_state.historico_buscas.insert(
            0,
            {
                "termo": termo,
                "resultados": len(resultados),
                "tipo": "Busca Simples",
                "testamento": filtro_testamento,
            },
        )
        st.session_state.historico_buscas = st.session_state.historico_buscas[:10]

        # Exibir resultados
        st.success(
            f"✅ Encontrados **{len(resultados)}** versículo(s) com o termo '{termo}'"
        )

        # Métricas rápidas
        col1, col2, col3 = st.columns(3)

        with col1:
            livros_unicos = resultados["Livro"].nunique()
            st.metric("Livros diferentes", livros_unicos)

        with col2:
            vt_count = len(
                resultados[
                    resultados["Livro"].isin(
                        [
                            "Gênesis",
                            "Êxodo",
                            "Levítico",
                            "Números",
                            "Deuteronômio",
                            "Josué",
                            "Juízes",
                            "Rute",
                            "I Samuel",
                            "II Samuel",
                            "I Reis",
                            "II Reis",
                            "I Crônicas",
                            "II Crônicas",
                            "Esdras",
                            "Neemias",
                            "Ester",
                            "Jó",
                            "Salmos",
                            "Provérbios",
                            "Eclesiastes",
                            "Cantares",
                            "Isaías",
                            "Jeremias",
                            "Lamentações",
                            "Ezequiel",
                            "Daniel",
                            "Oséias",
                            "Joel",
                            "Amós",
                            "Obadias",
                            "Jonas",
                            "Miquéias",
                            "Naum",
                            "Habacuque",
                            "Sofonias",
                            "Ageu",
                            "Zacarias",
                            "Malaquias",
                        ]
                    )
                ]
            )
            st.metric("Velho Testamento", vt_count)

        with col3:
            nt_count = len(resultados) - vt_count
            st.metric("Novo Testamento", nt_count)

        st.markdown("---")

        # Tabs para diferentes visualizações
        tab1, tab2 = st.tabs(["📊 Tabela", "📋 Lista"])

        with tab1:
            st.dataframe(
                resultados,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Livro": st.column_config.TextColumn("Livro", width="small"),
                    "Capítulo": st.column_config.NumberColumn("Cap.", width="small"),
                    "Versículo": st.column_config.NumberColumn("Ver.", width="small"),
                    "Texto": st.column_config.TextColumn("Texto", width="large"),
                },
            )

        with tab2:
            for idx, row in resultados.iterrows():
                with st.container():
                    c1, c2 = st.columns([1, 11])

                    with c1:
                        if st.button(
                            "📝", key=f"anot_{idx}", help="Adicionar anotação"
                        ):
                            st.session_state.anotacao_livro = row["Livro"]
                            st.session_state.anotacao_capitulo = row["Capítulo"]
                            st.session_state.anotacao_versiculo = row["Versículo"]
                            st.switch_page("pages/5_📝_Anotações.py")

                    with c2:
                        st.markdown(
                            f"""
                            <div style='padding: 10px; background-color: #f8f9fa; 
                                        border-left: 4px solid #667eea; border-radius: 5px; 
                                        margin-bottom: 10px;'>
                                <strong style='color: #667eea;'>
                                    {row['Livro']} {row['Capítulo']}:{row['Versículo']}
                                </strong><br>
                                <span style='font-size: 1.05em;'>{row['Texto']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    st.markdown("")

        # Exportação
        st.markdown("---")
        st.subheader("📥 Exportar Resultados")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            exportar_csv(resultados, f"busca_simples_{termo}")

        with c2:
            exportar_xlsx(resultados, f"busca_simples_{termo}")

        with c3:
            exportar_pdf(resultados, f"Busca: {termo}", f"busca_simples_{termo}")

        with c4:
            exportar_html(resultados, f"Busca: {termo}", f"busca_simples_{termo}")

    else:
        st.warning(f"⚠️ Nenhum versículo encontrado com o termo '{termo}'.")
        st.info(
            "💡 Tente:\n- Verificar a ortografia\n- Usar sinônimos\n- Buscar por palavras-chave mais gerais"
        )


# ---------------------------------------------------
# Campo de busca + filtro
# ---------------------------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    # Agora o valor vem exclusivamente de st.session_state.input_busca_simples
    termo = st.text_input(
        "Digite o que deseja buscar:",
        placeholder="Ex: amor, fé, salvação...",
        help="Digite uma palavra ou frase para buscar",
        key="input_busca_simples",
    )

with col2:
    st.write("")
    st.write("")
    filtro_testamento = st.selectbox(
        "Testamento:",
        ["Ambos", "Velho Testamento", "Novo Testamento"],
        key="filtro_testamento",
    )

# Mapear testamento
testamento_id = None
if filtro_testamento == "Velho Testamento":
    testamento_id = 1
elif filtro_testamento == "Novo Testamento":
    testamento_id = 2

# ---------------------------------------------------
# Disparo da busca
# ---------------------------------------------------
disparar = False

# Clique manual no botão Buscar
if st.button("🔍 Buscar", type="primary", use_container_width=False):
    disparar = True

# Disparo automático vindo de sugestão / histórico
if st.session_state.disparar_busca:
    disparar = True
    st.session_state.disparar_busca = False

# Executa a busca se necessário
if disparar:
    executar_busca(termo, filtro_testamento, testamento_id)

# ---------------------------------------------------
# Sidebar com histórico
# ---------------------------------------------------
with st.sidebar:
    st.markdown("### 📜 Histórico de Buscas")

    if "historico_buscas" in st.session_state and st.session_state.historico_buscas:
        buscas_simples = [
            b for b in st.session_state.historico_buscas if b["tipo"] == "Busca Simples"
        ]

        if buscas_simples:
            for i, busca in enumerate(buscas_simples[:5]):
                with st.expander(f"🔍 '{busca['termo']}'"):
                    st.write(f"**Resultados:** {busca['resultados']}")
                    st.write(f"**Testamento:** {busca['testamento']}")
                    if st.button("Buscar novamente", key=f"rebusca_{i}"):
                        st.session_state.sugestao_aplicada = busca["termo"]
                        st.session_state.disparar_busca = True
                        st.rerun()

            if st.button("🗑️ Limpar histórico", use_container_width=True):
                st.session_state.historico_buscas = []
                st.rerun()
        else:
            st.info("Nenhuma busca simples no histórico.")
    else:
        st.info("Nenhuma busca realizada ainda.")

    st.markdown("---")

    with st.expander("💡 Dicas de Busca"):
        st.markdown(
            """
        **Para melhores resultados:**
        
        - Use palavras completas  
        - Evite artigos (o, a, um, uma)  
        - Busque por temas principais  
        - Use sinônimos se não encontrar
        
        **Exemplos:**
        - ✅ "amor"
        - ✅ "salvação"
        - ✅ "fé esperança"
        - ❌ "o amor de deus"
        """
        )

    st.markdown("---")
    st.markdown("### ⚡ Atalhos")

    if st.button("🔍+ Busca Avançada", use_container_width=True):
        st.switch_page("pages/3_🔍+_Busca_Avançada.py")

    if st.button("📖 Ir para Leitura", use_container_width=True):
        st.switch_page("pages/1_📖_Leitura.py")

# ---------------------------------------------------
# Buscas sugeridas
# ---------------------------------------------------
st.markdown("---")
st.markdown("### 💡 Buscas Sugeridas")

col1, col2, col3, col4 = st.columns(4)

buscas_sugeridas = [
    ("❤️ Amor", "amor"),
    ("🙏 Oração", "oração"),
    ("✝️ Salvação", "salvação"),
    ("🕊️ Paz", "paz"),
    ("💪 Força", "força"),
    ("📖 Sabedoria", "sabedoria"),
    ("🌟 Esperança", "esperança"),
    ("🛡️ Fé", "fé"),
]

for i, (label, termo_sugerido) in enumerate(buscas_sugeridas):
    col = [col1, col2, col3, col4][i % 4]
    with col:
        if st.button(label, key=f"sugestao_{i}", use_container_width=True):
            # Marca o termo e diz para disparar a busca no próximo ciclo
            st.session_state.sugestao_aplicada = termo_sugerido
            st.session_state.disparar_busca = True
            st.rerun()

conexao.close()
