import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

from crud import supabase, listar_servicos,listar_todos_dados_servicos,incluir_servico,alterar_servico,excluir_servico

st.info(f'### Serviços Cadastrados',icon=':material/add_shopping_cart:')

if "aba" not in st.session_state:
    st.session_state.aba = "Listar"
if "pagina" not in st.session_state:
    st.session_state.pagina = 0
if "busca_descricao" not in st.session_state:
    st.session_state.busca_descricao = ""
if "servico_selecionado" not in st.session_state:
    st.session_state.servico_selecionado = None

PAGE_SIZE = 10

if st.session_state.aba == "Listar":
    busca_atual = st.text_input("Buscar por descrição do serviço", st.session_state.busca_descricao)
    if busca_atual != st.session_state.busca_descricao:
        st.session_state.busca_descricao = busca_atual
        st.session_state.pagina = 0
        st.rerun()

    servicos = listar_servicos(filtro_empresa=st.session_state.busca_descricao)
    total = len(servicos)
    inicio = st.session_state.pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE
    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    if servicos:
        servicos_paginados = servicos[inicio:fim]
        df = pd.DataFrame(servicos_paginados).copy()
        df["Selecionar"] = False
        df["id_servico"] = df["id_servico"].astype(str)

        resultado = st.data_editor(df,
                    # width= 'stretch', Somente na nova versão do streamlit
                    hide_index=True,
                    column_order=["Selecionar"] + [col for col in df.columns if col not in ("Selecionar", "id_servico")],
                    column_config={
                                        "descricao": st.column_config.TextColumn("Descrição"),
                                        "valor": st.column_config.NumberColumn("Valor(R$)", format='%.2f'),
                                   },
                    # key="tabela_servicos",
                    num_rows="dynamic")


        selecionados = resultado[resultado["Selecionar"] == True]
        if not selecionados.empty:
            idx = selecionados.index[0]
            id_selecionado = servicos_paginados[idx]["id_servico"]
            servico_completo = next((c for c in listar_todos_dados_servicos() if c["id_servico"] == id_selecionado), None)
            # print(servico_completo)
            if servico_completo:
                st.session_state.servico_selecionado = servico_completo
            if len(selecionados) > 1:
                st.error("Selecione apenas 1 registro por vez.")
                if st.button("Voltar"):
                    st.rerun()
            elif len(selecionados) == 1:
                idx = selecionados.index[0]
                id_sel = resultado.loc[idx, "id_servico"]
                

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
    st.subheader("Incluir Novo Serviço")
    with st.form("form_incluir"):
        dados = {
            "descricao": st.text_input("Descricao").strip(),  # retira espaçoes da string
            "ref": st.text_input("Referencia").strip(),
            #"valor": st.text_input("Valor em R$").strip(),
            "valor": st.number_input("Valor em R$", value=0.00, format= '%.2f', step=100.00),
            "codigo": st.text_input("Código").strip(),
            "codigo_raiz": st.text_input("Código Raiz").strip(),
            #"tipo": st.text_input("Tipo").strip(),
            "tipo": st.selectbox("Tipo", index= 0, options=['Serviço','Produto']),
        }
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Incluir")
        with col2:    
            voltar_inc = st.form_submit_button("Voltar sem incluir")
        if submitted:
            try:
                incluir_servico(dados)
                st.success("Serviço incluído com sucesso!")
            except ValueError as e:
                st.error(str(e))
            st.session_state.aba = "Listar"
            st.rerun()
        if voltar_inc:
                # print('Voltar sem incluir')
                st.session_state.aba = "Listar"
                st.rerun()        

elif st.session_state.aba == "Alterar":
    st.subheader("Alterar Serviço")
    servicos = listar_todos_dados_servicos()
    servico = st.session_state.servico_selecionado or (servicos[0] if servicos else None)

    if servico:
        with st.form("form_alterar"):
            if servico.get('tipo') == 'Serviço':
                tipo_servico = 0,
            else: 
                tipo_servico = 1
            dados = {
                "descricao": st.text_input("Descricao", value=servico.get("descricao", "")),
                "ref": st.text_input("Referencia", value=servico.get("ref", "")),
                #"valor": st.text_input("Valor em R$", value=servico.get("valor", "")),
                "valor": st.number_input("Valor em R$", value=servico.get("valor", ""), format= '%.2f', step=100.0),
                "codigo": st.text_input("Código", value=servico.get("codigo", "")),
                "codigo_raiz": st.text_input("Código Raiz", value=servico.get("codigo_raiz", "")),
                #"tipo": st.text_input("Tipo", value=servico.get("tipo", "")),
                "tipo": st.selectbox("Tipo", index=tipo_servico, options=['Serviço','Produto']),
            }
            
            col1, col2 = st.columns(2)
            with col1:
                submitted_alter = st.form_submit_button("Salvar Alterações")
            with col2:    
                voltar_alter = st.form_submit_button("Voltar sem Alterar")
          
            if submitted_alter:
                try:
                    alterar_servico(servico["id_servico"], dados)
                    st.success("Serviço alterado com sucesso!")
                except ValueError as e:
                    st.error(str(e))
                st.session_state.aba = "Listar"   
                st.rerun() 
            if voltar_alter:
                st.session_state.aba = "Listar"
                st.rerun()        

elif st.session_state.aba == "Excluir":
    st.subheader("Excluir Serviço")
    servicos = listar_servicos()
    servico = st.session_state.servico_selecionado or (servicos[0] if servicos else None)

    if servico:
        st.write(f"Deseja realmente excluir o serviço: {servico['descricao']} ?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Excluir Serviço"):
                excluir_servico(servico["id_servico"])
                st.success("Serviço excluído com sucesso!")
                st.session_state.servico_selecionado = None
                st.session_state.aba = "Listar"
                st.rerun()
        with col2:
            if st.button("Voltar sem excluir"):
                st.session_state.aba = "Listar"
                st.rerun()
