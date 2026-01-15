import streamlit as st
import os

# session_state dá a informação de quem está logado no navegador na hora de entrar no site

sessao_usuario = st.session_state
#st.write(sessao_usuario)
nome_usuario = None
if 'username' in sessao_usuario:
    nome_usuario = sessao_usuario.name

coluna_esquerda, coluna_direita = st.columns([1,1.5]) # Cria 2 colunas e a segunda é 50% maior que a primeira

coluna_esquerda.title('SA SOLUTIONS')
coluna_esquerda.markdown("##### :orange[Gerador de propostas comerciais]") 
coluna_esquerda.markdown("##### :orange[Gerador de relatórios]")
coluna_esquerda.markdown("##### ") # Gera espaço entre otítulo e Versão

coluna_esquerda.markdown("#### :blue-background[Versão 2.2]") 
if nome_usuario:
    coluna_esquerda.write(f'#### Bem vindo, {nome_usuario}')  # markdown

conteiner = coluna_direita.container(border=False)
caminho_img = os.path.join("Imagens","logoSite.png")
conteiner.image(caminho_img) 

if "ger_aba" in st.session_state:
    st.session_state.ger_aba = "Listar"
