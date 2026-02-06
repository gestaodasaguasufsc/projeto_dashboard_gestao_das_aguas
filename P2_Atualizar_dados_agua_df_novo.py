# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 16:46:06 2026

@author: Usuario
"""

import os
import pandas as pd
import numpy as np
import glob


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
    if csv == "2025_12.csv":
        break
    else:
        pass
    
caminho_dados_agua_df_saida = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df_.csv')
dados_agua_df.to_csv(caminho_dados_agua_df_saida, index=False)



