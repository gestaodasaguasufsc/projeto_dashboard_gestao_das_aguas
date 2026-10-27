# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 16:46:06 2026

@author: Usuario
"""

import os
import pandas as pd
import numpy as np
import glob
import shutil


#### Parte 1 - Atualiza dados_agua_df

pasta_projeto = os.path.dirname(os.path.abspath('__file__')) 
pasta_atualizacao_df = os.path.join(pasta_projeto,'Dados','Produtos','atualizacao_dfs')


### - criando um dataframe vazio com as colunas existentes do colunas_df.csv:
 
caminho_colunas_df_csv = os.path.join(pasta_projeto,'Dados' , 'Origem','colunas_df_droped.csv')
dados_agua_df_vazio = pd.read_csv(caminho_colunas_df_csv)

### - read csvs   

pasta_dados_csv = os.path.join(pasta_projeto, 'Dados', 'Origem', 'CSVs')

dados_agua_df = dados_agua_df_vazio

referencia = "2026_09" #<----- atualizar aqui

ref_csv = referencia +".csv"
for csv in os.listdir(pasta_dados_csv):
    caminho = os.path.join(pasta_dados_csv, csv)
    df = pd.read_csv(caminho, encoding='utf-8')
    df.dropna(subset=['CODIGO'],inplace=True)
    df = df.sort_values(by='CODIGO', ascending=True)
    df.columns = dados_agua_df_vazio.columns
    dados_agua_df = pd.concat([dados_agua_df,df], ignore_index=True)
    print(csv)
    if csv == ref_csv: 
        break
    else:
        pass
    
   
caminho_dados_agua_df_saida = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df.csv')

dados_agua_df.to_csv(caminho_dados_agua_df_saida, index=False)


#### Parte 2 - copia das faturas do google drive para pasta de projeto no mês de referência

caminho_faturas_drive = r'G:\Meu Drive\Gestão das Águas - Pastas compartilhadas\p09 - Site Gestao das Aguas - CGA\2 - Faturas de água e esgoto'

meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
meses_n = np.arange(13)[1:]

meses_dict = {}
ref_mes = "09"

for i in range(len(meses)):

    if meses_n[i] < 10:
        mes = "0" + str(meses_n[i])
        meses_dict[mes] = mes + " - " + meses[i].upper()
    else:
        mes = str(meses_n[i])
        meses_dict[mes] = mes + " - " + meses[i].upper()
print(meses_dict)
referencia = "2026_09"

ref_ano = referencia.split("_")[0]
ref_mes = referencia.split("_")[1]

caminho_faturas_drive_ano_mes = os.path.join(caminho_faturas_drive,ref_ano, meses_dict[ref_mes])
#print(caminho_faturas_drive_ano_mes)

caminho_faturas_saida = os.path.join(pasta_projeto,'Dados' , 'Origem','CGA - Faturas', ref_ano)

try:
    os.mkdir(caminho_faturas_saida)
    #print(f"criando pasta {caminho_faturas_saida}")
except:
    print("pasta ano já existe")
    pass

caminho_faturas_saida = os.path.join(caminho_faturas_saida, meses_dict[ref_mes])

try:
    os.mkdir(caminho_faturas_saida)
    print(f"criando pasta {caminho_faturas_saida}")
except:
    print("pasta mês já existe")
    pass



for fatura in os.listdir(caminho_faturas_drive_ano_mes):
    if fatura.endswith(".pdf"):
        destino = os.path.join(caminho_faturas_drive_ano_mes,fatura)
        if os.path.isfile(destino):
            print(f"arquivo {fatura} já existe na pasta")
            pass
        else:
            shutil.copy2(destino, caminho_faturas_saida)
            print(f"arquivo {fatura} criado na pasta")
    
