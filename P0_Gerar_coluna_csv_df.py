# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 12:46:48 2025

@author: Usuario
"""
import os
import pandas as pd

pasta_projeto = os.path.dirname(os.path.abspath('__file__'))
    


caminho_colunas_csv = os.path.join(pasta_projeto,'Dados' , 'Origem', 'xls_origem','colunas.csv')
df_vazio= pd.read_csv(caminho_colunas_csv)
coluna = df_vazio.columns.tolist()
nova_lista = coluna[0].split(';')
dados_agua_df_vazio = pd.DataFrame(columns = nova_lista)
dados_agua_df_vazio.to_csv(os.path.join(pasta_projeto,'Dados', 'Origem','colunas_df.csv' ),index=False)


caminho_colunas_df_csv = os.path.join(pasta_projeto,'Dados' , 'Origem','colunas_df.csv')

#resultado:
dados_agua_df_vazio_2 = pd.read_csv(caminho_colunas_df_csv)
