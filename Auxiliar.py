# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 08:45:59 2025

@author: Usuario
"""
import os
import pandas as pd
import geopandas as gpd
from datetime import date
import numpy as np
import plotly.express as px
from plotly.offline import plot
import altair as alt
import streamlit as st
import plotly.colors as pc


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
#for i, item in enumerate(lista_cidade):
#    print(i, item)


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
#print(lista_agrupamento)
    
dict_dataframes = {}


for i, item in enumerate(dict_agrupamento.values()):
   df_concatenado = pd.DataFrame(columns=dados_agua_df_sHU.columns)
   #print(i, item)
   if item[0] == 'UFSC - Total':
       dataframe = dados_agua_df_sHU
       df_concatenado = pd.concat([df_concatenado, dataframe], axis=0)
   else:
       
       for subitem in item:
           #print(subitem)
           dataframe = dados_agua_df_sHU[dados_agua_df_sHU['Cidade']==subitem]
           df_concatenado = pd.concat([df_concatenado, dataframe], axis=0)
   dict_dataframes[lista_agrupamento[i]] = df_concatenado
        
#for item in dict_dataframes.values():
 #   print('dict_dataframes', item)

# manual - exemplo
agrupamento_selecionado = 'Campus Florianópolis - excluído Campus Trindade'

df_selecionado = dict_dataframes[agrupamento_selecionado] 
volume_faturado_por_ano = df_selecionado.groupby(['ANO'])['VOLUME_FATURADO'].sum().reset_index()
custo_faturado_por_ano = df_selecionado.groupby(['ANO'])['VALOR_TOTAL'].sum().reset_index()
#print(volume_faturado_por_ano)
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


#dados_agua_df_sHU.info()


anos_selecionados_fig1 = st.multiselect("Selecione os anos desejados no gráfico:",
    options=volume_faturado_por_mes_ano['ANO'].unique(),  # Opções do multi-check
    default=volume_faturado_por_mes_ano['ANO'].unique()   # Valores padrão selecionados
    )

# Filtrar o DataFrame com base nos anos selecionados
filtered_df_fig1 = volume_faturado_por_mes_ano[volume_faturado_por_mes_ano['ANO'].isin(anos_selecionados_fig1)]
fig1 = boxplot_func_px(filtered_df_fig1)
#plot(fig1)


anos_selecionados_fig2 = st.multiselect(    "Selecione os anos desejados no gráfico:",
    options=volume_faturado_por_mes_ano['ANO'].unique(),  # Opções do multi-check
    default=volume_faturado_por_mes_ano['ANO'].unique()  # Valores padrão selecionados
    )

# Filtrar o DataFrame com base nos anos selecionados
filtered_df_fig2 = volume_faturado_por_mes_ano[volume_faturado_por_mes_ano['ANO'].isin(anos_selecionados_fig2)]
fig2 = scatter_func_px(filtered_df_fig2)
#plot(fig2)


anos_selecionados_fig3 = st.multiselect(    "Selecione os anos desejados no gráfico:",
    options=volume_faturado_por_mes_ano['ANO'].unique(),  # Opções do multi-check
    default=volume_faturado_por_mes_ano['ANO'].unique()   # Valores padrão selecionados
    )

# Filtrar o DataFrame com base nos anos selecionados
filtered_df_fig3 = volume_faturado_por_mes_ano[volume_faturado_por_mes_ano['ANO'].isin(anos_selecionados_fig3)]

fig3 = line_func_px(filtered_df_fig3)
#plot(fig3)
# para o streamlit -> st.plotly_chart(fig2, theme="streamlit", use_container_width=True)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")  # Remove "#" se presente
    r = int(hex_color[0:2], 16)  # Converte os primeiros 2 caracteres para decimal (vermelho)
    g = int(hex_color[2:4], 16)  # Converte os próximos 2 caracteres para decimal (verde)
    b = int(hex_color[4:6], 16)  # Converte os últimos 2 caracteres para decimal (azul)
    return (r, g, b)  # Retorna a tupla RGB


def line_func_px(df):
    
    
    
    # Defina as duas cores desejadas
    cor1 =  st.color_picker("Escolha a cor 1", '#3100FB')
    cor2 =  st.color_picker("Escolha a cor 2", '#E411E4')
    cor3 =  st.color_picker("Escolha a cor 3", '#CEE411')
    
    
    cor1_rgb = hex_to_rgb(cor1)
    cor2_rgb = hex_to_rgb(cor2)
    cor3_rgb = hex_to_rgb(cor3)

    
    num_colors = len(df['ANO'].unique())
    
    if num_colors == 1:
        color_discrete_sequence_ = cor1_rgb
    elif num_colors == 2:
        color_discrete_sequence_ = cor1_rgb + cor2_rgb
    else:
        if num_colors % 2 == 0: #verifica se é par
            num_colors_seq1 = num_colors/2
            num_colors_seq2 = num_colors/2
        else:
            num_colors_seq1 = num_colors/2-0.5
            num_colors_seq2 = num_colors/2+0.5
        sequencia1 = pc.n_colors(cor1_rgb, cor2_rgb, int(num_colors_seq1), colortype='tuple')
        sequencia2 = pc.n_colors(cor2_rgb, cor3_rgb, int(num_colors_seq2), colortype='tuple')
        color_discrete_sequence_ = sequencia1 + sequencia2
    
    lista_cores = []
    for item in color_discrete_sequence_:
        cor = 'rgb'+str(item)
        lista_cores.append(cor)
    color_discrete_sequence_ = lista_cores
    
        
    chart = px.line(df,
                 x="MES_N",  # Month (column index after pivot)
                 y="VOLUME_FATURADO", # Values
                 labels={'ANO': 'Ano','VOLUME_FATURADO': 'Volume Faturado (m³)' },
                 color='ANO',  # Coluna para a cor
                 color_discrete_sequence=color_discrete_sequence_,
                 )
    chart.update_layout(xaxis=dict(dtick=1))
    # Definir o intervalo da legenda como 1 (se desejar)
    min_value = int(df['ANO'].min())
    max_value = int(df['ANO'].max())
    tickvals = np.arange(min_value, max_value + 1, 1)
    ticktext = tickvals.astype(str)
    chart.update_layout(coloraxis=dict(colorbar=dict(tickvals=tickvals, ticktext=ticktext)))    
    
    return chart

fig3 = line_func_px(filtered_df_fig3)
#plot(fig3)



# Passo 2 - carregar dicionário de shapes

#Carregando dados shapefile

#GDB Esri
#pasta_projeto = ""
pasta_projeto = pasta_projeto_func()
shapes_pasta = os.path.join(pasta_projeto, 'Dados','Origem','Shapes')
print(shapes_pasta)

dict_SAA_UFSC = {
    'hidrometros':'UFSC_Hidrometros',
    'Limite_UFSC' :  'CGA_Limite_Campus_UFSC_Trindade_112021_editado',
    'Rede_Interna_UFSC' : 'Rede_Interna_UFSC',
    'Rede_CASAN' : 'Rede_Casan_',
    'Reservatorios' : 'Reservatorios',
    'SubSetores_Agua' : 'SubSetores_Agua'
}

dict_shapes = {}

for chave in dict_SAA_UFSC:
  nome_shp =  f'{dict_SAA_UFSC[chave]}.shp'
  link = ""  
  link = os.path.join(shapes_pasta,nome_shp)
  shape = gpd.read_file(link)
  shape = shape.to_crs(epsg=4326)
  dict_shapes[chave] = shape



#Passo 3 - edição hidrometros_shp


#remover colunas 4 e 5 hidrometro_shp

x = 4 #coluna 4 - Xcoord
y = 5 #coluna 5 - Ycoord
hidrometros_shp = dict_shapes['hidrometros']
colunas_a_manter = np.r_[0:x, x+1:y, y+1:hidrometros_shp.shape[1]]
hidrometros_shp = hidrometros_shp.iloc[:,colunas_a_manter]
hidrometros_shp.rename(columns={'Nome_hidro': 'Hidrometro'}, inplace=True)

def localiza_hidrometro_func (df_i, valor, shp):
    df = df_i.iloc[:,[1,11]]
    df['nome_uc_local'] = df['Hidrometro'] +" " + df['Local']
    selecao = df.loc[df['nome_uc_local']==valor, 'Hidrometro'].iloc[0]
    lat = shp.loc[shp['Hidrometro']==selecao,'Latitude'].iloc[0]
    long = shp.loc[shp['Hidrometro']==selecao,'Longitude'].iloc[0]
    lista_keys = ['hid_sel', 'lat', 'long']
    saida = [selecao, lat, long]
    dict_saida = {}
    for i, item in enumerate(lista_keys):
        dict_saida[item] = saida[i]
    return dict_saida



selecao_uc_mapa = 	"H001 Almoxarifado e Transportes (PU 11 e 06)"


def localiza_hidrometro_1_func (df_i, valor):
    df = df_i.iloc[:,[1,11]]
    df['nome_uc_local'] = df['Hidrometro'] +" " + df['Local']
    selecao = df.loc[df['nome_uc_local']==valor, 'Hidrometro'].iloc[0]
    return selecao

#selecao = localiza_hidrometro_1_func (cadastro_hidrometros_df, selecao_uc_mapa)

#print(  'SELECAO: ',selecao)


#lat = hidrometros_shp.loc[hidrometros_shp['Hidrometro']=='H001','Latitude']
#print(lat)

#long = hidrometros_shp.loc[hidrometros_shp['Hidrometro']==selecao,'Longitude']

#with col1:
    #selecao_uc_mapa = st.selectbox('Selecione a unidade consumidora', lista_uc_local, key='selectbox_mapa_uc')        

dict_saida = localiza_hidrometro_func(cadastro_hidrometros_df, selecao_uc_mapa, hidrometros_shp)
#print(dict_saida)

#saida =  [selecao, lat, long]

hidrometros_shp_merge = hidrometros_shp.merge(cadastro_hidrometros_df, on='Hidrometro', how='left')

uc_selecionada = 'H001'

#for index, row in hidrometros_shp_merge.iterrows():
 #   if row.geometry is not None and row.geometry.is_valid:
                                    
  #        if row['Hidrometro'] == uc_selecionada:
              #print("SIM", row['Hidrometro'])
              
              
#Gerando lista_ucs_local


lista_ucs = dados_agua_df_sHU['Hidrometro'].unique().tolist()
lista_local = dados_agua_df_sHU['Local'].unique().tolist()
lista_uc_local = []

for i,uc in enumerate(lista_ucs):
    nome_uc_local = lista_ucs[i] + " " + lista_local[i]
    lista_uc_local.append(nome_uc_local)

lista_uc_local.sort()
lista_uc_local.append("UFSC - visão geral")
index_visao_geral =lista_uc_local.index("UFSC - visão geral")
    

#gerando dicionário com dataframes filtrados por agrupamentos de campi

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


#def cria_listas_campi_func (df_i):
 #   lista_cidades = df_i['Cidade'].unique()
  #  lista_nomes = ['Trindade','Outros','Araquari','Curitibanos','Joinville','Ararangua','Blumenau']
   # df = df_i.iloc[:,[4,33,31]]
    #df['nome_uc_local'] = df['Hidrometro'] + " " + df['Local']
    #dict_df = {}
    #for i,item in enumerate(lista_nomes):
     #   nome = f'df_cidades_{item}'
        #dict_cidades[nome] = lista_cidades[i]

        
df_i = cadastro_hidrometros_df

lista_cidades = df_i['Cidade'].unique()
n = 6

selecao_cidade = lista_cidades[n]
    
def gerador_lista_uc_local_por_campi_func (df_i, selecao_cidade):
    df_i = df_i[df_i['Cidade']!= 'Florianópolis  HU']
    df = df_i.iloc[:,[1,11,9]]
    df['nome_uc_local'] = df['Hidrometro'] + " " + df['Local']
    df_filtrada = df[df['Cidade'] == selecao_cidade]
    lista = df_filtrada['nome_uc_local'].tolist()
    return lista

df = df_i.iloc[:,[1,11,9]]
df['nome_uc_local'] = df['Hidrometro'] + " " + df['Local']
df_filtrada = df[df['Cidade'] == selecao_cidade]
lista_uc_local_2 = df_filtrada['nome_uc_local'].tolist()



#lista_uc_local_2 = gerador_lista_uc_local_por_campi_func (df_i,selecao_cidade)

#for item in lista_uc_local_2:
 #   print(item)
                       
def agrupado_por_ano_func(volume_faturado_por_ano, custo_faturado_por_ano):
    
                 
   # gráfico de volume
    fig1 = px.bar(volume_faturado_por_ano,
                  x='ANO',
                  y='VOLUME_FATURADO',
                  labels={'ANO': 'Ano', 'VOLUME_FATURADO': 'Volume Faturado (m³)'},
                  barmode='group'
                  )
    fig1.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1          # Set interval between ticks (and implicitly bars) to 1
                    ))
    
     # gráfico de custo   
    fig2 = px.bar(custo_faturado_por_ano,
                  x='ANO',
                  y='VALOR_TOTAL',
                  labels={'ANO': 'Ano', 'VALOR_TOTAL': 'Custo Faturado (m³)'},
                  barmode='group',  # Set barmode to 'group'
                        # Adjust height if necessary
                 )
    fig2.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1          # Set interval between ticks (and implicitly bars) to 1
        ))

    return fig1, fig2

def funcao_graf_uc_func(df, selecao_uc_mapa):
    df = df[df['Hidrometro']==selecao_uc_mapa]
    vol_uc = df.groupby(['ANO'])['VOLUME_FATURADO'].sum().reset_index()
    cus_uc = df.groupby(['ANO'])['VALOR_TOTAL'].sum().reset_index()
    graf_uc = agrupado_por_ano_func(vol_uc, cus_uc)
    return graf_uc[0], graf_uc[1]

df = dados_agua_df_sHU
selecao_uc_mapa = 'H001'
    

funcao_graf_uc = funcao_graf_uc_func(dados_agua_df_sHU, selecao_uc_mapa)
fig1 = funcao_graf_uc[0]              
plot(fig1)                   
fig2 = funcao_graf_uc[1]              
plot(fig2)                 
