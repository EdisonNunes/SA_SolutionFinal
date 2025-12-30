from datetime import datetime

def validar_datas_e_calcular_horas(data1_str, data2_str):
    """
    Valida duas datas no formato 'DD-MM-YYYY HH:MM' e calcula a diferença em horas entre elas.
    
    Parâmetros:
    - data1_str (str): primeira data/hora.
    - data2_str (str): segunda data/hora.
    
    Retorna:
    - int: número de horas entre as duas datas se forem válidas.
    - str: código de erro se alguma data for inválida.
    """
    formato = "%d-%m-%Y %H:%M"
    
    try:
        data1 = datetime.strptime(data1_str, formato)
    except ValueError:
        # return "ERRO_FORMATO_INVALIDO_DATA1"
        condicao = True
        return "", condicao
    
    try:
        data2 = datetime.strptime(data2_str, formato)
    except ValueError:
        # return "ERRO_FORMATO_INVALIDO_DATA2"
        condicao = True
        return "", condicao
    
    diferenca = abs(data2 - data1)
    total_minutos = int(diferenca.total_seconds() // 60)

    horas = total_minutos // 60
    minutos = total_minutos % 60

    # Verificação se data1 >= data2
    condicao = data2 >= data1

    return f"{horas:02}:{minutos:02}", condicao

def ShowErro(erro):
    match(erro):
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
 
    return message, etapa        

def string_para_float(tempo_str):
    """
    Converte uma string no formato "##:##" ou "#:##" em um número float,
    onde a parte antes dos dois pontos é a parte inteira,
    e a parte após os dois pontos é a parte decimal.
    
    Exemplo:
        "2:30" -> 2.30
        "12:05" -> 12.05
    """
    try:
        parte_inteira, parte_decimal = tempo_str.split(":")
        resultado = float(f"{int(parte_inteira)}.{parte_decimal}")
        return resultado
    except ValueError:
        return 0.0
        #raise ValueError("Formato inválido. A string deve estar no formato '#:##' ou '##:##'")

def RetiraCRLF(texto: str) -> str:

    if not isinstance(texto, str):
        return texto  # caso venha None ou outro tipo
    
    # 1. Remove CR/LF do início e do fim
    texto = texto.strip("\r\n")
    
    # 2. Substitui qualquer CR ou LF restante por espaço
    texto = texto.replace("\r", " ").replace("\n", " ")
    
    # Garante que múltiplos espaços não virem "buracos"
    texto = " ".join(texto.split())
    
    return texto

def formatar_moeda_br(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
