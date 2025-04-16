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

    caminho_dados_agua_csv = os.path.join(pasta_produtos, 'dados_agua_df_3.csv')
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



def tratamento_de_dados_func(pasta):
    
    
    link = os.path.join(pasta_projeto, 'Dados', 'Origem', 'Planilha_de_referencia_cadastro_hidrometros.csv')
    df_cad = pd.read_csv(link, sep = ';')
    try:
        df_cad = df_cad.drop(columns=['Consumo médio dos últimos 6 meses (m3) - ref 9_2024','Atualizacao_Cadastro'], axis=1)
        df_cad = df_cad.rename(columns={'Observacao': 'Faturamento'})
    except:
        pass
      
     
    df = pd.read_csv(os.path.join(pasta_projeto,'Dados', 'Produtos' , 'dados_agua_df_3.csv'))
    df['ANO'] = df['ANO'].astype('int')
    df = df.drop(columns=['CONCESSIONARIA','MATRICULA', 'CAMPUS','LOCAL','CIDADE','N_HIDROMETRO'], axis=1)
    df = df.rename(columns={'COD_HIDROMETRO': 'Hidrometro'})
    df = df.merge(df_cad, on='Hidrometro', how='left')
    
          
    df_sHU = df[df['Hidrometro']!='H014']
    
    anos = df['ANO'].unique().tolist()
    anos.sort(reverse=True)
    meses = df['MES_N'].unique().tolist()
    meses.sort(reverse=True)
    df_sHU['Dtime'] = pd.to_datetime(df_sHU['Dtime'])
    maior_tempo = df_sHU['Dtime'].max() #encontra o último mês e ano com dados disponíveis no banco de dados
    menor_tempo = df_sHU['Dtime'].min()
    maior_ano = maior_tempo.year
    index_ano = anos.index(maior_ano) #encontra o index do maior ano para usar no sidebox do streamlit
    maior_mes = maior_tempo.month
    index_mes = meses.index(maior_mes) #encontra o index do maior mês para usar no sidebox do streamlit
    menor_ano = menor_tempo.year
    menor_mes = menor_tempo.month
    
    
    lista_cidades = df_sHU['Cidade'].unique().tolist()
    
    # ordenando e filtrando colunas em dados_agua_df
    df_sHU = df_sHU.iloc[:,[2,21,4,24,33,12,20,10,11,13,14,15,16,17,18,19,31,32,5,6,7,8,9,39,26,29,30,34,36,37]]
    
    saida = [df_cad, df, df_sHU, anos, meses, maior_ano, index_ano, maior_mes, index_mes, lista_cidades, menor_ano, menor_mes]
    return saida

pasta_projeto = pasta_projeto_func()

trat_func = tratamento_de_dados_func(pasta_projeto)

cadastro_hidrometros_df =   trat_func[0]
dados_agua_df =             trat_func[1]
dados_agua_df_sHU =         trat_func[2]
anos =                      trat_func[3]
meses =                     trat_func[4]
maior_ano =                 trat_func[5]
index_ano =                 trat_func[6]
maior_mes =                 trat_func[7]
index_mes =                 trat_func[8]
lista_cidades =             trat_func[9]

dados_agua_df_sHU.info()
    
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


def dict_dataframes_func(dct, df):
    
    list_agr = list(dct.keys())
    dict_dataframes = {}
   
    for i, item in enumerate(dct.values()):
        df_zero = pd.DataFrame(columns=df.columns)
       
        if item[0] == 'UFSC - Total':
            df_concatenado = pd.concat([df_zero, df], axis=0)
        
        else:
            for subitem in item:
               df_zero = df[df['Cidade']==subitem]
               df_concatenado = pd.concat([df_concatenado, df_zero], axis=0)
        dict_dataframes[list_agr[i]] = df_concatenado
    
    return list_agr, dict_dataframes


funcao_dict_dfs = dict_dataframes_func(dict_agrupamento, dados_agua_df_sHU)
lista_agrupamento = funcao_dict_dfs[0]
dict_dataframes = funcao_dict_dfs[1]
    




        
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
    print(i, uc, lista_local[i] )
    try:
        nome_uc_local = lista_ucs[i] + " " + lista_local[i]
        lista_uc_local.append(nome_uc_local)
    except:
        pass

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
hidrometros_shp_merge.to_csv(os.path.join(pasta_projeto,'Dados','Produtos','hidrometros_shp_merge.csv'))

uc_selecionada = 'H001'

#for index, row in hidrometros_shp_merge.iterrows():
 #   if row.geometry is not None and row.geometry.is_valid:
                                    
  #        if row['Hidrometro'] == uc_selecionada:
              #print("SIM", row['Hidrometro'])
              
              
#Gerando lista_ucs_local


lista_ucs = dados_agua_df_sHU['Hidrometro'].unique().tolist()
lista_local = dados_agua_df_sHU['Local'].unique().tolist()
lista_uc_local = []

lista_ucs = dados_agua_df_sHU['Hidrometro'].unique().tolist()
lista_local = dados_agua_df_sHU['Local'].unique().tolist()
lista_uc_local = []
for i,uc in enumerate(lista_ucs):
    print(i, uc, lista_local[i] )
    try:
        nome_uc_local = lista_ucs[i] + " " + lista_local[i]
        lista_uc_local.append(nome_uc_local)
    except:
        pass

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
#plot(fig1)                   
fig2 = funcao_graf_uc[1]              
#plot(fig2)                 

def dict_dataframes_func(dct, df):
    
    list_agr = list(dct.keys())
    dict_dataframes = {}
   
    for i, item in enumerate(dct.values()):
        df_zero = pd.DataFrame(columns=df.columns)
       
        if item[0] == 'UFSC - Total':
            df_concatenado = pd.concat([df_zero, df], axis=0)
        
        else:
            for subitem in item:
               df_zero = df[df['Cidade']==subitem]
               df_concatenado = pd.concat([df_concatenado, df_zero], axis=0)
        dict_dataframes[list_agr[i]] = df_concatenado
        
   
    return list_agr, dict_dataframes

funcao_dict_dfs = dict_dataframes_func(dict_agrupamento, dados_agua_df_sHU)
lista_agrupamento = funcao_dict_dfs[0]
dict_dataframes = funcao_dict_dfs[1]


agrupamento_selecionado_ind = lista_agrupamento[0]
ano_selecionado_ind = 2024
mes_selecionado_ind = 9

df_selecionado_agrupamento_ind = dict_dataframes[agrupamento_selecionado_ind] 


df_selecionado_ind = df_selecionado_agrupamento_ind.groupby(['ANO', 'MES_N'])[['VOLUME_FATURADO','VALOR_TOTAL']].sum().reset_index()
#df_selecionado_ind = df_selecionado_ind.sort_index(ascending=False, inplace=False)
df_selecionado_ind['VOLUME_FATURADO'] = df_selecionado_ind['VOLUME_FATURADO'].astype(int)
#gerando a coluna de médias

lm = []


df_selecionado_ind['VOL_MED_U6M'] = 0
df_selecionado_ind['VOL_VAR_ABS'] = 0 #VOLUME NO MÊS - MEDIA
df_selecionado_ind['VOL_VAR_PER'] = 0
df_selecionado_ind['CUS_MED_U6M'] = 0
df_selecionado_ind['CUS_VAR_ABS'] = 0 #VOLUME NO MÊS - MEDIA
df_selecionado_ind['CUS_VAR_PER'] = 0


for i, item in enumerate(df_selecionado_ind['VOLUME_FATURADO']):
    if i<=5:
        lm.append(item)
    
    else:
        lm.append(item)
        media = ((lm[i-1] + lm[i-2] +lm[i-3] + lm[i-4] +lm[i-5] +lm[i-6])/6)
        media = int("{:.0f}".format(media))
        variacao_abs = item - media
        variacao_per = variacao_abs/item
        df_selecionado_ind['VOL_MED_U6M'][i] = media
        df_selecionado_ind['VOL_VAR_ABS'][i] = variacao_abs
        df_selecionado_ind['VOL_VAR_PER'][i] = variacao_per

lm = []
for i, item in enumerate(df_selecionado_ind['VALOR_TOTAL']):
    if i<=5:
        lm.append(item)
    
    else:
        lm.append(item)
        media = ((lm[i-1] + lm[i-2] +lm[i-3] + lm[i-4] +lm[i-5] +lm[i-6])/6)
        media = int("{:.0f}".format(media))
        variacao_abs = item - media
        variacao_per = variacao_abs/item
        df_selecionado_ind['CUS_MED_U6M'][i] = media
        df_selecionado_ind['CUS_VAR_ABS'][i] = variacao_abs
        df_selecionado_ind['CUS_VAR_PER'][i] = variacao_per


  
    
def indicadores_vol_cus_func(
        agrupamento_selecionado_ind,
        ano_selecionado_ind,
        mes_selecionado_ind,
        dict_dataframes):


    df_selecionado_ind = dict_dataframes[agrupamento_selecionado_ind] 


    df_selecionado_ind = df_selecionado_agrupamento_ind.groupby(['ANO', 'MES_N'])[['VOLUME_FATURADO','VALOR_TOTAL']].sum().reset_index()
    #df_selecionado_ind = df_selecionado_ind.sort_index(ascending=False, inplace=False)
    df_selecionado_ind['VOLUME_FATURADO'] = df_selecionado_ind['VOLUME_FATURADO'].astype(int)
    #gerando a coluna de médias

    lm = []


    df_selecionado_ind['VOL_MED_U6M'] = 0
    df_selecionado_ind['VOL_VAR_ABS'] = 0 #VOLUME NO MÊS - MEDIA
    df_selecionado_ind['VOL_VAR_PER'] = 0
    df_selecionado_ind['CUS_MED_U6M'] = 0
    df_selecionado_ind['CUS_VAR_ABS'] = 0 #VOLUME NO MÊS - MEDIA
    df_selecionado_ind['CUS_VAR_PER'] = 0


    for i, item in enumerate(df_selecionado_ind['VOLUME_FATURADO']):
        if i<=5:
            lm.append(item)
        
        else:
            lm.append(item)
            media = ((lm[i-1] + lm[i-2] +lm[i-3] + lm[i-4] +lm[i-5] +lm[i-6])/6)
            media = int("{:.0f}".format(media))
            variacao_abs = item - media
            variacao_per = variacao_abs/item
            df_selecionado_ind['VOL_MED_U6M'][i] = media
            df_selecionado_ind['VOL_VAR_ABS'][i] = variacao_abs
            df_selecionado_ind['VOL_VAR_PER'][i] = variacao_per

    lm = []
    for i, item in enumerate(df_selecionado_ind['VALOR_TOTAL']):
        if i<=5:
            lm.append(item)
        
        else:
            lm.append(item)
            media = ((lm[i-1] + lm[i-2] +lm[i-3] + lm[i-4] +lm[i-5] +lm[i-6])/6)
            media = int("{:.0f}".format(media))
            variacao_abs = item - media
            variacao_per = variacao_abs/item
            df_selecionado_ind['CUS_MED_U6M'][i] = media
            df_selecionado_ind['CUS_VAR_ABS'][i] = variacao_abs
            df_selecionado_ind['CUS_VAR_PER'][i] = variacao_per
            
    return df_selecionado_ind

linha_mes_ano = df_selecionado_ind[(df_selecionado_ind['ANO']== ano_selecionado_ind) & (df_selecionado_ind['MES_N'] == mes_selecionado_ind)]
index_ind = linha_mes_ano.index[0]
volume_mes = linha_mes_ano['VOLUME_FATURADO'].iloc[0]
volume_media = linha_mes_ano['VOL_MED_U6M'].iloc[0]
volume_variacao_abs = linha_mes_ano['VOL_VAR_ABS'].iloc[0]
volume_variacao_per = linha_mes_ano['VOL_VAR_PER'].iloc[0]
custo_mes = linha_mes_ano['VALOR_TOTAL'].iloc[0]
custo_media = linha_mes_ano['CUS_MED_U6M'].iloc[0]
custo_variacao_abs = linha_mes_ano['CUS_VAR_ABS'].iloc[0]
custo_variacao_per = linha_mes_ano['CUS_VAR_PER'].iloc[0]



texto = (f'{volume_media:,.2f} m³').replace(",", "_").replace(".", ",").replace("_", ".")
#texto = str(f'{volume_media:,.2f} m³'.replace("", ".")

#depois que tiver a coluna média feita

#print(index_ind)
#print(df_selecionado_ind.iloc[index_ind])

#linha_mes_ano_m1 = df_selecionado_ind.iloc[:, index_ind-1]

#df['media_6_meses_excluindo_atual'] = df['valor'].rolling(window=7, center=False).apply(lambda x: x[:-1].mean(), raw=True)


#print(volume_mes)
#print(custo_mes)
#print(linha_mes_ano)
#print(linha_mes_ano_m1)


def trat_acumulado_por_ano_func (dct, agr_sel):

    df_sel = dct[agr_sel] 
    vol_ano = df_sel.groupby(['ANO'])['VOLUME_FATURADO'].sum().reset_index()
    cus_ano = df_sel.groupby(['ANO'])['VALOR_TOTAL'].sum().reset_index()
    
    df = pd.concat([vol_ano, cus_ano],axis=1).reset_index()
    df['Agrupamento Selecionado'] = agr_sel
    df['VALOR_TOTAL'] = df['VALOR_TOTAL'].apply(lambda x: f"{x:.2f}")
    df['VOLUME_FATURADO'] = df['VOLUME_FATURADO'].apply(lambda x: f"{x:.0f}")
    df = df.sort_values(by='ANO', ascending=False)
    df = df.rename(columns=
                                                              {'ANO':'Ano',
                                                                  'VALOR_TOTAL': 'Custo Total (R$)',
                                                               'VOLUME_FATURADO': 'Volume Faturado (m³)'
                                                               })
    df = df.iloc[:,[0,3,1,2]]

    return vol_ano, cus_ano, df

dct = dict_dataframes
agr_sel = lista_agrupamento[0]

df_sel = dct[agr_sel] 
vol_ano = df_sel.groupby(['ANO'])['VOLUME_FATURADO'].sum().reset_index()
cus_ano = df_sel.groupby(['ANO'])['VALOR_TOTAL'].sum().reset_index()


df = pd.concat([vol_ano, cus_ano['VALOR_TOTAL']],axis=1).reset_index()
df['Agrupamento Selecionado'] = agr_sel
#df['VALOR_TOTAL'] = df['VALOR_TOTAL'].apply(lambda x: f"{x:.2f}")
#df['VOLUME_FATURADO'] = df['VOLUME_FATURADO'].apply(lambda x: f"{x:.0f}")
df = df.sort_values(by='ANO', ascending=False)
df = df[['ANO','VOLUME_FATURADO','VALOR_TOTAL','Agrupamento Selecionado']]

df = df.rename(columns=
                                                          {'ANO':'Ano',
                                                              'VALOR_TOTAL': 'Custo Total (R$)',
                                                           'VOLUME_FATURADO': 'Volume Faturado (m³)'
                                                           })

import webbrowser #para o spyder apenas

from streamlit_pdf_viewer import pdf_viewer

# Display a PDF file

meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

uc_selecionada = 'H002'
ano_fatura = 2023
mes_fatura = 1
if mes_fatura <= 9:
    mes_fatura_str = '0' + str(mes_fatura)
else: 
    mes_fatura_str = str(mes_fatura)

mes_fatura_texto = mes_fatura_str  + ' - ' + meses[mes_fatura-1].upper()  
pasta_faturas = os.path.join(pasta_projeto, 'Dados', 'Origem', 'CGA - Faturas', str(ano_fatura), mes_fatura_texto)
for item in os.listdir(pasta_faturas):
    if item[:4] == uc_selecionada:
        pdf = pdf_viewer(os.path.join(pasta_faturas, item), width=700, height=1000)
        #pdf = os.path.join(pasta_faturas, item)                            
    else:
        pass                           

def abrir_fatura_pdf(uc_selecionada, ano_fatura, mes_fatura):
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    uc_selecionada = 'H002'
    ano_fatura = 2023
    mes_fatura = 1
    if mes_fatura <= 9:
        mes_fatura_str = '0' + str(mes_fatura)
    else: 
        mes_fatura_str = str(mes_fatura)

    mes_fatura_texto = mes_fatura_str  + ' - ' + meses[mes_fatura-1].upper()  
    pasta_faturas = os.path.join(pasta_projeto, 'Dados', 'Origem', 'CGA - Faturas', str(ano_fatura), mes_fatura_texto)
    for item in os.listdir(pasta_faturas):
        if item[:4] == uc_selecionada:
            pdf = pdf_viewer(os.path.join(pasta_faturas, item), width=700, height=1000)
            
        #pdf = os.path.join(pasta_faturas, item)                            
        else:
            pass 
    return pdf         
    
#pdf = abrir_fatura_pdf(uc_selecionada, ano_fatura, mes_fatura)
#st.write(pdf, width=750, height=1100)

# open an HTML file on my own (Windows) computer
#url = pdf
#webbrowser.open(url,new=2)    

#def indicadores_vol_cus_func_ultimos36meses(
 #       agrupamento_selecionado_ind,
  #      ano_selecionado_ind,
   #     mes_selecionado_ind,
    #    dict_dataframes):




agrupamento_selecionado_ind = lista_agrupamento[0]
ano_selecionado_ind = 2024
mes_selecionado_ind = 12
dct = dict_dataframes



df = dict_dataframes[agrupamento_selecionado_ind] 

df_j = df.groupby(['ANO', 'MES_N'])[['VOLUME_FATURADO','VALOR_TOTAL']].sum().reset_index()

df = df_j
 
df['VOLUME_FATURADO'] = df['VOLUME_FATURADO'].astype(int)
 
df.info()

condicao = ( df['ANO'] == ano_selecionado_ind) &  (df['MES_N']== mes_selecionado_ind)


index_selecao_ind = df[condicao].index[0]
if index_selecao_ind >= 36:
    ver = 'Sim'
    index_inicial = index_selecao_ind-36
    df_36m = df.iloc[index_inicial:index_selecao_ind+1,:]
else:
    ver = 'Não'
    df_36m = df
    
df_36m['ANO_MES'] = "1"
for index, row in df_36m.iterrows():
    row['ANO_MES'] = str(row['ANO']) +'-'+ str(row['MES_N'])
    print(row)
    #df_36m['ANO_MES'][i] = str(df_36m['ANO'][i]) #+ '_' + str(row['MES_N'])


df = df_36m   
chart = px.line(df,
             x = df.index,  # Month (column index after pivot)
             y="VOLUME_FATURADO", # Values
             labels={'ANO_MES': 'ANO_MES','VOLUME_FATURADO': 'Volume Faturado (m³)' },
             #color='ANO',  # Coluna para a cor
             #color_discrete_sequence=color_discrete_sequence_,
             )
#chart.update_layout(xaxis=dict(dtick=1))

# Definir o intervalo da legenda como 1 (se desejar)
#min_value = df.index.min()
#max_value = df.index.max()
#tickvals = np.arange(min_value, max_value + 1, 1)
#ticktext = tickvals.astype(str)
#chart.update_layout(tickvals=tickvals, ticktext=ticktext)    

#plot(chart)

#csv = '122024'
csv = '2025_03'
csv = pd.read_csv(os.path.join(pasta_projeto,'Dados','Produtos','atualizacao_dfs',f'{csv}.csv' ))
soma = (csv['VOLUME_FATURADO'].sum() - csv[csv['CIDADE']=='Florianópolis  HU']['VOLUME_FATURADO'])
#print(csv[csv['CIDADE']=='Florianópolis  HU']['VOLUME_FATURADO'])
print(soma)
print(csv['VOLUME_FATURADO'])

