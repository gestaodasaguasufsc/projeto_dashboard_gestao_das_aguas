# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 23:35:15 2025

@author: Usuario
"""
import os
import pandas as pd
import numpy as np
import glob

#--------------------------------------------------------------------------------------------------------------------------------
    
pasta_projeto = os.path.dirname(os.path.abspath('__file__'))

nome_arquivo_xls = 'M00 - Dados mensais_R5.xlsx'
xls_file = pd.ExcelFile(os.path.join(pasta_projeto, 'Dados', 'Origem', 'xls_origem', nome_arquivo_xls))
    
pasta_dados_csv = os.path.join(pasta_projeto, 'Dados', 'Origem', 'CSVs')
try:
    os.mkdir(pasta_dados_csv)
except:
    pass
    
caminho_colunas_df_csv = os.path.join(pasta_projeto,'Dados' , 'Origem','colunas_df.csv')
dados_agua_df_vazio = pd.read_csv(caminho_colunas_df_csv)

for sheet_name in xls_file.sheet_names:
    if 'geral' in sheet_name.lower():
        pass
    elif 'ajuda' in sheet_name.lower():
        pass
    elif 'auxiliar_referencia' in sheet_name.lower():
        pass
    elif 'referencia_csv' in sheet_name.lower():
        pass
    else:
        df = pd.read_excel(xls_file, sheet_name)
        df.columns = dados_agua_df_vazio.columns
        df.to_csv(os.path.join(pasta_dados_csv,f'{sheet_name}.csv'), index=False)
   


# Percorrer cada csv, converter em dataframe e adicionar a um dicionário:
    
dict_dfs = {}

for csv in os.listdir(pasta_dados_csv):
    caminho = os.path.join(pasta_dados_csv,csv)
    nome = (f'{csv[:-4]}_df')
    df = pd.read_csv(caminho)
    
    dict_dfs[nome] = df

# Percorrer cada csv, converter em dataframe e adicionar a um dicionário:

lista_dict_dfs_chaves = list(dict_dfs.keys())
lista_dict_dfs_chaves.sort()
sorted_dict_dfs = {}
# Sorted Dictionary
for chave in lista_dict_dfs_chaves:
    sorted_dict_dfs[chave] = dict_dfs[chave]
   
dict_dfs = sorted_dict_dfs


dados_agua_df = dados_agua_df_vazio
for chave in dict_dfs:
    dados_agua_df = pd.concat([dados_agua_df, dict_dfs[chave]], ignore_index=True)


## - verificar e contar número de linhas com NAN na coluna ANO

dados_agua_df = dados_agua_df.dropna(subset=['ANO'])

dados_agua_df = dados_agua_df.reset_index(drop=True) # IMPORTANTE (PRECISA RESETAR O INDEX SENÃO HAVERÁ FALHAS NO DF FINAL]!!!!!!!!!!!!!!!


## - corrige texto da coluna Mês e associa a coluna mês-N o número do mês

        
meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
meses_n = np.arange(13)[1:]

# Substituindo texto mês com a primeira letra não maiuscula
#https://www.hashtagtreinamentos.com/pandas-where-ciencia-de-dados

lista_unique_mes = dados_agua_df['MES'].unique()
   
for i in range(len(meses)):
    dados_agua_df['MES'] = np.where(dados_agua_df['MES'] == meses[i].lower(), meses[i], dados_agua_df['MES'])
lista_unique_mes = dados_agua_df['MES'].unique()

   
# criando coluna df (MES_N) e associando com a coluna MES
   
for i in range(len(meses)):
    if i == 0:
        dados_agua_df['MES_N'] = np.where(dados_agua_df['MES'] == meses[i], meses_n[i], 0)
    else:
        dados_agua_df['MES_N'] = np.where(dados_agua_df['MES'] == meses[i], meses_n[i], dados_agua_df['MES_N'])

lista_unique_mes_N = dados_agua_df['MES_N'].unique()
   
## - corrige texto da coluna Mês e associa a coluna mês-N o número do mês

dados_agua_df['DIA'] = 20
df = dados_agua_df[['ANO','MES_N','DIA']]
df.columns = ["year", "month", "day"]
dados_agua_df['Dtime'] = pd.to_datetime(df)


## - remover coluna Volume Consumido, pois não representa o consumo, apenas a diferença entre as leituras dos hidrômetros, 
## - e estas retornam a zero, o que gera valores negativos:

dados_agua_df.info()
dados_agua_df = dados_agua_df.drop('VOLUME_CONSUMIDO', axis=1)
dados_agua_df = dados_agua_df.drop('VERIFICACAO', axis=1)
dados_agua_df = dados_agua_df.drop('DIFERENCA', axis=1)
dados_agua_df = dados_agua_df.drop('DIA', axis=1)
    
#sub-def 16: -------------------------------------
## - exportar o arquivo para um csv unico:

def exportar_pd_unico_to_csv(dados_agua_df, pasta_projeto):
    
    caminho_dados_agua_csv = os.path.join(pasta_projeto, 'Dados', 'Produtos', 'dados_agua_df.csv')
    dados_agua_df.to_csv(caminho_dados_agua_csv, index=False)
    


exportar_pd_unico_to_csv(dados_agua_df, pasta_projeto)
    


