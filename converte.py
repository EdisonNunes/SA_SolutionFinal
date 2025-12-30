#------------  Edison
# Você é um especialista em tratamento de dados na linguagem python.
# Crie uma função em python  que :
# 1. Leia um documento do word chamado "teste.docx"
# 2. Esse arquivo contém cabeçalho, logotipo, rodapé e tabelas
# 3. Envie esse documento para a API CloudConvert cuja chave é: CLOUDCONVERT_API_KEY 
# 4. O retorno da API deverá ser um arquivo chamado "teste.pdf" que seja uma cópia exata do arquivo docx
# 5. O arquivo teste.docx e teste.pdf estarão no diretório raiz da aplicação assim como o logotipo logo.png
# 6. Utilize a biblioteca "cloudconvert" para essa função
#------------  Manus
# Aqui está a função em Python que você solicitou. 
# Ela utiliza a biblioteca oficial cloudconvert para realizar a conversão de um 
# arquivo Word (teste.docx) para PDF (teste.pdf), garantindo a preservação de todos os 
# elementos visuais como cabeçalhos, rodapés, logotipos e tabelas.
# Detalhes da Implementação
# A função converter_docx_para_pdf segue o fluxo de trabalho recomendado pela API v2 do CloudConvert:
# Configuração: Inicializa o cliente com sua chave de API.
# Criação do Job: Define um conjunto de tarefas que inclui o upload do arquivo, 
# a conversão (usando o motor office para máxima fidelidade) e a exportação para uma URL de download.
# Upload: Envia o arquivo local teste.docx para os servidores do CloudConvert.
# Processamento: Aguarda a conclusão de todas as tarefas no servidor.
# Download: Recupera o arquivo convertido e o salva localmente como teste.pdf.
# Aqui está a versão atualizada da função, agora com um sistema robusto de tratamento de erros para lidar com as situações mais comuns ao utilizar a API CloudConvert.
# Principais Melhorias no Tratamento de Erros
# Validação de Arquivo Local: Antes de chamar a API, a função verifica se o arquivo teste.docx realmente existe no diretório, evitando erros desnecessários de rede.
# Tratamento de Autenticação (UnauthorizedAccess): Captura especificamente falhas relacionadas à chave de API inválida ou expirada.
# Erros de Conexão (ConnectionError): Lida com problemas de internet ou instabilidades nos servidores da CloudConvert.
# Erros de Processamento da API: Verifica o status das tarefas dentro do Job. Se a conversão falhar no servidor (por exemplo, um documento corrompido), a função captura a mensagem de erro retornada pela API.
# Parâmetros Inválidos (BadRequest): Captura erros caso a estrutura da requisição esteja incorreta

import cloudconvert
import os
import streamlit as st
import requests

CLOUDCONVERT_API_KEY = st.secrets["cloudconvert"]["CLOUDCONVERT_API_KEY"]
# [cloudconvert]
# CLOUDCONVERT_API_KEY= "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNWQxZGViODMxODA5NmM0MjgzM2MyYTY5ODM1Y2ZkZDE0MTY0OGMyOTY0ZTdkMGRkZDZmNGE3MzlkYTg2MzEzYWI1OTUyMDRmZTc5YjE5NWQiLCJpYXQiOjE3NjY1OTgwMjAuMjQzNDQyLCJuYmYiOjE3NjY1OTgwMjAuMjQzNDQzLCJleHAiOjQ5MjIyNzE2MjAuMjM4ODQ2LCJzdWIiOiI3MzgwNTg1NCIsInNjb3BlcyI6WyJ1c2VyLnJlYWQiLCJ1c2VyLndyaXRlIiwidGFzay5yZWFkIiwidGFzay53cml0ZSIsIndlYmhvb2sucmVhZCIsIndlYmhvb2sud3JpdGUiLCJwcmVzZXQucmVhZCIsInByZXNldC53cml0ZSJdfQ.NOa8TN9JB38LzCk4hiAsZATj8SIET4TKT6DSLE5UxFOoKHNW4qOhh7JzNFDsArXSYqqopTyOvs5Mv3secPFXWnyyZdgWoxeiAHMukSERRv07iblgII2yWP2NEUAwvWnuq74vCh3aGfKrNo40c_JMvaIMpX3155U9VXysbaqXuyoqy-f-CaGjmhWx0SvBl8_ThMAq32KfqFX-csIo6384xhguextSmCGfcny9dERn-ESVq6oXr_AnE0pruD8qNXwRjqF9iwRSF9SiXclX73I83xCTKZxr5AG_lrwo47eHkphXBphEwF4hk08oEcOA4Ux0VVA7f7QUAvHWnVgzQSt8GVdQqWn68UQaXqewkt8d0dhsEbc7KR77wXed_lly7JuBsvP5Z7z1EWt2HJ-AerqGc49QukQXIEmAT3ETdk9jEeMUKXsCX9ZneE3wRq43UV8fnMeQmoTB1xCoy9uwVKQg0Wma0LjZDF1MSBiBCkCr54_ngu64_Q8schOwn83RkOKvpZ8gCR76Puf8S72vSSO0Dq1Jmq3QInW1aH56EjLFBjMwnZICpPHJiUJY2WKJpSq7hOthWB_kt82lz8TjjrHxAwVglxjRbSmzhl4Mmnt1ba9e-7-krVg9lgjLpwH1wz0y-uX6PlVsPKA-g4TAp5c6rtELBUQNuU3-YIvrcUUhmSs"
# CLOUDCONVERT_API_KEY= "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiN2YwZTViMzI4MGNmNDBlNzhjN2M0ZmU0NTkxMDAwMDI1MzJiZjYzZjUzOWIzM2NhMjY3MDZmNWE3NzIzNGFjYTAwMzMyMWQxNjQ2ZjY1MTciLCJpYXQiOjE3NjcwMDY3NTAuMDcyNjksIm5iZiI6MTc2NzAwNjc1MC4wNzI2OTEsImV4cCI6NDkyMjY4MDM1MC4wNjY5NDksInN1YiI6IjczODI4NDA5Iiwic2NvcGVzIjpbInVzZXIucmVhZCIsInVzZXIud3JpdGUiLCJ0YXNrLnJlYWQiLCJ0YXNrLndyaXRlIiwid2ViaG9vay5yZWFkIiwid2ViaG9vay53cml0ZSIsInByZXNldC5yZWFkIiwicHJlc2V0LndyaXRlIl19.m_uUV0QiMDbc_BLgiDXw1vq13ZxK6PnwJ9nIyCkFJtwpJvDGTuSm6BjQ5WHlK_p7lb6X6cg6PY_dbZuz1suB_A-aamjBFg0OwEAXH875iP8WE7_vMTZZ8bCSWufqDnXA187n-KbZMCsZnudz_SfV9DghiuQmrmVy-bwmSTpZYkJOeH25eHkIeLIMUr7Rt_TlslehzqJgnK0pCnhGRGHDbA0zyu5NJ1d7IoAdBppZzaXN8F0p_dEH_L7zbRFe7TMWXEKHLQX4635pn15SQzE_mNcw2qsKzpE8Sj_cBky821-mYxP6Tcdz7wIZEgSaaqsQeVSMCY7FMKJBlAEwcrt0bpeSU7lDcJotpBQIBMShd0OvgKVaGxzdU98wuwYBNmceShWdjs3SbUQYUxZhB1TbqFz9rlYEWt6yqY1sWQDUAurQeZqPr5wnksYQGXV20Muc4DjItMFdMEeI5aMY51L-DyqkYEkfcEjizOh49qbJ2SoyRbITTdAqEP34b0FQWqf9zzyHlGVCfx2eaCfyrx2TFQd_mDw4MYDCiU9XMNz08Xzqm0Mg8qEfTH-XeKmaLJ8HHQOI6vkHeJWAEF5l_GJEYZfNfOQftiJF61uJV3TXaVMbR79XarnPf6QBHY4lCw_HCf1qrf8uyE24DZLeCpejZPep4OneweG0ItWHM_4R-bQ"


# Importação corrigida para a estrutura interna da biblioteca
from cloudconvert.exceptions.exceptions import (
    UnauthorizedAccess, 
    ResourceNotFound, 
    ConnectionError, 
    BadRequest
)

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


def converter_docx_para_pdf(api_key, docx_file='temp.docx', pdf_file='teste.pdf'):
    """
    Converte um arquivo DOCX para PDF usando a API CloudConvert com tratamento de erros corrigido.
    """
    try:
        # 1. Validação do arquivo local
        if not os.path.exists(docx_file):
            print(f"Erro: O arquivo '{docx_file}' não foi encontrado no diretório raiz.")
            return

        # 2. Configuração da API
        cloudconvert.configure(api_key=api_key, sandbox=False)

        print(f"Iniciando conversão de '{docx_file}'...")

        # 3. Criação do Job
        try:
            job = cloudconvert.Job.create(payload={
                "tasks": {
                    "import-1": {"operation": "import/upload"},
                    "convert-1": {
                        "operation": "convert",
                        "input": "import-1",
                        "output_format": "pdf",
                        "engine": "office"
                    },
                    "export-1": {"operation": "export/url", "input": "convert-1"}
                }
            })
        except UnauthorizedAccess:
            print("Erro de Autenticação: A chave da API CloudConvert é inválida.")
            return
        except BadRequest as e:
            print(f"Erro na Requisição: Verifique os parâmetros. {e}")
            return

        # 4. Upload do arquivo
        upload_task_id = next(task['id'] for task in job['tasks'] if task['name'] == 'import-1')
        upload_task = cloudconvert.Task.find(id=upload_task_id)
        
        print("Realizando upload...")
        cloudconvert.Task.upload(file_name=docx_file, task=upload_task)

        # 5. Aguardar processamento
        print("Aguardando conversão (isso pode levar alguns segundos)...")
        job_finished = cloudconvert.Job.wait(id=job['id'])

        # 6. Verificar status e baixar resultado
        export_task = next(task for task in job_finished['tasks'] if task['name'] == 'export-1')
        
        if export_task.get('status') == 'error':
            print(f"Erro no processamento da API: {export_task.get('message')}")
            return

        if export_task.get('result') and export_task['result'].get('files'):
            file_info = export_task['result']['files'][0]
            cloudconvert.download(filename=pdf_file, url=file_info['url'])
            print(f"Sucesso! Arquivo convertido salvo como: {pdf_file}")
        else:
            print("Erro: O arquivo convertido não foi gerado.")

    except ConnectionError as e:
        print(f"Erro de Conexão: Não foi possível conectar à API. {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


