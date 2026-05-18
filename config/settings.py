"""
Configurações centralizadas do projeto SA Solutions.

Este módulo centraliza todas as configurações da aplicação incluindo
URLs, credenciais (via secrets), e configurações de logging.
"""

import os
import streamlit as st
from typing import Optional, Dict, Any


class Settings:
    """Classe para gerenciar configurações da aplicação."""
    
    # Configurações de ambiente
    ENV = os.getenv("ENVIRONMENT", "production")
    DEBUG = ENV == "development"
    
    # URLs e paths
    APP_TITLE = "SA Solutions"
    APP_DESCRIPTION = "Gerador de propostas comerciais e relatórios"
    APP_VERSION = "3.0"
    
    # Supabase (centralizado com segurança)
    @staticmethod
    def get_supabase_config() -> Dict[str, str]:
        """
        Obtém configurações do Supabase de forma segura.
        
        Returns:
            Dict com URL e KEY do Supabase
            
        Raises:
            ValueError: Se secrets não estão configurados
        """
        try:
            if "supabase" not in st.secrets:
                raise ValueError(
                    "Secrets não configurados. Verifique .streamlit/secrets.toml"
                )
            
            return {
                "url": st.secrets["supabase"]["SUPABASE_URL"],
                "key": st.secrets["supabase"]["SUPABASE_KEY"]
            }
        except KeyError as e:
            raise ValueError(f"Secret faltando: {e}")
    
    # CloudConvert (centralizado com segurança)
    @staticmethod
    def get_cloudconvert_api_key() -> str:
        """
        Obtém chave da API CloudConvert de forma segura.
        
        Returns:
            String com a chave de API
            
        Raises:
            ValueError: Se secret não está configurado
        """
        try:
            if "cloudconvert" not in st.secrets:
                raise ValueError(
                    "CloudConvert API key não configurada. "
                    "Verifique .streamlit/secrets.toml"
                )
            return st.secrets["cloudconvert"]["CLOUDCONVERT_API_KEY"]
        except KeyError:
            raise ValueError("CloudConvert API key ausente em secrets")
    
    # Configurações de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configurações de paginação
    ITEMS_PER_PAGE = 10
    
    # Configurações de validação
    MAX_EMPRESA_LENGTH = 100
    MAX_CNPJ_LENGTH = 18
    MAX_EMAIL_LENGTH = 100


# Instância global de settings
settings = Settings()
