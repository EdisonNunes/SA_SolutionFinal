from docx import Document   # pip install python-docx
from docx.shared import Pt
from datetime import datetime
# from converte import converter_docx_para_pdf
import streamlit as st

CLOUDCONVERT_API_KEY = st.secrets["cloudconvert"]["CLOUDCONVERT_API_KEY"]

# ======================================================
# 1. Função auxiliar: substituição de TAGS
# ======================================================
def substituir_tags(paragrafo, tags: dict):
    """
    Substitui tags dentro de um parágrafo do Word.
    Exemplo:
        substituir_tags(p, {"{{CLIENTE}}": "Cristália"})
    """

    if not paragrafo.text:
        return
    
    for chave, valor in tags.items():
        if chave in paragrafo.text:
            paragrafo.text = paragrafo.text.replace(chave, str(valor))

# ======================================================
# 2. Geração do documento Word
# ======================================================
def gerar_documento_pdf(
    supabase,
    id_proposta: int,
    caminho_template: str,
    caminho_saida: str
):
    # -------------------------------
    # Buscar dados da proposta
    # -------------------------------
    proposta = (
        supabase.table("propostas")
        .select("*")
        .eq("id_proposta", id_proposta)
        .single()
        .execute()
    ).data

    cliente = (
        supabase.table("clientes")
        .select("*")
        .eq("id", proposta["id_cliente"])
        .single()
        .execute()
    ).data

    itens = (
        supabase.table("itens_proposta")
        .select("*")
        .eq("id_proposta", id_proposta)
        .execute()
    ).data

    # -------------------------------
    # Carregar template
    # -------------------------------
    doc = Document(caminho_template)

    # -------------------------------
    # Criar dicionário de TAGS
    # -------------------------------
    data_emissao_formatada = datetime.strptime(
        proposta["data_emissao"], "%Y-%m-%d"
    ).strftime("%d/%m/%Y")

    tags = {
        "{{NUM_PROPOSTA}}": proposta["num_proposta"],
        "{{DATA_EMISSAO}}": data_emissao_formatada,
        "{{VALIDADE}}": proposta["validade"],
        "{{COND_PAGAMENTO}}": proposta["cond_pagamento"],
        "{{REFERENCIA}}": proposta["referencia"],

        # Dados do cliente
        "{{ID}}": cliente["id"],
        "{{CLIENTE}}": cliente["empresa"],
        "{{CNPJ}}": cliente["cnpj"],
        "{{ENDERECO}}": cliente["endereco"],
        "{{CIDADE}}": cliente["cidade"],
        "{{UF}}": cliente["uf"],
        "{{CONTATO}}": cliente["contato"],
        "{{EMAIL}}": cliente["email"],
        "{{TELEFONE}}": cliente["telefone"],
    }

    # -------------------------------
    # Substituir tags no documento
    # -------------------------------
    for p in doc.paragraphs:
        substituir_tags(p, tags)
        # Arial 8 somente para conteúdo
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(8)

    # -------------------------------
    # Substituir tags em todas as tabelas
    # -------------------------------
    for tabela in doc.tables:
        for linha in tabela.rows:
            for cel in linha.cells:
                for p in cel.paragraphs:
                    substituir_tags(p, tags)
                    # Arial 8
                    for run in p.runs:
                        run.font.name = "Arial"
                        run.font.size = Pt(8)
    # -------------------------------
    # Substituir tags no rodapé
    # -------------------------------
    for section in doc.sections:
        footer = section.footer
        for p in footer.paragraphs:
            substituir_tags(p, tags)
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(5) # Tamanho 5

    # ================================
    # 4) TABELA DE ITENS (SEGUNDA TABELA!)
    # ================================
    tabela_itens = doc.tables[1]   # <-- AQUI!

    # Validar número de colunas
    if len(tabela_itens.rows[0].cells) != 8:
        raise ValueError("A tabela do template deve ter 8 colunas.")

    # Remover TODAS as linhas após o cabeçalho
    while len(tabela_itens.rows) > 1:
        tabela_itens._element.remove(tabela_itens.rows[-1]._element)

    # ================================
    # 5) ADICIONAR ITENS
    # ================================
    total_proposta = 0

    for idx, item in enumerate(itens, start=1):
        qtd = float(item["qtd"])
        preco = float(item["preco_unitario"])
        desconto = float(item["desconto"])

        total_item = (qtd * preco) - (preco * desconto / 100)
        total_proposta += total_item

        linha = tabela_itens.add_row().cells

        linha[0].text = str(idx)
        linha[1].text = item["codigo_servico"]
        linha[2].text = item["descricao_servico"]
        linha[3].text = item["prazo_ddl"]
        linha[4].text = str(int(qtd))
        linha[5].text = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        linha[6].text = f"{desconto:.0f}%"
        linha[7].text = f"R$ {total_item:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        # aplica fonte Arial 8
        for cel in linha:
            for par in cel.paragraphs:
                for run in par.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8)
    # ================================
    # 6) LINHA EM BRANCO
    # ================================
    linha_vazia = tabela_itens.add_row().cells
    for cel in linha_vazia:
        par = cel.paragraphs[0]
        run = par.add_run(" ")
        run.font.name = "Arial"
        run.font.size = Pt(8)

    # ================================
    # 7) LINHA SUB.TOTAL
    # ================================
    linha_total = tabela_itens.add_row().cells

    linha_total[5].text = "Sub.Total:"
    linha_total[7].text = (
        f"R$ {total_proposta:,.2f}"
        .replace(",", "X").replace(".", ",").replace("X", ".")
    )
    for cel in linha_total:
        for par in cel.paragraphs:
            for run in par.runs:
                run.font.name = "Arial"
                run.font.size = Pt(8)

    
    doc.save('temp.docx')

    return caminho_saida
