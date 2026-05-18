"""
Módulo utils - Utilitários da aplicação.
"""

from utils.formatters import (
    formatar_moeda_br,
    validar_datas_e_calcular_horas,
    ShowErro,
    RetiraCRLF,
    remover_linhas_em_branco,
)
import importlib.util
import os

# Importar string_para_float do arquivo utils.py na raiz do projeto
_utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils.py')
spec = importlib.util.spec_from_file_location("utils_module", _utils_path)
utils_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils_module)
string_para_float = utils_module.string_para_float

__all__ = [
    "formatar_moeda_br",
    "validar_datas_e_calcular_horas",
    "ShowErro",
    "RetiraCRLF",
    "remover_linhas_em_branco",
    "string_para_float",
]
