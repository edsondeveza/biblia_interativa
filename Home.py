"""
Bíblia Interativa v2.0
Página Principal (Home)
"""

import streamlit as st
import os

# Configuração da página (deve ser a primeira chamada Streamlit)
st.set_page_config(
    page_title="Bíblia Interativa",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/seu-usuario/biblia_interativa',
        'Report a bug': "https://github.com/seu-usuario/biblia_interativa/issues",
        'About': "# Bíblia Interativa v2.0\nUma ferramenta moderna para estudo da Palavra de Deus."
    }
)

# Inicializar session_state
if 'anotacoes' not in st.session_state:
    st.session_state.anotacoes = {}

if 'historico_buscas' not in st.session_state:
    st.session_state.historico_buscas = []

# Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# === SIDEBAR ===
with st.sidebar:
    st.title("📖 Bíblia Interativa")
    st.markdown("### Configurações Globais")
    
    # Escolha da versão
    versoes = ["ACF", "ARA", "ARC", "AS21", "JFAA", "KJA", "KJF", "NAA", "NBV", "NTLH", "NVI", "NVT", "TB"]
    
    # Verificar versões disponíveis
    versoes_disponiveis = []
    for v in versoes:
        if os.path.exists(os.path.join(DATA_DIR, f"{v}.sqlite")):
            versoes_disponiveis.append(v)
    
    if versoes_disponiveis:
        if 'versao_selecionada' not in st.session_state:
            st.session_state.versao_selecionada = versoes_disponiveis[0]
        
        versao = st.selectbox(
            "🔖 Versão da Bíblia",
            versoes_disponiveis,
            index=versoes_disponiveis.index(st.session_state.versao_selecionada),
            help="Selecione a tradução bíblica",
            key="select_versao"
        )
        
        st.session_state.versao_selecionada = versao
        st.session_state.caminho_banco = os.path.join(DATA_DIR, f"{versao}.sqlite")
        
        st.success(f"✓ Usando: **{versao}**")
    else:
        st.error("❌ Nenhuma versão encontrada!")
        st.info("Coloque os arquivos .sqlite na pasta `data/`")
    
    st.markdown("---")
    
    # Estatísticas rápidas
    st.markdown("### 📊 Estatísticas")
    
    col1, col2 = st.columns(2)
    with col1:
        total_anotacoes = len(st.session_state.anotacoes)
        st.metric("Anotações", total_anotacoes)
    
    with col2:
        total_buscas = len(st.session_state.historico_buscas)
        st.metric("Buscas", total_buscas)
    
    st.markdown("---")
    
    # Links rápidos
    st.markdown("### 🔗 Acesso Rápido")
    
    if st.button("📖 Leitura", use_container_width=True):
        st.switch_page("pages/1_📖_Leitura.py")
    
    if st.button("🔍 Buscar", use_container_width=True):
        st.switch_page("pages/3_🔍+_Busca_Avançada.py")
    
    if st.button("📝 Anotações", use_container_width=True):
        st.switch_page("pages/5_📝_Anotações.py")
    
    st.markdown("---")
    
    # Rodapé
    st.markdown(
        """
        <div style='text-align: center; padding: 20px 0;'>
            <small>
                💖 Desenvolvido para estudo da Palavra<br>
                <strong>v2.0</strong> | 2024
            </small>
        </div>
        """,
        unsafe_allow_html=True
    )

# === CONTEÚDO PRINCIPAL ===
st.title("📖 Bem-vindo à Bíblia Interativa")

st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 30px; border-radius: 10px; color: white; margin: 20px 0;'>
    <h2 style='margin: 0; color: white;'>✨ Uma nova forma de estudar a Palavra de Deus</h2>
    <p style='margin: 10px 0 0 0; font-size: 1.1em;'>
        Ferramentas modernas para leitura, busca, comparação e anotações bíblicas.
    </p>
</div>
""", unsafe_allow_html=True)

# Seção de funcionalidades
st.markdown("## 🎯 Funcionalidades")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📖 Leitura
    
    Navegue pela Bíblia de forma intuitiva:
    - Por testamento
    - Por livro
    - Por capítulo
    - Visualização clara
    """)
    st.page_link(
        "pages/1_📖_Leitura.py",
        label="Ir para Leitura →",
        icon="📖",
    )

with col2:
    st.markdown("""
    ### 🔍 Busca Avançada
    
    Encontre o que procura:
    - Múltiplas palavras
    - Operadores lógicos
    - Filtros precisos
    - Histórico de buscas
    """)
    st.page_link(
        "pages/3_🔍+_Busca_Avançada.py",
        label="Ir para Busca →",
        icon="🔍",
    )

with col3:
    st.markdown("""
    ### 📝 Anotações
    
    Organize seus estudos:
    - Notas por versículo
    - Tags personalizadas
    - Backup/Restauração
    - Estatísticas
    """)
    st.page_link(
        "pages/5_📝_Anotações.py",
        label="Ir para Anotações →",
        icon="📝",
    )


st.markdown("---")

# Seção de novidades
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ⚖️ Comparação de Versões
    
    **Novidade!** Compare até 3 traduções lado a lado.
    
    Perfeito para:
    - Estudos aprofundados
    - Compreender nuances
    - Análise textual
    - Ensino e pregação
    """)
    
    if st.button("🔍 Comparar Versões", key="btn_comparar", use_container_width=True):
        st.switch_page("pages/4_⚖️_Comparação.py")

with col2:
    st.markdown("""
    ### 🎓 Como Usar
    
    **Passo a passo:**
    
    1. 📌 Escolha uma versão no menu lateral
    2. 🔍 Use a navegação ou busca
    3. 📝 Crie anotações durante o estudo
    4. 💾 Faça backup regularmente
    """)
    
    with st.expander("💡 Dicas Avançadas"):
        st.markdown("""
        - Use **tags** nas anotações para organizar temas
        - A **busca avançada** aceita múltiplas palavras
        - Compare versões para entender melhor o texto
        - Exporte seus estudos em PDF, Excel ou CSV
        """)

# Versículo do dia
st.markdown("---")
st.markdown("## 💭 Reflexão")

import random
versiculos_inspiracao = [
    ("Salmos 119:105", "Lâmpada para os meus pés é a tua palavra e luz, para o meu caminho."),
    ("2 Timóteo 3:16", "Toda Escritura é inspirada por Deus e útil para o ensino, para a repreensão, para a correção, para a educação na justiça."),
    ("Josué 1:8", "Não cesses de falar deste Livro da Lei; antes, medita nele dia e noite, para que tenhas cuidado de fazer segundo tudo quanto nele está escrito."),
    ("Hebreus 4:12", "Porque a palavra de Deus é viva, e eficaz, e mais cortante do que qualquer espada de dois gumes."),
    ("Mateus 4:4", "Não só de pão viverá o homem, mas de toda palavra que procede da boca de Deus."),
]

ref, texto = random.choice(versiculos_inspiracao)

st.info(f"""
**{ref}**

*"{texto}"*
""")

# Cards de recursos
st.markdown("---")
st.markdown("## 📚 Recursos Disponíveis")

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container():
        st.markdown("#### 📖 Múltiplas Versões")
        st.caption(f"{len(versoes_disponiveis)} traduções disponíveis")

with col2:
    with st.container():
        st.markdown("#### 🔍 Busca Inteligente")
        st.caption("Operadores lógicos E/OU")

with col3:
    with st.container():
        st.markdown("#### 💾 Exportação")
        st.caption("PDF, Excel e CSV")

with col4:
    with st.container():
        st.markdown("#### 📱 Responsivo")
        st.caption("Funciona em todos dispositivos")

# Call to action
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 30px; 
                background-color: #f0f2f6; border-radius: 10px;'>
        <h3 style='margin: 0 0 20px 0;'>Pronto para começar?</h3>
        <p>Escolha uma funcionalidade no menu ao lado e comece a explorar a Palavra de Deus!</p>
    </div>
    """, unsafe_allow_html=True)

# Informações técnicas (opcional, pode ser colapsado)
with st.expander("ℹ️ Informações Técnicas"):
    st.markdown(f"""
    **Versão do Sistema:** 2.0  
    **Versões Disponíveis:** {', '.join(versoes_disponiveis) if versoes_disponiveis else 'Nenhuma'}  
    **Diretório de Dados:** `{DATA_DIR}`  
    **Total de Anotações:** {len(st.session_state.anotacoes)}  
    **Total de Buscas:** {len(st.session_state.historico_buscas)}
    """)