import os
import logging
from typing import Optional

import cloudconvert
import requests

try:
    import streamlit as st
except ImportError:
    st = None

from cloudconvert.exceptions.exceptions import (
    UnauthorizedAccess,
    ConnectionError,
    BadRequest,
)

logger = logging.getLogger(__name__)


def _get_cloudconvert_api_key(api_key: Optional[str] = None) -> str:
    if api_key:
        return api_key

    if st is not None:
        try:
            return st.secrets["cloudconvert"]["CLOUDCONVERT_API_KEY"]
        except Exception:
            pass

    api_key = os.getenv("CLOUDCONVERT_API_KEY")
    if api_key:
        return api_key

    raise RuntimeError(
        "CloudConvert API key not found. "
        "Set CLOUDCONVERT_API_KEY environment variable or add it to Streamlit secrets."
    )


def _configure_cloudconvert(api_key: str) -> None:
    cloudconvert.configure(api_key=api_key, sandbox=False)


def _download_pdf_from_export_task(job_finished: dict) -> bytes:
    export_task = next(
        (task for task in job_finished.get("tasks", []) if task.get("name") == "export-1"),
        None,
    )

    if export_task is None:
        raise RuntimeError("Export task 'export-1' not found in CloudConvert job result.")

    if export_task.get("status") == "error":
        raise RuntimeError(
            f"CloudConvert export task failed: {export_task.get('message', 'unknown error')}"
        )

    result = export_task.get("result", {})
    files = result.get("files")
    if not files:
        raise RuntimeError("CloudConvert did not return any files for the export task.")

    pdf_url = files[0].get("url")
    if not pdf_url:
        raise RuntimeError("CloudConvert export task did not provide a PDF URL.")

    response = requests.get(pdf_url)
    response.raise_for_status()
    return response.content


def converter_para_pdf(input_file: str, api_key: Optional[str] = None) -> bytes:
    """
    Converte um arquivo DOCX para PDF usando a API CloudConvert e retorna os bytes do PDF.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

    api_key = _get_cloudconvert_api_key(api_key)
    _configure_cloudconvert(api_key)

    try:
        job = cloudconvert.Job.create(
            payload={
                "tasks": {
                    "import-1": {"operation": "import/upload"},
                    "convert-1": {
                        "operation": "convert",
                        "input": "import-1",
                        "output_format": "pdf",
                        "engine": "office",
                    },
                    "export-1": {"operation": "export/url", "input": "convert-1"},
                }
            }
        )
    except UnauthorizedAccess as exc:
        raise RuntimeError(
            "Erro de autenticação CloudConvert: chave inválida ou não autorizada."
        ) from exc
    except BadRequest as exc:
        raise RuntimeError(
            f"Requisição inválida para CloudConvert: {exc}"
        ) from exc

    upload_task_id = next(
        task["id"] for task in job.get("tasks", []) if task.get("name") == "import-1"
    )
    upload_task = cloudconvert.Task.find(id=upload_task_id)
    cloudconvert.Task.upload(file_name=input_file, task=upload_task)

    job_finished = cloudconvert.Job.wait(id=job["id"])
    return _download_pdf_from_export_task(job_finished)


def converter_docx_para_pdf(
    api_key: Optional[str] = None,
    docx_file: str = "temp.docx",
    pdf_file: str = "teste.pdf",
) -> bytes:
    """
    Converte um arquivo DOCX para PDF usando a API CloudConvert e salva o PDF localmente.
    """
    pdf_bytes = converter_para_pdf(docx_file, api_key=api_key)

    with open(pdf_file, "wb") as output_file:
        output_file.write(pdf_bytes)

    return pdf_bytes


