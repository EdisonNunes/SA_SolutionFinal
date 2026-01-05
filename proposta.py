import streamlit as st
# from crud import supabase,criar_proposta,atualizar_proposta,excluir_proposta,buscar_propostas,adicionar_item,buscar_itens,atualizar_item,excluir_item
from crud import *
from utils import formatar_moeda_br
from datetime import date, datetime
from maladireta import gerar_documento_word
from converte import converter_docx_para_pdf, converter_para_pdf
import tempfile
import pandas as pd
from cloudconvert.exceptions.exceptions import UnauthorizedAccess, ConnectionError
import os

CLOUDCONVERT_API_KEY = st.secrets["cloudconvert"]["CLOUDCONVERT_API_KEY"]

def proposta_existe(num_proposta: str) -> bool:
    if not num_proposta:
        return True
    res = (
        supabase.table("propostas")
        .select("id_proposta")
        .eq("num_proposta", num_proposta)
        .execute()
    )
    return len(res.data) > 0

def calcular_total_item(qtd, preco, desconto_pct):
    return (qtd * preco) - (preco * desconto_pct / 100)

def gerar_proxima_proposta(last_proposta: str) -> str:
    # Obter o ano atual do sistema
    ano_atual = date.today().year
    
    try:
        # Extrair o ano (YYYY) e o sequencial (NNN)
        ano_lido = int(last_proposta[2:6])
        sequencial_lido = int(last_proposta[6:])
        
        if ano_atual == ano_lido:
            # Incrementa se for o mesmo ano
            novo_sequencial = sequencial_lido + 1
            return f"C-{ano_atual}{novo_sequencial:03d}"
        else:
            # Reinicia se o ano mudou
            return f"C-{ano_atual}001"
            
    except (ValueError, IndexError):
        # Fallback para formato inválido
        return f"C-{ano_atual}001"

# =========================================
# DADOS AUXILIARES
# =========================================
clientes = supabase.table("clientes").select("id, empresa").order('empresa').execute().data
servicos = supabase.table("servicos").select("*").order('codigo').execute().data

map_clientes = {c["empresa"]: c["id"] for c in clientes}
map_servicos = {s["codigo"]: s for s in servicos}

# =========================================
# ESTADO INICIAL
# =========================================
									 
if "itens_novos" not in st.session_state:
    st.session_state.itens_novos = []

#=========================================
# INTERFACE
# =========================================
st.title("📄 Propostas Comerciais")

aba = st.tabs(["➕ Nova Proposta", "🔎 Editar Proposta / Gerar PDF"])

# =========================================
# ABA 1 – NOVA PROPOSTA
# =========================================    
with aba[0]:
    ultima_proposta = ler_last_proposta()
    proxima_proposta = gerar_proxima_proposta(ultima_proposta)
    st.subheader(f":orange[Proposta {proxima_proposta}]")
    col1, col2, col3 = st.columns(3)

			  
    empresa = col1.selectbox("Cliente", map_clientes.keys(), key="nova_cliente")
    id_cliente = map_clientes[empresa]

    data_emissao = col2.date_input("Data de Emissão", value=date.today(), key="nova_data_emissao", format="DD/MM/YYYY")
    validade = col3.text_input("Validade", placeholder="Exemplo : 15 DDL", key='nova_validade')
    
    col4, col5, col6 = st.columns(3)
    
    cond_pagamento = col4.text_input("Cond. Pagamento", placeholder="Exemplo : 30 DDL", key='nova_cond_pagamento')
    referencia = col5.text_input("Referência", key="nova_referencia")

    st.divider()
    st.subheader("Itens da Proposta")

    # -------------------------------------------------------------
    # 1) BUSCAR SERVIÇO (BUSCA GLOBAL)
    # -------------------------------------------------------------
    st.write("### 1. Buscar serviço")
    busca_codigo = st.text_input(
        "Digite qualquer parte do Código ou Descrição",
        placeholder="Ex: SAS, CAL, REP...",
        key="nova_busca_codigo_servico"
    )

    # Filtragem dos serviços com base na busca (Busca em todos os serviços)
    if busca_codigo:
        servicos_filtrados = [
            s for s in servicos 
            if busca_codigo.lower() in s["codigo"].lower() or busca_codigo.lower() in s["descricao"].lower()
        ]
    else:
        servicos_filtrados = servicos

    # -------------------------------------------------------------
    # 2) LÓGICA DE PAGINAÇÃO (Aplicada sobre os resultados filtrados)
    # -------------------------------------------------------------
    servicos_por_pagina = 10
    if "pagina_serv_nova" not in st.session_state:
        st.session_state.pagina_serv_nova = 1

    total_servicos = len(servicos_filtrados)
    total_paginas = max(1, (total_servicos + servicos_por_pagina - 1) // servicos_por_pagina)

    # Resetar para página 1 se a busca reduzir o número de páginas
    if st.session_state.pagina_serv_nova > total_paginas:
        st.session_state.pagina_serv_nova = 1

    inicio = (st.session_state.pagina_serv_nova - 1) * servicos_por_pagina
    fim = inicio + servicos_por_pagina

    st.write(f"Mostrando códigos de {inicio + 1} a {min(fim, total_servicos)} do total de {total_servicos} registros")

    # Fatiar a lista filtrada para exibição na página atual
    servicos_exibidos = servicos_filtrados[inicio:fim]

    # -------------------------------------------------------------
    # 3) GRID COM COLUNA "SELECIONAR"
    # -------------------------------------------------------------
    st.write("### 2. Lista de Serviços")

    if not servicos_exibidos:
        st.warning("Nenhum serviço encontrado.")
    else:
        # Criando o DataFrame para exibição
        df_exibicao = pd.DataFrame(servicos_exibidos)[["codigo", "descricao", "valor", "tipo"]]
        
        # Formatação do valor para exibição
        df_exibicao["valor_formatado"] = df_exibicao["valor"].apply(
            lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        # Adicionando a coluna visual "Selecionar"
        #df_exibicao["Selecionar"] = "🔘"
        df_exibicao["Selecionar"] = ""
        
        cols = ["Selecionar", "codigo", "descricao", "valor_formatado", "tipo"]
        
        # Exibição do Grid
        selecao = st.dataframe(
            df_exibicao[cols],
            hide_index=True,
            width='content',
            column_config={
                "Selecionar": st.column_config.TextColumn("Selecionar", help="Clique na linha para selecionar"),
                "codigo": st.column_config.TextColumn("Código"),
                "descricao": st.column_config.TextColumn("Descrição"),
                "valor_formatado": st.column_config.TextColumn("Valor(R$)"),
                "tipo": st.column_config.TextColumn("Tipo"),
            },
            selection_mode="single-row",
            on_select="rerun"
        )

        # Controles de Navegação da Paginação
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        
        if col_pag1.button("⬅️", key="nova_pg_prev", disabled=st.session_state.pagina_serv_nova <= 1):
            st.session_state.pagina_serv_nova -= 1
            st.rerun()

        col_pag2.write(f"Página {st.session_state.pagina_serv_nova} de {total_paginas}")

        if col_pag3.button("➡️", key="nova_pg_next", disabled=st.session_state.pagina_serv_nova >= total_paginas):
            st.session_state.pagina_serv_nova += 1
            st.rerun()

        # -------------------------------------------------------------
        # 4, 5 e 6) LÓGICA DE SELEÇÃO E INPUTS
        # -------------------------------------------------------------
        indices_selecionados = selecao.get("selection", {}).get("rows", [])
        
        if indices_selecionados:
            index = indices_selecionados[0]
            # Importante: buscar no 'servicos_exibidos' pois o índice do grid refere-se à página atual
            serv_selecionado = servicos_exibidos[index]

            # Formatação do valor para exibição
            preco_servico = formatar_moeda_br(float(serv_selecionado['valor']))
            texto1 = f'{serv_selecionado['codigo']} :material/move_item: {serv_selecionado['descricao']}'
            texto2 = f'Valor : R$ {preco_servico}'
            st.success(f'ITEM SELECIONADO \n###### :point_right: {texto1} \n###### :point_right: {texto2} ')



            col_prazo, col_qtd, col_desc = st.columns([1.3, 1, 1])
            
            prazo = col_prazo.text_input("Prazo (DDL)", key="novo_item_prazo", placeholder='Exemplo : 10 DDL')
            if prazo and prazo.strip() and 'DDL' not in prazo:
                prazo = prazo + ' DDL'

            
            qtd = col_qtd.number_input("Quantidade", min_value=1, step=1, format='%d', key="novo_item_qtd")
            desconto = col_desc.number_input("Desconto (%)", min_value=0, max_value=100, value=0, key="novo_item_desconto")
            
            if st.button("➕ Adicionar Item", key="btn_add_item"):
                st.session_state.itens_novos.append({
                    "id_servico": serv_selecionado["id_servico"],
                    "codigo_servico": serv_selecionado["codigo"],
                    "descricao_servico": serv_selecionado["descricao"],
                    "prazo_ddl": prazo,
                    "qtd": qtd,
                    "preco_unitario": float(serv_selecionado["valor"]),
                    "desconto": desconto
                })
                st.rerun()
        else:
            st.info("Clique em uma linha da tabela acima para selecionar o serviço.")

    # ==============================
    # VISUALIZAÇÃO DOS ITENS
    # ==============================
    st.divider()
    st.subheader("📋 Itens adicionados")

    total_proposta = 0

    if not st.session_state.itens_novos:
        st.info("Nenhum item adicionado ainda.")
    else:
        for idx, item in enumerate(st.session_state.itens_novos, start=1):
            total_item = calcular_total_item(
                item["qtd"], 
                item["preco_unitario"],  
                item["desconto"]
                )

            total_proposta += total_item

            col1, col2, col3, col4, col5, col6 = st.columns(
                [0.2, 0.8, 2.2, 0.4, 0.2, 0.7])

            col1.write(str(idx))
            col2.write(item["codigo_servico"])
            col3.write(item["descricao_servico"])
            col4.write(item["prazo_ddl"])
            col5.write(str(item["qtd"]))
            col6.write(f"R$ {formatar_moeda_br(total_item)}")

            if col6.button("🗑", key=f"del_temp_{idx}"):
                st.session_state.itens_novos.pop(idx - 1)
                st.rerun()

    st.success(f"💰 Total parcial da proposta: R$ {formatar_moeda_br(total_proposta)}")

    if st.button("💾 Salvar Proposta", key="btn_salvar_proposta"):
        # =========================
        # Validações
        # =========================
        if not proxima_proposta.strip():
            st.error("❌ O número da proposta deve ser informado.")
            st.stop()

        if proposta_existe(proxima_proposta.strip()):
            st.error(f"❌ Já existe uma proposta com o número '{proxima_proposta}'.")
            st.stop()

        if not st.session_state.itens_novos:
            st.error("❌ A proposta deve conter pelo menos um item.")
            st.stop()

        if validade and validade.strip() and 'DDL' not in validade:
            validade = validade + ' DDL'
    
        if cond_pagamento and cond_pagamento.strip() and 'DDL' not in cond_pagamento:
            cond_pagamento = cond_pagamento + ' DDL'

        # =========================
        # Criar proposta
        # =========================
        id_prop = criar_proposta({
            "id_cliente": id_cliente,
            "num_proposta": proxima_proposta,
            "data_emissao": data_emissao.isoformat(), # ✅ YYYY-MM-DD
            "validade": validade,
            "cond_pagamento": cond_pagamento,
            "referencia": referencia
        })

        for item in st.session_state.itens_novos:
            adicionar_item(id_prop, item)

        atualizar_last_proposta(proxima_proposta)   # Atualiza número da proposta na tabela

        num_proposta = ''
        validade = ''
        cond_pagamento = ''
        referencia = ''
        st.success(f"✅ Proposta criada com ID {id_prop}")
        st.session_state.itens_novos = []
        st.rerun()

# =========================================
# ABA 2 – BUSCAR / EDITAR PROPOSTA
# =========================================
with aba[1]:
    ####### st.subheader("Buscar Proposta")

    # -------------------------------
    # ESTADOS
    # -------------------------------
    if "edit_id_proposta" not in st.session_state:
        st.session_state.edit_id_proposta = None

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    # -------------------------------
    # BUSCA
    # -------------------------------
    # filtro = st.text_input(
    #     "Buscar por Nº da Proposta",
    #     key="busca_num_proposta"
    # )
    filtro = ''
    propostas = buscar_propostas(filtro)

    if not propostas:
        st.warning("Nenhuma proposta encontrada.")
        st.stop()

    # -------------------------------
    # SELEÇÃO DA PROPOSTA
    # -------------------------------
    proposta_sel = st.selectbox(
        "Selecione a proposta",
        propostas,
        format_func=lambda x: f"{x['num_proposta']}  👉  {x['empresa']}",
        key="busca_select_proposta"
    )

    # -------------------------------
    # DETECTA TROCA DE PROPOSTA
    # -------------------------------
    if st.session_state.edit_id_proposta != proposta_sel["id_proposta"]:
        st.session_state.edit_id_proposta = proposta_sel["id_proposta"]
        st.session_state.edit_mode = False  # volta para leitura

        st.session_state.edit_data_emissao = (
            datetime.strptime(proposta_sel["data_emissao"], "%Y-%m-%d").date()
            if proposta_sel["data_emissao"]
            else date.today()
        )

        st.session_state.edit_referencia = proposta_sel.get("referencia", "")
        st.session_state.edit_validade = proposta_sel.get("validade", "")
        st.session_state.edit_cond_pagamento = proposta_sel.get("cond_pagamento", "")

    id_prop = proposta_sel["id_proposta"]
    num_proposta = proposta_sel["num_proposta"]
    st.divider()
    st.subheader("Dados da Proposta")

    # -------------------------------
    # BOTÃO MODO EDIÇÃO
    # -------------------------------
    col_btn1, col_btn2 = st.columns([1, 4])

    if not st.session_state.edit_mode:
        if col_btn1.button("✏️ Editar Proposta", key="btn_ativar_edicao"):
            st.session_state.edit_mode = True
            st.rerun()
    else:
        col_btn1.success("📝 Editando...")


    # -----------------------------------
    # BOTÃO GERAR WORD
    # -----------------------------------
    if not st.session_state.edit_mode:
        texto_help = f'Gera PDF da proposta {num_proposta}'
        if col_btn2.button("📄 Gerar PDF", key="btn_word", help=texto_help):    
            erro = False
            temp_docx = None
            proposta_name = f'Proposta_{num_proposta}'
            try: 
               # 1. Gerar DOCX temporário  
               with st.spinner('Gerando documento ...', show_time=True):
                    temp_docx, proposta_name = gerar_documento_word(supabase=supabase,
                                        id_proposta= id_prop,
                                        caminho_template='matriz.docx',
                                        caminho_saida=num_proposta
                                        )
                    # 2. Converter para PDF 
                    #print("Convertendo para PDF via CloudConvert...")
                    pdf_bytes = converter_para_pdf(temp_docx)

                # 3. Disponibilizar para Download
                    st.download_button(
                        label="Clique aqui para baixar o PDF",
                        data=pdf_bytes,
                        file_name=f"Proposta_{proposta_name}.pdf",
                        mime="application/pdf"
                    )

            except UnauthorizedAccess:
                st.error("Erro de API: Chave do CloudConvert inválida ou e-mail não verificado.", icon="🚨")
                erro = True
            except Exception as e:
                st.error(f"Erro Inesperado: {str(e)}", icon="🚨")
                erro = True
            finally:
                # 4. Tratamento dos arquivos temporários
                if temp_docx and os.path.exists(temp_docx):
                    if not erro:
                        # Se deu tudo certo, apaga o Word
                        os.remove(temp_docx)
                    else:
                        # Se houve erro, oferece o download do WORD como alternativa
                       st.warning(f'Baixe o arquivo Proposta_{proposta_name}.docx e faça a conversão para PDF no site : https://cloudconvert.com/ ')
                       with open(temp_docx, "rb") as file:
                            btn_docx = st.download_button(
                                label=f"📥 Baixar  Proposta_{proposta_name}.docx",
                                data=file,
                                file_name=f"Proposta_{proposta_name}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
    else:            
        col_btn2.button("📄 Gerar PDF", key="btn_word_disabled", disabled=True)        
    # -------------------------------
    # CAMPOS DA PROPOSTA
    # -------------------------------
    nova_data_emissao = st.date_input(
        "Data de Emissão",
        key="edit_data_emissao",
        format="DD/MM/YYYY",
        disabled=not st.session_state.edit_mode
    )

    nova_ref = st.text_input(
        "Referência",
        key="edit_referencia",
        disabled=not st.session_state.edit_mode
    )

    nova_validade = st.text_input(
        "Validade",
        key="edit_validade",
        disabled=not st.session_state.edit_mode
    )

    nova_cond = st.text_input(
        "Cond. Pagamento",
        key="edit_cond_pagamento",
        disabled=not st.session_state.edit_mode
    )

    # -------------------------------
    # AÇÕES DA PROPOSTA
    # -------------------------------
    if st.session_state.edit_mode:
        col_save, col_del, col_back = st.columns([1,1,1])

        if col_save.button("💾 Salvar Alterações", key="edit_btn_salvar"):
            atualizar_proposta(id_prop, {
                "data_emissao": nova_data_emissao.isoformat(),
                "referencia": nova_ref,
                "validade": nova_validade,
                "cond_pagamento": nova_cond
            })
            st.success("✅ Proposta atualizada")
            st.session_state.edit_mode = False
            st.rerun()

        if col_del.button("❌ Excluir Proposta", key="edit_btn_del_prop"):
            excluir_proposta(id_prop)
            st.error("❌ Proposta excluída")
            st.session_state.edit_id_proposta = None
            st.session_state.edit_mode = False
            st.rerun()
        if col_back.button("↩️ Voltar sem Alterar", key="edit_btn_voltar"):
            st.session_state.edit_mode = False
            st.rerun()    

    # =========================
    # ITENS DA PROPOSTA
    # =========================
    st.divider()
    st.subheader("Itens da Proposta")

    itens = buscar_itens(id_prop)
    total = 0

    if not itens:
        st.info("Nenhum item nesta proposta.")
    else:
        for item in itens:
            total_item = (
                item["qtd"] * item["preco_unitario"]
                - (item["preco_unitario"] * item["desconto"] / 100)
            )

            total += total_item

            with st.expander(f"{item['codigo_servico']}"):
                st.write(item["descricao_servico"])

                qtd = st.number_input(
                    "Qtd",
                    value=float(item["qtd"]),
                    key=f"edit_qtd_{item['id_item_prop']}",
                    disabled=not st.session_state.edit_mode
                )

                desconto = st.number_input(
                    "Desconto (%)",
                    value=float(item["desconto"]),
                    key=f"edit_desc_{item['id_item_prop']}",
                    disabled=not st.session_state.edit_mode
                )

                st.write(f"💰 Total do item: R$ {formatar_moeda_br(total_item)}")

                if st.session_state.edit_mode:
                    col_i1, col_i2 = st.columns(2)

                    if col_i1.button(
                        "💾 Atualizar Item",
                        key=f"edit_btn_item_{item['id_item_prop']}"
                    ):
                        atualizar_item(item["id_item_prop"], {
                            "qtd": qtd,
                            "desconto": desconto
                        })
                        st.success("Item atualizado")
                        st.rerun()

                    if col_i2.button(
                        "🗑 Excluir Item",
                        key=f"edit_btn_del_{item['id_item_prop']}"
                    ):
                        excluir_item(item["id_item_prop"])
                        st.warning("Item excluído")
                        st.rerun()

    st.info(f"💰 Total da Proposta: R$ {formatar_moeda_br(total)}")

