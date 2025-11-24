"""
Página de Anotações de Estudo
Sistema completo para criar, gerenciar e organizar anotações bíblicas
"""

from src.annotations import (
    salvar_anotacao,
    carregar_anotacao,
    listar_anotacoes,
    excluir_anotacao,
    exportar_anotacoes_json,
    importar_anotacoes_json,
    obter_estatisticas_anotacoes,
    buscar_anotacoes,
    obter_todas_tags,
)
from src.database import (
    conectar_banco,
    carregar_testamentos,
    carregar_livros_testamento,
    carregar_capitulos,
    carregar_versiculos,
)
import streamlit as st
import sys
import os
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Anotações", page_icon="📝", layout="wide")

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
            versao_atual = st.session_state.get(
                "versao_selecionada", versoes_disponiveis[0]
            )

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

st.title("📝 Minhas Anotações de Estudo")

# Verificar se versão foi selecionada
if "caminho_banco" not in st.session_state:
    st.warning("⚠️ Por favor, selecione uma versão da Bíblia na página inicial.")
    if st.button("← Voltar para Home"):
        st.switch_page("Home.py")
    st.stop()

# Conectar ao banco
try:
    conexao = conectar_banco(st.session_state.caminho_banco)
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco de dados: {e}")
    st.stop()

# Inicializar anotações no session_state
if "anotacoes" not in st.session_state:
    st.session_state.anotacoes = {}

# Inicializar estado auxiliar para TAG selecionada na aba 3
if "tag_busca_sel" not in st.session_state:
    st.session_state.tag_busca_sel = None

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs(
    ["➕ Nova Anotação", "📚 Minhas Anotações", "🔍 Buscar Anotações", "⚙️ Gerenciar"]
)


def limpar_form_anotacao():
    # Só limpa se existir, para evitar KeyError
    if "texto_nova_anot" in st.session_state:
        st.session_state["texto_nova_anot"] = ""
    if "tags_anot" in st.session_state:
        st.session_state["tags_anot"] = ""
    if "anot_vers" in st.session_state:
        st.session_state["anot_vers"] = 1
    if "mostrar_sugestoes_tags" in st.session_state:
        st.session_state["mostrar_sugestoes_tags"] = False


# ========== TAB 1: NOVA ANOTAÇÃO ==========
with tab1:
    st.markdown("### ✍️ Criar Nova Anotação")

    # Verificar se veio de outra página com versículo pré-selecionado
    if "anotacao_livro" in st.session_state:
        st.info(
            f"📍 Anotação para: {st.session_state.anotacao_livro} "
            f"{st.session_state.anotacao_capitulo}:{st.session_state.anotacao_versiculo}"
        )

    col1, col2, col3 = st.columns(3)

    # ---------- Testamento ----------
    with col1:
        testamentos = carregar_testamentos(conexao)

        if testamentos.empty:
            st.error("Nenhum testamento foi encontrado no banco de dados.")
            st.stop()

        opcoes_test = testamentos["name"].tolist()

        testamento = st.selectbox(
            "Testamento:",
            opcoes_test,
            key="anot_test",
        )

        linha_test = testamentos[testamentos["name"] == testamento]

        if linha_test.empty:
            st.error(
                "Não foi possível localizar o testamento selecionado no banco de dados."
            )
            st.write("Selecionado:", repr(testamento))
            st.write("Disponíveis:", opcoes_test)
            st.stop()

        testamento_id = int(linha_test["id"].iloc[0])

    # ---------- Livro ----------
    with col2:
        livros = carregar_livros_testamento(conexao, testamento_id)

        if livros.empty:
            st.error("Nenhum livro foi encontrado para este testamento.")
            st.stop()

        opcoes_livros = livros["name"].tolist()

        # Pré-selecionar livro se veio de outra página
        livro_index = 0
        if "anotacao_livro" in st.session_state:
            try:
                livro_index = opcoes_livros.index(st.session_state.anotacao_livro)
            except ValueError:
                # Se não achar, mantém índice 0
                pass

        livro = st.selectbox(
            "Livro:",
            opcoes_livros,
            key="anot_livro",
            index=livro_index,
        )

        linha_livro = livros[livros["name"] == livro]
        if linha_livro.empty:
            st.error(
                "Não foi possível localizar o livro selecionado no banco de dados."
            )
            st.write("Selecionado:", repr(livro))
            st.write("Disponíveis:", opcoes_livros)
            st.stop()

        livro_id = int(linha_livro["id"].iloc[0])

    # ---------- Capítulo ----------
    with col3:
        capitulos = carregar_capitulos(conexao, livro_id)

        if capitulos.empty:
            st.error("Nenhum capítulo foi encontrado para este livro.")
            st.stop()

        opcoes_cap = capitulos["chapter"].tolist()

        # Pré-selecionar capítulo se veio de outra página
        cap_index = 0
        if "anotacao_capitulo" in st.session_state:
            try:
                cap_index = opcoes_cap.index(st.session_state.anotacao_capitulo)
            except ValueError:
                pass

        capitulo = st.selectbox(
            "Capítulo:",
            opcoes_cap,
            key="anot_cap",
            index=cap_index,
        )

        capitulo = int(capitulo)  # type: ignore

    # ---------- Versículo ----------
    versiculo_default = st.session_state.get("anotacao_versiculo", 1)
    versiculo = st.number_input(
        "Versículo:",
        min_value=1,
        value=versiculo_default,
        key="anot_vers",
    )

    # Limpar estado temporário (veio da outra aba)
    if "anotacao_livro" in st.session_state:
        del st.session_state.anotacao_livro
        del st.session_state.anotacao_capitulo
        del st.session_state.anotacao_versiculo

    # Mostrar texto do versículo
    st.markdown("---")
    try:
        versiculos_df = carregar_versiculos(conexao, livro_id, capitulo)
        if not versiculos_df.empty and versiculo <= len(versiculos_df):
            filtro_vers = versiculos_df[versiculos_df["Versículo"] == versiculo]
            if not filtro_vers.empty:
                texto_versiculo = filtro_vers["Texto"].values[0]

                st.markdown(
                    f"""
                    <div style='padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                border-radius: 10px; color: white; margin: 20px 0;'>
                        <h4 style='margin: 0; color: white;'>📖 {livro} {capitulo}:{versiculo}</h4>
                        <p style='margin: 10px 0 0 0; font-size: 1.1em; line-height: 1.6;'>
                            "{texto_versiculo}"
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning("⚠️ Versículo não encontrado na lista retornada.")
        else:
            st.warning("⚠️ Versículo não encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar versículo: {e}")

    st.markdown("---")

    # Verificar se já existe anotação
    anotacao_existente = carregar_anotacao(livro, capitulo, versiculo)

    if anotacao_existente:
        st.info(
            "ℹ️ Já existe uma anotação para este versículo. "
            "Você pode editá-la ou excluí-la."
        )

    # Campo de texto
    texto_anotacao = st.text_area(
        "✍️ Sua Anotação:",
        value=anotacao_existente["texto"] if anotacao_existente else "",
        height=200,
        placeholder="Digite suas reflexões, insights ou estudos sobre este versículo...",
        help="Escreva suas observações, perguntas, aplicações pessoais, etc.",
        key="texto_nova_anot",
    )

    # Tags
    col1, col2 = st.columns([3, 1])

    with col1:
        tags_input = st.text_input(
            "🏷️ Tags (separe por vírgula):",
            value=", ".join(anotacao_existente["tags"]) if anotacao_existente else "",
            placeholder="Ex: oração, fé, promessa, estudo",
            help="Use tags para organizar e buscar suas anotações",
            key="tags_anot",
        )

    with col2:
        st.write("")
        st.write("")
        if st.button("💡 Sugestões"):
            st.session_state.mostrar_sugestoes_tags = not st.session_state.get(
                "mostrar_sugestoes_tags", False
            )

    # Sugestões de tags
    if st.session_state.get("mostrar_sugestoes_tags", False):
        st.info(
            """
        **Tags Sugeridas:**  
        🙏 oração | ✝️ salvação | ❤️ amor | 💪 força | 🕊️ paz | 📖 sabedoria  
        🌟 esperança | 🛡️ fé | ⚔️ luta | 🎁 promessa | 📚 estudo | 💭 reflexão
        """
        )

    # Processar tags
    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

    # Botões de ação
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("💾 Salvar Anotação", type="primary", use_container_width=True):
            if texto_anotacao:
                sucesso = salvar_anotacao(
                    livro, capitulo, versiculo, texto_anotacao, tags
                )
                if sucesso:
                    st.success("✅ Anotação salva com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Erro ao salvar anotação.")
            else:
                st.warning("⚠️ Digite algo antes de salvar.")

    with col2:
        if anotacao_existente:
            if st.button("🗑️ Excluir", use_container_width=True):
                if excluir_anotacao(livro, capitulo, versiculo):
                    st.success("Anotação excluída!")
                    st.rerun()

    with col3:
        st.button(
            "🔄 Limpar",
            use_container_width=True,
            on_click=limpar_form_anotacao,
        )

# ========== TAB 2: MINHAS ANOTAÇÕES ==========
with tab2:
    st.markdown("### 📚 Todas as Anotações")

    todas_anotacoes = listar_anotacoes()

    if todas_anotacoes:
        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            todas_tags = obter_todas_tags()
            tag_filtro = st.selectbox(
                "Filtrar por tag:",
                ["Todas"] + todas_tags,
                key="filtro_tag_visualizar",
            )

        with col2:
            ordenar_por = st.selectbox(
                "Ordenar por:",
                ["Mais recente", "Mais antiga", "Livro (A-Z)", "Livro (Z-A)"],
            )

        with col3:
            visualizacao = st.selectbox(
                "Visualização:",
                ["Expansível", "Lista Compacta"],
            )

        # Aplicar filtro
        if tag_filtro != "Todas":
            anotacoes_filtradas = listar_anotacoes(filtro_tag=tag_filtro)
        else:
            anotacoes_filtradas = todas_anotacoes

        # Ordenar
        if ordenar_por == "Mais recente":
            anotacoes_filtradas = sorted(
                anotacoes_filtradas,
                key=lambda x: x.get("data_modificacao", ""),
                reverse=True,
            )
        elif ordenar_por == "Mais antiga":
            anotacoes_filtradas = sorted(
                anotacoes_filtradas,
                key=lambda x: x.get("data_modificacao", ""),
            )
        elif ordenar_por == "Livro (A-Z)":
            anotacoes_filtradas = sorted(
                anotacoes_filtradas,
                key=lambda x: x.get("livro", ""),
            )
        else:  # Z-A
            anotacoes_filtradas = sorted(
                anotacoes_filtradas,
                key=lambda x: x.get("livro", ""),
                reverse=True,
            )

        # Exibir anotações
        st.markdown(f"**{len(anotacoes_filtradas)} anotação(ões) encontrada(s)**")
        st.markdown("---")

        if visualizacao == "Expansível":
            # Visualização expansível
            for i, anot in enumerate(anotacoes_filtradas):
                with st.expander(
                    f"📖 {anot['livro']} {anot['capitulo']}:{anot['versiculo']} | "
                    f"🗓️ {anot.get('data_modificacao', 'Sem data')[:10]}",
                    expanded=False,
                ):
                    # Tags
                    if anot.get("tags"):
                        tags_html = " ".join([f"`{tag}`" for tag in anot["tags"]])
                        st.markdown(f"🏷️ {tags_html}")
                        st.markdown("")

                    # Texto
                    st.markdown(anot["texto"])

                    # Metadados
                    st.caption(
                        f"Criado: {anot.get('data_criacao', 'N/A')[:16]} | "
                        f"Modificado: {anot.get('data_modificacao', 'N/A')[:16]}"
                    )

                    # Ações
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button(f"✏️ Editar", key=f"edit_{i}"):
                            st.session_state.anotacao_livro = anot["livro"]
                            st.session_state.anotacao_capitulo = anot["capitulo"]
                            st.session_state.anotacao_versiculo = anot["versiculo"]
                            st.rerun()

                    with col2:
                        if st.button(f"📖 Ver Texto", key=f"ver_{i}"):
                            st.session_state.anotacao_livro = anot["livro"]
                            st.session_state.anotacao_capitulo = anot["capitulo"]
                            st.session_state.anotacao_versiculo = anot["versiculo"]
                            st.switch_page("pages/1_📖_Leitura.py")

                    with col3:
                        if st.button(f"🗑️ Excluir", key=f"del_{i}"):
                            excluir_anotacao(
                                anot["livro"],
                                anot["capitulo"],
                                anot["versiculo"],
                            )
                            st.success("Excluída!")
                            st.rerun()
        else:
            # Visualização compacta
            for i, anot in enumerate(anotacoes_filtradas):
                col1, col2 = st.columns([10, 2])

                with col1:
                    preview = (
                        anot["texto"][:100] + "..."
                        if len(anot["texto"]) > 100
                        else anot["texto"]
                    )

                    st.markdown(
                        f"""
                        <div style='padding: 10px; background-color: #f8f9fa; 
                                    border-left: 3px solid #667eea; border-radius: 5px; 
                                    margin-bottom: 10px;'>
                            <strong style='color: #667eea;'>
                                {anot['livro']} {anot['capitulo']}:{anot['versiculo']}
                            </strong>
                            {' | ' + ' '.join([f"<code>{tag}</code>" for tag in anot.get('tags', [])]) if anot.get('tags') else ''}
                            <br>
                            <span style='color: #666;'>{preview}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:
                    st.write("")
                    if st.button("👁️", key=f"view_{i}", help="Ver completo"):
                        st.session_state[f"mostrar_anot_{i}"] = not st.session_state.get(
                            f"mostrar_anot_{i}", False
                        )

                if st.session_state.get(f"mostrar_anot_{i}", False):
                    st.markdown("**Texto completo:**")
                    st.write(anot["texto"])
                    st.markdown("---")
    else:
        st.info(
            "📭 Você ainda não tem anotações. Comece criando uma na aba 'Nova Anotação'!"
        )

        if st.button("➕ Criar Primeira Anotação"):
            st.rerun()

# ========== TAB 3: BUSCAR ANOTAÇÕES ==========
with tab3:
    st.markdown("### 🔍 Buscar nas Anotações")

    col1, col2 = st.columns([3, 1])

    with col1:
        termo_busca = st.text_input(
            "Digite o que deseja buscar:",
            placeholder="Ex: oração, fé, promessa...",
            key="busca_anotacoes_input",
        )

    with col2:
        st.write("")
        st.write("")
        buscar_btn = st.button("🔍 Buscar", type="primary", use_container_width=True)

    if buscar_btn and termo_busca:
        resultados = buscar_anotacoes(termo_busca)

        if resultados:
            st.success(f"✅ {len(resultados)} anotação(ões) encontrada(s)")

            for i, anot in enumerate(resultados):
                with st.expander(
                    f"📖 {anot['livro']} {anot['capitulo']}:{anot['versiculo']}"
                ):
                    st.write(anot["texto"])

                    if anot.get("tags"):
                        st.markdown(f"🏷️ {', '.join(anot['tags'])}")
        else:
            st.warning("⚠️ Nenhuma anotação encontrada com esse termo.")

    st.markdown("---")
    st.markdown("### 🏷️ Tags Mais Usadas")

    stats = obter_estatisticas_anotacoes()
    if stats["tags_mais_usadas"]:
        cols = st.columns(5)
        for i, (tag, count) in enumerate(stats["tags_mais_usadas"]):
            with cols[i % 5]:
                if st.button(f"{tag} ({count})", key=f"tag_busca_{i}"):
                    # Salva a tag selecionada e recarrega para exibir resultados
                    st.session_state.tag_busca_sel = tag
                    st.rerun()

        # Se alguma tag foi selecionada, mostra as anotações logo abaixo
        if st.session_state.tag_busca_sel:
            st.markdown("---")
            st.markdown(
                f"### 📎 Anotações com a tag: `{st.session_state.tag_busca_sel}`"
            )

            anotacoes_tag = listar_anotacoes(
                filtro_tag=st.session_state.tag_busca_sel
            )

            if anotacoes_tag:
                for i, anot in enumerate(anotacoes_tag):
                    with st.expander(
                        f"📖 {anot['livro']} {anot['capitulo']}:{anot['versiculo']}"
                    ):
                        st.write(anot["texto"])
                        if anot.get("tags"):
                            st.markdown(f"🏷️ {', '.join(anot['tags'])}")
            else:
                st.info("Nenhuma anotação encontrada para essa tag.")
    else:
        st.info("Nenhuma tag usada ainda.")

# ========== TAB 4: GERENCIAR ==========
with tab4:
    st.markdown("### ⚙️ Gerenciar Anotações")

    stats = obter_estatisticas_anotacoes()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Anotações", stats["total"])

    with col2:
        st.metric("Tags Diferentes", stats["total_tags"])

    with col3:
        st.metric("Livro Mais Anotado", stats["livro_mais_anotado"])

    with col4:
        palavras_total = sum(len(a["texto"].split()) for a in listar_anotacoes())
        st.metric("Total de Palavras", palavras_total)

    st.markdown("---")
    st.markdown("#### 💾 Backup e Restauração")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📥 Exportar Anotações**")
        st.write("Faça backup de todas as suas anotações em JSON.")

        if st.button("📥 Gerar Backup", use_container_width=True):
            json_data = exportar_anotacoes_json()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            st.download_button(
                label="⬇️ Baixar Arquivo JSON",
                data=json_data,
                file_name=f"anotacoes_biblia_{timestamp}.json",
                mime="application/json",
                use_container_width=True,
            )

    with col2:
        st.markdown("**📤 Importar Anotações**")
        st.write("Restaure anotações de um backup JSON.")

        arquivo_upload = st.file_uploader(
            "Selecione o arquivo JSON:",
            type=["json"],
            key="upload_json_anot",
        )

        if arquivo_upload:
            if st.button("📤 Importar", use_container_width=True):
                try:
                    json_string = arquivo_upload.read().decode("utf-8")
                    if importar_anotacoes_json(json_string):
                        st.success("✅ Anotações importadas!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao importar.")
                except Exception as e:
                    st.error(f"❌ Erro: {e}")

    st.markdown("---")
    st.markdown("#### 🗑️ Gerenciamento em Massa")

    with st.expander("⚠️ Zona de Perigo"):
        st.warning("**Atenção:** Estas ações não podem ser desfeitas!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Excluir Todas as Anotações", use_container_width=True):
                st.session_state.confirmar_exclusao = True

        if st.session_state.get("confirmar_exclusao", False):
            st.error("⚠️ Tem certeza? Todas as anotações serão perdidas!")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Sim, excluir tudo"):
                    st.session_state.anotacoes = {}
                    st.session_state.confirmar_exclusao = False
                    st.success("Todas as anotações foram excluídas.")
                    st.rerun()

            with col2:
                if st.button("❌ Cancelar"):
                    st.session_state.confirmar_exclusao = False
                    st.rerun()

# Sidebar (resumo rápido)
with st.sidebar:
    st.markdown("### 📊 Resumo Rápido")

    stats = obter_estatisticas_anotacoes()
    st.metric("Anotações", stats["total"])
    st.metric("Tags", stats["total_tags"])

    st.markdown("---")
    st.markdown("### ⚡ Atalhos")

    if st.button("📖 Leitura", use_container_width=True):
        st.switch_page("pages/1_📖_Leitura.py")

    if st.button("🔍 Buscar", use_container_width=True):
        st.switch_page("pages/3_🔍+_Busca_Avançada.py")

conexao.close()
