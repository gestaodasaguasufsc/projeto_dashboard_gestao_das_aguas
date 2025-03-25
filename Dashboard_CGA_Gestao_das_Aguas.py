import os
import pandas as pd
from datetime import date
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import folium
import folium.plugins as plugins
import base64 #pip install pybase4
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import mapclassify as mc
import streamlit as st
import altair as alt
import plotly.express as px
from streamlit_folium import folium_static
import plotly.express as px
import plotly.colors as pc


# Passo 0 - funções para carregar csv unico com com todos os dados de água de 2023 ao momento presente

#Main def1
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


dados_agua_df = dados_agua_df.rename(columns={'COD_HIDROMETRO': 'Hidrometro'})

# ordenando e filtrando colunas em dados_agua_df
dados_agua_df = dados_agua_df.iloc[:,[2,21,4,24,33,12,20,10,11,13,14,15,16,17,18,19,31,32,5,6,7,8,9,39,26,29,30,34,36,37]]

# Gerando dados_agua_sf_sHU
dados_agua_df_sHU = dados_agua_df[dados_agua_df['Hidrometro']!='H014'] #remove o Hospital Universitário da análise


#Gerando lista_ucs_local
lista_ucs = dados_agua_df_sHU['Hidrometro'].unique().tolist()
lista_local = dados_agua_df_sHU['Local'].unique().tolist()
lista_uc_local = []
for i,uc in enumerate(lista_ucs):
    nome_uc_local = lista_ucs[i] + " " + lista_local[i]
    lista_uc_local.append(nome_uc_local)

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

lista_agrupamento = list(dict_agrupamento.keys())
    
dict_dataframes = {}


for i, item in enumerate(dict_agrupamento.values()):
   df_concatenado = pd.DataFrame(columns=dados_agua_df_sHU.columns)
   
   if item[0] == 'UFSC - Total':
       dataframe = dados_agua_df_sHU
       df_concatenado = pd.concat([df_concatenado, dataframe], axis=0)
   else:
       
       for subitem in item:
           
           dataframe = dados_agua_df_sHU[dados_agua_df_sHU['Cidade']==subitem]
           df_concatenado = pd.concat([df_concatenado, dataframe], axis=0)
   dict_dataframes[lista_agrupamento[i]] = df_concatenado
        

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

#Passo 4

#retirar o consumo do hospital universitario, valor muito alto em relação aos demais pontos
hidrometros_shp_filtered = hidrometros_shp[hidrometros_shp['Hidrometro'] != 'H014']

#Passo 5 - Correções no arquivo subsetores_agua

subsetores_agua = dict_shapes['SubSetores_Agua']
subsetores_agua.rename(columns={'Hidrômetr': 'Hidrometro'}, inplace=True)
filtered_subsetores_agua = subsetores_agua[subsetores_agua['Hidrometro'] != 'H014']

#passo 6 - carregar shapes fixos

reservatorios = dict_shapes['Reservatorios']
redes_CASAN = dict_shapes['Rede_CASAN']
rede_interna_UFSC = dict_shapes['Rede_Interna_UFSC']
limite_UFSC = dict_shapes['Limite_UFSC']

#passo 7 - carregar hidrometros shape e mesclar com cadastro, para gerar hidrometros_shp_merge (com H014)

hidrometros_shp_merge = hidrometros_shp.merge(cadastro_hidrometros_df, on='Hidrometro', how='left')


#Plot with folium
#https://geopandas.org/en/stable/gallery/plotting_with_folium.html

# Map Folium - Defs


# folium.Choropleth para subsetores_agua - Camada de fundo


def chropleth_subsetores_agua_func(dados_agua_df_ano_mes_selecionado, filtered_subsetores_agua):
  from folium.features import GeoJsonTooltip, GeoJsonPopup

  subsetores_agua_merged = filtered_subsetores_agua.merge(dados_agua_df_ano_mes_selecionado, on='Hidrometro', how='left')

  subsetores_group = folium.FeatureGroup(name="Subsetores", show=True)

  # Create Choropleth layer (without tooltip)
  choropleth = folium.Choropleth(
      geo_data=subsetores_agua_merged,
      name='Sub Setores Água',
      data=subsetores_agua_merged,
      columns=['Hidrometro', 'VOLUME_FATURADO'],
      key_on='feature.properties.Hidrometro',
      fill_color='YlOrRd',
      fill_opacity=0.8,
      line_opacity=0.2,
      legend_name='Volume Faturado (m³)',
      # Remove tooltip from Choropleth
  ).add_to(map)

  # Add GeoJson layer for popups
  folium.GeoJson(
      data=subsetores_agua_merged,
      name='Sub Setores Água - Popups',  # Give it a name
      style_function=lambda x: {'color': 'transparent', 'fillColor': 'transparent'},  # Make it invisible
      tooltip=None,  # Disable tooltip for this layer
      popup=folium.GeoJsonPopup(
          fields=['Hidrometro', 'Local','Setor', 'SubSetor', 'Campus','Cidade','VOLUME_FATURADO'],
          aliases=['Hidrometro', 'Local','Setor', 'SubSetor:', 'Campus','Cidade', 'Volume Faturado (m³):'],
          localize=True,
          style="""
              background-color: #F0EFEF;
              border: 2px solid black;
              border-radius: 3px;
              box-shadow: 3px;
              color: black;
          """
      )
  ).add_to(map)




#### ____________________________________________________________________________________________________________________________
#### Parte xx - Inclusão de shapes fixos (não variam no tempo)

# Camadas fixas - não alteram no tempo



def camadas_fixas_shapes_func(reservatorios, redes_CASAN, rede_interna_UFSC, limite_UFSC, hidrometros_shp_merge):

    # Camada 1. Reservatórios

    reservatorios['Volume_Category'] = pd.qcut(
        reservatorios['Volume2'], 5, labels=False
    )

    # Função para definir o tamanho do ícone com base na categoria de volume
    def get_icon_size(volume_category):
        if volume_category <1:
            return 6  # Tamanho para a categoria menor
        elif volume_category < 5:
            return 8
        elif volume_category < 10:
            return 10
        elif volume_category <20:
            return 12
        elif volume_category <50:
            return 14
        elif volume_category <500:
            return 16
        elif volume_category <1000:
            return 18
        elif volume_category <2000:
            return 20
        else:
            return 25  # Tamanho para a categoria maior

    reservatorios_group = folium.FeatureGroup(name="Reservatórios", show=True)


    for index, row in reservatorios.iterrows():
        popup_content = f"Volume: {row['Name']}"
        volume_category = row['Volume_Category']
        icon_size = get_icon_size(volume_category)
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],  # Usando as coordenadas do reservatório
            popup=folium.Popup(popup_content, max_width=300),
            icon=plugins.BeautifyIcon(
                icon_shape='rectangle-dot',
                border_color='blue',
                border_width=1,
                icon_size=[icon_size, icon_size],
                background_color='lightblue',
                text_color='black',
            )
        ).add_to(reservatorios_group)

    reservatorios_group.add_to(map)

    # Camada 2. Rede de Água CASAN

    for index, row in redes_CASAN.iterrows():
        popup_content = f"Rede CASAN: {row['Diâmetro']}"
        folium.GeoJson(
            row.geometry.__geo_interface__,  # Get GeoJSON representation of geometry
            name="Rede CASAN",  # Nome da camada
            style_function=lambda x: {
                'fillColor': '#000080',  # Azul marinho
                'color': '#000080',  # Azul marinho para a borda
                'weight': 2,  # Espessura da linha
                'fillOpacity': 0.5},
            popup=folium.Popup(popup_content, max_width=300)

        ).add_to(map)

    # Camada 3. Rede de Água interna UFSC


    for index, row in rede_interna_UFSC.iterrows():
        popup_content = f"Rede interna UFSC: {row['Obs']}"
        folium.GeoJson(
            row.geometry.__geo_interface__,  # Get GeoJSON representation of geometry
            name="Rede interna UFSC",  # Nome da camada
            style_function=lambda x: {
              'fillColor': 'purple',  # Azul marinho
              'color': 'purple',  # Azul marinho para a borda
              'weight': 1.2,  # Espessura da linha
              'fillOpacity': 0.5  # Opacidade do preenchimento (opcional)
            },
            popup=folium.Popup(popup_content, max_width=300)
            ).add_to(map)


    # Camada 4. Limite UFSC Campus Trindade


    folium.GeoJson(
        limite_UFSC,
        name="Limite_UFSC",  # Nome da camada
        style_function=lambda x: {
            'fillColor': 'red',
            'color': 'red',
            'weight': 2,  # Espessura da linha
            'fillOpacity': 0.5,
            'dashArray': '10, 5',  # Added dash pattern# Opacidade do preenchimento (opcional)
            }
        ).add_to(map)


    # Camada 5. Hidrometros (classificados de acordo com o campo Categoria = FIXO)

    hidrometros_group = folium.FeatureGroup(name="Hidrometros", show=True)

    n = 10
    icon_size = (n , n)

    for index, row in hidrometros_shp_merge.iterrows():
        if row.geometry is not None and row.geometry.is_valid:
          texto = (
          'Hidrometro: '+row['Hidrometro']+
          '<br>'+'Local: '+row['Local']+
          '<br>'+'Campus: '+row['Campus']+
          '<br>'+'Cidade: '+row['Cidade']+
          '<br>'+'Setor: '+row['Setor de Abastecimento CGA']+
          '<br>'+'SubSetor: '+row['Setor de Abastecimento CGA.1']
          )

          texto = texto if pd.isna(row['Matricula']) else texto + '<br>'+'Matrícula: '+str(int(row['Matricula']))
          pasta_figuras = os.path.join(pasta_projeto, 'Auxiliar', 'Info_Hidrometros')
          figura_nome = row['Hidrometro']+'.jpg'
          figura_url = os.path.join(pasta_figuras, figura_nome)
          if os.path.isfile(figura_url)==True:
            with open(figura_url, "rb") as image_file:
              encoded_string = base64.b64encode(image_file.read()).decode()
          else:
            pass
          figura_src = f"<img src='data:image/jpeg;base64,{encoded_string}' width='400'>" if os.path.isfile(figura_url) else ""
          popup_content = (
              f"{texto}<br>{figura_src}"
              )

          lista_cores = ('blue', 'red', 'green')
          background_color = ('yellow', 'black', 'black')

          if row['Categoria'] == 'Medidor faturado pela UFSC':
              i = 0
          elif row['Categoria'] == 'Medidor não faturado pela UFSC':
              i = 1
          elif row['Categoria'] == 'Medidor Interno':
              i = 2
          else:
              pass

          folium.Marker(
              location=[row.geometry.y, row.geometry.x],
              popup=folium.Popup(popup_content, max_width=300),
              icon=plugins.BeautifyIcon(
                  icon="circle",
                  icon_shape="circle-dot",
                  border_color=lista_cores[i],
                  text_color="#007799",
                  background_color=background_color[i],
                  icon_size=icon_size)
              ).add_to(hidrometros_group)
        else:
          pass

    hidrometros_group.add_to(map)


#### ____________________________________________________________________________________________________________________________
#### Parte xx -
# Classificando hidrômetros de acordo com o volume - alteram no tempo


def classificar_hidrometros_volume_func(hidrometros_shp_filtered, dados_agua_df_ano_mes_selecionado):

    hidrometros_shp_volume = hidrometros_shp_filtered.merge(dados_agua_df_ano_mes_selecionado, on='Hidrometro', how='left')
    hidrometros_shp_volume = hidrometros_shp_volume.dropna(subset=['VOLUME_FATURADO'])

    # Color scheme
    scheme = mc.Quantiles(hidrometros_shp_volume['VOLUME_FATURADO'], k=10)

    # Point sizes
    min_consumption = hidrometros_shp_volume['VOLUME_FATURADO'].min()
    max_consumption = hidrometros_shp_volume['VOLUME_FATURADO'].max()
    second_max_consuption = hidrometros_shp_volume['VOLUME_FATURADO'].nlargest(2).iloc[-1]

    def get_point_size(volume):
      return (volume - min_consumption) / (max_consumption - min_consumption) * 10 + 10

        # Colormap
    cmap = cm.get_cmap('inferno_r')

    # Creating the FeatureGroup with embedded legend
    points_group = folium.FeatureGroup(name="Pontos Hidrômetros - Volume Faturado", show=True)

    # Add CircleMarkers directly to the map
    for index, row in hidrometros_shp_volume.iterrows():
        consumption = row['VOLUME_FATURADO']
        point_size = get_point_size(consumption)

        # Get color from the colormap (normalized consumption value)
        color_rgba = cmap((consumption - min_consumption) / (max_consumption - min_consumption))
        color_hex = "#%02x%02x%02x" % tuple(int(c * 255) for c in color_rgba[:3])

        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=point_size,
            color=color_hex,
            fill=True,
            fill_color=color_hex,
            fill_opacity=0.7,
            popup=f"Volume Faturado: {consumption:.2f} m³ <br> Hidrometro: {row['Hidrometro']}"
        ).add_to(points_group)




    # Adding the custom legend HTML to the FeatureGroup
    legend_html = """
        <div id="consumption-legend" style="position: fixed;
                    bottom: 50px; left: 50px; width: 150px; height: 150px;
                    border:2px solid grey; z-index:9999; font-size:10px;
                    background-color: white;
                    ">
            &nbsp; <b>Volume Faturado (m³)</b><br>
        """
    # Add legend entries for each quantile
    for i in range(scheme.k-1):
        color_rgba = cmap(i / scheme.k)  # Get color for the quantile
        color_hex = "#%02x%02x%02x" % tuple(int(c * 255) for c in color_rgba[:3])
        legend_html += f"""
            &nbsp; <i class="fa fa-circle fa-1x" style="color:{color_hex}"></i>
            &nbsp; {scheme.bins[i]:.0f} - {scheme.bins[i + 1]:.0f}<br>
        """
    legend_html += """
        </div>
    """

    points_group.add_child(folium.Element(legend_html))
    points_group.add_to(map)

def adicionar_camadas_de_fundo_func(map):
    #Map Folium Configuração 2:

    # Adicionar tiles como camadas de seleção


 
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite'
    ).add_to(map)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite'
    ).add_to(map)
    
  
  

    # Adicionar LayerControl para permitir a seleção de camadas
    folium.LayerControl().add_to(map)


    #map.save('map.html')


# gráfico 1
# Gerar lineplot para volume faturado por ano

def barplot_para_mes_ano_selecionado_func(dados_agua_df_ano_mes_selecionado):
    fig1 = px.bar(dados_agua_df_ano_mes_selecionado, x='Hidrometro', y='VOLUME_FATURADO',
                  labels={'Hidrometro': 'Hidrômetro', 'VOLUME_FATURADO': 'Volume Faturado (m³)'})
    fig2 = px.bar(dados_agua_df_ano_mes_selecionado, x='Hidrometro', y='VALOR_TOTAL',
                  labels={'Hidrometro': 'Hidrômetro', 'VALOR_TOTAL': 'Custo Faturado (R$)'})
    
    return fig1 , fig2


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



# gráfico 2
# gerar lineplot para volume faturado por mês
# Passo 3 - Gerar lineplot de toda a série de volume faturado agrupado por mês
#### Reorganizando totais mensais:
#### - Agrupando dados por ano e por mês a partir de dados_agua_df_sHU com dados de volume faturado mensal

def boxplot_func_px(df):
   
    chart = px.box(df,
                 x="MES_N",  # Month (column index after pivot)
                 y="VOLUME_FATURADO", # Values
                 color='ANO',
                 labels={'ANO': 'Ano','VOLUME_FATURADO': 'Volume Faturado (m³)' },
                 boxmode='group',
                 points='all'
                 )
    chart.update_layout(xaxis=dict(dtick=1))    
    
    return chart

def scatter_func_px(df):
   
    chart = px.scatter(df,
                 x="MES_N",  # Month (column index after pivot)
                 y="VOLUME_FATURADO", # Values
                 labels={'ANO': 'Ano','VOLUME_FATURADO': 'Volume Faturado (m³)' },
                 color='ANO',  # Coluna para a cor
                 color_continuous_scale='Viridis' 
                 )
    chart.update_layout(xaxis=dict(dtick=1))   
    
    # Definir o intervalo da legenda como 1
    min_value = int(df['ANO'].min())
    max_value = int(df['ANO'].max())
    tickvals = np.arange(min_value, max_value + 1, 1)  # Cria um array de valores de tick com intervalo de 1
    ticktext = tickvals.astype(str)  # Converte os valores de tick para strings para exibição na legenda
    
    
    chart.update_layout(coloraxis=dict(colorbar=dict(tickvals=tickvals, ticktext=ticktext)))
    
    return chart

def line_func_px(df):
    # Defina as duas cores desejadas
    cor1 = 'rgb(255, 0, 0)'
    cor2 = 'rgb(255, 0, 255)'

    
    num_colors = len(df['ANO'].unique())
    color_discrete_sequence_ = pc.n_colors(cor1, cor2, num_colors, colortype='rgb')
    
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







###_________________________________________________________________________________

#Configurações Streamlit

st.set_page_config(
    page_title="Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


# Map Folium Configurações 1 - Iniciais

map = folium.Map(width = 1200, height=600, location=[-27.6, -48.52], zoom_start=15.5)
                    
    #DADOS A SEREM UTILIZADOS NO STREAMLIT
    # Consumo mensal de um mês e ano a serem selecionados no STREAMLIT SIDEBAR
    # Add a selectbox to the sidebar
    
    
with st.sidebar:
    col1, col2, col3, col4 = st.sidebar.columns(4)
    with col1:     
        link_logoUFSC = os.path.join(pasta_projeto,'Auxiliar', 'Logos','brasao_ufsc.png')
        st.image(link_logoUFSC,width=100)
    with col2:
        link_logoCGA = os.path.join(pasta_projeto,'Auxiliar', 'Logos','cropped-logo-cga-1.jpg')
        st.image(link_logoCGA,width=100)
    with col3:
        link_logoUS = os.path.join(pasta_projeto,'Auxiliar', 'Logos','Logo-UFSC-Sustentável-colorido-fundo-transp.png')
        st.image(link_logoUS,width=100)
    with col4:
        link_logoGA = os.path.join(pasta_projeto,'Auxiliar', 'Logos','Gestao_das_Aguas_Logo.png')
        st.image(link_logoGA,width=100)
            
    st.title("Dashboard Monitoramento do Consumo de Água da UFSC")        
    
    st.sidebar.caption("Escolha o mês e ano para visualizar distribuição do consumo mensal por unidade consumidora no mapa. Por padrão o último mês com dados disponíveis está apresentado.")
        
    ano_selecionado = st.sidebar.selectbox('Selecione o ano', anos , index = index_ano)
    mes_selecionado = st.sidebar.selectbox('Selecione o mes', meses, index = index_mes)         
    uc_selecionado = st.sidebar.selectbox('Selecione a unidade consumidora', lista_uc_local)
    
    
    
    
    # Filter the dataframe based on the selected year
    dados_agua_df_ano_mes_selecionado = dados_agua_df_sHU[(dados_agua_df_sHU['ANO'] == ano_selecionado) & (dados_agua_df_sHU['MES_N'] == mes_selecionado)]
    dados_agua_df_ano_mes_selecionado = dados_agua_df_ano_mes_selecionado.sort_values(by=['VOLUME_FATURADO'], ascending=False).reset_index(drop=True)
    dados_agua_df_ano_mes_selecionado.index = np.arange(1, len(dados_agua_df_ano_mes_selecionado) + 1)
    
         
    chropleth_subsetores_agua_func(dados_agua_df_ano_mes_selecionado, filtered_subsetores_agua)
    #classificar_hidrometros_volume_func(hidrometros_shp_filtered, dados_agua_df_ano_mes_selecionado)
    camadas_fixas_shapes_func(reservatorios, redes_CASAN, rede_interna_UFSC, limite_UFSC, hidrometros_shp_merge)
    adicionar_camadas_de_fundo_func(map)
   
    st.sidebar.caption("Coordenadoria de Gestão Ambiental - CGA/DGG/GR/UFSC https://gestaoambiental.ufsc.br")
    st.sidebar.caption("Projeto desenvolvido em Python 3.10 - mar/2025")
    st.sidebar.caption("contato: gestaodasaguas@contato.ufsc.br")

tab1, tab2, tab3, tab4 = st.tabs(["Mapa", "Volume no mês selecionado por UC", "Volume acumulado anual", "Volumes mensais acumulados por mês e ano"])

with tab1:
    
    st.write("Mapa de hidrômetros, redes e subsetores de Água da UFSC")
    st.caption('Os subsetores correspondem a área estimada que cada hidrômetro abastece.' 
               ' O mapa apresenta os subsetores com o consumo do mês selecionado ao lado. ' 
               ' Também pode ser visualizado as redes da UFSC e da concessionária e os reservatórios. '
               ' Clique nas camadas do mapa, como hidrômetros, redes e área de subsetores para visualizar maiores informações.'
               )
    
    folium_static(map, width=1200, height=600)


with tab2:
    st.write("\n Volume faturado (m³) por unidade consumidora em ordem descrescente no mês e ano selecionados:")
    fig1 = barplot_para_mes_ano_selecionado_func(dados_agua_df_ano_mes_selecionado)[0]
    st.write(fig1)
    st.write("\n Custo faturado (R$) por unidade consumidora em ordem descrescente no mês e ano selecionados:")
    fig2 = barplot_para_mes_ano_selecionado_func(dados_agua_df_ano_mes_selecionado)[1]
    st.write(fig2)
    
    st.write("\n Relação de unidades consumidoras em ordem descrescente de volume faturado (m³) no mês e ano selecionados:")
    dataframe = dados_agua_df_ano_mes_selecionado
    dataframe = dataframe.rename(
        columns={
        'VOLUME_FATURADO': 'Volume Faturado m³',
        'VALOR_TOTAL': 'Valor Total R$',
                }
                                 )
    
    st.dataframe(dataframe, width=1200, height=500) # Or any other way you want to display the data

 
with tab3:

    st.write('Acumulados anuais: Volume e Custo')
    
       
    agrupamento_selecionado = st.selectbox('Selecione o  agrupamento dos dados:', 
                                           lista_agrupamento, 
                                           index = 0, 
                                           key='selectbox_agrupamento1'
                                           )
    
    df_selecionado = dict_dataframes[agrupamento_selecionado] 
    volume_faturado_por_ano = df_selecionado.groupby(['ANO'])['VOLUME_FATURADO'].sum().reset_index()
    custo_faturado_por_ano = df_selecionado.groupby(['ANO'])['VALOR_TOTAL'].sum().reset_index()
    
    df_selecionado_dataframe = pd.concat([volume_faturado_por_ano, custo_faturado_por_ano['VALOR_TOTAL']],axis=1)
    df_selecionado_dataframe['Agrupamento Selecionado'] = agrupamento_selecionado
    df_selecionado_dataframe['VALOR_TOTAL'] = df_selecionado_dataframe['VALOR_TOTAL'].apply(lambda x: f"{x:.2f}")
    df_selecionado_dataframe['VOLUME_FATURADO'] = df_selecionado_dataframe['VOLUME_FATURADO'].apply(lambda x: f"{x:.0f}")
    df_selecionado_dataframe = df_selecionado_dataframe.sort_values(by='ANO', ascending=False)
    df_selecionado_dataframe = df_selecionado_dataframe.rename(columns=
                                                              {'ANO':'Ano',
                                                                  'VALOR_TOTAL': 'Custo Total (R$)',
                                                               'VOLUME_FATURADO': 'Volume Faturado (m³)'
                                                               })
    df_selecionado_dataframe = df_selecionado_dataframe.iloc[:,[0,3,1,2]]
    
    
  
    
    #Volume Faturado acumulado por ano
    st.caption('Volume acumulado por ano')
    
    fig3 = agrupado_por_ano_func(volume_faturado_por_ano, custo_faturado_por_ano)[0]
    st.write(fig3)
    
    st.caption('Custo acumulado por ano')
    fig4 = agrupado_por_ano_func(volume_faturado_por_ano, custo_faturado_por_ano)[1]
    st.write(fig4)
    

    st.write("\n Volume e custo acumulado por ano para o agrupamento selecionado:")
                    
    st.dataframe(df_selecionado_dataframe, width=1200, height=600) # Or any other way you want to display the data

with tab4:

    st.write('Volumes e custos mensais acumulados por ano para o agrupamento selecionado:')
    
    
    agrupamento_selecionado2 = st.selectbox('Selecione o  agrupamento dos dados:', 
                                           lista_agrupamento, 
                                           index = 0, 
                                           key='selectbox_agrupamento2'
                                           )
    df_selecionado2 = dict_dataframes[agrupamento_selecionado2] 
    
    df_selecionado2 = df_selecionado2.groupby(['ANO', 'MES_N'])['VOLUME_FATURADO'].sum().reset_index()
    #volume_faturado_pivot = volume_faturado_por_mes_ano.pivot(index='ANO', columns='MES_N', values='VOLUME_FATURADO')


 
    anos_selecionados_fig1 = st.multiselect("Selecione os anos desejados no gráfico:",
        options=df_selecionado2['ANO'].unique(),  # Opções do multi-check
        default=df_selecionado2['ANO'].unique(),
        key='multiselect_anos_fig1'
        )

    # Filtrar o DataFrame com base nos anos selecionados
    filtered_df_fig1 = df_selecionado2[df_selecionado2['ANO'].isin(anos_selecionados_fig1)]
    fig1 = boxplot_func_px(filtered_df_fig1)
    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)


    anos_selecionados_fig2 = st.multiselect(    "Selecione os anos desejados no gráfico:",
        options=df_selecionado2['ANO'].unique(),  # Opções do multi-check
        default=df_selecionado2['ANO'].unique(),  # Valores padrão selecionados
        key='multiselect_anos_fig2'
        )

    # Filtrar o DataFrame com base nos anos selecionados
    filtered_df_fig2 = df_selecionado2[df_selecionado2['ANO'].isin(anos_selecionados_fig2)]
    fig2 = scatter_func_px(filtered_df_fig2)
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)


    anos_selecionados_fig3 = st.multiselect(    "Selecione os anos desejados no gráfico:",
        options=df_selecionado2['ANO'].unique(),  # Opções do multi-check
        default=df_selecionado2['ANO'].unique(),   # Valores padrão selecionados
        key='multiselect_anos_fig3'
        )

    # Filtrar o DataFrame com base nos anos selecionados
    filtered_df_fig3 = df_selecionado2[df_selecionado2['ANO'].isin(anos_selecionados_fig3)]

    fig3 = line_func_px(filtered_df_fig3)
    st.plotly_chart(fig3, theme="streamlit", use_container_width=True)
    
    
   

   
       

