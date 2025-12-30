import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

from crud import supabase,  listar_clientes, listar_todos_dados_clientes, incluir_cliente,excluir_cliente, alterar_cliente

st.info(f'### Clientes Cadastrados',icon=':material/thumb_up:')

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
        df = pd.DataFrame(clientes_paginados).copy()
        df["Selecionar"] = False
        df["id"] = df["id"].astype(str)

        resultado = st.data_editor(df,
                    # width= 'stretch', Somente na nova versão do streamlit
                    hide_index=True,
                    column_order=["Selecionar"] + [col for col in df.columns if col not in ("Selecionar", "id")],
                    column_config={
                                    "empresa": st.column_config.TextColumn("Empresa"),
                                    "cidade": st.column_config.TextColumn("Cidade"),
                                    "telefone": st.column_config.TextColumn("Telefone"),
                                    "contato": st.column_config.TextColumn("Contato"),
                                   },
                    # key="tabela_clientes",
                    num_rows="dynamic")


        selecionados = resultado[resultado["Selecionar"] == True]
        if not selecionados.empty:
            idx = selecionados.index[0]
            id_selecionado = clientes_paginados[idx]["id"]
            cliente_completo = next((c for c in listar_todos_dados_clientes() if c["id"] == id_selecionado), None)
            # print(cliente_completo)
            if cliente_completo:
                st.session_state.cliente_selecionado = cliente_completo
            if len(selecionados) > 1:
                st.error("Selecione apenas 1 registro por vez.")
                if st.button("Voltar"):
                    st.rerun()
            elif len(selecionados) == 1:
                idx = selecionados.index[0]
                id_sel = resultado.loc[idx, "id"]
                

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.pagina > 0:
            if st.button("⬅ Página anterior"):
                st.session_state.pagina -= 1
                st.rerun()
    with col2:
        if fim < total:
            if st.button("Próxima página ➡"):
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
        st.write(f"Deseja realmente excluir o cliente: {cliente['empresa']} Filial : {cliente['cidade']}?")
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
