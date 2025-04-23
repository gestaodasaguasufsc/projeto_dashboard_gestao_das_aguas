# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 09:16:47 2025

@author: Usuario
"""
import os
import pandas as pd
import numpy as np
import glob


pasta_projeto = os.path.dirname(os.path.abspath('__file__')) 
pasta_atualizacao_df = os.path.join(pasta_projeto,'Dados','Produtos','atualizacao_dfs')

try:
    os.mkdir(os.path.join(pasta_atualizacao_df))
except:
    pass


### - criando um dataframe vazio com as colunas existentes do colunas_df.csv:
 
caminho_colunas_df_csv = os.path.join(pasta_projeto,'Dados' , 'Origem','colunas_df.csv')
dados_agua_df_vazio = pd.read_csv(caminho_colunas_df_csv)

#passo1 = converter excel em df (para novos dados até código definitivo ficar pronto)
    
    
nome_arquivo_xls= 'M00 - Dados Mensais 202210 a 202303.xlsx'

xls_file = pd.ExcelFile(os.path.join(pasta_projeto, 'Dados', 'Origem', 'xls_origem', nome_arquivo_xls))
     
pasta_dados_csv = os.path.join(pasta_projeto, 'Dados', 'Origem', 'CSVs')
try:
    os.mkdir(pasta_dados_csv)
except:
    pass


     
for sheet_name in xls_file.sheet_names:   
      
    df = pd.read_excel(xls_file, sheet_name)    
    df.columns = dados_agua_df_vazio.columns
    df.to_csv(os.path.join(pasta_atualizacao_df,f'{sheet_name}.csv'), index=False)
    

dict_dfs = {}

for csv in os.listdir(pasta_atualizacao_df):
    
    if csv == 'dados_agua_df_para_atualizar.csv':
        pass
    else:
        print(csv)
        nome = (f'{csv[:-4]}_df')
        df_csv = pd.read_csv(os.path.join(pasta_atualizacao_df, csv),encoding='utf-8')
        #df_csv = df_csv.dropna() 
        dict_dfs[nome] = df_csv
    

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
    
    
 
## - exportar o arquivo para um csv unico:

def exportar_pd_unico_to_csv(dados_agua_df, pasta_atualizacao_df):
    
    caminho_dados_agua_csv = os.path.join(pasta_atualizacao_df, 'dados_agua_df_para_atualizar.csv')
    dados_agua_df.to_csv(caminho_dados_agua_csv, index=False)
    

exportar_pd_unico_to_csv(dados_agua_df, pasta_atualizacao_df)


#
concatenar = 'SIM'

caminho_dados_agua_df = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df.csv')
dados_agua_df_antigo = pd.read_csv(caminho_dados_agua_df, encoding='utf-8')
dados_agua_df_antigo['Dtime']= pd.to_datetime(dados_agua_df_antigo['Dtime'])

if concatenar == 'SIM':
    
    dados_agua_df = pd.concat([dados_agua_df_antigo, dados_agua_df], ignore_index=True)
    #neste caso, origem e saida são o mesmo arquivo, irá sobreescrever
    caminho_dados_agua_df_saida = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df_4.csv')
    dados_agua_df.to_csv(caminho_dados_agua_df_saida, index=False)
else:
    pass
#----------------------------------------------------------------

dados_agua_df_antigo.info()
dados_agua_df.info()


