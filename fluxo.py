import re
import pandas as pd
import os
import subprocess
import numpy as np
from scipy.stats import t
import time
import matplotlib.pyplot as plt
import random
import json
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
    execucoes_T = df_filtrado["Exec_T"].dropna().apply(json.loads).tolist()
    execucoes_E = df_filtrado["Exec_E"].dropna().apply(json.loads).tolist()

    # Se retornou [[...]] em vez de [...]
    if len(execucoes_T) == 1:
        execucoes_T = execucoes_T[0]

    if len(execucoes_E) == 1:
        execucoes_E = execucoes_E[0]

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

    # Carregar CSV (ou criar novo caso não exista)
    try:
        df = pd.read_csv("resultados.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Tamanho","Versao","Threads",
            "Exec_T","Media_T","Confianca_T",
            "Exec_E","Media_E","Confianca_E"
        ])

    # Filtro da tripla identificadora
    filtro = (
        (df["Tamanho"] == tamanho) &
        (df["Threads"] == thread) &
        (df["Versao"] == versao)
    )

    linha_json_T = json.dumps(execucoes_T)
    linha_json_E = json.dumps(execucoes_E)

    if not df.loc[filtro].empty:
        # Caso exista → atualizar
        df.loc[filtro, "Exec_T"] = linha_json_T
        df.loc[filtro, "Media_T"] = media_T
        df.loc[filtro, "Confianca_T"] = conf_T

        df.loc[filtro, "Exec_E"] = linha_json_E
        df.loc[filtro, "Media_E"] = media_E
        df.loc[filtro, "Confianca_E"] = conf_E

    else:
        # Caso não exista → criar nova linha
        df.loc[len(df)] = [
            tamanho, versao, thread,
            linha_json_T, media_T, conf_T,
            linha_json_E, media_E, conf_E
        ]

    # Salvar CSV final
    df.to_csv("resultados.csv", index=False)



'Funções para plotar os resultados obtidos ao fim das execuções'
def plota_resultados_versaoxmetrica(metric, threads_list, tamanho, nome_arquivo, titulo="Comparação de Versões"):
    """
    Gera e salva um gráfico onde:
    - eixo X = versão do algoritmo
    - eixo Y = tempo médio ou energia média
    - várias curvas = diferentes números de threads
    - filtrado por tamanho específico
    - salva como PNG na pasta 'gráficos'
    """

    # Ler o CSV
    df = pd.read_csv("resultados.csv")

    # Filtrar pelo tamanho fornecido
    df = df[df["Tamanho"] == tamanho]

    if df.empty:
        raise ValueError(f"Não há dados para tamanho {tamanho} no CSV.")

    # Validar métrica
    if metric not in ["Media_T", "Media_E"]:
        raise ValueError("metric deve ser 'Media_T' ou 'Media_E'.")

    # Criar pasta 'gráficos' se não existir
    if not os.path.exists("gráficos"):
        os.makedirs("gráficos")

    plt.figure(figsize=(10, 6))

    # Plota uma linha para cada número de threads
    for th in threads_list:
        df_th = df[df["Threads"] == th]

        if df_th.empty:
            print(f"Aviso: não há dados para {th} threads e tamanho {tamanho}.")
            continue

        # Grupo por versão e pega média
        df_group = df_th.groupby("Versao")[metric].mean().reset_index()

        plt.plot(df_group["Versao"], df_group[metric], marker="o", label=f"{th} threads")

    # Labels e título
    plt.xlabel("Versão do algoritmo")
    plt.ylabel("Tempo (s)" if metric == "Media_T" else "Energia (J)")
    plt.title(f"{titulo}\n(Tamanho = {tamanho})")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend(title="Threads")
    plt.tight_layout()

    # Caminho do arquivo de saída
    caminho_png = os.path.join("gráficos", nome_arquivo + ".png")

    # Salvar como PNG
    plt.savefig(caminho_png, dpi=300)
    plt.close()

    print(f"Gráfico salvo em: {caminho_png}")

def plotar_comparacao_por_tamanho(
    metrica,
    threads_lista,
    versao,
    nome_arquivo,
    titulo="Comparação de tamanhos"
):

    # Criar pasta "gráficos"
    os.makedirs("gráficos", exist_ok=True)

    # Carregar CSV
    try:
        df = pd.read_csv("resultados.csv")
    except FileNotFoundError:
        print("❌ Arquivo resultados.csv não encontrado.")
        return
    
    # Filtrar por versão
    df = df[df["Versao"] == versao]

    if df.empty:
        print(f"❌ Nenhum dado encontrado para a versão {versao}.")
        return

    # Validar métrica
    if metrica not in ["Media_T", "Media_E"]:
        print("❌ Métrica inválida. Use 'Media_T' ou 'Media_E'.")
        return

    metric_label = "Energia (J)" if metrica == "Media_E" else "Tempo (s)"

    # Obter todos os tamanhos usados
    tamanhos_disponiveis = sorted(df["Tamanho"].unique())

    # =============== GRÁFICO DE LINHAS =================
    plt.figure(figsize=(10, 6))

    for thread in threads_lista:
        df_thread = df[df["Threads"] == thread]

        if df_thread.empty:
            print(f"Aviso: Nenhum dado para thread = {thread}")
            continue

        df_thread = df_thread.sort_values("Tamanho")

        plt.plot(
            df_thread["Tamanho"],
            df_thread[metrica],
            marker="o",
            label=f"{thread} threads"
        )

    plt.xlabel("Tamanho da Matriz (N)")
    plt.ylabel(metric_label)
    plt.title(titulo + f" (Versão {versao})")
    plt.legend()
    plt.grid(True)

    # ticks exatos do dataset
    plt.xticks(tamanhos_disponiveis)

    caminho_linha = os.path.join("gráficos", f"{nome_arquivo}_linhas.png")
    plt.savefig(caminho_linha, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✔ Gráfico de linhas salvo em: {caminho_linha}")

    # =============== GRÁFICO DE BARRAS =================

    plt.figure(figsize=(12, 7))

    largura = 0.75 / len(threads_lista)  # largura de cada barra
    posicoes = np.arange(len(tamanhos_disponiveis))

    for i, thread in enumerate(threads_lista):
        df_thread = df[df["Threads"] == thread]
        valores = []

        for tam in tamanhos_disponiveis:
            linha = df_thread[df_thread["Tamanho"] == tam]
            if not linha.empty:
                valores.append(float(linha[metrica].iloc[0]))
            else:
                valores.append(0)

        x_offsets = posicoes + i * largura

        plt.bar(
            x_offsets,
            valores,
            width=largura,
            label=f"{thread} threads"
        )

    plt.xlabel("Tamanho da Matriz (N)")
    plt.ylabel(metric_label)
    plt.title(titulo + f" (Versão {versao})")
    plt.xticks(posicoes + largura * (len(threads_lista)-1) / 2, tamanhos_disponiveis)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    caminho_barras = os.path.join("gráficos", f"{nome_arquivo}_barras.png")
    plt.savefig(caminho_barras, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✔ Gráfico de barras salvo em: {caminho_barras}")

def plotar_melhoria_fixa(
    metrica,
    threads_lista,
    versao,
    tamanho,
    nome_arquivo,
    titulo="Tamanho x Tempo"
):
    """
    Compara aceleração relativa à execução com 1 thread,
    para uma versão e tamanho fixos.
    Gera gráficos de linhas e barras.
    """

    os.makedirs("gráficos", exist_ok=True)

    try:
        df = pd.read_csv("resultados.csv")
    except FileNotFoundError:
        print("❌ resultados.csv não encontrado.")
        return

    # Verificação da métrica
    if metrica not in ["Media_T", "Media_E"]:
        print("❌ Métrica inválida. Use Media_T ou Media_E.")
        return

    metric_label = "Aceleração (Tempo)" if metrica == "Media_T" else "Aceleração (Energia)"

    # Filtrar pela versão e tamanho
    df = df[(df["Versao"] == versao) & (df["Tamanho"] == tamanho)]

    if df.empty:
        print(f"❌ Não há dados para versão {versao} e tamanho {tamanho}.")
        return

    # Verificar se existe 1 thread
    if 1 not in df["Threads"].unique():
        print("❌ Não há dados para 1 thread — aceleração impossível.")
        return

    # Obter valor de referência (1 thread)
    linha_ref = df[df["Threads"] == 1]
    ref = float(linha_ref[metrica].iloc[0])

    # ==========================================================
    #              Cálculo da aceleração por thread
    # ==========================================================

    aceleracoes = []
    threads_disponiveis = []

    for thread in threads_lista:
        linha = df[df["Threads"] == thread]

        if linha.empty:
            # thread não existe -> aceleração 0
            aceleracoes.append(0)
        else:
            val = float(linha[metrica].iloc[0])
            aceleracoes.append(ref / val if val != 0 else 0)

        threads_disponiveis.append(thread)

    # ==========================================================
    #                      GRÁFICO DE LINHAS
    # ==========================================================

    plt.figure(figsize=(9, 6))
    plt.plot(threads_disponiveis, aceleracoes, marker="o")
    plt.xlabel("Número de Threads")
    plt.ylabel(metric_label)
    plt.title(f"{titulo} — Versão {versao} — Tamanho {tamanho}")
    plt.grid(True)
    plt.xticks(threads_disponiveis)

    caminho_linhas = os.path.join("gráficos", f"{nome_arquivo}_melhoria_linhas.png")
    plt.savefig(caminho_linhas, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✔ Gráfico de linhas salvo em: {caminho_linhas}")

    # ==========================================================
    #                      GRÁFICO DE BARRAS
    # ==========================================================

    plt.figure(figsize=(9, 6))
    plt.bar(threads_disponiveis, aceleracoes)
    plt.xlabel("Número de Threads")
    plt.ylabel(metric_label)
    plt.title(f"{titulo} — Versão {versao} — Tamanho {tamanho}")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(threads_disponiveis)

    caminho_barras = os.path.join("gráficos", f"{nome_arquivo}_melhoria_barras.png")
    plt.savefig(caminho_barras, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✔ Gráfico de barras salvo em: {caminho_barras}")

tamanhos = [1024,2048,4096,8192]
threads = [1,2,4]
versoes = [1,2,3,4,5,6]



'Fluxo de execução: Executar todos os números de Thread para cada tamanho'
'Depois seguir adiante para o próximo tamanho e repetir'
'Sempre antes de executar uma combinação Thread, tamanho, versão, verificar se ela já está satisfeita'
'Satisfeita: Pelo menos 5 execuções e confiança abaixo do limite'
for tamanho in tamanhos:
    Cria_matriz_teste(tamanho)
    for thread in threads:
        for versao in versoes:

            # 1. Verificar no CSV se já existe essa combinação
            sats,resultados_T,resultados_E=combinacao_satisfeita(tamanho, thread, versao)
            
            if(sats):
                continue  # pula para a próxima

            # 2. Caso contrário, executar até satisfazer
            while len(resultados_T) < 5 or not (confianca_aceitavel(resultados_T,0.05) and confianca_aceitavel(resultados_E,0.05)):
                # tempo,energia = executa_programa(thread, versao)
                tempo,energia = random.randint(1,10),random.randint(1,10)
                resultados_T.append(tempo)
                resultados_E.append(energia)

                # salva no CSV cada execução além de computar média e confiança
                salva_media_csv(tamanho, thread, versao, resultados_T,resultados_E)

plota_resultados_versaoxmetrica("Media_T",[1,2,4],2048,"Comparação de Tempo")
plotar_comparacao_por_tamanho("Media_T",[1,2,4],6,"Tamanho x Tempo")
plotar_melhoria_fixa("Media_T",[1,2,4],6,2048,"Tamanho x Tempo")
