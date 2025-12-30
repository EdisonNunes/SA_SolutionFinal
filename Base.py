import streamlit as st
from calculos import *
from crud import supabase
from datetime import datetime
from utils import validar_datas_e_calcular_horas,ShowErro,RetiraCRLF


def CalculaPBEstimado(prd_res1_10, prd_res2_10, prd_res3_10,
                      wfi_res1_09, wfi_res2_09, wfi_res3_09, pb_padraowfi_09):
    erro = 0
    if erro < 14 or erro > 19:
        try:
               	
            # rpb_membr_1 = pi_memb_1_09 / pf_memb_1_13
            # rpb_membr_2 = pi_memb_2_09 / pf_memb_2_13
            # rpb_membr_3 = pi_memb_3_09 / pf_memb_3_13

            rpb_membr_1 = prd_res1_10 / wfi_res1_09
            rpb_membr_2 = prd_res2_10 / wfi_res2_09
            rpb_membr_3 = prd_res3_10 / wfi_res3_09

            rpb_media = (rpb_membr_1 + rpb_membr_2 + rpb_membr_3) / 3

            # PB Estimado	=C28*L3		Célula J7		ETAPA 8		2 casas
            pb_estimado = pb_padraowfi_09 * rpb_media

            # print('================= CalculaPBEstimado ====================================================')
            # print('RPB Membrana 1 : ', rpb_membr_1,'   ',prd_res1_10,'   ',wfi_res1_09)
            # print('RPB Membrana 2 : ', rpb_membr_2,'   ',prd_res2_10,'   ',wfi_res2_09)
            # print('RPB Membrana 3 : ', rpb_membr_3,'   ',prd_res3_10,'   ',wfi_res3_09)
            # print('rpb_media : ', rpb_media)
            # print('pb_padrao : ', pb_padraowfi_09)
            # print('pb_estimado : ', pb_estimado)
            # print('pb_estimado arredondado : ', round(pb_estimado,1))
            return round(pb_estimado,1), 0
        except:
            return 0.0, erro
       
    else:
        return 0.0, erro  
    


def formulario_padrao(dados=None, combo_clientes=None):
    format_1casa='%0.1f'
    format_2casas='%0.2f'
    format_3casas='%0.3f'
    # Exemplo de chamada da função de inicialização de campos
    motivo_01 = ""
    dt_agendada_01 = ""
    dt_emissao_01 = ""

    if dados:       # Alterar
        relatorio= dados['relatorio']
    else:           # Incluir
        hoje = GetHoraLocal('America/Sao_Paulo')
        relatorio = 'R-CQ' + hoje.strftime('%Y%m%d-%H%M%S')
        condicao = True

    titulo = f'Planilha de Compatibilidade Química\n Relatório :point_right: {relatorio}'
    st.info(f'### {titulo}',icon=':material/thumb_up:')

    ################## Etapa 1 - Status de pedido ##################
    st.markdown(':orange-background[Etapa 1 - Status de pedido]')
    container1 = st.container(border=True)
    with container1:
        # opcoes = ['Pendente', 'Agendado', 'Cancelado', 'Parcial', 'Concluído']
        opcoes = ['Pendente', 'Agendado', 'Cancelado', 'Parcial']
        # ajuda = '''
        #     🕗 Pendente: Aguardando pedido do cliente\n
        #     📅 Agendado: Preenchimento de dados não envolvidos com cálculos\n
        #     ❌ Cancelado: Relatório suspenso\n
        #     📝 Parcial: Preenchimento parcial dos dados de campo\n
        #     ✅ Concluído: Relatório concluído - Não disponível para edição.
        # '''
        ajuda = '''
            🕗 Pendente: Aguardando pedido do cliente\n
            📅 Agendado: Preenchimento de dados não envolvidos com cálculos\n
            ❌ Cancelado: Relatório suspenso\n
            📝 Parcial: Preenchimento parcial dos dados de campo\n
        '''
        try:
            valor_status_rel01  = dados.get("status_rel_01", "")
        except:
            valor_status_rel01 = 'Agendado'

        idx_status_rel_01  = opcoes.index(valor_status_rel01)  if valor_status_rel01 in opcoes  else 1 

        status_rel_01 = st.radio('Status Atual', options=opcoes, index=idx_status_rel_01, horizontal=True,
                                 help=ajuda)
        if status_rel_01 == 'Agendado':
            dt_agendada_01 = st.text_input('Data Agendada:',placeholder='DD-MM-AAAA',
                                       value=dados.get("dt_agendada_01", "") if dados else "")
        if status_rel_01 == 'Cancelado':
            motivo_01 = st.text_area('Motivo do cancelamento:', placeholder='Digite o motivo do cancelamento',
                                       value=dados.get("motivo_01", "") if dados else "")
        if status_rel_01 == 'Parcial' or status_rel_01 == 'Concluído':
            dt_emissao_01 = st.text_input('Data de emissão do Relatório Preliminar:',placeholder='DD-MM-AAAA',
                                       value=dados.get("dt_emissao_01", "") if dados else "")    

    
    ################## Etapa 2 - Identificação do Cliente  ##################
    st.markdown(':orange-background[Etapa 2 - Identificação do Cliente]')

    container2 = st.container(border=True)
    with container2:
        cliente_valor = dados.get("cliente", "") if dados else ""
        cidade_valor = dados.get("cidade_02", "") if dados else ""

        # Encontra índice com tolerância a erros
        cliente_default = 0
        for i, nome in enumerate(combo_clientes):
             #print('i= ',i, '   Nome: ', nome) 
             if nome.split(' - ')[0] == cliente_valor.strip():
                 cliente_default = i
                 break
            
        cliente = st.selectbox("Empresa:", combo_clientes, index=cliente_default)

        nome_empresa = f"{cliente.split('-')[0].strip()}"
        cidade = f"{cliente.split('-')[1].strip()}"

        resposta = supabase.table("clientes").select("*").eq("empresa", nome_empresa).eq("cidade", cidade).execute()
        empresa = resposta.data[0]

        opcoes = ['SIM', 'NÃO']
        local_realizado_02 = st.radio('O local de realização é o mesmo do cadastro?', options=opcoes, horizontal=True)
        if local_realizado_02 == 'SIM':
            endereco_02  = st.text_input('Endereço:', max_chars= 100, value= empresa['endereco'], disabled=True)
        else:
            endereco_02  = st.text_input('Endereço:', max_chars= 100, 
                                         value= dados.get("endereco_02", "") if dados else '', disabled=False)

        col1, col2, col3 = st.columns(3)
        with col1:
            if local_realizado_02 == 'SIM':
                cidade_02 = st.text_input('Cidade:', max_chars= 50, value= empresa['cidade'], disabled=True)
                cnpj_02 = st.text_input('CNPJ:', max_chars= 20, value= empresa['cnpj'], disabled=True)
            else:    
                cidade_02 = st.text_input('Cidade:', max_chars= 50, 
                                          value= dados.get("cidade_02", "") if dados else '', disabled=False)
                cnpj_02 = st.text_input('CNPJ:', max_chars= 50, 
                                      value= dados.get("cnpj_02", "") if dados else '', disabled=False)
        with col2:  
            if local_realizado_02 == 'SIM':
                uf_02 = st.text_input('UF:', max_chars= 50, value= empresa['uf'], disabled=True) 
                tel_02 = st.text_input('Telefone:', max_chars= 50, value= empresa['telefone'],  disabled=True)
            else:
                uf_02 = st.text_input('UF:', max_chars= 50, 
                                      value= dados.get("uf_02", "") if dados else '', disabled=False)  
                tel_02 = st.text_input('Telefone:', max_chars= 50, 
                                       value= dados.get("tel_02", "") if dados else '', disabled=False)   
           
        with col3:  
            if local_realizado_02 == 'SIM':
                cep_02 = st.text_input('CEP:', max_chars= 12, value= empresa['cep'], disabled=True)
                email_02 = st.text_input('E-mail:', max_chars= 50, value= empresa['email'],  disabled=True) 
            else:
                cep_02 = st.text_input('CEP:', max_chars= 50, 
                                      value= dados.get("cep_02", "") if dados else '', disabled=False)
                email_02 = st.text_input('E-mail:', max_chars= 50, 
                                         value= dados.get("email_02", "") if dados else '', disabled=False)


    ################## Etapa 3 - Local de Realização dos Serviços  ##################
    st.markdown(':orange-background[Etapa 3 - Local de Realização dos Serviços]')
    container3 = st.container(border=True)
    with container3:
        col1, col2 = st.columns(2)
        with col1:
            local_teste_03  = st.text_input('Local de Teste:', max_chars= 20, 
                                         value=dados.get("local_teste_03", "") if dados else "")
            pessoa_local_03 = st.text_input('Pessoa Local:', max_chars= 20, 
                                         value=dados.get("pessoa_local_03", "") if dados else "")
            setor_03 = st.text_input('Setor:', max_chars= 30, value= dados.get("setor_03", "") if dados else "")
            id_sala_03 = st.text_input('ID da Sala:', max_chars= 12, 
                                     value=dados.get("id_sala_03", "") if dados else "")
        with col2:   
            dt_chegada_03 = st.text_input('Data e Hora - Chegada ao Local:',placeholder='DD-MM-AAAA HH:MM',
                                       value=dados.get("dt_chegada_03", "") if dados else "")
            hr_chegada_03 = st.text_input('Data e Hora - Chegada da Pessoa:',placeholder='DD-MM-AAAA HH:MM',
                                       value=dados.get("hr_chegada_03", "") if dados else "")
            cargo_03 = st.text_input('Cargo:',   max_chars= 50, value= dados.get("cargo_03", "") if dados else "")
            pedido_03 = st.text_input('Número do Pedido:',
                                       value=dados.get("pedido_03", "") if dados else "")
        coment_03  = st.text_input('Complemento:', value= dados.get("coment_03", "") if dados else "")   
    
    ################## Etapa 4 - Checklist do local  ##################
    st.markdown(':orange-background[Etapa 4 - Checklist do local]')   

    try:
       valor_ckl_ponto_04  = dados.get("ckl_ponto_04", "")
       valor_ckl_espaco_04 = dados.get("ckl_espaco_04", "")   
       valor_ckl_tomada_04 = dados.get("ckl_tomada_04", "")
       valor_ckl_balan_04  = dados.get("ckl_balan_04", "")
       valor_ckl_agua_04   = dados.get("ckl_agua_04", "")
       valor_ckl_conex_04  = dados.get("ckl_conex_04", "")
       valor_ckl_veda_04   = dados.get("ckl_veda_04", "")
       valor_ckl_freez_04  = dados.get("ckl_freez_04", "")
    except:
       valor_ckl_ponto_04  = 'Não OK'
       valor_ckl_espaco_04 = 'Não OK'   
       valor_ckl_tomada_04 = 'Não OK'
       valor_ckl_balan_04  = 'Não OK'
       valor_ckl_agua_04   = 'Não OK'
       valor_ckl_conex_04  = 'Não OK'
       valor_ckl_veda_04   = 'Não OK'
       valor_ckl_freez_04  = 'Não OK'

    opcoes_ckl = ['OK', 'Não OK']
    idx_ckl_ponto_04  = opcoes_ckl.index(valor_ckl_ponto_04)  if opcoes_ckl in opcoes_ckl  else 1
    idx_ckl_espaco_04 = opcoes_ckl.index(valor_ckl_espaco_04) if opcoes_ckl in opcoes_ckl  else 1
    idx_ckl_tomada_04 = opcoes_ckl.index(valor_ckl_tomada_04) if opcoes_ckl in opcoes_ckl  else 1
    idx_ckl_balan_04  = opcoes_ckl.index(valor_ckl_balan_04)  if opcoes_ckl in opcoes_ckl  else 1
    idx_ckl_agua_04   = opcoes_ckl.index(valor_ckl_agua_04)   if opcoes_ckl in opcoes_ckl  else 1
    idx_ckl_conex_04  = opcoes_ckl.index(valor_ckl_conex_04)  if opcoes_ckl in opcoes_ckl  else 1
    idx_ckl_veda_04   = opcoes_ckl.index(valor_ckl_veda_04)   if opcoes_ckl in opcoes_ckl  else 1
    idx_ckl_freez_04  = opcoes_ckl.index(valor_ckl_freez_04)  if opcoes_ckl in opcoes_ckl  else 1


    container4 = st.container(border=True)
    with container4:
        opcoes_ckl = ['OK', 'Não OK']
        col1, col2 = st.columns(2)
        with col1:
            ckl_ponto_04 = st.radio('Ponto de Ar Comprimido Regulado e com Tubo de 6mm?', 
                                    options=opcoes_ckl, index=idx_ckl_ponto_04,  horizontal=True)
            ckl_espaco_04 = st.radio('Espaço da bancada: pelo menos 2000mm x 800mm', 
                                    options=opcoes_ckl, index=idx_ckl_espaco_04, horizontal=True)
            ckl_tomada_04 = st.radio('3 Tomadas padrão Nacional NBR14136',
                                    options=opcoes_ckl, index=idx_ckl_tomada_04, horizontal=True)
            ckl_balan_04 = st.radio('Estabilizador de Balança', 
                                    options=opcoes_ckl, index=idx_ckl_balan_04,  horizontal=True)
        with col2:    
            ckl_agua_04 = st.radio('10L de água purificada (WFI) a temperatura ambiente (23-25ºC)', 
                                    options=opcoes_ckl, index=idx_ckl_agua_04,  horizontal=True)
            ckl_conex_04 = st.radio('Tubulações e conexões triclamps de 1” e ½”', 
                                    options=opcoes_ckl, index=idx_ckl_conex_04, horizontal=True)
            ckl_veda_04 = st.radio('Abraçadeiras e vedações triclamps', 
                                    options=opcoes_ckl, index=idx_ckl_veda_04,  horizontal=True)
            ckl_freez_04 = st.radio('Geladeira/Freezer ou Estufas', 
                                    options=opcoes_ckl, index=idx_ckl_freez_04, horizontal=True)

        coment_04  = st.text_area('Comentários Checklist:', value= dados.get("coment_04", "") if dados else "")

    ################## Etapa 5 - Checklist do local  ##################
    st.markdown(':orange-background[Etapa 5 - Identificação do Material de Estudo]') 

    container5 = st.container(border=True)
    with container5:
        opcoes_gas = ['Nitrogênio','Ar Comprimido']
        try:
            valor_tipo_gas_05  = dados.get("tipo_gas_05", "")
        except:
            valor_tipo_gas_05 = 'Ar Comprimido'

        idx_tipo_gas_05  = opcoes_ckl.index(valor_tipo_gas_05)  if opcoes_ckl in opcoes_ckl  else 1     

        col1, col2, col3 = st.columns(3)
        with col1:
            linha_05  = st.text_input('Linha do Filtro:', max_chars= 40, value=dados.get("linha_05", "") if dados else "")
            cat_membr_05 = st.text_input('Nº Catálogo da Membrana:',max_chars= 40, value=dados.get("cat_membr_05", "") if dados else "")
        with col2:   
            fabricante_05 = st.text_input('Fabricante do Filtro:',max_chars= 40, value=dados.get("fabricante_05", "") if dados else "") 
            poro_cat_membr_05= st.text_input('Poro:', max_chars= 12, value=dados.get("poro_cat_membr_05", "") if dados else "")

        col1, col2, col3 = st.columns(3)
        with col1:
            temp_filtra_05 = st.text_input('Temperatura de Filtração (°C):', max_chars= 12, 
                                        value=dados.get("temp_filtra_05", "") if dados else "")
            tara_05  = st.text_input('Tara da Balança (g):', max_chars= 12, value=dados.get("tara_05", "") if dados else "")
            produto_05 = st.text_input('Produto', max_chars= 20, value=dados.get("produto_05", "") if dados else "")
            area_mem_05 = st.text_input('Area efetiva da membrana', max_chars= 20, value=dados.get("area_mem_05", "") if dados else "")
        with col2:   
            tmp_contato_05 = st.text_input('Tempo de Contato (h):', max_chars= 10, 
                                        value=dados.get("tmp_contato_05", "") if dados else "")  
            tempera_local_05 = st.text_input('Temperatura Local (°C):',max_chars= 12, 
                                          value=dados.get("tempera_local_05", "") if dados else "")
            lote_05 = st.text_input('Lote Do Produto:', max_chars= 12, value=dados.get("lote_05", "") if dados else "") 
            area_dis_05 = st.text_input('Area efetiva do dispositivo', max_chars= 20, value=dados.get("area_dis_05", "") if dados else "")
        with col3:  
            armaz_05 = st.text_input('Armazenagem Local:',max_chars= 20, value=dados.get("armaz_05", "") if dados else "")  
            umidade_05 = st.text_input('Umidade (%):',max_chars= 20, value=dados.get("umidade_05", "") if dados else "") 
            volume_05 = st.text_input('Volume:', max_chars= 12, value=dados.get("volume_05", "") if dados else "")   
            tipo_gas_05 = st.radio('Tipo de gás exigido', options=opcoes_gas, index=idx_tipo_gas_05) 

    ################## Etapa 6 - Lote / Catálogo / Serial  ##################
    st.markdown(':orange-background[Etapa 6 - Lote / Catálogo / Serial]')
    container6 = st.container(border=True)

    with container6:
        col1, col2, col3 = st.columns(3)   
        with col1:  
            lotem1_06 = st.text_input('Lote Membrana #1:', max_chars= 10, value=dados.get("lotem1_06", "") if dados else "") 
            lotes1_06 = st.text_input('Lote Serial #1:', max_chars= 10, value=dados.get("lotes1_06", "") if dados else "") 
            cat_disp_06 = st.text_input('Catálogo do Dispositivo:', max_chars= 12, value=dados.get("cat_disp_06", "") if dados else "") 
        with col2:  
            lotem2_06 = st.text_input('Lote Membrana #2:', max_chars= 10, value=dados.get("lotem2_06", "") if dados else "") 
            lotes2_06 = st.text_input('Lote Serial #2:', max_chars= 10, value=dados.get("lotes2_06", "") if dados else "")
            lote_disp_06 = st.text_input('Lote do Dispositivo:', max_chars= 10, value=dados.get("lote_disp_06", "") if dados else "")
        with col3:  
            lotem3_06 = st.text_input('Lote Membrana #3:', max_chars= 10, value=dados.get("lotem3_06", "") if dados else "") 
            lotes3_06 = st.text_input('Lote Serial #3:', max_chars= 10, value=dados.get("lotes3_06", "") if dados else "")
            serial_cat_disp_06 = st.text_input('Serial Dispositivo:', max_chars= 6, 
                                            value=dados.get("serial_cat_disp_06", "") if dados else "")    

    ################## Etapa 7 - Formulação  ##################
    st.markdown(':orange-background[Etapa 7 - Formulação]')
    container7 = st.container(border=True)
    with container7:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="text-align: center;"><h5>FORMULAÇÃO</h5></div>', unsafe_allow_html=True)
            form_01_07 = st.text_input('Fórmula 1:',   max_chars= 40, value= dados.get("form_01_07", "") if dados else "")
            form_02_07 = st.text_input('Fórmula 2:',   max_chars= 40, value= dados.get("form_02_07", "") if dados else "")
            form_03_07 = st.text_input('Fórmula 3:',   max_chars= 40, value= dados.get("form_03_07", "") if dados else "")
            form_04_07 = st.text_input('Fórmula 4:',   max_chars= 40, value= dados.get("form_04_07", "") if dados else "")
            form_05_07 = st.text_input('Fórmula 5:',   max_chars= 40, value= dados.get("form_05_07", "") if dados else "")
            form_06_07 = st.text_input('Fórmula 6:',   max_chars= 40, value= dados.get("form_06_07", "") if dados else "")
            form_07_07 = st.text_input('Fórmula 7:',   max_chars= 40, value= dados.get("form_07_07", "") if dados else "")
            form_08_07 = st.text_input('Fórmula 8:',   max_chars= 40, value= dados.get("form_08_07", "") if dados else "")
            form_09_07 = st.text_input('Fórmula 9:',   max_chars= 40, value= dados.get("form_09_07", "") if dados else "")
            form_10_07 = st.text_input('Fórmula 10:',  max_chars= 40, value= dados.get("form_10_07", "") if dados else "")

        with col2:
            st.markdown('<div style="text-align: center;"><h5>CONCENTRAÇÃO</h5></div>', unsafe_allow_html=True)
            conc_01_07 = st.text_input('Concentração 1:',   max_chars= 40, value= dados.get("conc_01_07", "") if dados else "") 
            conc_02_07 = st.text_input('Concentração 2:',   max_chars= 40, value= dados.get("conc_02_07", "") if dados else "")
            conc_03_07 = st.text_input('Concentração 3:',   max_chars= 40, value= dados.get("conc_03_07", "") if dados else "")
            conc_04_07 = st.text_input('Concentração 4:',   max_chars= 40, value= dados.get("conc_04_07", "") if dados else "")
            conc_05_07 = st.text_input('Concentração 5:',   max_chars= 40, value= dados.get("conc_05_07", "") if dados else "")
            conc_06_07 = st.text_input('Concentração 6:',   max_chars= 40, value= dados.get("conc_06_07", "") if dados else "")
            conc_07_07 = st.text_input('Concentração 7:',   max_chars= 40, value= dados.get("conc_07_07", "") if dados else "")
            conc_08_07 = st.text_input('Concentração 8:',   max_chars= 40, value= dados.get("conc_08_07", "") if dados else "")
            conc_09_07 = st.text_input('Concentração 9:',   max_chars= 40, value= dados.get("conc_09_07", "") if dados else "")
            conc_10_07 = st.text_input('Concentração 10:',  max_chars= 40, value= dados.get("conc_10_07", "") if dados else "")

    ################## Etapa 8 - Informações adicionais  ##################
    st.markdown(':orange-background[Etapa 8 - Informações adicionais]')
    try:
        valor_mat   = dados.get("ckl_mat_08", "")
        valor_sens  = dados.get("ckl_sens_08", "")   
    except:
        valor_mat   = 'Policarbonato' 
        valor_sens  = 'Sensibilidade ao Aço'

    opcoes_mat  = ['Silicone', 'Aço', 'Policarbonato', 'Nenhuma incompatibilidade conhecida']
    opcoes_sens = ['Sensível á Oxigênio', 'Sensível á Luz', 'Sensibilidade ao Aço','Sensibilidade a borbulhamento',
                   'Nenhuma sensibilidade conhecida']
    idx_mat  = opcoes_mat.index(valor_mat)   if valor_mat  in opcoes_mat  else 3
    idx_sens = opcoes_sens.index(valor_sens) if valor_sens in opcoes_sens else 4
    container8 = st.container(border=True)
    with container8:
        col1, col2 = st.columns(2)
        with col1:
            ckl_mat_08 = st.radio('Incompatibilidade do produto / material', options=opcoes_mat, index=idx_mat)
        with col2:    
            ckl_sens_08 = st.radio('Sensibilidade do Produto', options=opcoes_sens, index=idx_sens)

        estab_08 = st.text_input('Estabilidade do Produto:',  max_chars= 50, value= dados.get("estab_08", "") if dados else "")

    ################## Etapa 9 - Início  ##################
    st.markdown(':orange-background[Etapa 9 - Início]')
    container9 = st.container(border=True)
    with container9:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div style="height: 280px; display: flex; justify-content: center; align-items: center;">
                <div style="writing-mode: vertical-rl; transform: rotate(180deg); font-size: 20px;">
                    Pesagem Inicial (g)
                </div>
            </div>
        """, unsafe_allow_html=True)
        with col2:
            pi_memb_1_09 = st.number_input('Membrana #1 PI:', format=format_3casas, 
                                        value=float(dados.get("pi_memb_1_09", 0.0)) if dados else 0.0)   
            pi_memb_2_09 = st.number_input('Membrana #2 PI:', format=format_3casas, 
                                        value=float(dados.get("pi_memb_2_09", 0.0)) if dados else 0.0) 
            pi_memb_3_09 = st.number_input('Membrana #3 PI:', format=format_3casas, 
                                        value=float(dados.get("pi_memb_3_09", 0.0)) if dados else 0.0)
        with col3:   
            st.markdown("""
            <div style="height: 280px; display: flex; justify-content: center; align-items: center;">
                <div style="writing-mode: vertical-rl; transform: rotate(180deg); font-size: 20px;">
                    Fluxo Inicial (min)
                </div>
            </div>
        """, unsafe_allow_html=True)            
        with col4:   
            fli_memb_1_09 = st.text_input('Membrana #1 FI:', max_chars= 5, placeholder='MM:SS', 
                                       value=dados.get("fli_memb_1_09", "") if dados else "")
            fli_memb_2_09 = st.text_input('Membrana #2 FI:', max_chars= 5, placeholder='MM:SS', 
                                       value=dados.get("fli_memb_2_09", "") if dados else "")
            fli_memb_3_09 = st.text_input('Membrana #3 FI:', max_chars= 5, placeholder='MM:SS', 
                                       value=dados.get("fli_memb_3_09", "") if dados else "")

        st.divider()
        st.markdown('<div style="text-align: center;"><h5>Teste de Integridade - Fluido Padrão</h5></div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            pb_padraowfi_09 = st.number_input('PB Padrão Fluido Padrão (psi):', format=format_1casa, step=0.1, 
                                            value=float(dados.get("pb_padraowfi_09", 0.0)) if dados else 0.0)
        with col2:
            wfi_res1_09 = st.number_input('Fluido Padrão Resultado #1:', format=format_1casa, step=0.1, 
                                        value=float(dados.get("wfi_res1_09", 0.0)) if dados else 0.0)  
            wfi_res2_09 = st.number_input('Fluido Padrão Resultado #2:', format=format_1casa, step=0.1, 
                                        value=float(dados.get("wfi_res2_09", 0.0)) if dados else 0.0)
            wfi_res3_09 = st.number_input('Fluido Padrão Resultado #3:', format=format_1casa, step=0.1, 
                                        value=float(dados.get("wfi_res3_09", 0.0)) if dados else 0.0)
        with col3:
            wfi_id1_09 = st.text_input('Fluido Padrão ID #1:', max_chars= 20, value=dados.get("wfi_id1_09", "") if dados else "")  
            wfi_id2_09 = st.text_input('Fluido Padrão ID #2:', max_chars= 20, value=dados.get("wfi_id2_09", "") if dados else "")
            wfi_id3_09 = st.text_input('Fluido Padrão ID #3:', max_chars= 20, value=dados.get("wfi_id3_09", "") if dados else "")   

        st.divider()
        st.markdown('<div style="text-align: left;"><h5>Tempo de contato com o produto (Inicial)</h5></div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            dt_wfi_09 = st.text_input('Data:',placeholder='DD-MM-AAAA', value=dados.get("dt_wfi_09", "") if dados else "")
        with col2:
            hr_wfi_09 = st.text_input('Hora:',placeholder='HH:MM', value=dados.get("hr_wfi_09", "") if dados else "")
        
    ################## Etapa 10 - Tempo de contato  ##################   
    st.markdown(':orange-background[Etapa 10 - Tempo de contato]')
    container10 = st.container(border=True)
    with container10:
        texto1 = 'Realizar a análise visual.'
        texto2 = 'Registrar com fotográfico.'
        st.warning(f' :warning: ATENÇÃO !\n###### :point_right: {texto1} \n###### :point_right: {texto2} ')

        st.markdown('<div style="text-align: left;"><h5>Tempo de contato com o Produto (Final)</h5></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            dt_wfip_10 = st.text_input('Data Final:',placeholder='DD-MM-AAAA', 
                                    value=dados.get("dt_wfip_10", "") if dados else "")
        with col2:
            hr_wfip_10 = st.text_input('Hora Final:',placeholder='HH:MM', value=dados.get("hr_wfip_10", "") if dados else "")
        
        if dt_wfi_09 and hr_wfi_09 and dt_wfip_10 and hr_wfip_10:
            data1 = corrige_formato_dthr(dt_wfi_09  + ' ' + hr_wfi_09)
            data2 = corrige_formato_dthr(dt_wfip_10 + ' ' + hr_wfip_10)

        with col3:
            if dt_wfi_09 and hr_wfi_09 and dt_wfip_10 and hr_wfip_10:
                horas_contato_10, condicao = validar_datas_e_calcular_horas(data1, data2)
            else:
                horas_contato_10 = '00:00'    
            contato_wfip = st.text_input('Total de Horas:',value= str(horas_contato_10), disabled= True, 
                                        help='Diferença entre hora do teste Fluido Padrão e hora do teste de integridade do produto')


        st.markdown('<div style="text-align: center;"><h5>Teste de Integridade - PRODUTO</h5></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            pb_refproduto_10 = st.number_input('PB Referencial (psi):', format=format_1casa, 
                                            value=float(dados.get("pb_refproduto_10", 0.0)) if dados else 0.0, 
                                            help= 'Usar teste Referencial', step=0.1)
        with col2:
            prd_res1_10 = st.number_input('PB-P #1', format=format_1casa, step=0.1, 
                                        value=float(dados.get("prd_res1_10", 0.0)) if dados else 0.0)  
            prd_res2_10 = st.number_input('PB-P #2', format=format_1casa, step=0.1, 
                                        value=float(dados.get("prd_res2_10", 0.0)) if dados else 0.0)
            prd_res3_10 = st.number_input('PB-P #3', format=format_1casa, step=0.1, 
                                        value=float(dados.get("prd_res3_10", 0.0)) if dados else 0.0)
        with col3:
            prd_id1_10 = st.text_input('ID #1 Produto:', max_chars= 20, value=dados.get("prd_id1_10", "") if dados else "")  
            prd_id2_10 = st.text_input('ID #2 Produto:', max_chars= 20, value=dados.get("prd_id2_10", "") if dados else "")
            prd_id3_10 = st.text_input('ID #3 Produto:', max_chars= 20, value=dados.get("prd_id3_10", "") if dados else "")   

    ################## Etapa 11 - Cálculo da Vazão Final  ##################
    st.markdown(':orange-background[Etapa 11 - Cálculo da Vazão Final]')
    container11 = st.container(border=True)
    with container11:
        # texto1 = 'Enxaguar as membranas para o medir vazão final'
        # st.warning(f' :warning: AVISO\n###### :point_right: {texto1} ')
        st.markdown('<div style="text-align: left;"><h5>Fluxo Final (min)</h5></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            tmp_final1_11 = st.text_input('Tempo Final #1', max_chars= 5, placeholder='MM:SS', 
                                       value=dados.get("tmp_final1_11", "") if dados else "")
        with col2:   
            tmp_final2_11 = st.text_input('Tempo Final #2', max_chars= 5, placeholder='MM:SS', 
                                       value=dados.get("tmp_final2_11", "") if dados else "")
        with col3: 
            tmp_final3_11 = st.text_input('Tempo Final #3', max_chars= 5, placeholder='MM:SS', 
                                       value=dados.get("tmp_final3_11", "") if dados else "")

    ################## Etapa 12 - Teste de Integridade com Fluido Padrao - Final  ##################           
    st.markdown(':orange-background[Etapa 12 - Teste de Integridade com Fluido Padrao - Final]')
    container12 = st.container(border=True)
    with container12:
        texto1 = 'Enxaguar as membranas para teste de Integridade com Fluido Padrão Final'
        st.warning(f' :warning: AVISO\n###### :point_right: {texto1} ')

        st.markdown('<div style="text-align: center;"><h5>Teste de Integridade - Fluido Padrão</h5></div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            texto = f'PB Referencial : {pb_refproduto_10:.1f}'
            st.markdown(f"<div style='color: orange; font-size: 22px; font-weight: bold;'>{texto}</div>", unsafe_allow_html=True)

        with col2:
            res_padr1_12 = st.number_input('Resultado #1:', format=format_1casa, step=0.1, 
                                        value=float(dados.get("res_padr1_12", 0.0)) if dados else 0.0)  
            res_padr2_12 = st.number_input('Resultado #2:', format=format_1casa, step=0.1, 
                                        value=float(dados.get("res_padr2_12", 0.0)) if dados else 0.0)
            res_padr3_12 = st.number_input('Resultado #3:', format=format_1casa, step=0.1, 
                                        value=float(dados.get("res_padr3_12", 0.0)) if dados else 0.0)
        with col3:
            id_padr1_12 = st.text_input('ID #1:', max_chars= 20, value=dados.get("id_padr1_12", "") if dados else "")  
            id_padr2_12 = st.text_input('ID #2:', max_chars= 20, value=dados.get("id_padr2_12", "") if dados else "")
            id_padr3_12 = st.text_input('ID #3:', max_chars= 20, value=dados.get("id_padr3_12", "") if dados else "") 


    ################## Etapa 13 - Aferiçao de Massa Final  ##################
    st.markdown(':orange-background[Etapa 13 - Aferiçao de Massa Final]')
    container13 = st.container(border=True)
    with container13:
        texto1 = 'Secar as membranas antes da pesagem'
        st.warning(f' :warning: ATENÇÃO !\n###### :point_right: {texto1} ')

        st.markdown('<div style="text-align: left;"><h5>Pesagem Final (g)</h5></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: 
            pf_memb_1_13 = st.number_input('Peso Final #1:', format=format_3casas, step=0.01, 
                                        value=float(dados.get("pf_memb_1_13", 0.0)) if dados else 0.0)
        with col2:   
            pf_memb_2_13 = st.number_input('Peso Final #2:', format=format_3casas, step=0.01, 
                                        value=float(dados.get("pf_memb_2_13", 0.0)) if dados else 0.0) 
        with col3: 
            pf_memb_3_13 = st.number_input('Peso Final #3:', format=format_3casas, step=0.01, 
                                        value=float(dados.get("pf_memb_3_13", 0.0)) if dados else 0.0)

    ################## Etapa 14 - Teste de Integridade - Dispositivo  ##################        
    st.markdown(':orange-background[Etapa 14 - Teste de Integridade - Dispositivo]')
    container14 = st.container(border=True)
    with container14:
        col1, col2 = st.columns(2)
        with col1:
            peso_calc_14, erro = CalculaPBEstimado(prd_res1_10, prd_res2_10, prd_res3_10,
                      wfi_res1_09, wfi_res2_09, wfi_res3_09, pb_padraowfi_09)

            if erro == 0:
                texto = f'PB Calculado: {peso_calc_14}'
                st.info(f' ###### :point_right: {texto}')
            else:
                if erro >= 14 and erro <= 19:
                    message, etapa = ShowErro(erro=erro)
                    st.warning(f' ###### :point_right: {message} \n:warning: INVÁLIDO ! \n :mag_right: ETAPA :point_right: {etapa}') 
        with col2:
            if peso_calc_14 < pb_padraowfi_09:
                st.warning('PB Produto abaixo do valor esperado')

        col1, col2, col3 = st.columns(3)
        with col1:
            texto = 'Enxaguar o dispositivo por 10 min com Fluido Padrão corrente'
            st.info(f' ###### :material/Clock_Loader_40: {texto}')

        with col2:
            dis_res1_14 = st.number_input('Resultado #1 Dispositivo:', format=format_1casa, step=0.1, 
                                       value=float(dados.get("dis_res1_14", 0.0)) if dados else 0.0)  
            dis_res2_14 = st.number_input('Resultado #2 Dispositivo:', format=format_1casa, step=0.1, 
                                       value=float(dados.get("dis_res2_14", 0.0)) if dados else 0.0)

        with col3:
            dis_id1_14 = st.text_input('ID #1 Dispositivo:', max_chars= 20, value=dados.get("dis_id1_14", "") if dados else "")  
            dis_id2_14 = st.text_input('ID #2 Dispositivo:', max_chars= 20, value=dados.get("dis_id2_14", "") if dados else "")
        
    
    ################## Etapa 15 - Critérios de Avaliação  ##################
    st.markdown(':orange-background[Etapa 15 - Critérios de Avaliação]')    
    container15 = st.container(border=True)
    with container15:
        coluna_1, coluna_2 = st.columns([1,1])
        col1, col2 = st.columns(2)
        with col1:
            crit_var_peso_15 = st.number_input('Variação de Peso <= (%):', format=format_1casa, step=0.1, 
                                            value=float(dados.get("crit_var_peso_15", 0.0)) if dados else 10.0) 
            volume_ref_15 = st.number_input('Volume referencial (ml):', format='%d', step=10, 
                                            value=int(dados.get("volume_ref_15", 0)) if dados else 100)
        with col2:   
            crit_var_vazao_15 = st.number_input('Variação de Vazão <= (%):', format=format_1casa, step=0.1,
                                             value=float(dados.get("crit_var_vazao_15", 0.0)) if dados else 10.0)
    
    return {
        'relatorio': relatorio.strip(),
        'status_rel_01': status_rel_01.strip(),
        'dt_agendada_01': dt_agendada_01.strip() if dt_agendada_01 is not None else None, #### dt_agendada_01.strip(),
        'motivo_01': motivo_01 ,
        'dt_emissao_01': dt_emissao_01.strip() if dt_emissao_01 is not None else None, #### dt_emissao_01.strip(),
        'cliente': nome_empresa.strip(), #cliente,
        'local_realizado_02': local_realizado_02.strip(),
        'endereco_02': endereco_02.strip(),
        'cidade_02': cidade_02.strip(),
        'uf_02': uf_02.strip(),
        'cep_02': cep_02.strip(),
        'cnpj_02': cnpj_02.strip(),
        'tel_02': tel_02.strip(),
        'email_02': email_02.strip(),
        'local_teste_03': local_teste_03.strip(),
        'pessoa_local_03': pessoa_local_03.strip(),
        'dt_chegada_03': dt_chegada_03.strip(), 
        'hr_chegada_03': hr_chegada_03.strip(), 
        'setor_03': setor_03.strip(),
        'cargo_03': cargo_03,
        'id_sala_03': id_sala_03,
        'pedido_03': pedido_03,
        'coment_03': coment_03,
        'ckl_ponto_04': ckl_ponto_04.strip(),
        'ckl_espaco_04': ckl_espaco_04.strip(),
        'ckl_tomada_04': ckl_tomada_04.strip(),
        'ckl_balan_04': ckl_balan_04.strip(),
        'ckl_agua_04': ckl_agua_04.strip(),
        'ckl_conex_04': ckl_conex_04.strip(),
        'ckl_veda_04': ckl_veda_04.strip(),
        'ckl_freez_04': ckl_freez_04.strip(),
        'coment_04': RetiraCRLF(coment_04),
        "linha_05": linha_05.strip(),
        "fabricante_05": fabricante_05.strip(),
        "cat_membr_05": cat_membr_05.strip(),
        "poro_cat_membr_05":poro_cat_membr_05.strip(),
        "temp_filtra_05": temp_filtra_05.strip(),
        "tara_05": tara_05.strip(),
        "produto_05": produto_05.strip(),
        'area_mem_05': area_mem_05.strip().strip(),
        "tmp_contato_05": tmp_contato_05.strip(),
        'tempera_local_05':tempera_local_05.strip(),
        'lote_05':lote_05.strip(),
        'area_dis_05':area_dis_05.strip(),
        "armaz_05": armaz_05.strip(),
        'umidade_05':umidade_05.strip(),
        'volume_05':volume_05.strip(),
        'tipo_gas_05': tipo_gas_05.strip(),
        'lotem1_06':lotem1_06.strip(),
        'lotes1_06':lotes1_06.strip(),
        'cat_disp_06':cat_disp_06.strip(),
        'lotem2_06':lotem2_06.strip(),
        'lotes2_06':lotes2_06.strip(),
        'lote_disp_06':lote_disp_06.strip(),
        'lotem3_06':lotem3_06.strip(),
        'lotes3_06':lotes3_06.strip(),
        'serial_cat_disp_06':serial_cat_disp_06.strip(),
        'form_01_07': form_01_07.strip(),
        'conc_01_07': conc_01_07.strip(),
        'form_02_07': form_02_07.strip(),
        'conc_02_07': conc_02_07.strip(),
        'form_03_07': form_03_07.strip(),
        'conc_03_07': conc_03_07.strip(),
        'form_04_07': form_04_07.strip(),
        'conc_04_07': conc_04_07.strip(),
        'form_05_07': form_05_07.strip(),
        'conc_05_07': conc_05_07.strip(),
        'form_06_07': form_06_07.strip(),
        'conc_06_07': conc_06_07.strip(),
        'form_07_07': form_07_07.strip(),
        'conc_07_07': conc_07_07.strip(),
        'form_08_07': form_08_07.strip(),
        'conc_08_07': conc_08_07.strip(),
        'form_09_07': form_09_07.strip(),
        'conc_09_07': conc_09_07.strip(),
        'form_10_07': form_10_07.strip(),
        'conc_10_07': conc_10_07.strip(),
        'ckl_mat_08': ckl_mat_08.strip(),
        'ckl_sens_08': ckl_sens_08.strip(),
        'estab_08': estab_08.strip(),
        'pi_memb_1_09':pi_memb_1_09,
        'pi_memb_2_09':pi_memb_2_09,
        'pi_memb_3_09':pi_memb_3_09,
        'fli_memb_1_09':fli_memb_1_09.strip(),  # string_para_float(fli_memb_1_09),
        'fli_memb_2_09':fli_memb_2_09.strip(),  # string_para_float(fli_memb_2_09),
        'fli_memb_3_09':fli_memb_3_09.strip(),  # string_para_float(fli_memb_3_09),
        "pb_padraowfi_09": pb_padraowfi_09,
        'wfi_res1_09':wfi_res1_09,
        'wfi_res2_09':wfi_res2_09,
        'wfi_res3_09':wfi_res3_09,
        'wfi_id1_09':str(wfi_id1_09).strip(),
        'wfi_id2_09':str(wfi_id2_09).strip(),
        'wfi_id3_09':str(wfi_id3_09).strip(),
        'dt_wfi_09':dt_wfi_09.strip(), # dwfi,
        'hr_wfi_09': hr_wfi_09.strip(), # hwfi,
        'dt_wfip_10':dt_wfip_10.strip(), # dwfip,
        'hr_wfip_10': hr_wfip_10.strip(), # hwfip,
        'horas_contato_10': horas_contato_10.strip(), 
        'pb_refproduto_10':pb_refproduto_10,
        "prd_res1_10": prd_res1_10,
        "prd_res2_10": prd_res2_10,
        "prd_res3_10": prd_res3_10,
        'prd_id1_10':str(prd_id1_10).strip(),
        'prd_id2_10':str(prd_id2_10).strip(),
        'prd_id3_10':str(prd_id3_10).strip(),
        'tmp_final1_11': tmp_final1_11.strip(),  # string_para_float(tmp_final1_11),
        'tmp_final2_11': tmp_final2_11.strip(),  # string_para_float(tmp_final2_11),
        'tmp_final3_11': tmp_final3_11.strip(),  # string_para_float(tmp_final3_11),
        'res_padr1_12':res_padr1_12,
        'res_padr2_12':res_padr2_12,
        'res_padr3_12':res_padr3_12,
        'id_padr1_12':str(id_padr1_12).strip(),
        'id_padr2_12':str(id_padr2_12).strip(),
        'id_padr3_12':str(id_padr3_12).strip(),
        'pf_memb_1_13':pf_memb_1_13,
        'pf_memb_2_13':pf_memb_2_13,
        'pf_memb_3_13':pf_memb_3_13,
        'peso_calc_14': peso_calc_14,
        'dis_res1_14':dis_res1_14,
        'dis_res2_14':dis_res2_14,
        'dis_id1_14':dis_id1_14.strip(),
        'dis_id2_14':dis_id2_14.strip(),
        'crit_var_peso_15':crit_var_peso_15,
        'volume_ref_15':volume_ref_15,
        'crit_var_vazao_15':crit_var_vazao_15
    }, condicao

