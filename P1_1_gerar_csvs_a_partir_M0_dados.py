# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 09:16:47 2025

@author: Usuario
"""
import os
import pandas as pd
import numpy as np
import glob
from datetime import datetime


pasta_projeto = os.path.dirname(os.path.abspath('__file__')) 

caminho_dados_agua_csv = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df - Copia.csv')
caminho_dados_csvs2 = os.path.join(pasta_projeto,'Dados' , 'Origem','CSVs_2')
dados_agua_df_copia = pd.read_csv(caminho_dados_agua_csv)

data_lista = dados_agua_df_copia['Dtime'].unique()

    
nome_arquivo_xls = 'M00 - Dados mensais.xlsx'
xls_file = pd.ExcelFile(os.path.join(pasta_projeto, 'Dados', 'Origem', 'xls_origem', nome_arquivo_xls))

caminho_colunas_df_droped_csv = os.path.join(pasta_projeto,'Dados' , 'Origem','colunas_df_droped.csv')
dados_agua_df_vazio = pd.read_csv(caminho_colunas_df_droped_csv)

# =============================================================================
# dados_agua_df_vazio['MES_N'] = 0
# dados_agua_df_vazio['Dtime'] = 0
# dados_agua_df_vazio.to_csv(caminho_colunas_df_droped_csv,index=False)
# =============================================================================


caminho_dados_csvs = os.path.join(pasta_projeto,'Dados' , 'Origem','CSVs')

for sheet_name in xls_file.sheet_names:
    if 'planilha_de_referencia_cadastro' in sheet_name.lower():
        pass
    elif 'auxiliar_referencia' in sheet_name.lower():
        pass
    elif 'geral' in sheet_name.lower():
        pass
    elif 'aux' in sheet_name.lower():
        pass
    else:
        print(sheet_name)
        df = pd.read_excel(xls_file, sheet_name)
        ## - corrige texto da coluna Mês e associa a coluna mês-N o número do mês
        df.dropna(subset=['Código'])
                
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        meses_n = np.arange(13)[1:]

        # Substituindo texto mês com a primeira letra não maiuscula
        
        try:
            df = df.rename(columns={'MÊS': 'MES'})
        except:
            pass
        
        lista_unique_mes = df['MES'].unique()
           
        for i in range(len(meses)):
            df['MES'] = np.where(df['MES'] == meses[i].lower(), meses[i], df['MES'])
        lista_unique_mes = df['MES'].unique()

           
        # criando coluna df (MES_N) e associando com a coluna MES
           
        for i in range(len(meses)):
            if i == 0:
                df['MES_N'] = np.where(df['MES'] == meses[i], meses_n[i], 0)
            else:
                df['MES_N'] = np.where(df['MES'] == meses[i], meses_n[i], df['MES_N'])

        lista_unique_mes_N = df['MES_N'].unique()
        
        
        if int(df.iloc[:,2].unique()[0]) <= 2018: #iloc coluna ANO
            df['ANORMALIDADE'] = ""
            col = df.pop('ANORMALIDADE')
            
            df.insert(21, 'ANORMALIDADE', col)
                        
        else:
            pass
                     
        
        
        ## - corrige texto da coluna Mês e associa a coluna mês-N o número do mês

        df['DIA'] = 20
        df_data = df[['ANO','MES_N','DIA']]
        df_data.columns = ["year", "month", "day"]
        df['Dtime'] = pd.to_datetime(df_data)

        df.info()
        
        
        df = df.drop(df.columns[[18,28,29,31]], axis=1) 
        #volume consumido
        #verificação
        #diferença
        #dia
              
             
        
        df.columns = dados_agua_df_vazio.columns
        
        csv_name = sheet_name+'.csv'
        df.to_csv(os.path.join(caminho_dados_csvs,csv_name),index=False)

# =============================================================================
#         if sheet_name == "2025_12": #limite de geração de CSVs
#             break
#         else:
#             pass
# =============================================================================
        
# 
#
# concatenar = 'SIM'
# 
# caminho_dados_agua_df = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df.csv')
# caminho_dados_agua_df_antigo = os.path.join(pasta_projeto,'Dados' , 'Produtos','Auxiliar_produtos','dados_agua_df_antigo.csv')
# dados_agua_df_antigo = pd.read_csv(caminho_dados_agua_df, encoding='utf-8')
# dados_agua_df_antigo['Dtime']= pd.to_datetime(dados_agua_df_antigo['Dtime'])
# dados_agua_df_antigo.to_csv(caminho_dados_agua_df_antigo, index=False) #exporta cópia do df antigo para pasta auxiliar
# 
# if concatenar == 'SIM':
#     
#     dados_agua_df = pd.concat([dados_agua_df_antigo, dados_agua_df], ignore_index=True)
#     #neste caso, origem e saida são o mesmo arquivo, irá sobreescrever
#     caminho_dados_agua_df_saida = os.path.join(pasta_projeto,'Dados' , 'Produtos','dados_agua_df.csv')
#     dados_agua_df.to_csv(caminho_dados_agua_df_saida, index=False)
# else:
#     pass
# #----------------------------------------------------------------
# 
# dados_agua_df_antigo.info()
# dados_agua_df.info()
# 
# =============================================================================


