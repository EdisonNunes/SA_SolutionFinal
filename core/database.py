"""
Cliente Supabase centralizado com cache.

Fornece um único ponto de acesso ao banco de dados Supabase
para toda a aplicação, otimizado com caching.
"""

import streamlit as st
from supabase import create_client, Client
from config.settings import settings
from core.logger import LoggerManager
from core.exceptions import ConfigurationError, DatabaseError

logger = LoggerManager.get_logger(__name__)


@st.cache_resource
def get_supabase_client() -> Client:
    """
    Obtém cliente Supabase com caching.
    
    Esta função usa @st.cache_resource para garantir que apenas
    uma instância do cliente Supabase seja criada por sessão.
    
    Returns:
        Cliente Supabase configurado
        
    Raises:
        ConfigurationError: Se as credenciais não estão configuradas
        DatabaseError: Se não conseguir conectar ao banco
    """
    try:
        config = settings.get_supabase_config()
        logger.info("Conectando ao Supabase...")
        
        client = create_client(config["url"], config["key"])
        
        # Testar conexão
        response = client.table("clientes").select("id").limit(1).execute()
        logger.info("Conexão com Supabase estabelecida com sucesso")
        
        return client
        
    except ConfigurationError as e:
        logger.error(f"Erro de configuração: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro ao conectar com Supabase: {e}")
        raise DatabaseError(f"Falha na conexão com banco de dados: {e}")


# Alias para compatibilidade com código existente
def get_db() -> Client:
    """Alias curto para get_supabase_client."""
    return get_supabase_client()
