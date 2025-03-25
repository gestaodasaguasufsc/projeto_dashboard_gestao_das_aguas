# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 08:45:59 2025

@author: Usuario
"""
import os
import pandas as pd
from datetime import date
import numpy as np
import plotly.express as px
from plotly.offline import plot
import altair as alt
import streamlit as st

def main_abrir_csv_unico_func():
    dados_agua_df = abrir_csv_unico_func(pasta_produtos_func(pasta_projeto_func()))
    return dados_agua_df   

    #sub-def 1: -------------------------------------
def pasta_projeto_func():
    pasta_projeto = os.path.dirname(os.path.abspath('__file__'))
    return pasta_projeto


    #sub-def 2: -------------------------------------
def pasta_produtos_func(pasta_projeto):
    pasta_produtos = os.path.join(pasta_projeto,'Dados', 'Produtos')
    return pasta_produtos

    #sub-def 3: -------------------------------------
def abrir_csv_unico_func(pasta_produtos):

    caminho_dados_agua_csv = os.path.join(pasta_produtos, 'dados_agua_df.csv')
    dados_agua_df = pd.read_csv(caminho_dados_agua_csv)
    return dados_agua_df

    #sub-def 4: ------------------------------------
def pasta_figuras_func(pasta_projeto):
    # mudando para pasta de figuras
    pasta_figuras = os.path.join(pasta_projeto,'Figuras')
    print('Pasta figuras: ', pasta_figuras)
    return pasta_figuras   

############## Parte 2 - código geração de mapas e dados tabulares de consumo de água de 2013 ao momento presente

# Passo 1 - gerar df único (dados_agua_df_sHU) com todos os dados de água

pasta_projeto = pasta_projeto_func()
dados_agua_df = main_abrir_csv_unico_func()
dados_agua_df['ANO'] = dados_agua_df['ANO'].astype('int')
dados_agua_df = dados_agua_df.drop(columns=['CONCESSIONARIA','MATRICULA', 'CAMPUS','LOCAL','CIDADE','N_HIDROMETRO'], axis=1)
dados_agua_df = dados_agua_df.rename(columns={'COD_HIDROMETRO': 'HIDROMETRO'})

cadastro_hidrometros_link = os.path.join(pasta_projeto, 'Dados', 'Origem', 'Planilha_de_referencia_cadastro_hidrometros.csv')
cadastro_hidrometros_df = pd.read_csv(cadastro_hidrometros_link, encoding='latin-1', sep = ';')
cadastro_hidrometros_df = cadastro_hidrometros_df.drop(columns=['Consumo médio dos últimos 6 meses (m3) - ref 9_2024','Atualizacao_Cadastro'], axis=1)
cadastro_hidrometros_df = cadastro_hidrometros_df.rename(columns={'Observacao': 'Faturamento'})

dados_agua_df = dados_agua_df.rename(columns={'HIDROMETRO': 'Hidrometro'})
dados_agua_df = dados_agua_df.merge(cadastro_hidrometros_df, on='Hidrometro', how='left')

dados_agua_df_sHU = dados_agua_df[dados_agua_df['Hidrometro']!='H014'] #remove o Hospital Universitário da análise


anos = dados_agua_df['ANO'].unique().tolist()
anos.sort(reverse=True)
meses = dados_agua_df['MES_N'].unique().tolist()
meses.sort(reverse=True)

dados_agua_df['Dtime'] = pd.to_datetime(dados_agua_df['Dtime'],format='%Y-%m-%d') #formata a coluna Dtime para datetime
maior_tempo = dados_agua_df['Dtime'].max() #encontra o último mês e ano com dados disponíveis no banco de dados

maior_ano = maior_tempo.year
index_ano = anos.index(maior_ano) #encontra o index do maior ano para usar no sidebox do streamlit
maior_mes = maior_tempo.month
index_mes = meses.index(maior_mes) #encontra o index do maior mês para usar no sidebox do streamlit

dados_agua_df = dados_agua_df.rename(columns={'COD_HIDROMETRO': 'HIDROMETRO'})

dados_agua_df = dados_agua_df.rename(columns={'HIDROMETRO': 'Hidrometro'})

dados_agua_df_sHU = dados_agua_df[dados_agua_df['Hidrometro']!='H014'] 

dados_agua_df_sHU['ANO_Categ']= dados_agua_df_sHU['ANO']
dados_agua_df_sHU['ANO_Categ'] = dados_agua_df_sHU['ANO_Categ'].astype('str')

lista_cidade = dados_agua_df_sHU['Cidade'].unique().tolist()
for i, item in enumerate(lista_cidade):
    print(i, item)


dict_agrupamento = {
    'UFSC - Total':['UFSC - Total'],
    'Campus Florianópolis - todos':['Florianópolis - Trindade', 'Florianópolis - Outros'],
    'UFSC - Total campi excluído Florianópolis':['Araquari', 'Curitibanos', 'Joinville', 'Araranguá', 'Blumenau'],
    'Campus Florianópolis - excluído Campus Trindade':['Florianópolis - Outros'],
    'Campus Florianópolis - somente Campus Trindade':['Florianópolis - Trindade'],
    'Campus Araranguá':['Araranguá'],
    'Campus Blumenau': ['Blumenau'],
    'Campus Curitibanos':['Curitibanos'],
    'Campus Joinville': ['Joinville'],
    'Unidade Araquari':['Araquari']
    }

lista_agrupamento = list(dict_agrupamento.keys())
print(lista_agrupamento)
    
dict_dataframes = {}


for i, item in enumerate(dict_agrupamento.values()):
   df_concatenado = pd.DataFrame(columns=dados_agua_df_sHU.columns)
   print(i, item)
   if item[0] == 'UFSC - Total':
       dataframe = dados_agua_df_sHU
       df_concatenado = pd.concat([df_concatenado, dataframe], axis=0)
   else:
       
       for subitem in item:
           print(subitem)
           dataframe = dados_agua_df_sHU[dados_agua_df_sHU['Cidade']==subitem]
           df_concatenado = pd.concat([df_concatenado, dataframe], axis=0)
   dict_dataframes[lista_agrupamento[i]] = df_concatenado
        
for item in dict_dataframes.values():
    print('dict_dataframes', item)

# manual - exemplo
agrupamento_selecionado = 'Campus Florianópolis - excluído Campus Trindade'

df_selecionado = dict_dataframes[agrupamento_selecionado] 
volume_faturado_por_ano = df_selecionado.groupby(['ANO'])['VOLUME_FATURADO'].sum().reset_index()
custo_faturado_por_ano = df_selecionado.groupby(['ANO'])['VALOR_TOTAL'].sum().reset_index()
print(volume_faturado_por_ano)
df_selecionado_dataframe = pd.concat([volume_faturado_por_ano, custo_faturado_por_ano['VALOR_TOTAL']],axis=1)
df_selecionado_dataframe['Agrupamento Selecionado'] = agrupamento_selecionado
df_selecionado_dataframe = df_selecionado_dataframe.rename(columns=
                                                          {'ANO':'Ano',
                                                              'VALOR_TOTAL': 'Custo Total (R$)',
                                                           'VOLUME_FATURADO': 'Volume Faturado (m³)'
                                                           })
df_selecionado_dataframe = df_selecionado_dataframe.iloc[:,[0,3,1,2]]


lista_ucs = dados_agua_df_sHU['Hidrometro'].unique().tolist()
lista_local = dados_agua_df_sHU['Local'].unique().tolist()
lista_uc_local = []
for i,uc in enumerate(lista_ucs):
    nome_uc_local = lista_ucs[i] + " " + lista_local[i]
    lista_uc_local.append(nome_uc_local)
    

def boxplot_func_px(volume_faturado_por_mes_ano):
   
    chart = px.box(volume_faturado_por_mes_ano,
                 x="MES_N",  # Month (column index after pivot)
                 y="VOLUME_FATURADO", # Values
                 color='ANO',
                 labels={'ANO': 'Ano','VOLUME_FATURADO': 'Volume Faturado (m³)' },
                 boxmode='group',
                 points='all'
                 )
        
    
    return chart

def scatter_func_px(volume_faturado_por_mes_ano):
   
    chart = px.scatter(volume_faturado_por_mes_ano,
                 x="MES_N",  # Month (column index after pivot)
                 y="VOLUME_FATURADO", # Values
                 labels={'ANO': 'Ano','VOLUME_FATURADO': 'Volume Faturado (m³)' },
                 color='ANO',  # Coluna para a cor
                 color_continuous_scale='Viridis', 
                 )
        
    
    return chart

def line_func_px(volume_faturado_por_mes_ano):
   
    chart = px.line(volume_faturado_por_mes_ano,
                 x="MES_N",  # Month (column index after pivot)
                 y="VOLUME_FATURADO", # Values
                 labels={'ANO': 'Ano','VOLUME_FATURADO': 'Volume Faturado (m³)' },
                 color='ANO'  # Coluna para a cor
                 #color_continuous_scale='Viridis',
                 )
        
    
    return chart



volume_faturado_por_mes_ano = dados_agua_df_sHU.groupby(['ANO', 'MES_N'])['VOLUME_FATURADO'].sum().reset_index()
#volume_faturado_pivot = volume_faturado_por_mes_ano.pivot(index='ANO', columns='MES_N', values='VOLUME_FATURADO')


dados_agua_df_sHU.info()


anos_selecionados_fig1 = st.multiselect("Selecione os anos desejados no gráfico:",
    options=volume_faturado_por_mes_ano['ANO'].unique(),  # Opções do multi-check
    default=volume_faturado_por_mes_ano['ANO'].unique()   # Valores padrão selecionados
    )

# Filtrar o DataFrame com base nos anos selecionados
filtered_df_fig1 = volume_faturado_por_mes_ano[volume_faturado_por_mes_ano['ANO'].isin(anos_selecionados_fig1)]
fig1 = boxplot_func_px(filtered_df_fig1)
plot(fig1)


anos_selecionados_fig2 = st.multiselect(    "Selecione os anos desejados no gráfico:",
    options=volume_faturado_por_mes_ano['ANO'].unique(),  # Opções do multi-check
    default=volume_faturado_por_mes_ano['ANO'].unique()  # Valores padrão selecionados
    )

# Filtrar o DataFrame com base nos anos selecionados
filtered_df_fig2 = volume_faturado_por_mes_ano[volume_faturado_por_mes_ano['ANO'].isin(anos_selecionados_fig2)]
fig2 = scatter_func_px(filtered_df_fig2)
plot(fig2)


anos_selecionados_fig3 = st.multiselect(    "Selecione os anos desejados no gráfico:",
    options=volume_faturado_por_mes_ano['ANO'].unique(),  # Opções do multi-check
    default=volume_faturado_por_mes_ano['ANO'].unique()   # Valores padrão selecionados
    )

# Filtrar o DataFrame com base nos anos selecionados
filtered_df_fig3 = volume_faturado_por_mes_ano[volume_faturado_por_mes_ano['ANO'].isin(anos_selecionados_fig3)]

fig3 = line_func_px(filtered_df_fig3)
plot(fig3)
# para o streamlit -> st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

