"""
Serviço de conversão de arquivos DOCX para PDF.

Usa CloudConvert API com tratamento de erros robusto e seguro.
"""

import os
import requests
import cloudconvert
from typing import Optional
from core import (
    LoggerManager,
    ConversionError,
    ConfigurationError,
)
from config.settings import settings
from cloudconvert.exceptions.exceptions import (
    UnauthorizedAccess,
    ResourceNotFound,
    ConnectionError,
    BadRequest
)


logger = LoggerManager.get_logger(__name__)


class FileConversionService:
    """Serviço de conversão de arquivos."""
    
    def __init__(self):
        """Inicializa serviço com API key do CloudConvert."""
        try:
            self.api_key = settings.get_cloudconvert_api_key()
            cloudconvert.configure(api_key=self.api_key, sandbox=False)
            logger.info("CloudConvert configurado com sucesso")
        except ConfigurationError as e:
            logger.error(f"Erro ao configurar CloudConvert: {e}")
            raise
    
    def converter_para_pdf_bytes(self, input_file: str) -> bytes:
        """
        Converte DOCX para PDF e retorna os bytes.
        
        Args:
            input_file: Caminho do arquivo DOCX
            
        Returns:
            Bytes do arquivo PDF
            
        Raises:
            ConversionError: Se conversão falhar
        """
        try:
            logger.info(f"Iniciando conversão de {input_file}...")
            
            # Validar arquivo local
            if not os.path.exists(input_file):
                raise ConversionError(f"Arquivo '{input_file}' não encontrado")
            
            # Criar job
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
            
            # Upload
            upload_task_id = next(
                task["id"] for task in job["tasks"]
                if task["name"] == "import-1"
            )
            upload_task = cloudconvert.Task.find(id=upload_task_id)
            cloudconvert.Task.upload(file_name=input_file, task=upload_task)
            
            logger.info("Arquivo enviado, aguardando conversão...")
            
            # Aguardar processamento
            job_finished = cloudconvert.Job.wait(id=job["id"])
            
            # Verificar status
            export_task = next(
                task for task in job_finished["tasks"]
                if task["name"] == "export-1"
            )
            
            if export_task.get("status") == "error":
                error_msg = export_task.get("message", "Erro desconhecido")
                raise ConversionError(f"Erro na conversão: {error_msg}")
            
            if not export_task.get("result") or not export_task["result"].get("files"):
                raise ConversionError("Arquivo convertido não foi gerado")
            
            # Download
            pdf_url = export_task["result"]["files"][0]["url"]
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Conversão concluída com sucesso")
            return response.content
            
        except ConversionError:
            raise
        except UnauthorizedAccess as e:
            logger.error(f"Erro de autenticação CloudConvert: {e}")
            raise ConversionError("Credenciais inválidas do CloudConvert")
        except ConnectionError as e:
            logger.error(f"Erro de conexão com CloudConvert: {e}")
            raise ConversionError("Erro de conexão com CloudConvert")
        except BadRequest as e:
            logger.error(f"Requisição inválida para CloudConvert: {e}")
            raise ConversionError("Parâmetros inválidos para conversão")
        except Exception as e:
            logger.error(f"Erro inesperado na conversão: {e}")
            raise ConversionError(f"Erro na conversão: {e}")
    
    def converter_para_arquivo(
        self,
        input_file: str,
        output_file: str
    ) -> None:
        """
        Converte DOCX para PDF e salva em arquivo.
        
        Args:
            input_file: Caminho do arquivo DOCX
            output_file: Caminho do arquivo PDF de saída
            
        Raises:
            ConversionError: Se conversão falhar
        """
        try:
            pdf_bytes = self.converter_para_pdf_bytes(input_file)
            
            # Salvar arquivo
            with open(output_file, "wb") as f:
                f.write(pdf_bytes)
            
            logger.info(f"PDF salvo em {output_file}")
            
        except ConversionError:
            raise
        except IOError as e:
            logger.error(f"Erro ao salvar arquivo {output_file}: {e}")
            raise ConversionError(f"Erro ao salvar PDF: {e}")
