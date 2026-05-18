"""
Utilitários para formatação e validação.

Fornece funções auxiliares para formatação monetária e validação de datas.
"""

from datetime import datetime
from typing import Tuple


def formatar_moeda_br(valor: float) -> str:
    """
    Formata número como moeda brasileira.
    
    Args:
        valor: Valor numérico
        
    Returns:
        String formatada (ex: "R$ 1.234,56")
    """
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"


def validar_datas_e_calcular_horas(
    data1_str: str,
    data2_str: str
) -> Tuple[str, bool]:
    """
    Valida duas datas e calcula diferença em horas.
    
    Formato esperado: 'DD-MM-YYYY HH:MM'
    
    Args:
        data1_str: Primeira data/hora
        data2_str: Segunda data/hora
        
    Returns:
        Tupla (tempo_formatado, valido) onde:
        - tempo_formatado: String no formato "HH:MM"
        - valido: True se ambas as datas são válidas
    """
    formato = "%d-%m-%Y %H:%M"
    
    try:
        data1 = datetime.strptime(data1_str, formato)
    except ValueError:
        return "", False
    
    try:
        data2 = datetime.strptime(data2_str, formato)
    except ValueError:
        return "", False
    
    # Calcular diferença
    diferenca = abs(data2 - data1)
    total_minutos = int(diferenca.total_seconds() // 60)
    
    horas = total_minutos // 60
    minutos = total_minutos % 60
    
    # Verificar se data2 >= data1
    condicao = data2 >= data1
    
    return f"{horas:02d}:{minutos:02d}", condicao


def ShowErro(erro: int) -> Tuple[str, int]:
    """
    Retorna mensagem de erro e etapa baseada no código de erro.
    
    Args:
        erro: Código de erro (1-27)
        
    Returns:
        Tupla (mensagem, etapa)
    """
    match erro:
        case 1: 
            message = 'Membrana #1 PI'
            etapa = 9
        case 2: 
            message = 'Membrana #2 PI'
            etapa = 9
        case 3: 
            message = 'Membrana #3 PI'
            etapa = 9
        case 4: 
            message = 'PB Padrão Fluido Padrão (psi)'
            etapa = 9
        case 5: 
            message = 'Fluido Padrão Resultado #1'
            etapa = 9
        case 6: 
            message = 'Fluido Padrão Resultado #2'
            etapa = 9
        case 7: 
            message = 'Fluido Padrão Resultado #3'
            etapa = 9
        case 8: 
            message = 'PB Referencial (psi)'
            etapa = 10
        case 9: 
            message = 'PB-P #1'
            etapa = 10
        case 10: 
            message = 'PB-P #2'
            etapa = 10
        case 11: 
            message = 'PB-P #3'
            etapa = 10
        case 12: 
            message = 'Resultado #1'
            etapa = 12
        case 13: 
            message = 'Resultado #2'
            etapa = 12
        case 14: 
            message = 'Resultado #3'
            etapa = 12
        case 15: 
            message = 'Peso Final #1'
            etapa = 13
        case 16: 
            message = 'Peso Final #2'
            etapa = 13
        case 17: 
            message = 'Peso Final #3'
            etapa = 13
        case 18: 
            message = 'Resultado #1 Dispositivo'
            etapa = 14
        case 19: 
            message = 'Resultado #2 Dispositivo'
            etapa = 14
        case 20: 
            message = 'Critério Variação Peso ≤ (%)'
            etapa = 15
        case 21: 
            message = 'Critério Variação Vazão ≤ (%)'
            etapa = 15
        case 22: 
            message = 'Membrana #1 FI' 
            etapa = 9            
        case 23: 
            message = 'Membrana #2 FI'
            etapa = 9           
        case 24: 
            message = 'Membrana #3 FI'
            etapa = 9   
        case 25: 
            message = 'Tempo Final #1'
            etapa = 11            
        case 26: 
            message = 'Tempo Final #2'
            etapa = 11            
        case 27: 
            message = 'Tempo Final #3'
            etapa = 11            
        case _:
            message = 'Erro desconhecido'
            etapa = 0
    
    return message, etapa


def RetiraCRLF(texto: str) -> str:
    """
    Remove caracteres de quebra de linha e formata texto.
    
    Args:
        texto: Texto a ser processado
        
    Returns:
        Texto limpo sem quebras de linha
    """
    if not isinstance(texto, str):
        return texto  # caso venha None ou outro tipo
    
    # 1. Remove CR/LF do início e do fim
    texto = texto.strip("\r\n")
    
    # 2. Substitui qualquer CR ou LF restante por espaço
    texto = texto.replace("\r", " ").replace("\n", " ")
    
    # Garante que múltiplos espaços não virem "buracos"
    texto = " ".join(texto.split())
    
    return texto


def remover_linhas_em_branco(texto: str) -> str:
    """
    Remove linhas em branco de um texto.
    
    Args:
        texto: Texto com possíveis linhas em branco
        
    Returns:
        Texto limpo
    """
    if not texto:
        return ""
    
    return "\n".join(
        linha.strip()
        for linha in texto.split("\n")
        if linha.strip()
    )
