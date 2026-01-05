import streamlit as st

st.set_page_config(layout="wide", page_title="SA Solutions")
#import streamlit_authenticator as stauth

# SA_SOLUTIONFINAL/
# ├── .gitignore
# ├── .streamlit/
# │   └── config.toml              # Configurações de layout do Streamlit 
# │   └── secrets.toml             # Arquivo local com segredos (SUPABASE + CLOUDCONVERTER)
# ├── main.py                      # Arquivo principal do Streamlit
# ├── requirements.txt             # Dependências do projeto
# ├── crud.py                      # Código para conexão e CRUD com Supabase
# ├── utils.py                     # Funções auxiliares
# ├── clientes.py                  # Cadastro de Clientes
# ├── servicos.py                  # Cadastro de Serviços 
# ├── compatquimica.py             # Planilha de Compatibilidade Química
# ├── Base.py                      # Preenchimento do Relatório de Cmpatibilidade Química
# ├── calculos.py                  # Cálculos para o Relatório de Cmpatibilidade Química
# ├── pontobolha.py                # Planilha de Ponto Bolha
# ├── exporta_cli.py               # Exporta Cadastro de Clientes
# ├── exporta_rel.py               # Exporta Relatório de Cmpatibilidade Química
# ├── exporta_serv.py              # Exporta Serviços
# └── README.md


# CSS para esconder os botões do canto superior direito
# hide_streamlit_style = """
#     <style>
#     button[title="Open GitHub"] {visibility: hidden;}  }
#     button[title="Edit this app"] {visibility: hidden;}
#     /* Esconda ícones de configurações se necessário */
#     [data-testid="stToolbar"] {visibility: hidden;}
#     </style>
# """
hide_streamlit_style = """
    <style>
    button[title="Open GitHub"] {display: none;}  }
    button[title="Edit this app"] {display: none;}
    /* Esconda ícones de configurações se necessário */
    [data-testid="stToolbar"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

pg = st.navigation(
    {              
        'SA SOLUTION':[st.Page('homepage.py',   title='Home',               icon=':material/filter_alt:')],
        'Propostas': [st.Page('proposta.py',    title='Proposta Comercial', icon=':material/amend:')], 
        'Gerenciar Relatórios':  [
                       st.Page('compatquimica.py',      title='Compatibilidade Química',    icon=':material/thumb_up:'),
                       st.Page('pontobolha.py',     title='Ponto de Bolha',             icon=':material/thumb_up:'),
                       st.Page('exporta_rel.py',    title='Exporta Relatório',          icon=':material/csv:')
                      ],
        'Cadastros':   [
                        st.Page('clientes.py',      title='Cadastro de Clientes',   icon=':material/groups:'),
                        st.Page('exporta_cli.py',   title='Exporta Clientes',       icon=':material/csv:'),
                        st.Page('servicos.py',      title='Cadastro de Serviços',   icon=':material/add_shopping_cart:'),
                        st.Page('exporta_serv.py',  title='Exporta Serviços',       icon=':material/csv:'),
                        ] 
    }
)

pg.run()


# https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
# Google's Material Symbols font library
# https://fonts.google.com/icons