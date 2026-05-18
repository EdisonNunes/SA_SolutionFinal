"""
Serviço de gerenciamento de serviços.

Fornece operações CRUD para serviços com validação e tratamento de erros.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from core import (
    get_db,
    LoggerManager,
    DatabaseError,
    ValidationError,
    DuplicateServicoError,
    ServicoNotFoundError,
)


logger = LoggerManager.get_logger(__name__)


@dataclass
class ServicoValidator:
    """Validador de dados de serviço."""
    
    @staticmethod
    def validar_descricao(descricao: str) -> None:
        """Valida campo descricao."""
        if not descricao or not descricao.strip():
            raise ValidationError("Descrição não pode estar vazia")
    
    @staticmethod
    def validar_valor(valor: float) -> None:
        """Valida campo valor."""
        try:
            valor_float = float(valor)
            if valor_float < 0:
                raise ValidationError("Valor não pode ser negativo")
        except (ValueError, TypeError):
            raise ValidationError("Valor deve ser um número válido")
    
    @staticmethod
    def validar_servico(dados: Dict[str, Any]) -> None:
        """Valida todos os campos de serviço."""
        ServicoValidator.validar_descricao(dados.get("descricao", ""))
        ServicoValidator.validar_valor(dados.get("valor", 0))


class ServicoService:
    """Serviço de gerenciamento de serviços."""
    
    def __init__(self):
        """Inicializa serviço com cliente Supabase."""
        self.db = get_db()
        self.validator = ServicoValidator()
    
    def listar(self, filtro_descricao: str = "", limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Lista serviços com filtro opcional.
        
        Args:
            filtro_descricao: Filtro por descrição (ilike)
            limit: Número máximo de registros
            
        Returns:
            Lista de serviços
        """
        try:
            query = self.db.table("servicos").select(
                "id_servico, descricao, valor, ref, codigo, tipo"
            )
            
            if filtro_descricao:
                query = query.filter("descricao", "ilike", f"%{filtro_descricao}%")
            
            query = query.order("descricao", desc=False).limit(limit)
            response = query.execute()
            
            logger.info(f"Listados {len(response.data)} serviços")
            return response.data
            
        except Exception as e:
            logger.error(f"Erro ao listar serviços: {e}")
            raise DatabaseError(f"Erro ao listar serviços: {e}")
    
    def listar_todos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os serviços com todos os campos.
        
        Returns:
            Lista de serviços
        """
        try:
            response = self.db.table("servicos").select("*").order("descricao", desc=False).execute()
            logger.info(f"Listados {len(response.data)} serviços (todos os campos)")
            return response.data
            
        except Exception as e:
            logger.error(f"Erro ao listar todos os serviços: {e}")
            raise DatabaseError(f"Erro ao listar serviços: {e}")
    
    def obter_por_id(self, id_servico: int) -> Dict[str, Any]:
        """
        Obtém um serviço pelo ID.
        
        Args:
            id_servico: ID do serviço
            
        Returns:
            Dados do serviço
            
        Raises:
            ServicoNotFoundError: Se serviço não existe
        """
        try:
            response = self.db.table("servicos").select("*").eq("id_servico", id_servico).execute()
            
            if not response.data:
                raise ServicoNotFoundError(f"Serviço {id_servico} não encontrado")
            
            return response.data[0]
            
        except ServicoNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao obter serviço {id_servico}: {e}")
            raise DatabaseError(f"Erro ao obter serviço: {e}")
    
    def criar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo serviço.
        
        Args:
            dados: Dados do serviço
            
        Returns:
            Serviço criado
            
        Raises:
            ValidationError: Se dados inválidos
            DuplicateServicoError: Se serviço duplicado
        """
        try:
            # Validar dados
            self.validator.validar_servico(dados)
            
            # Verificar duplicata
            existe = self.db.table("servicos").select("*") \
                .eq("descricao", dados["descricao"]) \
                .execute()
            
            if existe.data:
                raise DuplicateServicoError(
                    f"Serviço '{dados['descricao']}' já existe"
                )
            
            # Inserir
            response = self.db.table("servicos").insert(dados).execute()
            
            logger.info(f"Serviço criado: {dados['descricao']}")
            return response.data[0] if response.data else {}
            
        except (ValidationError, DuplicateServicoError):
            raise
        except Exception as e:
            logger.error(f"Erro ao criar serviço: {e}")
            raise DatabaseError(f"Erro ao criar serviço: {e}")
    
    def atualizar(self, id_servico: int, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um serviço existente.
        
        Args:
            id_servico: ID do serviço
            dados: Dados a atualizar
            
        Returns:
            Serviço atualizado
            
        Raises:
            ValidationError: Se dados inválidos
            ServicoNotFoundError: Se serviço não existe
        """
        try:
            # Validar dados
            self.validator.validar_servico(dados)
            
            # Verificar existência
            self.obter_por_id(id_servico)
            
            # Atualizar
            response = self.db.table("servicos").update(dados).eq("id_servico", id_servico).execute()
            
            logger.info(f"Serviço {id_servico} atualizado")
            return response.data[0] if response.data else {}
            
        except (ValidationError, ServicoNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar serviço {id_servico}: {e}")
            raise DatabaseError(f"Erro ao atualizar serviço: {e}")
    
    def excluir(self, id_servico: int) -> None:
        """
        Exclui um serviço.
        
        Args:
            id_servico: ID do serviço
            
        Raises:
            ServicoNotFoundError: Se serviço não existe
        """
        try:
            # Verificar existência
            self.obter_por_id(id_servico)
            
            # Excluir
            self.db.table("servicos").delete().eq("id_servico", id_servico).execute()
            
            logger.info(f"Serviço {id_servico} excluído")
            
        except ServicoNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao excluir serviço {id_servico}: {e}")
            raise DatabaseError(f"Erro ao excluir serviço: {e}")
    
    def verificar_uso(self, id_servico: int) -> List[Dict[str, Any]]:
        """
        Verifica se o serviço está em uso em alguma proposta.
        
        Args:
            id_servico: ID do serviço
            
        Returns:
            Lista de propostas que usam o serviço
        """
        try:
            response = self.db.table("itens_proposta") \
                .select("propostas(num_proposta, empresa, cidade, data_emissao)") \
                .eq("id_servico", id_servico) \
                .execute()
            
            propostas = []
            if response.data:
                ids_vistos = set()
                for item in response.data:
                    prop = item.get("propostas")
                    if prop:
                        num = prop.get("num_proposta")
                        if num and num not in ids_vistos:
                            ids_vistos.add(num)
                            propostas.append(prop)
            
            logger.info(f"Serviço {id_servico} usado em {len(propostas)} proposta(s)")
            return propostas
            
        except Exception as e:
            logger.error(f"Erro ao verificar uso do serviço {id_servico}: {e}")
            raise DatabaseError(f"Erro ao verificar uso do serviço: {e}")
