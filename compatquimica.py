import streamlit as st
from supabase import create_client, Client
import pandas as pd
from Base import *
# from BaseComDefault import *
from crud import supabase, listar_registros,listar_todos_registros,ComboBoxClientes,incluir_registro,alterar_registro,excluir_registro
from utils import string_para_float
from datetime import datetime

# Inicialização do cliente Supabase
supabase_url = st.secrets['supabase']['SUPABASE_URL']
supabase_key = st.secrets['supabase']['SUPABASE_KEY']
supabase: Client = create_client(supabase_url, supabase_key)

st.info(f'### Gerenciar Relatórios - Compatibilidade Química',icon=':material/thumb_up:')

# Inicializa session_state
if "ger_aba" not in st.session_state:
    st.session_state.ger_aba = "Listar"
if "ger_pagina" not in st.session_state:
    st.session_state.ger_pagina = 0
if "ger_busca_relatorio" not in st.session_state:
    st.session_state.ger_busca_relatorio = ""
if "ger_item_selecionado" not in st.session_state:
    st.session_state.ger_item_selecionado = None

PAGE_SIZE = 10
# 🔹 Inicializar resultado como None
resultado = None

def DadosVazios(dados) -> int:
    erro = 0
    if dados['pi_memb_1_09'] == 0.0:        # Membrana PI #1 0.000
        erro =  1
    elif dados['pi_memb_2_09'] == 0.0:      # Membrana PI #2 0.000
        erro = 2
    elif dados['pi_memb_3_09'] == 0.0:      # Membrana PI #3 0.000
        erro =  3
    elif dados['pb_padraowfi_09'] == 0.0:  # PB Padrão Fluido Padrão 0.0
        erro =  4
    elif dados['wfi_res1_09'] == 0.0:      # Fluido Padrão Resultado #1 0.0
        erro =  5 
    elif dados['wfi_res2_09'] == 0.0:      # Fluido Padrão Resultado #2 0.0
        erro =  6
    elif dados['wfi_res3_09'] == 0.0:      # Fluido Padrão Resultado #3 0.0
        erro =  7
    # elif dados['pb_refproduto'] == 0.0:      # PB Referencial (psi)
    #     erro =  8
    elif dados['prd_res1_10'] == 0.0:      # Fluido Padrão Resultado #1
        erro =  9
    elif dados['prd_res2_10'] == 0.0:      # Fluido Padrão Resultado #2
        erro =  10
    elif dados['prd_res3_10'] == 0.0:      # Fluido Padrão Resultado #3
        erro =  11
    # elif dados['wfif_res1'] == 0.0:     # Fluido Padrão final Resultado #1 0.0
    #     erro =  12
    # elif dados['wfif_res2'] == 0.0:     # Fluido Padrão final Resultado #2 0.0
    #     erro =  13
    # elif dados['wfif_res3'] == 0.0:     # Fluido Padrão final Resultado #3 0.0
    #     erro =  14
    elif dados['pf_memb_1_13'] == 0.0:      # Peso Final #1 0.000
        erro =  15   
    elif dados['pf_memb_2_13'] == 0.0:      # Peso Final #2 0.000
        erro =  16
    elif dados['pf_memb_3_13'] == 0.0:      # Peso Final #3 0.000
        erro =  17 
    # elif dados['dis_res1'] == 0.0:      # Resultado PRD#1
    #     erro =  18  
    # elif dados['dis_res2'] == 0.0:      # Resultado PRD#2
    #     erro =  19
    elif dados['crit_var_peso_15'] == 0.0:  #Critério Variação Peso 0.0
        erro =  20                                                       
    elif dados['crit_var_vazao_15'] == 0.0: # Critério Variação Vazão 0.0
        erro =  21  
    elif string_para_float(dados['fli_memb_1_09']) == 0.0:     # Membrana FI #1 mm:ss string_para_float(tempo_str) --> 0.0
        erro =  22
    elif string_para_float(dados['fli_memb_2_09']) == 0.0:     # Membrana FI #2 mm:ss
        erro =  23
    elif string_para_float(dados['fli_memb_3_09']) == 0.0:     # Membrana FI #3 mm:ss
        erro =  24
    elif string_para_float(dados['tmp_final1_11']) == 0.0:     # Fluxo Final #1 mm:ss 
        erro =  25    
    elif string_para_float(dados['tmp_final2_11']) == 0.0:     # Fluxo Final #2 mm:ss 
        erro =  26    
    elif string_para_float(dados['tmp_final3_11']) == 0.0:     # Fluxo Final #3 mm:ss 
        erro =  27    

    return erro

def ShowWarning(dados, condicao):    

    # Variaveis string que não necessariamente deverão ser preenchidas
    dict_warning = {}

    if dados['local_teste_03'] == '':
        dict_warning['Local de Teste']= 'Etapa 3'
    if dados['pessoa_local_03'] == '' : 
        dict_warning['Pessoa Local']= 'Etapa 3'  
    if dados['id_sala_03'] == '' : 
        dict_warning['ID da Sala']= 'Etapa 3'  
    if dados['dt_chegada_03'] == '' : 
        dict_warning['Data e Hora - Chegada Local']= 'Etapa 3'  
    if dados['hr_chegada_03'] == '' : 
        dict_warning['Data e Hora - Chegada Pessoa']= 'Etapa 3' 
    if dados['setor_03'] == '':
        dict_warning['Setor']= 'Etapa 3'    
    if dados['cargo_03'] == '':
        dict_warning['Cargo']= 'Etapa 3'    
    

    if dados['endereco_02'] == '':
        dict_warning['Endereço']= 'Etapa 2'    
    if dados['cidade_02'] == '':
        dict_warning['Cidade']= 'Etapa 2'    
    if dados['uf_02'] == '':
        dict_warning['UF']= 'Etapa 2'    
    if dados['tel_02'] == '':
        dict_warning['Telefone']= 'Etapa 2'    
    if dados['email_02'] == '':
        dict_warning['E-mail']= 'Etapa 2'    

    if dados['linha_05'] == '' : 
        dict_warning['Linha do Filtro']= 'Etapa 5'
    if dados['fabricante_05'] == '' : 
        dict_warning['Fabricante do Filtro']= 'Etapa 5'
    if dados['cat_membr_05'] == '' : 
        dict_warning['Nº Catálogo da Membrana']= 'Etapa 5'
    if dados['poro_cat_membr_05'] == '' : 
        dict_warning['Poro']= 'Etapa 5'
    if dados['temp_filtra_05'] == '' : 
        dict_warning['Temperatura de Filtração (°C)']= 'Etapa 5'
    if dados['tara_05'] == '' : 
        dict_warning['Tara da Balança (g)']= 'Etapa 5' 
    if dados['produto_05'] == '' : 
        dict_warning['Produto']= 'Etapa 5'       
    if dados['tmp_contato_05'] == '' : 
        dict_warning['Tempo de contato (h)']= 'Etapa 5'
    if dados['tempera_local_05'] == '' : 
        dict_warning['Temperatura Local (°C)']= 'Etapa 5'                 
    if dados['lote_05'] == '' : 
        dict_warning['Lote Do Produto']= 'Etapa 5'
    if dados['armaz_05'] == '' : 
        dict_warning['Armazenagem Local']= 'Etapa 5'
    if dados['umidade_05'] == '' : 
        dict_warning['Umidade (%)']= 'Etapa 5'
    if dados['volume_05'] == '' : 
        dict_warning['Volume']= 'Etapa 5'
    if dados['area_mem_05'] == '' : 
        dict_warning['Area efetiva da membrana']= 'Etapa 5'
    if dados['area_dis_05'] == '' : 
        dict_warning['Area efetiva do dispositivo']= 'Etapa 5'

    if dados['lotem1_06'] == '' : 
        dict_warning['Lote Membrana #1']= 'Etapa 6'
    if dados['lotem2_06'] == '' : 
        dict_warning['Lote Membrana  #2']= 'Etapa 6'
    if dados['lotem3_06'] == '' : 
        dict_warning['Lote Membrana  #3']= 'Etapa 6'
    if dados['lotes1_06'] == '' : 
        dict_warning['Lote Serial #1']= 'Etapa 6'
    if dados['lotes2_06'] == '' : 
        dict_warning['Lote Serial #2']= 'Etapa 6'
    if dados['lotes3_06'] == '' : 
        dict_warning['Lote Serial #3']= 'Etapa 6'
    if dados['cat_disp_06'] == '' : 
        dict_warning['Catálogo do Dispositivo']= 'Etapa 6'
    if dados['lote_disp_06'] == '' : 
        dict_warning['Lote do Dispositivo']= 'Etapa 6'
    if dados['serial_cat_disp_06'] == '' : 
        dict_warning['Serial Dispositivo']= 'Etapa 6'

    # if dados['estab_08'] == '' : 
    #     dict_warning['Estabilidade do Produto']= 'Etapa 8'

    if dados['wfi_res1_09'] == '' : 
        dict_warning['Fluido Padrão ID #1']= 'Etapa 9'
    if dados['wfi_res2_09'] == '' : 
        dict_warning['Fluido Padrão ID #2']= 'Etapa 9'
    if dados['wfi_res3_09'] == '' : 
        dict_warning['Fluido Padrão ID #3']= 'Etapa 9'
    if dados['dt_wfi_09'] == '' : 
        dict_warning['Data']= 'Etapa 9'
    if dados['hr_wfi_09'] == '' : 
        dict_warning['Hora']= 'Etapa 9'

    if dados['dt_wfip_10'] == '' : 
        dict_warning['Data Final']= 'Etapa 10'
    if dados['hr_wfip_10'] == '' : 
        dict_warning['Hora Final']= 'Etapa 10'
    if dados['prd_id1_10'] == '' : 
        dict_warning['ID #1 Produto']= 'Etapa 10'
    if dados['prd_id2_10'] == '' : 
        dict_warning['ID #2 Produto']= 'Etapa 10'
    if dados['prd_id3_10'] == '' : 
        dict_warning['ID #3 Produto']= 'Etapa 10'

    if dados['id_padr1_12'] == '' : 
        dict_warning['ID #1']= 'Etapa 12'
    if dados['id_padr2_12'] == '' : 
        dict_warning['ID #2']= 'Etapa 12'
    if dados['id_padr3_12'] == '' : 
        dict_warning['ID #3']= 'Etapa 12'

    if dados['dis_id1_14'] == '' : 
        dict_warning['ID #1 - Dispositivo']= 'Etapa 14'
    if dados['dis_id2_14'] == '' : 
        dict_warning['ID #2 - Dispositivo']= 'Etapa 14'

    if condicao  == False:
        dict_warning['Data Final anterior a Data Inicial']= 'Etapa 10'  

    return dict_warning


def ShowRelatorio(novos_dados):
    # Analizar se os dados estão totalmente preenchidos
    df = Previsao_Relat(novos_dados)
    dict_ret = {}
    col1, col2, col3 = st.columns([1, 4, 1])  # col2 maior, centralizada
    with col2:
        st.info('## :point_right:   Prévia  dos  Resultados')

    
    # ------------------------- % Variação de Peso ------------------------------------- 
    st.markdown(f'<div style="text-align: left;"><h5>% Variação Peso - Critério <= {novos_dados['crit_var_peso_15']:.1f}%</h5></div>', unsafe_allow_html=True)

    df_VarPeso = df[['% Variação Peso - Membrana 1',
                    '% Variação Peso - Membrana 2',
                    '% Variação Peso - Membrana 3', 
                    'ResultadoP Membrana 1',
                    'ResultadoP Membrana 2',
                    'ResultadoP Membrana 3',
                    # 'Média % Variação Peso']]
                    'Perc Variação Massa (PVM)',
                    'Status Peso']]
    

    Resultado_1 = df_VarPeso['ResultadoP Membrana 1'][0]
    Resultado_2 = df_VarPeso['ResultadoP Membrana 2'][0]
    Resultado_3 = df_VarPeso['ResultadoP Membrana 3'][0]

    df_VarPeso = df_VarPeso.drop(columns=['ResultadoP Membrana 1','ResultadoP Membrana 2','ResultadoP Membrana 3']) 

    
    st.dataframe(df_VarPeso, 
                column_config={
                        "% Variação Peso - Membrana 1": Resultado_1, 
                        "% Variação Peso - Membrana 2": Resultado_2,
                        "% Variação Peso - Membrana 3": Resultado_3,
                        
                },
                hide_index=True)
    
    xxx = df_VarPeso.to_dict(orient='records')
    var_peso_membr_1 = xxx[0]['% Variação Peso - Membrana 1']
    var_peso_membr_2 = xxx[0]['% Variação Peso - Membrana 2']
    var_peso_membr_3 = xxx[0]['% Variação Peso - Membrana 3']
    pvm = xxx[0]['Perc Variação Massa (PVM)']
    status_peso = xxx[0]['Status Peso']

    dict_ret['var_peso_membr_1']= var_peso_membr_1
    dict_ret['var_peso_membr_2']= var_peso_membr_2
    dict_ret['var_peso_membr_3']= var_peso_membr_3
    dict_ret['pvm']= pvm
    dict_ret['status_peso']= status_peso


    # ------------------------- % Variação de Vazão ------------------------------------- 
    st.markdown(f'<div style="text-align: left;"><h5>% Variação Vazão - Critério <= {novos_dados['crit_var_vazao_15']:.1f}%</h5></div>', unsafe_allow_html=True)

    df_VarVazao = df[['% Variação Vazao - Membrana 1',
                    '% Variação Vazao - Membrana 2',
                    '% Variação Vazao - Membrana 3',
                    'ResultadoV Membrana 1',
                    'ResultadoV Membrana 2',
                    'ResultadoV Membrana 3', 
                    # 'Média % Variação Vazão']]
                    'Perc Variação Vazão (PVV)',
                    'Status Fluxo']]
    
    Resultado_4 = df_VarVazao['ResultadoV Membrana 1'][0]
    Resultado_5 = df_VarVazao['ResultadoV Membrana 2'][0]
    Resultado_6 = df_VarVazao['ResultadoV Membrana 3'][0]

    df_VarVazao = df_VarVazao.drop(columns=['ResultadoV Membrana 1','ResultadoV Membrana 2','ResultadoV Membrana 3'])          
    st.dataframe(df_VarVazao, 
                column_config={
                        "% Variação Vazao - Membrana 1": Resultado_4, 
                        "% Variação Vazao - Membrana 2": Resultado_5,
                        "% Variação Vazao - Membrana 3": Resultado_6,
                        
                },
                hide_index=True)
    
    xxx = df_VarVazao.to_dict(orient='records')
    var_vazao_membr_1 = xxx[0]['% Variação Vazao - Membrana 1']
    var_vazao_membr_2 = xxx[0]['% Variação Vazao - Membrana 2']
    var_vazao_membr_3 = xxx[0]['% Variação Vazao - Membrana 3']
    pvv = xxx[0]['Perc Variação Vazão (PVV)']
    status_vazao = xxx[0]['Status Fluxo']

    dict_ret['var_vazao_membr_1']= var_vazao_membr_1
    dict_ret['var_vazao_membr_2']= var_vazao_membr_2
    dict_ret['var_vazao_membr_3']= var_vazao_membr_3
    dict_ret['pvv']= pvv
    dict_ret['status_vazao']= status_vazao
    
    df_RPB = df[['RPB Membrana 1','RPB Membrana 2','RPB Membrana 3']]
    st.dataframe(df_RPB, hide_index=True)  

    xxx = df_RPB.to_dict(orient='records')
    rpb_membrana_1 = xxx[0]['RPB Membrana 1']
    rpb_membrana_2 = xxx[0]['RPB Membrana 2']
    rpb_membrana_3 = xxx[0]['RPB Membrana 3']
    dict_ret['rpb_membrana_1']= rpb_membrana_1
    dict_ret['rpb_membrana_2']= rpb_membrana_2
    dict_ret['rpb_membrana_3']= rpb_membrana_3


    df_PBEstimado = df[['RPB','PB Referencial','PB Estimado (PBMe)']]   
    st.dataframe(df_PBEstimado, hide_index=True, width='content') 

    xxx = df_PBEstimado.to_dict(orient='records')
    pb_referencial = xxx[0]['PB Referencial']
    pb_estimado = xxx[0]['PB Estimado (PBMe)']
    media_rpb = xxx[0]['RPB']
    dict_ret['media_rpb']= media_rpb
    dict_ret['pb_referencial']= pb_referencial
    dict_ret['pb_estimado']= pb_estimado
    
    return  dict_ret


# Interface de listagem
if st.session_state.ger_aba == "Listar":
    busca = st.text_input("Buscar por relatório", st.session_state.ger_busca_relatorio)
    if busca != st.session_state.ger_busca_relatorio:
        st.session_state.ger_busca_relatorio = busca
        st.session_state.ger_pagina = 0
        st.rerun()

    registros = listar_registros(filtro_relatorio=st.session_state.ger_busca_relatorio, tipo="R-CQ")
      
    total = len(registros)
    inicio = st.session_state.ger_pagina * PAGE_SIZE
    fim = inicio + PAGE_SIZE

    st.write(f"Mostrando {inicio + 1} - {min(fim, total)} de {total} registros")

    st.session_state.ger_item_selecionado = None  # Reset seleção ao carregar listagem

    if registros:
        paginados = registros[inicio:fim]

        df = pd.DataFrame(paginados)

        # Adicionar coluna Selecionar
        df["Selecionar"] = False

        # Dicionário de equivalência para status
        status_map = {
            "Cancelado": "❌ Cancelado",    # "❌ Cancelado"
            "Concluído": "✅ Concluído",    # "✅Concluído"  :white_check_mark: 11
            "Pendente": "🕗 Pendente",      # "🕗 Pendente" :clock9: 1060
            "Agendado": "📅 Agendado",      # "📅 Agendado" :date: 924
            "Parcial": "📝 Parcial",        # "📝 Parcial" :memo: 949
            }
        
        # Criar coluna OK com base no status_rel_01
        df["OK"] = df["status_rel_01"].map(status_map).fillna("")
        
        resultado = st.data_editor(df,
                                   # width='stretch',
                                   hide_index=True,
                                   column_order=["Selecionar", "OK", "relatorio", "cliente"],
                                   column_config={
                                        "OK": st.column_config.TextColumn("Status"),
                                        "relatorio": st.column_config.TextColumn("Relatório"),
                                        "cliente": st.column_config.TextColumn("Empresa"),
                                   },
                                   #key="tabela_planilhanova",
                                   num_rows="dynamic")
        
        if resultado is not None:
            selecionados = resultado[resultado["Selecionar"] == True]
            if len(selecionados) > 1:
                st.error("Selecione apenas 1 registro por vez.")
            elif len(selecionados) == 1:
                idx = selecionados.index[0]
                id_sel = resultado.loc[idx, "id"]
                registro_completo = next((r for r in listar_todos_registros() if r["id"] == id_sel), None)
                if registro_completo:
                    st.session_state.ger_item_selecionado = registro_completo

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.ger_pagina > 0:
            if st.button("⬅ Página anterior"):
                st.session_state.ger_pagina -= 1
                st.rerun()
    with col2:
        if fim < total:
            if st.button("Próxima página ➡"):
                st.session_state.ger_pagina += 1
                st.rerun()

    
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Mostrar"):
            st.session_state.ger_aba = "Listar"
            st.rerun()
        if col2.button("Novo"):
            st.session_state.ger_aba = "Incluir"
            st.rerun()
        if col3.button("Altera Selecionado"):
            st.session_state.ger_aba = "Alterar"
            st.rerun()
        if col4.button("Exclui Selecionado"):
            st.session_state.ger_aba = "Excluir"
            st.rerun()

if st.session_state.ger_aba == "Incluir":
    st.subheader("Incluir Nova Planilha")

    novos_dados, dataOK = formulario_padrao(dados=None, combo_clientes=ComboBoxClientes())

    desabilita_botoes = st.session_state.get("exibir_alerta", False)
    col1, col2, col3 = st.columns(3)
    with col1:
        submitted_parcial = st.button("💾 Salvar Parcial", disabled=desabilita_botoes)
    with col2:
        disabilita = False
        submitted_verify = st.button("📄 Ver Relatório", disabled=desabilita_botoes)
    with col3:
        submitted_return = st.button("🔙 Voltar", disabled=desabilita_botoes)

    if submitted_parcial:
        try:
            erro = DadosVazios(novos_dados)
            if erro == 0:
                dict_warning = ShowWarning(novos_dados, True)
                if dict_warning:
                    st.session_state.campos_incompletos = dict_warning
                    st.session_state.novos_dados_cache = novos_dados
                    st.session_state.exibir_alerta = True
                    st.rerun()
                else:
                    incluir_registro(dados=novos_dados )
                    st.success("Planilha salva com sucesso!")
                    st.session_state.ger_aba = "Listar"
                    st.rerun()
            else:
                message, etapa = ShowErro(erro)
                st.warning(f' ##### Campo :point_right: {message} :warning: INVÁLIDO !  :mag_right: ETAPA :point_right: {etapa}')
        except Exception as e:
            st.error(f'Erro ao atualizar o registro {e}', icon="🔥")
            # print(f'Erro ao atualizar o registro {e}', icon="🔥")

    if submitted_verify:
        erro = DadosVazios(novos_dados)
        if erro > 0 and erro < 100:
            message, etapa = ShowErro(erro)
            st.warning(f' ##### Campo :point_right: {message} :warning: INVÁLIDO !  :mag_right: ETAPA :point_right: {etapa}')
        if erro == 0 or erro >= 100:
            dict_rel = ShowRelatorio(novos_dados)
            st.session_state.ger_dict_rel = dict_rel

    if submitted_return:
        st.session_state.ger_aba = "Listar"
        st.rerun()

    # ✅ FORA DO FORM — SALVA DADOS - INCLUIR
    if st.session_state.get("ger_dict_rel"):

        conclusao  = st.text_area('CONCLUSÃO:', value= novos_dados.get("conclusao", "") if novos_dados else "")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted_salvar = st.button("💾 Salvar e Concluir")
        with col2:
            submitted_voltar5 = st.button("🔙 Voltar a Edição")
        if submitted_salvar:
            dadoscomrelatorio = novos_dados | st.session_state.ger_dict_rel
            # print('dadoscomrelatorio =' , dadoscomrelatorio)
            dadoscomrelatorio['status_rel_01'] = 'Concluído'
            dadoscomrelatorio['conclusao'] = RetiraCRLF(conclusao)
            incluir_registro(dados=dadoscomrelatorio )
            st.success("Planilha salva com sucesso!")
            st.session_state.ger_dict_rel = None
            st.session_state.ger_aba = "Listar"
            st.rerun()
        if submitted_voltar5:
            st.session_state.ger_dict_rel = None
            st.session_state.ger_aba = "Incluir"
            st.rerun()

    # ✅ FORA DO FORM — MOSTRAR ALERTA SE HOUVER CAMPOS INCOMPLETOS
    if st.session_state.get("exibir_alerta"):
        st.warning("Existem campos obrigatórios não preenchidos. Deseja continuar mesmo assim?", icon="⚠️")

        for campo, etapa in st.session_state.campos_incompletos.items():
            st.markdown(
             f'❌ **{campo}** <span style="background-color:#575115; color:white; padding:2px 6px; border-radius:4px;">{etapa}</span>',
            unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Voltar e corrigir"):
                st.info("Você optou por revisar os dados.")
                st.session_state.exibir_alerta = False
                st.rerun()
            
        with col2:
            if st.button("Salvar mesmo assim"):
                incluir_registro(dados=novos_dados )
                st.success("Salvo com campos incompletos.")
                st.session_state.ger_aba = "Listar"
                st.session_state.exibir_alerta = False
                st.rerun()
 
if st.session_state.ger_aba == "Alterar":
    st.subheader("Alterar Registro")
    registro = st.session_state.ger_item_selecionado
    if registro:
        if registro.get("status_rel_01") == 'Concluído':
            st.error(f"### O relatório :point_right: {registro.get('relatorio')} já foi concluído.")
            if st.button("Mostra Relatórios"):
                st.session_state.ger_aba = "Listar"
                st.rerun()
        else:
            novos_dados, dataOK = formulario_padrao(dados=registro, combo_clientes=ComboBoxClientes())

            desabilita_botoes_alterar = st.session_state.get("exibir_alerta_alterar", False)
            col1, col2, col3 = st.columns(3)
            with col1:
                submitted = st.button("💾 Salvar Alterações", disabled=desabilita_botoes_alterar)
            with col2:
                verify2 = st.button("📄 Ver Relatório", disabled=desabilita_botoes_alterar)
            with col3:
                voltar1 = st.button("🔙 Retornar", disabled=desabilita_botoes_alterar)

            if submitted:
                try:
                    erro = DadosVazios(novos_dados)
                    if erro == 0:
                        dict_warning = ShowWarning(novos_dados, dataOK)

                        if dict_warning:
                            st.session_state.campos_incompletos = dict_warning
                            st.session_state.novos_dados_cache = novos_dados
                            st.session_state.registro_id_cache = registro["id"]
                            st.session_state.exibir_alerta_alterar = True
                            st.rerun()  # <- ESSENCIAL!
                        else:
                            alterar_registro(registro["id"], novos_dados)
                            st.success("Planilha alterada com sucesso!")
                            st.session_state.ger_aba = "Listar"
                            st.rerun()
                    else:
                        message, etapa = ShowErro(erro)
                        st.session_state.exibir_alerta_alterar = False
                        st.warning(f' ##### Campo :point_right: {message} :warning: INVÁLIDO !  :mag_right: ETAPA :point_right: {etapa}')
                except Exception as e:
                    st.error(f'Erro ao atualizar o registro {e}', icon="🔥")

            if verify2:
                erro = DadosVazios(novos_dados)
                if erro > 0 and erro < 100:
                    message, etapa = ShowErro(erro)
                    st.warning(f' ##### Campo :point_right: {message} :warning: INVÁLIDO !  :mag_right: ETAPA :point_right: {etapa}')
                if erro == 0 or erro >= 100:
                    dict_rel = ShowRelatorio(novos_dados)
                    st.session_state.ger_dict_rel = dict_rel

            if voltar1:
                st.session_state.ger_aba = "Listar"
                st.rerun()
    else:
        st.info("Selecione um item na aba 'Listar' para editar.")
        if st.button('Retorna para listar'):
            st.session_state.ger_aba = "Listar"
            st.rerun()

    # ✅ FORA DO FORM — SALVA DADOS - ALTERAR
    if st.session_state.get("ger_dict_rel"):

        conclusao  = st.text_area('CONCLUSÃO:', value= novos_dados.get("conclusao", "") if novos_dados else "") 

        col1, col2 = st.columns(2)
        with col1:
            submitted_salvar = st.button("💾 Salvar e Concluir")
        with col2:
            submitted_voltar5 = st.button("🔙 Voltar a Edição")
        if submitted_salvar:
            dadoscomrelatorio = novos_dados | st.session_state.ger_dict_rel
            # print('dadoscomrelatorio =' , dadoscomrelatorio)
            dadoscomrelatorio['status_rel_01'] = 'Concluído'
            dadoscomrelatorio['conclusao'] = RetiraCRLF(conclusao)
            alterar_registro(id= registro['id'], dados=dadoscomrelatorio)   
            st.success("Planilha salva com sucesso!")
            st.session_state.ger_dict_rel = None
            st.session_state.ger_aba = "Listar"
            st.rerun()
        if submitted_voltar5:
            st.session_state.ger_dict_rel = None
            st.session_state.ger_aba = "Alterar"
            st.rerun()        

    # ✅ FORA DO FORM — ALERTA DE CAMPOS PENDENTES NA ALTERAÇÃO
    if st.session_state.get("exibir_alerta_alterar"):
        st.warning(" Existem campos obrigatórios não preenchidos. Deseja salvar mesmo assim?", icon="⚠️")

        for campo, etapa in st.session_state.campos_incompletos.items():
            st.markdown(f"- ❌ **{campo}** ({etapa})")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Salvar mesmo assim - Alterar"):
                alterar_registro(
                    st.session_state.registro_id_cache,
                    st.session_state.novos_dados_cache
                )
                st.success("Alterações salvas com campos incompletos.")
                st.session_state.ger_aba = "Listar"
                st.session_state.exibir_alerta_alterar = False
                st.rerun()
        with col2:
            if st.button("Voltar e corrigir - Alterar"):
                st.info("Você optou por revisar os dados.")
                st.session_state.exibir_alerta_alterar = False
                st.rerun()

if st.session_state.ger_aba == "Excluir":
    st.subheader("Excluir Relatório")
    registro = st.session_state.ger_item_selecionado
    if registro:
        texto1 = f'Deseja realmente excluir o relatório {registro['relatorio']} ?'
        texto2 = f"Cliente: {registro['cliente']}"
        st.warning(f' :warning: ATENÇÃO !\n##### :point_right: {texto1}\n:point_right: {texto2}')

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Excluir"):
                try:
                    excluir_registro(registro["id"])
                    st.success("Relatório excluído com sucesso!")
                    st.session_state.ger_item_selecionado = None
                    st.session_state.ger_aba = "Listar"
                    st.rerun()
                except Exception  as e:  
                    st.error(f'Erro ao excluir o registro {e}', icon="🔥")  
        with col2:     
            if st.button("Retornar"):
                st.session_state.ger_aba = "Listar"
                st.rerun()   
    else:
        st.info("Selecione um item na aba 'Listar' para excluir.")

