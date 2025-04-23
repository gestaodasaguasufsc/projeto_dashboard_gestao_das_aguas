# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 08:51:37 2025

@author: Usuario
"""

import os
import pandas as pd
import numpy as np
import glob


pasta_projeto = os.path.dirname(os.path.abspath('__file__')) 
pasta_sapiens_df = os.path.join(pasta_projeto,'Dados','Origem','xls_origem', 'Sapiens')
pasta_sapiens_csv = os.path.join(pasta_sapiens_df,'csv')


try:
    os.mkdir(os.path.join(pasta_sapiens_df))
except:
    pass

try:
    os.mkdir(os.path.join(pasta_sapiens_csv))
except:
    pass



### - criando um dataframe vazio com as colunas existentes do colunas_df.csv:
 
caminho_colunas_df_csv = os.path.join(pasta_projeto,'Dados' , 'Origem','colunas_df.csv')
dados_agua_df_vazio = pd.read_csv(caminho_colunas_df_csv)

#passo1 = converter excel em df (para novos dados até código definitivo ficar pronto)
    
    
nome_arquivo_xls= 'M00 - Dados mensais_Sapiens2017_2025_.xlsx'

xls_file = pd.ExcelFile(os.path.join(pasta_sapiens_df, nome_arquivo_xls))
     
     
for sheet_name in xls_file.sheet_names:   
      
    df = pd.read_excel(xls_file, sheet_name)    
    df.columns = dados_agua_df_vazio.columns
    df.to_csv(os.path.join(pasta_sapiens_csv,f'{sheet_name}.csv'), index=False)
    

dict_dfs = {}

for csv in os.listdir(pasta_sapiens_csv):
    
    df_csv = pd.read_csv(os.path.join(pasta_sapiens_csv, csv),encoding='utf-8')
    #df_csv = df_csv.dropna() 
    dict_dfs[csv] = df_csv
    

### - percorrer cada csv, converter em dataframe e adicionar a um dicionário:

lista_dict_dfs_chaves = list(dict_dfs.keys())
lista_dict_dfs_chaves.sort()
sorted_dict_dfs = {}
# Sorted Dictionary
for chave in lista_dict_dfs_chaves:
    sorted_dict_dfs[chave] = dict_dfs[chave]
   
dict_dfs = sorted_dict_dfs
    


          
## - concatenar todos os dataframes em um único dataframe, 


dados_agua_df = dados_agua_df_vazio
for chave in dict_dfs:
    dados_agua_df = pd.concat([dados_agua_df, dict_dfs[chave]], ignore_index=True)
    

dados_agua_df = dados_agua_df.dropna(subset=['ANO'])
    
dados_agua_df = dados_agua_df.reset_index(drop=True) # IMPORTANTE (PRECISA RESETAR O INDEX SENÃO HAVERÁ FALHAS NO DF FINAL]!!!!!!!!!!!!!!!
    
## - corrige texto da coluna MES e associa a coluna MES-N o número do mês
      
meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
meses_n = np.arange(13)[1:]
    
# Substituindo texto mês com a primeira letra não maiuscula
#https://www.hashtagtreinamentos.com/pandas-where-ciencia-de-dados


   
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
   


## - corrige texto da coluna MES e associa a coluna MES-N o número do mês

    #https://stackoverflow.com/questions/58072683/combine-year-month-and-day-in-python-to-create-a-date
    #inserir dia 20 a todos os registros
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
    
sapiens_df =  dados_agua_df  
 
## - exportar o arquivo para um csv unico:

def exportar_pd_unico_to_csv(sapiens_df, pasta_sapiens_csv):
    
    caminho_sapiens_csv = os.path.join(pasta_sapiens_csv, 'Sapiens.csv')
    sapiens_df.to_csv(caminho_sapiens_csv, index=False)
    

exportar_pd_unico_to_csv(sapiens_df, pasta_sapiens_csv)



#
concatenar = 'SIM'

caminho_dados_agua_df_antigo = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df_4.csv')
dados_agua_df_antigo = pd.read_csv(caminho_dados_agua_df_antigo, encoding='utf-8')

df = dados_agua_df_antigo
df = df[df['COD_HIDROMETRO']!='H130']
df = df[df['COD_HIDROMETRO']!='H131']

dados_agua_df_antigo = df
dados_agua_df_antigo['Dtime']= pd.to_datetime(dados_agua_df_antigo['Dtime'])

if concatenar == 'SIM':
    
    dados_agua_df = pd.concat([dados_agua_df_antigo, sapiens_df], ignore_index=True)        
else:
    pass

dados_agua_df = dados_agua_df.sort_values(by=['Dtime', 'COD_HIDROMETRO'], ascending=[True, True])


#----------------------------------------------------------------


caminho_dados_agua_df_saida = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df_5_202503_com_sapiens.csv')
dados_agua_df.to_csv(caminho_dados_agua_df_saida, index=False)


#dados_agua_df_antigo.info()
dados_agua_df.info()
