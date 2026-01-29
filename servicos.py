import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

# from crud import supabase, listar_servicos,listar_todos_dados_servicos,incluir_servico,alterar_servico,excluir_servico, verificar_uso_servico
from crud import *
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
        df_exibicao = pd.DataFrame(servicos_paginados).copy()
        
        # Formatação de campos para exibição
        df_exibicao["valor_formatado"] = df_exibicao["valor"].apply(
            lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        df_exibicao["Selecionar"] = ""
        df_exibicao["id_servico"] = df_exibicao["id_servico"].astype(str)

        # Colunas e Configuração
        cols_exibicao = ["Selecionar", "descricao", "valor_formatado", "ref", "codigo", "tipo"]
        
        selecao = st.dataframe(
            df_exibicao[cols_exibicao],
            hide_index=True,
            width='stretch',
            column_config={
                "Selecionar": st.column_config.TextColumn("Selecionar", help="Clique na linha para selecionar"),
                "descricao": st.column_config.TextColumn("Descrição"),
                "valor_formatado": st.column_config.TextColumn("Valor (R$)"),
                "ref": st.column_config.TextColumn("Referência"),
                "codigo": st.column_config.TextColumn("Código"),
                "tipo": st.column_config.TextColumn("Tipo"),
            },
            selection_mode="single-row",
            on_select="rerun",
            key="grid_servicos"
        )

        # Lógica de Seleção
        indices_selecionados = selecao.get("selection", {}).get("rows", [])
        
        if indices_selecionados:
            idx_paginado = indices_selecionados[0]
            if idx_paginado < len(servicos_paginados):
                id_selecionado = servicos_paginados[idx_paginado]["id_servico"]
                
                servico_completo = next((c for c in listar_todos_dados_servicos() if c["id_servico"] == id_selecionado), None)
                
                if servico_completo:
                    st.session_state.servico_selecionado = servico_completo
        else:
             st.session_state.servico_selecionado = None

    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    total_paginas = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

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
        # Verifica se o serviço está em uso
        usado_em = verificar_uso_servico(servico["id_servico"])
        if usado_em:
            texto1= f"O serviço  {servico['descricao']} "
            if len(usado_em) == 1:
                texto2=f"Não pode ser excluído pois está vinculado à proposta 📝{usado_em[0]['num_proposta']}"
            else:
                texto2= "Não pode ser excluído pois está vinculado às seguintes propostas 📝"    
            st.success(f'##### :warning: ATENÇÃO !\n###### 👉 {texto1}\n###### 🔴 {texto2}')
            # Formata os dados para exibição (opcional, mas st.table aceita lista de dicts)
            # Cria DataFrame para formatar a exibição
            df_uso = pd.DataFrame(usado_em)
            # Ordena as colunas (num_proposta, empresa, cidade, data_emissao)
            colunas_ordenadas = ["num_proposta", "empresa", "cidade", "data_emissao"]
            # Garante que só seleciona as que existem (caso o retorno mude no futuro)
            colunas_finais = [c for c in colunas_ordenadas if c in df_uso.columns]
            df_uso = df_uso[colunas_finais]
            
            # Formata a data para dd-mm-YYYY
            if "data_emissao" in df_uso.columns:
                df_uso["data_emissao"] = pd.to_datetime(df_uso["data_emissao"]).dt.strftime('%d-%m-%Y')
 
            # Renomeia as colunas
            df_uso = df_uso.rename(columns={
                "num_proposta": "Proposta",
                "empresa": "Empresa",
                "cidade": "Cidade",
                "data_emissao": "Emitida em"
            })
            
            # Remove o índice visualmente definindo-o como string vazia
            if not df_uso.empty:
                df_uso.index = [""] * len(df_uso)
            
            st.table(df_uso)

            if st.button("Voltar"):
                    st.session_state.aba = "Listar"
                    st.rerun()
        else:
            texto1 = f"Deseja realmente excluir o serviço: "
            texto2 = f'{servico['descricao']}'
            st.success(f'##### :warning: ATENÇÃO !\n##### 👉 {texto1}\n###### 🟢 {texto2}')
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
