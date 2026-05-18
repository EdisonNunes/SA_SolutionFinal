"""
Sistema de logging estruturado para SA Solutions.

Fornece logging consistente em toda a aplicação com níveis apropriados.
"""

import logging
import sys
from typing import Optional
from config.settings import settings


class LoggerManager:
    """Gerenciador centralizado de logging."""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Obtém ou cria um logger para um módulo.
        
        Args:
            name: Nome do módulo (geralmente __name__)
            
        Returns:
            Logger configurado
        """
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            
            # Evitar handlers duplicados
            if not logger.handlers:
                # Handler para console
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
                
                # Formatador
                formatter = logging.Formatter(settings.LOG_FORMAT)
                console_handler.setFormatter(formatter)
                
                # Adicionar handler ao logger
                logger.addHandler(console_handler)
                logger.setLevel(getattr(logging, settings.LOG_LEVEL))
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]
