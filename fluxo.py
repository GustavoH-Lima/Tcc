import re
import pandas as pd
import os
import subprocess
import numpy as np
from scipy.stats import t
import time
def Cria_csv():
    'Cria o arquivo para armazenar os resultados caso ele não exista, faz nada caso contrário'
    if not os.path.exists("resultados.csv"): 
        d = {
            'Tamanho': [],
            'Versao': [],
            'Threads': [],
            'Exec_T': [],
            'Media_T': [],
            'Confianca_T':[],
            'Exec_E': [],
            'Media_E': [],
            'Confianca_E':[]
        }
        df = pd.DataFrame(d)
        df.to_csv("resultados.csv", index=False)

def Media_inicial(): #Por enquanto não usarei esta função
    pass

def Cria_matriz_teste(tamanho = 2048):
    'Função para criar as matrizes que serão usadas no teste'
    subprocess.run(["./gera", "m1", str(tamanho)])
    subprocess.run(["./gera", "m2" ,str(tamanho)])

def coleta_consumo(pid_alvo,saida_scaph):
    'Coleta a linha com as informações'
    'Coleta o consumption'
    padrao = rf'"pid"\s*:\s*{pid_alvo}.*?"consumption"\s*:\s*([0-9]+(?:\.[0-9]+)?)'

    'Transforma em float'
    consumos = [float(x) for x in re.findall(padrao, saida_scaph)]

    'Pegando a soma já em Joules'
    resultado = sum(consumos)/1e6
    return resultado

def executa_programa(thread,versao): #ToDo
    'Executa o programa e faz as medidas necessárias'

    #Executando o scaphandre para tomar as medições
    scaph = subprocess.Popen([
        "sudo","scaphandre","json",
        "-s","1"],
        stdout=subprocess.PIPE, stderr = subprocess.DEVNULL,text=True)
    
    #Executando a multiplicação de matrizes
    proc = subprocess.Popen(
        ["./mult_paralelo", "m1", "m2", str(versao), str(thread)],
        stdout=subprocess.PIPE, text=True
    )

    pid_proc = proc.pid
    tempo = float(proc.communicate()[0].strip())
    time.sleep(1.5)
    scaph.kill()

    saida_scaph = scaph.stdout.read()
    energia = coleta_consumo(pid_proc,saida_scaph)
    
    return tempo,energia

'Funções para intervalo de confiança, etc'
def confidence(valores): #Calcula a confiança de um conjunto de dados
    'Calcular o intervalo de confiança dos testes'

    if(len(valores) < 2):
        return float('inf')

    media = np.mean(valores)
    desvio = np.std(valores, ddof=1)

    # erro padrão
    erro = desvio / np.sqrt(len(valores))

    # intervalo de 95%
    t_crit = t.ppf(0.975, df=len(valores)-1)

    intervalo = t_crit * erro
    
    return intervalo / media
def confianca_aceitavel(valores, limite):
    'Verifica se o intervalo de confiança dos testes está dentro do limite aceitável'

    # exemplo: intervalo / média < limite
    return (confidence(valores)) < limite

'Função de verificação de controle'
def combinacao_satisfeita(tamanho, thread, versao, limite_confianca=0.05): #Retorna Bool(Se está satisfeito), Lista de execuções de Tempo, Lista de execuções de Energia
    'Função para verificar se já atingiu 5 execuções e se o limite está aceitável'
    Cria_csv()
    try:
        df = pd.read_csv("resultados.csv")
    except FileNotFoundError:
        return False,[],[]

    # filtrar pela combinação
    filtro = (
        (df["Tamanho"] == tamanho) &
        (df["Threads"] == thread) &
        (df["Versao"] == versao)
    )
    df_filtrado = df[filtro]

    # não existe nenhuma execução → não está satisfeito
    if df_filtrado.empty:
        return False,[],[]
    
    # pegar lista de execuções já armazenadas
    execucoes_T = df_filtrado["Exec_T"].dropna().tolist()
    execucoes_E = df_filtrado["Exec_E"].dropna().tolist()

    # 1) Tem menos que 5 execuções? então NÃO satisfeito
    if len(execucoes_T) < 5:
        return False,execucoes_T,execucoes_E

    # 2) Calcular confiança para o tempo
    confianca_tempo=confianca_aceitavel(execucoes_T, limite_confianca)

    # 3) Calcular confiança para a energia
    confianca_energia=confianca_aceitavel(execucoes_E,limite_confianca)

    return confianca_energia and confianca_tempo,execucoes_T,execucoes_E

'Função para salvar no Csv as informações parciais acerca do processo'
def salva_media_csv(tamanho, thread, versao, execucoes_T, execucoes_E):
    
    # Tomando as médias
    media_T = sum(execucoes_T) / len(execucoes_T)
    media_E = sum(execucoes_E) / len(execucoes_E)

    conf_T = confidence(execucoes_T)
    conf_E = confidence(execucoes_E)

    df = pd.read_csv("resultados.csv")

    # Localizar a linha com a mesma tripla
    filtro = (
        (df["Tamanho"] == tamanho) &
        (df["Threads"] == thread) &
        (df["Versao"] == versao)
    )

    if not any(filtro):
        # Se não existir, cria a linha
        df.loc[len(df)] = [
            tamanho, versao, thread,
            str(execucoes_T), media_T, conf_T,
            str(execucoes_E), media_E, conf_E
        ]
    else:
        # Se existir, apenas atualiza
        df.loc[filtro, "Exec_T"] = str(execucoes_T)
        df.loc[filtro, "Media_T"] = media_T
        df.loc[filtro, "Confianca_T"] = conf_T

        df.loc[filtro, "Exec_E"] = str(execucoes_E)
        df.loc[filtro, "Media_E"] = media_E
        df.loc[filtro, "Confianca_E"] = conf_E

    df.to_csv("resultados.csv", index=False)



'Cria o csv que irá armazenar todos os resultado para posteriormente gerar os gráficos'

Cria_matriz_teste()


tamanhos = [2048]
threads = [2]
versoes = [6]

'Fluxo de execução: Executar todos os números de Thread para cada tamanho'
'Depois seguir adiante para o próximo tamanho e repetir'
'Sempre antes de executar uma combinação Thread, tamanho, versão, verificar se ela já está satisfeita'
'Satisfeita: Pelo menos 5 execuções e confiança abaixo do limite'
for tamanho in tamanhos:
    for thread in threads:
        for versao in versoes:

            # 1. Verificar no CSV se já existe essa combinação
            sats,resultados_T,resultados_E=combinacao_satisfeita(tamanho, thread, versao)

            if(sats):
                continue  # pula para a próxima

            # 2. Caso contrário, executar até satisfazer
            while len(resultados_T) < 5 or not (confianca_aceitavel(resultados_T,0.05) and confianca_aceitavel(resultados_E,0.05)):
                tempo,energia = executa_programa(thread, versao)
                resultados_T.append(tempo)
                resultados_E.append(energia)

                # salva no CSV cada execução além de computar média e confiança
                salva_media_csv(tamanho, thread, versao, resultados_T,resultados_E)
