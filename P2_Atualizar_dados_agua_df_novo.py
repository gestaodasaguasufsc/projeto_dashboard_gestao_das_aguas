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

pasta_projeto = os.path.dirname(os.path.abspath('__file__')) 
pasta_atualizacao_df = os.path.join(pasta_projeto,'Dados','Produtos','atualizacao_dfs')

# =============================================================================
# try:
#     os.mkdir(os.path.join(pasta_atualizacao_df))
# except:
#     pass
# =============================================================================


### - criando um dataframe vazio com as colunas existentes do colunas_df.csv:
 
caminho_colunas_df_csv = os.path.join(pasta_projeto,'Dados' , 'Origem','colunas_df_droped.csv')
dados_agua_df_vazio = pd.read_csv(caminho_colunas_df_csv)

#passo1 = converter excel em df (para novos dados até código definitivo ficar pronto)
  
    
pasta_dados_csv = os.path.join(pasta_projeto, 'Dados', 'Origem', 'CSVs')

#read csvs
dados_agua_df = dados_agua_df_vazio

for csv in os.listdir(pasta_dados_csv):
    caminho = os.path.join(pasta_dados_csv, csv)
    df = pd.read_csv(caminho, encoding='utf-8')
    df.dropna(subset=['CODIGO'],inplace=True)
    df = df.sort_values(by='CODIGO', ascending=True)
    df.columns = dados_agua_df_vazio.columns
    dados_agua_df = pd.concat([dados_agua_df,df], ignore_index=True)
    print(csv)
    if csv == "2026_08.csv":
        break
    else:
        pass
    
caminho_dados_agua_df_copia_antigo = os.path.join(pasta_projeto,'Dados' , 'Produtos','Auxiliar_produtos','dados_agua_df_antigo.csv')     
caminho_dados_agua_df_saida = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df.csv')

shutil.copy2(caminho_dados_agua_df_saida, caminho_dados_agua_df_copia_antigo)

dados_agua_df.to_csv(caminho_dados_agua_df_saida, index=False)


#### Parte 2 - copia das faturas do google drive para pasta de projeto no mês de referência



meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
meses_n = np.arange(13)[1:]

meses_dict = {}

for i in range(len(meses)):

    if meses_n[i] < 10:
        mes = "0" + str(meses_n[i])
        meses_dict[mes] = mes + " - " + meses[i].upper()
    else:
        mes = str(meses_n[i])
        meses_dict[mes] = mes + " - " + meses[i].upper()
#print(meses_dict)


ref_ano = referencia.split("_")[0]
ref_mes = referencia.split("_")[1]

caminho_faturas_drive = r'G:\Meu Drive\Gestão das Águas - Pastas compartilhadas\p09 - Site Gestao das Aguas - CGA\2 - Faturas de água e esgoto'

caminho_faturas_drive_ano_mes = os.path.join(caminho_faturas_drive,ref_ano, meses_dict[ref_mes])




