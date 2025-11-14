'É necessário gerar um arquivo "consumo.json que esteja formatado corretamente"'
with open("consumo.json","r+",encoding="utf-8") as file:
    cont=file.read()
pos=cont.rfind('}{"host"')
with open("consumo.json","w+",encoding="utf-8") as arquivo:
    arquivo.write(cont[:pos]+"}")