import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

from crud import supabase,  listar_clientes, listar_todos_dados_clientes, incluir_cliente,excluir_cliente, alterar_cliente

st.info(f'### Clientes Cadastrados',icon=':material/groups:')

# Inicializa session_state
if "user" not in st.session_state:
    st.session_state.user = None
if "modo" not in st.session_state:
    st.session_state.modo = "login"
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "aba" not in st.session_state:
    st.session_state.aba = "Listar"
if "pagina" not in st.session_state:
    st.session_state.pagina = 0
if "busca_empresa" not in st.session_state:
    st.session_state.busca_empresa = ""
if "cliente_selecionado" not in st.session_state:
    st.session_state.cliente_selecionado = None

PAGE_SIZE = 10

if st.session_state.aba == "Listar":
    #st.subheader("Lista de Clientes")
    busca_atual = st.text_input("Buscar por empresa", st.session_state.busca_empresa)
    if busca_atual != st.session_state.busca_empresa:
        st.session_state.busca_empresa = busca_atual
        st.session_state.pagina = 0
        st.rerun()

    clientes = listar_clientes(filtro_empresa=st.session_state.busca_empresa)
    total = len(clientes)
    inicio = st.session_state.pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if clientes:
        clientes_paginados = clientes[inicio:fim]
        df_exibicao = pd.DataFrame(clientes_paginados).copy()
        
        # Adicionar coluna visual de seleção (vazia)
        df_exibicao["Selecionar"] = ""
        df_exibicao["id"] = df_exibicao["id"].astype(str)

        # Definir colunas para exibição
        cols_exibicao = ["Selecionar", "empresa", "cidade", "telefone", "contato"]

        # Configurar Grid
        selecao = st.dataframe(
            df_exibicao[cols_exibicao],
            hide_index=True,
            width='stretch',
            column_config={
                "Selecionar": st.column_config.TextColumn("Selecionar", help="Clique na linha para selecionar"),
                "empresa": st.column_config.TextColumn("Empresa"),
                "cidade": st.column_config.TextColumn("Cidade"),
                "telefone": st.column_config.TextColumn("Telefone"),
                "contato": st.column_config.TextColumn("Contato"),
            },
            selection_mode="single-row",
            on_select="rerun",
            key="grid_clientes"
        )

        # Lógica de Seleção
        indices_selecionados = selecao.get("selection", {}).get("rows", [])
        
        if indices_selecionados:
            idx_paginado = indices_selecionados[0]
            # O índice retornado é relativo à página exibida (0 a PAGE_SIZE-1)
            # Precisamos pegar o cliente correspondente na lista paginada
            if idx_paginado < len(clientes_paginados):
                cliente_selecionado_pag = clientes_paginados[idx_paginado]
                id_selecionado = cliente_selecionado_pag["id"]
                
                # Buscar dados completos (caso a lista inicial seja resumida)
                # O código original busca todos os dados apenas do selecionado
                cliente_completo = next((c for c in listar_todos_dados_clientes() if c["id"] == id_selecionado), None)
                
                if cliente_completo:
                    st.session_state.cliente_selecionado = cliente_completo
        else:
            # Se nada selecionado na grid, limpamos a seleção (opcional, mas bom pra consistência)
             st.session_state.cliente_selecionado = None

    # Controles de Navegação (Estilo proposta.py)
    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    # Ajuste para base 1 na visualização, mas mantendo base 0 no estado se preferir, 
    # ou migrando tudo para base 1.
    # O código original usava base 0 (inicio = st.session_state.pagina * PAGE_SIZE).
    # O código proposta.py usa base 1. 
    # Vamos manter base 0 no backend (session_state.pagina) para minimizar impacto no resto do código, 
    # mas exibir como Base 1.

    if col_pag1.button("⬅️", disabled=st.session_state.pagina <= 0):
        st.session_state.pagina -= 1
        st.rerun()

    col_pag2.write(f"Página {st.session_state.pagina + 1} de {total_paginas}")

    if col_pag3.button("➡️", disabled=(st.session_state.pagina + 1) >= total_paginas):
        st.session_state.pagina += 1
        st.rerun()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Listar"):
            st.session_state.aba = "Listar"
            st.rerun()
        if col2.button("Incluir"):
            st.session_state.aba = "Incluir"
            st.rerun()
        if col3.button("Alterar"):
            st.session_state.aba = "Alterar"
            st.rerun()
        if col4.button("Excluir"):
            st.session_state.aba = "Excluir"
            st.rerun()

elif st.session_state.aba == "Incluir":
    st.subheader("Incluir Novo Cliente")
    with st.form("form_incluir"):
        dados = {
            "empresa": st.text_input("Empresa").strip(),  # retira espaçoes da string
            "cnpj": st.text_input("CNPJ").strip(),
            "cep": st.text_input("CEP").strip(),
            "endereco": st.text_input("Endereço").strip(),
            "cidade": st.text_input("Cidade").strip(),
            "uf": st.text_input("UF").strip(),
            "contato": st.text_input("Contato").strip(),
            "departamento": st.text_input("Departamento").strip(),
            "telefone": st.text_input("Telefone").strip(),
            "mobile": st.text_input("Celular").strip(),
            "email": st.text_input("Email").strip(),
        }
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Incluir")
        with col2:    
            voltar_inc = st.form_submit_button("Voltar sem incluir")
        if submitted:
            try:
                incluir_cliente(dados)
                st.success("Cliente incluído com sucesso!")
            except ValueError as e:
                st.error(str(e))
            st.session_state.aba = "Listar"
            st.rerun()
        if voltar_inc:
                # print('Voltar sem incluir')
                st.session_state.aba = "Listar"
                st.rerun()        

elif st.session_state.aba == "Alterar":
    st.subheader("Alterar Cliente")
    clientes = listar_todos_dados_clientes()
    cliente = st.session_state.cliente_selecionado or (clientes[0] if clientes else None)

    if cliente:
        with st.form("form_alterar"):
            dados = {
                "empresa": st.text_input("Empresa", value=cliente.get("empresa", "")),
                "cnpj": st.text_input("CNPJ", value=cliente.get("cnpj", "")),
                "cep": st.text_input("CEP", value=cliente.get("cep", "")),
                "endereco": st.text_input("Endereço", value=cliente.get("endereco", "")),
                "cidade": st.text_input("Cidade", value=cliente.get("cidade", "")),
                "uf": st.text_input("UF", value=cliente.get("uf", "")),
                "contato": st.text_input("Contato", value=cliente.get("contato", "")),
                "departamento": st.text_input("Departamento", value=cliente.get("departamento", "")),
                "telefone": st.text_input("Telefone", value=cliente.get("telefone", "")),
                "mobile": st.text_input("Celular", value=cliente.get("mobile", "")),
                "email": st.text_input("Email", value=cliente.get("email", "")),
            }
            # print('id = ',cliente.get('id'),dados)
            col1, col2 = st.columns(2)
            with col1:
                submitted_alter = st.form_submit_button("Salvar Alterações")
            with col2:    
                voltar_alter = st.form_submit_button("Voltar sem Alterar")
          
            if submitted_alter:
                try:
                    alterar_cliente(cliente["id"], dados)
                    st.success("Cliente alterado com sucesso!")
                except ValueError as e:
                    st.error(str(e))
                st.session_state.aba = "Listar"   
                st.rerun() 
            if voltar_alter:
                st.session_state.aba = "Listar"
                st.rerun()        

elif st.session_state.aba == "Excluir":
    st.subheader("Excluir Cliente")
    clientes = listar_clientes()
    cliente = st.session_state.cliente_selecionado or (clientes[0] if clientes else None)

    if cliente:
        texto1 = "Deseja realmente excluir o cliente: "
        texto2 = f'{cliente['empresa']} 👉Filial : {cliente['cidade']}'
        st.success(f'##### :warning: ATENÇÃO !\n###### 👉 {texto1}\n###### 🟢 {texto2}')
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Excluir Cliente"):
                excluir_cliente(cliente["id"])
                st.success("Cliente excluído com sucesso!")
                st.session_state.cliente_selecionado = None
                st.session_state.aba = "Listar"
                st.rerun()
        with col2:
            if st.button("Voltar sem excluir"):
                st.session_state.aba = "Listar"
                st.rerun()
