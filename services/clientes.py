"""
Serviço de gerenciamento de clientes.

Fornece operações CRUD para clientes com validação e tratamento de erros.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from core import (
    get_db,
    LoggerManager,
    DatabaseError,
    ValidationError,
    DuplicateClienteError,
    ClienteNotFoundError,
)
from config.settings import settings


logger = LoggerManager.get_logger(__name__)


@dataclass
class ClienteValidator:
    """Validador de dados de cliente."""
    
    @staticmethod
    def validar_empresa(empresa: str) -> None:
        """Valida campo empresa."""
        if not empresa or not empresa.strip():
            raise ValidationError("Empresa não pode estar vazia")
        if len(empresa) > settings.MAX_EMPRESA_LENGTH:
            raise ValidationError(
                f"Empresa não pode ter mais de {settings.MAX_EMPRESA_LENGTH} caracteres"
            )
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> None:
        """Valida campo CNPJ."""
        if not cnpj or not cnpj.strip():
            raise ValidationError("CNPJ não pode estar vazio")
        if len(cnpj) > settings.MAX_CNPJ_LENGTH:
            raise ValidationError(f"CNPJ inválido (máx {settings.MAX_CNPJ_LENGTH} caracteres)")
    
    @staticmethod
    def validar_email(email: str) -> None:
        """Valida campo email."""
        if email and len(email) > settings.MAX_EMAIL_LENGTH:
            raise ValidationError(f"Email muito longo (máx {settings.MAX_EMAIL_LENGTH} caracteres)")
        if email and "@" not in email:
            raise ValidationError("Email inválido")
    
    @staticmethod
    def validar_cliente(dados: Dict[str, Any]) -> None:
        """Valida todos os campos de cliente."""
        ClienteValidator.validar_empresa(dados.get("empresa", ""))
        ClienteValidator.validar_cnpj(dados.get("cnpj", ""))
        ClienteValidator.validar_email(dados.get("email", ""))
        
        # Validações adicionais
        if not dados.get("cidade"):
            raise ValidationError("Cidade é obrigatória")
        if not dados.get("uf"):
            raise ValidationError("UF é obrigatória")


class ClienteService:
    """Serviço de gerenciamento de clientes."""
    
    def __init__(self):
        """Inicializa serviço com cliente Supabase."""
        self.db = get_db()
        self.validator = ClienteValidator()
    
    def listar(self, filtro_empresa: str = "", limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Lista clientes com filtro opcional.
        
        Args:
            filtro_empresa: Filtro por nome da empresa (ilike)
            limit: Número máximo de registros
            
        Returns:
            Lista de clientes
        """
        try:
            query = self.db.table("clientes").select(
                "id, empresa, cidade, telefone, contato"
            )
            
            if filtro_empresa:
                query = query.filter("empresa", "ilike", f"%{filtro_empresa}%")
            
            query = query.order("empresa", desc=False).limit(limit)
            response = query.execute()
            
            logger.info(f"Listados {len(response.data)} clientes")
            return response.data
            
        except Exception as e:
            logger.error(f"Erro ao listar clientes: {e}")
            raise DatabaseError(f"Erro ao listar clientes: {e}")
    
    def listar_todos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os clientes com todos os campos.
        
        Returns:
            Lista de clientes
        """
        try:
            response = self.db.table("clientes").select("*").order("empresa", desc=False).execute()
            logger.info(f"Listados {len(response.data)} clientes (todos os campos)")
            return response.data
            
        except Exception as e:
            logger.error(f"Erro ao listar todos os clientes: {e}")
            raise DatabaseError(f"Erro ao listar clientes: {e}")
    
    def obter_por_id(self, id_cliente: int) -> Dict[str, Any]:
        """
        Obtém um cliente pelo ID.
        
        Args:
            id_cliente: ID do cliente
            
        Returns:
            Dados do cliente
            
        Raises:
            ClienteNotFoundError: Se cliente não existe
        """
        try:
            response = self.db.table("clientes").select("*").eq("id", id_cliente).execute()
            
            if not response.data:
                raise ClienteNotFoundError(f"Cliente {id_cliente} não encontrado")
            
            return response.data[0]
            
        except ClienteNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao obter cliente {id_cliente}: {e}")
            raise DatabaseError(f"Erro ao obter cliente: {e}")
    
    def criar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo cliente.
        
        Args:
            dados: Dados do cliente
            
        Returns:
            Cliente criado
            
        Raises:
            ValidationError: Se dados inválidos
            DuplicateClienteError: Se cliente duplicado
        """
        try:
            # Validar dados
            self.validator.validar_cliente(dados)
            
            # Verificar duplicata
            existe = self.db.table("clientes").select("*") \
                .eq("empresa", dados["empresa"]) \
                .eq("cidade", dados["cidade"]) \
                .execute()
            
            if existe.data:
                raise DuplicateClienteError(
                    f"Cliente '{dados['empresa']}' em '{dados['cidade']}' já existe"
                )
            
            # Inserir
            response = self.db.table("clientes").insert(dados).execute()
            
            logger.info(f"Cliente criado: {dados['empresa']}")
            return response.data[0] if response.data else {}
            
        except (ValidationError, DuplicateClienteError):
            raise
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            raise DatabaseError(f"Erro ao criar cliente: {e}")
    
    def atualizar(self, id_cliente: int, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um cliente existente.
        
        Args:
            id_cliente: ID do cliente
            dados: Dados a atualizar
            
        Returns:
            Cliente atualizado
            
        Raises:
            ValidationError: Se dados inválidos
            ClienteNotFoundError: Se cliente não existe
        """
        try:
            # Validar dados
            self.validator.validar_cliente(dados)
            
            # Verificar existência
            self.obter_por_id(id_cliente)
            
            # Atualizar
            response = self.db.table("clientes").update(dados).eq("id", id_cliente).execute()
            
            logger.info(f"Cliente {id_cliente} atualizado")
            return response.data[0] if response.data else {}
            
        except (ValidationError, ClienteNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente {id_cliente}: {e}")
            raise DatabaseError(f"Erro ao atualizar cliente: {e}")
    
    def excluir(self, id_cliente: int) -> None:
        """
        Exclui um cliente.
        
        Args:
            id_cliente: ID do cliente
            
        Raises:
            ClienteNotFoundError: Se cliente não existe
        """
        try:
            # Verificar existência
            self.obter_por_id(id_cliente)
            
            # Excluir
            self.db.table("clientes").delete().eq("id", id_cliente).execute()
            
            logger.info(f"Cliente {id_cliente} excluído")
            
        except ClienteNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao excluir cliente {id_cliente}: {e}")
            raise DatabaseError(f"Erro ao excluir cliente: {e}")
