import streamlit as st
import os
import cloudconvert
import requests
from docx import Document
import io

# Configurações
CLOUDCONVERT_API_KEY = st.secrets["cloudconvert"]["CLOUDCONVERT_API_KEY"]
TEMPLATE_PATH = 'matriz.docx'

def preencher_template(template_path, num_proposta):
    """Preenche o template e retorna o conteúdo binário do DOCX."""
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        if '{{NUMERO}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{NUMERO}}', num_proposta)
    
    # Salva em um buffer de memória em vez de arquivo físico se possível, 
    # mas para o CloudConvert upload precisamos de um arquivo real ou buffer compatível.
    temp_name = f"temp_{num_proposta}.docx"
    doc.save(temp_name)
    return temp_name

def converter_para_pdf(input_file):
    """Realiza a conversão e retorna os bytes do PDF."""
    cloudconvert.configure(api_key=CLOUDCONVERT_API_KEY, sandbox=False)
    job = cloudconvert.Job.create(payload={
        "tasks": {
            "import-1": {"operation": "import/upload"},
            "convert-1": {"operation": "convert", "input": "import-1", "output_format": "pdf", "engine": "office"},
            "export-1": {"operation": "export/url", "input": "convert-1"}
        }
    })
    
    upload_task_id = next(task['id'] for task in job['tasks'] if task['name'] == 'import-1')
    upload_task = cloudconvert.Task.find(id=upload_task_id)
    cloudconvert.Task.upload(file_name=input_file, task=upload_task)
    
    job_finished = cloudconvert.Job.wait(id=job['id'])
    export_task = next(task for task in job_finished['tasks'] if task['name'] == 'export-1')
    pdf_url = export_task['result']['files'][0]['url']
    return requests.get(pdf_url).content

# Interface Streamlit
st.title("Gerador de Propostas PDF")

num_proposta = st.text_input("Número da Proposta", value="12345")

if st.button("Processar Documento"):
    with st.spinner("Gerando e convertendo... aguarde."):
        try:
            # 1. Gerar DOCX temporário
            temp_docx = preencher_template(TEMPLATE_PATH, num_proposta)
            
            # 2. Converter para PDF
            pdf_bytes = converter_para_pdf(temp_docx)
            
            # 3. Limpar temporário
            os.remove(temp_docx)
            
            # 4. Disponibilizar para Download
            st.success("Conversão concluída!")
            st.download_button(
                label="Clique aqui para baixar o PDF",
                data=pdf_bytes,
                file_name=f"Proposta_{num_proposta}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erro: {e}")
