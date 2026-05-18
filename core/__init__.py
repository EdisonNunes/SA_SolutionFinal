"""
Módulo core - Funcionalidades essenciais da aplicação.
"""

from core.logger import LoggerManager
from core.database import get_supabase_client, get_db
from core.exceptions import (
    SAError,
    DatabaseError,
    ValidationError,
    ConfigurationError,
    ConversionError,
    ClienteNotFoundError,
    ServicoNotFoundError,
    PropostaNotFoundError,
    DuplicateClienteError,
    DuplicateServicoError,
)

__all__ = [
    "LoggerManager",
    "get_supabase_client",
    "get_db",
    "SAError",
    "DatabaseError",
    "ValidationError",
    "ConfigurationError",
    "ConversionError",
    "ClienteNotFoundError",
    "ServicoNotFoundError",
    "PropostaNotFoundError",
    "DuplicateClienteError",
    "DuplicateServicoError",
]
