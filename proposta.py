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


def preparar_dados_proposta(dados: dict) -> dict:
    """Retorna apenas os campos válidos para a tabela propostas."""
    campos_validos = {
        "id_cliente",
        "num_proposta",
        "status_rel_01",
        "local_realizacao",
        "dt_agendada_01",
        "dt_emissao_rel_01",
        "motivo_cancelamento",
        "data_emissao",
        "validade",
        "cond_pagamento",
        "referencia",
    }
    return {k: v for k, v in dados.items() if k in campos_validos}

# =========================================
# DADOS AUXILIARES
# =========================================
clientes = supabase.table("clientes").select("id, empresa, cidade, endereco, uf, cep, cnpj, telefone, email").order('empresa').execute().data
servicos = supabase.table("servicos").select("*").order('codigo').execute().data

map_clientes = {c["empresa"]: c["id"] for c in clientes}
map_servicos = {s["codigo"]: s for s in servicos}

combo_clientes = [f"{c['empresa']} - {c['cidade']}" for c in clientes]

# =========================================
# FUNÇÕES REUTILIZÁVEIS
# =========================================
def exibir_busca_servicos(key_suffix, on_add_callback):
    """
    Exibe a interface de busca, paginação e seleção de serviços.
    
    Args:
        key_suffix (str): Sufixo para as chaves dos widgets do Streamlit (ex: "_nova", "_edit").
        on_add_callback (func): Função callback chamada quando o usuário clica em "Adicionar Item".
                                Recebe um dicionário com os dados do item.
    """
    # 1) BUSCAR SERVIÇO (BUSCA GLOBAL)
    st.write("### 1. Buscar serviço")
    busca_codigo = st.text_input(
        "Digite qualquer parte do Código ou Descrição",
        placeholder="Ex: SAS, CAL, REP...",
        key=f"busca_codigo_servico{key_suffix}"
    )

    # Filtragem dos serviços
    if busca_codigo:
        servicos_filtrados = [
            s for s in servicos 
            if busca_codigo.lower() in s["codigo"].lower() or busca_codigo.lower() in s["descricao"].lower()
        ]
    else:
        servicos_filtrados = servicos

    # 2) LÓGICA DE PAGINAÇÃO
    servicos_por_pagina = 10
    key_pagina = f"pagina_serv{key_suffix}"
    
    if key_pagina not in st.session_state:
        st.session_state[key_pagina] = 1

    total_servicos = len(servicos_filtrados)
    total_paginas = max(1, (total_servicos + servicos_por_pagina - 1) // servicos_por_pagina)

    if st.session_state[key_pagina] > total_paginas:
        st.session_state[key_pagina] = 1

    inicio = (st.session_state[key_pagina] - 1) * servicos_por_pagina
    fim = inicio + servicos_por_pagina

    st.write(f"Mostrando códigos de {inicio + 1} a {min(fim, total_servicos)} do total de {total_servicos} registros")

    servicos_exibidos = servicos_filtrados[inicio:fim]

    # 3) GRID COM COLUNA "SELECIONAR"
    st.write("### 2. Lista de Serviços")

    if not servicos_exibidos:
        st.warning("Nenhum serviço encontrado.")
    else:
        df_exibicao = pd.DataFrame(servicos_exibidos)[["codigo", "descricao", "valor", "tipo"]]
        
        df_exibicao["valor_formatado"] = df_exibicao["valor"].apply(
            lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        df_exibicao["Selecionar"] = False
        
        cols = ["Selecionar", "codigo", "descricao", "valor_formatado", "tipo"]
        
        selecao = st.data_editor(
            df_exibicao[cols].reset_index(drop=True),
            hide_index=True,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar", help="Marque para selecionar"),
                "codigo": st.column_config.TextColumn("Código"),
                "descricao": st.column_config.TextColumn("Descrição"),
                "valor_formatado": st.column_config.TextColumn("Valor"),
                "tipo": st.column_config.TextColumn("Tipo"),
            },
            key=f"grid_servicos{key_suffix}"
        )

        # Controles de Navegação
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        
        if col_pag1.button("⬅️", key=f"pg_prev{key_suffix}", disabled=st.session_state[key_pagina] <= 1):
            st.session_state[key_pagina] -= 1
            st.rerun()

        col_pag2.write(f"Página {st.session_state[key_pagina]} de {total_paginas}")

        if col_pag3.button("➡️", key=f"pg_next{key_suffix}", disabled=st.session_state[key_pagina] >= total_paginas):
            st.session_state[key_pagina] += 1
            st.rerun()

        # 4, 5 e 6) LÓGICA DE SELEÇÃO E INPUTS
        selecionados = selecao[selecao["Selecionar"] == True]
        
        if len(selecionados) == 1:
            index = selecionados.index[0]
            serv_selecionado = servicos_exibidos[index]

            preco_servico = formatar_moeda_br(float(serv_selecionado['valor']))
            texto1 = f"{serv_selecionado['codigo']} :material/move_item: {serv_selecionado['descricao']}"
            texto2 = f"Valor : {preco_servico}"
            st.success(f'ITEM SELECIONADO \n###### :point_right: {texto1} \n###### :point_right: {texto2} ')

            col_prazo, col_qtd, col_desc = st.columns([1.3, 1, 1])
            
            prazo = col_prazo.text_input("Prazo (DDL)", key=f"item_prazo{key_suffix}", placeholder='Exemplo : 10 DDL')
            if prazo and prazo.strip() and 'DDL' not in prazo:
                prazo = prazo + ' DDL'

            qtd = col_qtd.number_input("Quantidade", min_value=1, step=1, format='%d', key=f"item_qtd{key_suffix}")
            desconto = col_desc.number_input("Desconto (%)", min_value=0, max_value=100, value=0, key=f"item_desconto{key_suffix}")
            
            if st.button("➕ Adicionar Item", key=f"btn_add_item{key_suffix}"):
                item_data = {
                    "id_servico": serv_selecionado["id_servico"],
                    "codigo_servico": serv_selecionado["codigo"],
                    "descricao_servico": serv_selecionado["descricao"],
                    "prazo_ddl": prazo,
                    "qtd": qtd,
                    "preco_unitario": float(serv_selecionado["valor"]),
                    "desconto": desconto
                }
                on_add_callback(item_data)
        elif len(selecionados) > 1:
            st.error("Selecione apenas 1 serviço por vez.")
        else:
            st.info("Marque a caixa na linha da tabela acima para selecionar o serviço.")


# =========================================
# ESTADO INICIAL
# =========================================
									 
if "itens_novos" not in st.session_state:
    st.session_state.itens_novos = []

#=========================================
# INTERFACE
# =========================================
# st.title("📄 Propostas Comerciais")
st.info("### Gerenciamento de Propostas Comerciais", icon=":material/amend:")

aba = st.tabs(["➕ Nova Proposta", "🔎 Editar Proposta / Gerar PDF"])

# =========================================
# ABA 1 – NOVA PROPOSTA
# =========================================    
with aba[0]:
    ultima_proposta = ler_last_proposta()
    proxima_proposta = gerar_proxima_proposta(ultima_proposta)
    st.subheader(f":orange[Proposta {proxima_proposta}]")

    ################## Etapa 1 - Identificação do Cliente  ##################
    st.markdown(':orange-background[Identificação do Cliente]')

    container_cliente = st.container(border=True)
    with container_cliente:
        cliente = st.selectbox("Empresa:", combo_clientes, index=0, key="nova_cliente")

        nome_empresa = cliente.split(' - ')[0].strip()
        cidade_sel = cliente.split(' - ')[1].strip()

        empresa_data = next((c for c in clientes if c['empresa'] == nome_empresa and c['cidade'] == cidade_sel), None)

        if empresa_data:
            col1, col2, col3 = st.columns(3)
            with col1:
                endereco = st.text_input('Endereço:', value=empresa_data['endereco'], disabled=True)
                cidade_input = st.text_input('Cidade:', value=empresa_data['cidade'], disabled=True)
            with col2:
                uf = st.text_input('UF:', value=empresa_data['uf'], disabled=True)
                tel = st.text_input('Telefone:', value=empresa_data['telefone'], disabled=True)
            with col3:
                cep = st.text_input('CEP:', value=empresa_data['cep'], disabled=True)
                email = st.text_input('E-mail:', value=empresa_data['email'], disabled=True)
                cnpj = st.text_input('CNPJ:', value=empresa_data['cnpj'], disabled=True)

        id_cliente = empresa_data['id'] if empresa_data else None

    ################## Detalhes da Proposta  ##################
    st.markdown(':orange-background[Detalhes da Proposta]')
    container_proposta = st.container(border=True)
    with container_proposta:
        opcoes = ['Pendente', 'Agendado', 'Cancelado']
        ajuda = '''
            🕗 Pendente: Aguardando pedido do cliente\n
            📅 Agendado: Preenchimento de dados não envolvidos com cálculos\n
            ❌ Cancelado: Relatório suspenso\n
        '''

        col_status, col_local = st.columns(2)
        with col_status:
            status_rel_01 = st.radio(
                'Status Atual',
                options=opcoes,
                index=1,
                horizontal=True,
                help=ajuda
            )

        with col_local:
            local_realizacao = st.radio(
                'Local de Realização dos serviços',
                options=['Interno', 'Externo'],
                format_func=lambda x: 'Laboratório Interno' if x == 'Interno' else 'Laboratório Externo',
                index=0,
                horizontal=True,
                key='nova_local_realizacao'
            )

        dt_agendada_01 = None
        dt_emissao_01 = None
        motivo_01 = ''

        col_data_1, col_data_2 = st.columns(2)
        with col_data_1:
            dt_agendada_01 = st.date_input(
                'Data Agendada',
                key='nova_dt_agendada_01',
                format='DD/MM/YYYY'
            )

        with col_data_2:
            dt_emissao_01 = st.date_input(
                'Data de emissão do Relatório Preliminar',
                key='nova_dt_emissao_01',
                format='DD/MM/YYYY'
            )

        col_emissao_prop, col_validade_prop = st.columns(2)
        with col_emissao_prop:
            data_emissao = st.date_input(
                'Data de Emissão da Proposta',
                value=date.today(),
                key='nova_data_emissao',
                format='DD/MM/YYYY'
            )

        with col_validade_prop:
            pass

        if status_rel_01 == 'Cancelado':
            motivo_01 = st.text_area(
                'Motivo do cancelamento:',
                placeholder='Digite o motivo do cancelamento',
                key='nova_motivo_01',
                height=120
            )

        col_validade, col_cond = st.columns(2)
        with col_validade:
            validade = st.text_input("Validade", placeholder="Exemplo : 15 DDL", key='nova_validade')
        with col_cond:
            cond_pagamento = st.text_input("Cond. Pagamento", placeholder="Exemplo : 30 DDL", key='nova_cond_pagamento')

    # Retirada a pedido do Leandro referencia = col5.text_input("Referência", key="nova_referencia")
    referencia = ''

    st.divider()
    st.subheader("Itens da Proposta")

    # Função callback para Nova Proposta
    def add_item_nova_proposta(item):
        st.session_state.itens_novos.append(item)
        st.rerun()

    exibir_busca_servicos(key_suffix="_nova", on_add_callback=add_item_nova_proposta)

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
            col6.write(f" {formatar_moeda_br(total_item)}")

            if col6.button("🗑", key=f"del_temp_{idx}"):
                st.session_state.itens_novos.pop(idx - 1)
                st.rerun()

    st.success(f"💰 Total parcial da proposta: {formatar_moeda_br(total_proposta)}")

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
        payload_proposta = preparar_dados_proposta({
            "id_cliente": id_cliente,
            "num_proposta": proxima_proposta,
            "status_rel_01": status_rel_01,
            "local_realizacao": local_realizacao,
            "data_emissao": data_emissao.isoformat(),
            "dt_agendada_01": dt_agendada_01.isoformat() if dt_agendada_01 else None,
            "dt_emissao_rel_01": dt_emissao_01.isoformat() if dt_emissao_01 else None,
            "motivo_cancelamento": motivo_01,
            "validade": validade,
            "cond_pagamento": cond_pagamento,
            "referencia": referencia
        })
        id_prop = criar_proposta(payload_proposta)

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

    if "edit_data_emissao" not in st.session_state:
        st.session_state.edit_data_emissao = date.today()
    if "edit_referencia" not in st.session_state:
        st.session_state.edit_referencia = ""
    if "edit_validade" not in st.session_state:
        st.session_state.edit_validade = ""
    if "edit_cond_pagamento" not in st.session_state:
        st.session_state.edit_cond_pagamento = ""
    if "edit_status_rel_01" not in st.session_state:
        st.session_state.edit_status_rel_01 = "Agendado"
    if "edit_local_realizacao" not in st.session_state:
        st.session_state.edit_local_realizacao = "Interno"
    if "edit_dt_agendada_01" not in st.session_state:
        st.session_state.edit_dt_agendada_01 = date.today()
    if "edit_dt_emissao_rel_01" not in st.session_state:
        st.session_state.edit_dt_emissao_rel_01 = date.today()
    if "edit_motivo_cancelamento" not in st.session_state:
        st.session_state.edit_motivo_cancelamento = ""

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
            pdf_bytes = None
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

            except UnauthorizedAccess:
                st.error("Erro de API: Chave do CloudConvert inválida ou e-mail não verificado.", icon="🚨")
                erro = True
            except Exception as e:
                st.error(f"Erro Inesperado: {str(e)}", icon="🚨")
                erro = True
            finally:
                if temp_docx and os.path.exists(temp_docx):
                    if not erro:
                        os.remove(temp_docx)

            if not erro and pdf_bytes is not None:
                st.download_button(
                    label="Clique aqui para baixar o PDF",
                    data=pdf_bytes,
                    file_name=f"Proposta_{proposta_name}.pdf",
                    mime="application/pdf"
                )
            elif erro and temp_docx and os.path.exists(temp_docx):
                st.warning(
                    f'Baixe o arquivo Proposta_{proposta_name}.docx e faça a conversão para PDF no site : https://cloudconvert.com/'
                )
                with open(temp_docx, "rb") as file:
                    st.download_button(
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
    st.markdown(':orange-background[Detalhes da Proposta]')
    
    # Garantir que os dados estão sempre carregados da proposta selecionada
    if st.session_state.edit_id_proposta != proposta_sel["id_proposta"]:
        st.session_state.edit_id_proposta = proposta_sel["id_proposta"]
        st.session_state.edit_mode = False

        # Carregar dados da proposta para os campos de edição
        try:
            st.session_state.edit_data_emissao = (
                datetime.strptime(proposta_sel["data_emissao"], "%Y-%m-%d").date()
                if proposta_sel.get("data_emissao") else date.today()
            )
        except (ValueError, TypeError):
            st.session_state.edit_data_emissao = date.today()

        st.session_state.edit_referencia = proposta_sel.get("referencia", "") or ""
        st.session_state.edit_validade = proposta_sel.get("validade", "") or ""
        st.session_state.edit_cond_pagamento = proposta_sel.get("cond_pagamento", "") or ""
        status_atual = proposta_sel.get("status_rel_01", "Agendado") or "Agendado"
        if status_atual not in ["Pendente", "Agendado", "Cancelado"]:
            status_atual = "Agendado"
        st.session_state.edit_status_rel_01 = status_atual
        st.session_state.edit_local_realizacao = proposta_sel.get("local_realizacao", "Interno") or "Interno"
        
        try:
            st.session_state.edit_dt_agendada_01 = (
                datetime.strptime(proposta_sel["dt_agendada_01"], "%Y-%m-%d").date()
                if proposta_sel.get("dt_agendada_01") else date.today()
            )
        except (ValueError, TypeError):
            st.session_state.edit_dt_agendada_01 = date.today()
        
        try:
            st.session_state.edit_dt_emissao_rel_01 = (
                datetime.strptime(proposta_sel["dt_emissao_rel_01"], "%Y-%m-%d").date()
                if proposta_sel.get("dt_emissao_rel_01") else date.today()
            )
        except (ValueError, TypeError):
            st.session_state.edit_dt_emissao_rel_01 = date.today()
        
        st.session_state.edit_motivo_cancelamento = proposta_sel.get("motivo_cancelamento", "") or ""

    container_edit = st.container(border=True)
    with container_edit:
        opcoes_status = ['Pendente', 'Agendado', 'Cancelado']
        
        col_status_edit, col_local_edit = st.columns(2)
        with col_status_edit:
            nova_status = st.radio(
                'Status Atual',
                options=opcoes_status,
                horizontal=True,
                key='edit_status_rel_01',
                disabled=not st.session_state.edit_mode
            )
        
        with col_local_edit:
            nova_local = st.radio(
                'Local de Realização dos serviços',
                options=['Interno', 'Externo'],
                format_func=lambda x: 'Laboratório Interno' if x == 'Interno' else 'Laboratório Externo',
                horizontal=True,
                key='edit_local_realizacao',
                disabled=not st.session_state.edit_mode
            )
        
        col_data_1_edit, col_data_2_edit = st.columns(2)
        with col_data_1_edit:
            nova_dt_agendada = st.date_input(
                'Data Agendada',
                value=st.session_state.edit_dt_agendada_01,
                key='edit_dt_agendada_01',
                format='DD/MM/YYYY',
                disabled=not st.session_state.edit_mode
            )
        
        with col_data_2_edit:
            nova_dt_emissao_rel = st.date_input(
                'Data de emissão do Relatório Preliminar',
                value=st.session_state.edit_dt_emissao_rel_01,
                key='edit_dt_emissao_rel_01',
                format='DD/MM/YYYY',
                disabled=not st.session_state.edit_mode
            )
        
        if nova_status == 'Cancelado':
            nova_motivo = st.text_area(
                'Motivo do cancelamento:',
                placeholder='Digite o motivo do cancelamento',
                value=st.session_state.edit_motivo_cancelamento,
                key='edit_motivo_cancelamento',
                height=120,
                disabled=not st.session_state.edit_mode
            )
        else:
            nova_motivo = st.session_state.edit_motivo_cancelamento
        
        col1, col2, col3 = st.columns(3)
        nova_data_emissao = col1.date_input(
            "Data de Emissão",
            key="edit_data_emissao",
            format="DD/MM/YYYY",
            disabled=not st.session_state.edit_mode
        )

        # Retirada a pedido do Leandro
        # nova_ref = st.text_input(
        #     "Referência",
        #     key="edit_referencia",
        #     disabled=not st.session_state.edit_mode
        # )
        nova_ref = ''

        nova_validade = col2.text_input(
            "Validade",
            key="edit_validade",
            disabled=not st.session_state.edit_mode
        )

        nova_cond = col3.text_input(
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
            payload_proposta = preparar_dados_proposta({
                "status_rel_01": nova_status,
                "local_realizacao": nova_local,
                "data_emissao": nova_data_emissao.isoformat(),
                "dt_agendada_01": nova_dt_agendada.isoformat() if nova_dt_agendada else None,
                "dt_emissao_rel_01": nova_dt_emissao_rel.isoformat() if nova_dt_emissao_rel else None,
                "motivo_cancelamento": nova_motivo,
                "referencia": nova_ref,
                "validade": nova_validade,
                "cond_pagamento": nova_cond
            })
            atualizar_proposta(id_prop, payload_proposta)
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

                st.write(f"💰 Total do item:  {formatar_moeda_br(total_item)}")

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
    if st.session_state.edit_mode:
        if "edit_adding_item" not in st.session_state:
            st.session_state.edit_adding_item = False

        if not st.session_state.edit_adding_item:
            col_newitem, col_del1, col_back1 = st.columns([1,1,1])

            if col_newitem.button("➕ Acrecentar Item na Proposta", key="edit_btn_newitem"):
                st.session_state.edit_adding_item = True
                st.rerun()
        else:
            st.divider()
            st.subheader("Adicionar Novo Item")
            
            def add_item_edit_proposta(item):
                # Remover chaves que não existem na tabela itens_proposta se necessário
                # Mas o crud.adicionar_item espera chaves compatíveis. 
                # O dicionário 'item' tem: id_servico, codigo_servico, descricao_servico, prazo_ddl, qtd, preco_unitario, desconto
                
                adicionar_item(id_prop, item)
                st.success("Item adicionado com sucesso!")
                st.session_state.edit_adding_item = False
                st.rerun()

            exibir_busca_servicos(key_suffix="_edit", on_add_callback=add_item_edit_proposta)
            
            if st.button("Cancelar Adição", key="btn_cancel_add_item"):
                 st.session_state.edit_adding_item = False
                 st.rerun()
    st.info(f"💰 Total da Proposta:  {formatar_moeda_br(total)}")

