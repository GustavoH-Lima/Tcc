import re
import pandas as pd
import os
import subprocess
import numpy as np
from scipy.stats import t
import matplotlib.pyplot as plt
import random
import json

'Funções para iniciar os testes'
def Cria_csv():
    'Cria o arquivo para armazenar os resultados caso ele não exista, faz nada caso contrário'
    if not os.path.exists("resultados.csv"): 
        d = {
            'Tamanho': [],
            'Versao': [],
            'Threads': [],
            'Otimizacao':[],
            'Exec_T': [],
            'Media_T': [],
            'Confianca_T':[],
            'Exec_E': [],
            'Media_E': [],
            'Confianca_E':[]
        }
        df = pd.DataFrame(d)
        df.to_csv("resultados.csv", index=False)
def Cria_matriz_teste(tamanho = 2048):
    'Função para criar as matrizes que serão usadas no teste'
    subprocess.run(["./gera", "m1", str(tamanho)])
    subprocess.run(["./gera", "m2" ,str(tamanho)])

'Funções para executar o programa e coletar as métricas'
def extrair_metricas_likwid(saida):
    """
    Extrai:
      - Energy [J]
      - Runtime (RDTSC) [s]
      - Energy DRAM [J]
    da saída do comando likwid-perfctr.
    """
    # Energy [J]
    padrao_energy = r"Energy \[J\]\s*\|\s*([0-9]+\.[0-9]+)"
    m_energy = re.search(padrao_energy, saida)
    energia = float(m_energy.group(1)) if m_energy else None

    # Runtime (RDTSC) [s]
    padrao_runtime = r"Runtime \(RDTSC\) \[s\]\s*\|\s*([0-9]+\.[0-9]+)"
    m_runtime = re.search(padrao_runtime, saida)
    runtime = float(m_runtime.group(1)) if m_runtime else None

    # Energy DRAM [J]
    padrao_dram = r"Energy DRAM \[J\]\s*\|\s*([0-9]+\.[0-9]+)"
    m_dram = re.search(padrao_dram, saida)
    energia_dram = float(m_dram.group(1)) if m_dram else None

    return energia, runtime, energia_dram
def executa_programa(thread,versao): #Agora, Usando o likwid
    'Executa o programa e faz as medidas necessárias'

    #Executando o scaphandre para tomar as medições
    
    processo = subprocess.run([
        "sudo","likwid-perfctr", "-C", "0", "-g", "ENERGY", 
        "./mult_paralelo", "m1", "m2",str(versao),str(thread)],
        stdout = subprocess.PIPE,stderr = subprocess.DEVNULL,text=True)

    saida = processo.stdout
    energia, tempo, dram = extrair_metricas_likwid(saida)
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
def combinacao_satisfeita(tamanho, thread, versao,otm, limite_confianca=0.05): #Retorna Bool(Se está satisfeito), Lista de execuções de Tempo, Lista de execuções de Energia
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
        (df["Versao"] == versao) &
        (df["Otimizacao"] == otm)
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
def salva_media_csv(tamanho, thread, versao,otm, execucoes_T, execucoes_E):

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
            "Tamanho","Versao","Threads","Otimizacao",
            "Exec_T","Media_T","Confianca_T",
            "Exec_E","Media_E","Confianca_E"
        ])

    # Filtro da tripla identificadora
    filtro = (
        (df["Tamanho"] == tamanho) &
        (df["Threads"] == thread) &
        (df["Versao"] == versao) &
        (df["Otimizacao"] == otm)
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
            tamanho, versao, thread,otm,
            linha_json_T, media_T, conf_T,
            linha_json_E, media_E, conf_E
        ]

    # Salvar CSV final
    df.to_csv("resultados.csv", index=False)



'Funções para plotar os resultados obtidos ao fim das execuções'
def plota_resultados_versaoxmetrica(
    metric,
    threads_list,
    tamanho,
    otimizacao,
    nome_arquivo,
    titulo="Comparação de Versões"
):
    """
    Agora também filtra pela otimização usada (ex: -O0, -O1, -O2, -O3)

    Gera e salva um gráfico onde:
    - eixo X = versão do algoritmo
    - eixo Y = tempo médio ou energia média
    - várias curvas = diferentes números de threads
    - filtrado por tamanho E otimização
    """

    # Ler o CSV
    df = pd.read_csv("resultados.csv")

    # Filtrar pelo tamanho e pela otimização
    df = df[(df["Tamanho"] == tamanho) & (df["Otimizacao"] == otimizacao)]

    if df.empty:
        raise ValueError(
            f"Não há dados para tamanho={tamanho} e Otimizacao={otimizacao} no CSV."
        )

    # Validar métrica
    if metric not in ["Media_T", "Media_E"]:
        raise ValueError("metric deve ser 'Media_T' ou 'Media_E'.")

    # Criar pasta 'gráficos' se não existir
    os.makedirs("gráficos", exist_ok=True)

    plt.figure(figsize=(10, 6))

    # Plota uma linha para cada número de threads
    for th in threads_list:
        df_th = df[df["Threads"] == th]

        if df_th.empty:
            print(f"Aviso: não há dados para {th} threads, tamanho {tamanho}, otimização {otimizacao}.")
            continue

        # Grupo por versão e pega média
        df_group = df_th.groupby("Versao")[metric].mean().reset_index()

        plt.plot(
            df_group["Versao"],
            df_group[metric],
            marker="o",
            label=f"{th} threads"
        )

    # Labels e título
    plt.xlabel("Versão do algoritmo")
    plt.ylabel("Tempo (s)" if metric == "Media_T" else "Energia (J)")
    plt.title(f"{titulo}\n(Tamanho={tamanho}, Otimização=O{otimizacao})")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend(title="Threads")
    plt.tight_layout()

    # Caminho do arquivo de saída
    caminho_png = os.path.join("gráficos", nome_arquivo + f"_O{otimizacao}.png")

    # Salvar como PNG
    plt.savefig(caminho_png, dpi=300)
    plt.close()

    print(f"Gráfico salvo em: {caminho_png}")

def plotar_comparacao_por_tamanho(
    metrica,
    threads_lista,
    versao,
    otimizacao,
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
    
    # Filtrar por versão e otimização
    df = df[(df["Versao"] == versao) & (df["Otimizacao"] == otimizacao)]

    if df.empty:
        print(f"❌ Nenhum dado encontrado para versão {versao} e otimização O{otimizacao}.")
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
    plt.title(f"{titulo} (Versão {versao}, Otimização O{otimizacao})")
    plt.legend()
    plt.grid(True)

    # Definir ticks apenas para tamanhos existentes
    plt.xticks(tamanhos_disponiveis)

    caminho_linha = os.path.join("gráficos", f"{nome_arquivo}_O{otimizacao}_linhas.png")
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
    plt.title(f"{titulo} (Versão {versao}, Otimização O{otimizacao})")
    plt.xticks(
        posicoes + largura * (len(threads_lista)-1) / 2,
        tamanhos_disponiveis
    )
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    caminho_barras = os.path.join("gráficos", f"{nome_arquivo}_O{otimizacao}_barras.png")
    plt.savefig(caminho_barras, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✔ Gráfico de barras salvo em: {caminho_barras}")

def plotar_melhoria_fixa(
    metrica,
    threads_lista,
    versao,
    otimizacao,
    tamanho,
    nome_arquivo,
    titulo="Tamanho x Tempo"
):
    """
    Compara aceleração relativa à execução com 1 thread,
    filtrando por versão, tamanho e otimização.
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

    # Filtrar pela versão, tamanho e otimização
    df = df[
        (df["Versao"] == versao) &
        (df["Tamanho"] == tamanho) &
        (df["Otimizacao"] == otimizacao)
    ]

    if df.empty:
        print(f"❌ Não há dados para versão {versao}, tamanho {tamanho} e otimização O{otimizacao}.")
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
    plt.title(f"{titulo} — Versão {versao} — O{otimizacao} — Tamanho {tamanho}")
    plt.grid(True)
    plt.xticks(threads_disponiveis)

    caminho_linhas = os.path.join("gráficos", f"{nome_arquivo}_O{otimizacao}_melhoria_linhas.png")
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
    plt.title(f"{titulo} — Versão {versao} — O{otimizacao} — Tamanho {tamanho}")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(threads_disponiveis)

    caminho_barras = os.path.join("gráficos", f"{nome_arquivo}_O{otimizacao}_melhoria_barras.png")
    plt.savefig(caminho_barras, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✔ Gráfico de barras salvo em: {caminho_barras}")

# tamanhos = [1024,2048,4096,8192]
tamanhos = [1024]
threads = [2]
versoes = [1,2,3,4,5,6]
otimizacao = [0,1,2,3]

'Fluxo de execução: Executar todos os números de Thread para cada tamanho'
'Depois seguir adiante para o próximo tamanho e repetir'
'Sempre antes de executar uma combinação Thread, tamanho, versão, verificar se ela já está satisfeita'
'Satisfeita: Pelo menos 5 execuções e confiança abaixo do limite'
for otm in otimizacao:
    subprocess.run([
        "gcc","O"+str(otm) ,"-o","mult_paralelo", "func.c","paralelo_matmul.c",
        "-Wall", "-fopenmp"],stderr = subprocess.DEVNULL)
    for tamanho in tamanhos:
        Cria_matriz_teste(tamanho)
        for thread in threads:
            for versao in versoes:

                # 1. Verificar no CSV se já existe essa combinação
                sats,resultados_T,resultados_E=combinacao_satisfeita(tamanho, thread, versao,otm)
                
                if(sats):
                    continue  # pula para a próxima

                # 2. Caso contrário, executar até satisfazer
                while len(resultados_T) < 5 or not (confianca_aceitavel(resultados_T,0.05) and confianca_aceitavel(resultados_E,0.05)):
                    # tempo,energia = executa_programa(thread, versao)
                    tempo,energia = random.randint(14,18),random.randint(6,10)
                    resultados_T.append(tempo)
                    resultados_E.append(energia)

                    # salva no CSV cada execução além de computar média e confiança
                    salva_media_csv(tamanho, thread, versao, otm,resultados_T,resultados_E)

plota_resultados_versaoxmetrica("Media_T",[1,2,4],1024,1,"Comparação de Tempo")
plotar_comparacao_por_tamanho("Media_T",[1,2,4],6,1,"Tamanho x Tempo")
plotar_melhoria_fixa("Media_T",[1,2,4],6,1,1024,"Tamanho x Tempo")
