"""
Exceções personalizadas para SA Solutions.

Define exceções específicas do domínio para tratamento de erros mais preciso.
"""


class SAError(Exception):
    """Exceção base para SA Solutions."""
    pass


class DatabaseError(SAError):
    """Erro ao interagir com o banco de dados."""
    pass


class ValidationError(SAError):
    """Erro de validação de dados."""
    pass


class ConfigurationError(SAError):
    """Erro de configuração da aplicação."""
    pass


class ConversionError(SAError):
    """Erro ao converter arquivo (DOCX para PDF)."""
    pass


class ClienteNotFoundError(DatabaseError):
    """Cliente não encontrado no banco."""
    pass


class ServicoNotFoundError(DatabaseError):
    """Serviço não encontrado no banco."""
    pass


class PropostaNotFoundError(DatabaseError):
    """Proposta não encontrada no banco."""
    pass


class DuplicateClienteError(ValidationError):
    """Cliente duplicado (empresa + cidade já existe)."""
    pass


class DuplicateServicoError(ValidationError):
    """Serviço duplicado (descrição já existe)."""
    pass
