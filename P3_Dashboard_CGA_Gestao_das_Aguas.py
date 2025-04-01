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






############## Parte 2 - código geração de mapas e dados tabulares de consumo de água de 2013 ao momento presente



def tratamento_de_dados_func(pasta_projeto):
    
    
    link = os.path.join(pasta_projeto, 'Dados', 'Origem', 'Planilha_de_referencia_cadastro_hidrometros.csv')
    df_cad = pd.read_csv(link, encoding='latin-1', sep = ';')
    df_cad = df_cad.drop(columns=['Consumo médio dos últimos 6 meses (m3) - ref 9_2024','Atualizacao_Cadastro'], axis=1)
    df_cad = df_cad.rename(columns={'Observacao': 'Faturamento'})
    
    df = pd.read_csv(os.path.join(pasta_projeto,'Dados', 'Produtos' , 'dados_agua_df_2.csv'))
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


# Passo 0 - funções para carregar csv unico com com todos os dados de água de 2023 ao momento presente

pasta_projeto = os.path.dirname(os.path.abspath('__file__'))

# Passo 1 - gerar df único (dados_agua_df_sHU) com todos os dados de água e variáveis iniciais

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
menor_ano =                 trat_func[10]
menor_mes =                 trat_func[11]

       

# Passo 2 - carregar dicionário de shapes

#Carregando dados shapefile

#GDB Esri
#pasta_projeto = ""

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

#Passo 4 - retirar o consumo do hospital universitario, valor muito alto em relação aos demais pontos

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
#### Parte xx - Inclusão de outros shapes 


# demais camadas



def camadas_shapes_func(reservatorios, redes_CASAN, rede_interna_UFSC, limite_UFSC, hidrometros_shp_merge, uc_selecionada):

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
              
                           
              if row['Hidrometro'] == uc_selecionada:
                # Modificar cor, tamanho e adicionar ao grupo para o ponto específico
                    folium.Marker(
                        location=[row.geometry.y, row.geometry.x],
                        popup=folium.Popup(popup_content, max_width=300),
                        icon=plugins.BeautifyIcon(
                            icon="circle",
                            icon_shape="circle-dot",
                            border_color='red',  # Mudar cor para vermelho
                            text_color="#007799",
                            background_color='red',  # Mudar cor de fundo para vermelho
                            icon_size=(20, 20)  # Mudar tamanho para 15x15 pixels
                                                )
                                ).add_to(hidrometros_group)
              else:
                    # Criar marcador com as configurações originais para outros pontos
                    folium.Marker(
                        location=[row.geometry.y, row.geometry.x],
                        popup=folium.Popup(popup_content, max_width=300),
                        icon=plugins.BeautifyIcon(
                            icon="circle",
                            icon_shape="circle-dot",
                            border_color=lista_cores[i],
                            text_color="#007799",
                            background_color=background_color[i],
                            icon_size=icon_size
                        )
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

###### Gráficos

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
                 #color='ANO',
                 labels={'ANO': 'Ano','VOLUME_FATURADO': 'Volume Faturado (m³)' },
                 boxmode='group',
                 points='all'
                 )
    chart.update_layout(xaxis=dict(dtick=1))    
    
    return chart

def scatter_func_px_vol(df):
   
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

def scatter_func_px_cus(df):
   
    chart = px.scatter(df,
                 x="MES_N",  # Month (column index after pivot)
                 y="VALOR_TOTAL", # Values
                 labels={'ANO': 'Ano','VALOR_TOTAL': 'Valor Total (R$)' },
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

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")  # Remove "#" se presente
    r = int(hex_color[0:2], 16)  # Converte os primeiros 2 caracteres para decimal (vermelho)
    g = int(hex_color[2:4], 16)  # Converte os próximos 2 caracteres para decimal (verde)
    b = int(hex_color[4:6], 16)  # Converte os últimos 2 caracteres para decimal (azul)
    return (r, g, b)  # Retorna a tupla RGB


def line_func_px(df):
    
      
    # Defina as duas cores desejadas
    
    container1 = st.container()
    with container1:
        col1, col2, col3 = st.columns(3)
        with col1:
            cor1 =  st.color_picker("Escolha a cor 1", '#3100FB')
        with col2:    
            cor2 =  st.color_picker("Escolha a cor 2", '#E411E4')
        with col3:    
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



#### Defs streamlit

#Localiza hidrômetro, entrada com cadastro_hidrometros_df, valor selecionado)  
def localiza_lat_long_hidrometro_func (df_i, valor, shp):
    df = df_i.iloc[:,[1,11]]
    df['nome_uc_local'] = df['Hidrometro'] +" " + df['Local']
    selecao = df.loc[df['nome_uc_local']==valor, 'Hidrometro'].iloc[0]
    try:
        lat = shp.loc[shp['Hidrometro']==selecao,'Latitude'].iloc[0]
        long = shp.loc[shp['Hidrometro']==selecao,'Longitude'].iloc[0]
    except:
        lat = ""
        long = ""
    lista_keys = ['hid_sel', 'lat', 'long']
    saida = [selecao, lat, long]
    dict_saida = {}
    for i, item in enumerate(lista_keys):
        dict_saida[item] = saida[i]
    return dict_saida

def gerador_lista_uc_local_por_campi_func (df, selecao_cidade):
    df = df[df['Cidade']!= 'Florianópolis  HU']
    df = df.iloc[:,[1,11,9]]
    df['nome_uc_local'] = df['Hidrometro'] + " " + df['Local']
    df_filtrada = df[df['Cidade'] == selecao_cidade]
    lista = df_filtrada['nome_uc_local'].tolist()
    lista.sort()
    lista.append("UFSC - visão geral")
    index_ = lista.index("UFSC - visão geral")
    return lista, index_

def lista_cidades_index_func(df):
        df = df[df['Cidade']!= 'Florianópolis  HU']
        lista = df['Cidade'].unique().tolist()
        index_ = lista.index('Florianópolis - Trindade')
        return lista, index_
   
    
def funcao_graf_uc_ano_func(df, selecao_uc_mapa):
    df = df[df['Hidrometro']==selecao_uc_mapa]
    vol_uc = df.groupby(['ANO'])['VOLUME_FATURADO'].sum().reset_index()
    cus_uc = df.groupby(['ANO'])['VALOR_TOTAL'].sum().reset_index()
    graf_uc = agrupado_por_ano_func(vol_uc, cus_uc)
    return graf_uc[0], graf_uc[1]

def funcao_graf_uc_mes_func(df, selecao_uc_mapa):
    df = df[df['Hidrometro']==selecao_uc_mapa]
    return scatter_func_px_vol(df), scatter_func_px_cus(df)


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




def dict_dataframes_func(dct, df):
    
    list_agr = list(dct.keys())
    dict_dataframes = {}
   
    for i, item in enumerate(dct.values()):
        df_zero = pd.DataFrame(columns=df.columns)
       
        if item[0] == 'UFSC - Total':
            df_concatenado = pd.concat([df_zero, df], axis=0)
        
        else:
            df_concatenado = df_zero
            for subitem in item:
               df_subitem = df[df['Cidade']==subitem]
               df_concatenado = pd.concat([df_concatenado, df_subitem], axis=0)
        dict_dataframes[list_agr[i]] = df_concatenado
    
    return list_agr, dict_dataframes



def trat_acumulado_por_ano_func (dct, agr_sel):

    df_sel = dct[agr_sel] 
    vol_ano = df_sel.groupby(['ANO'])['VOLUME_FATURADO'].sum().reset_index()
    cus_ano = df_sel.groupby(['ANO'])['VALOR_TOTAL'].sum().reset_index()
    
    df = pd.concat([vol_ano, cus_ano['VALOR_TOTAL']],axis=1)
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

funcao_dict_dfs = dict_dataframes_func(dict_agrupamento, dados_agua_df_sHU)
lista_agrupamento = funcao_dict_dfs[0]
dict_dataframes = funcao_dict_dfs[1]

def indicadores_vol_cus_func(
        agrupamento_selecionado_ind,
        ano_selecionado_ind,
        mes_selecionado_ind,
        dict_dataframes):


    df_selecionado_ind = dict_dataframes[agrupamento_selecionado_ind] 


    df_selecionado_ind = df_selecionado_ind.groupby(['ANO', 'MES_N'])[['VOLUME_FATURADO','VALOR_TOTAL']].sum().reset_index()
    
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
            variacao_abs = float("{:.2f}".format(item - media))
            if item is None == True:
                variacao_per = "Dados insuficientes"
            elif item == 0:
                variacao_per = "Divisão por zero" 
            else: 
                variacao_per = float("{:.2f}".format(variacao_abs/item))
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
            media = float("{:.2f}".format(media))
            variacao_abs = float("{:.2f}".format(item - media))
            if item is None == True:
                variacao_per = "Dados insuficientes"
            elif item == 0:
                variacao_per = "Divisão por zero" 
            else: 
                variacao_per = float("{:.2f}".format(variacao_abs/item))
            
            df_selecionado_ind['CUS_MED_U6M'][i] = media
            df_selecionado_ind['CUS_VAR_ABS'][i] = variacao_abs
            df_selecionado_ind['CUS_VAR_PER'][i] = variacao_per


    return df_selecionado_ind

###_________________________________________________________________________________

#Configurações Streamlit

st.set_page_config(
    page_title="Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

#alt.themes.enable("dark")


# Map Folium Configurações 1 - Iniciais

map = folium.Map(width = 950, height=750, location=[-27.6, -48.52], zoom_start=15.5)
                    
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
    
     
    st.sidebar.caption("Coordenadoria de Gestão Ambiental - CGA/DGG/GR/UFSC https://gestaoambiental.ufsc.br")
    st.sidebar.caption("Projeto desenvolvido em Python 3.10 - mar/2025")
    st.sidebar.caption("contato: gestaodasaguas@contato.ufsc.br")

tab1, tab2, tab3, tab4, tab5 = st.tabs(['Indicadores', "Mapa Cadastral e informações por UC", 
                                  "Dados gerais de UCs por ano e mês selecionado", "Dados agrupados anuais", "Dados agrupados mensais"])


#INDICADORES--------------------------------------------

with tab1: 
    
     
    col1, col2, col3, col4 = st.columns(4)
    with col1:     
        ano_selecionado_ind = st.selectbox('Selecione o ano', anos , index = index_ano, key='selectbox_indicadores_ano')
    with col2:
        mes_selecionado_ind = st.selectbox('Selecione o mes', meses, index = index_mes, key='selectbox_indicadores_mes')
    with col3:
            st.caption(f'Último ano/mês com dados disponível: {maior_ano}/{maior_mes}')
            st.caption(f'Primeiro ano/mês com dados disponível: {menor_ano}/{menor_mes}')
    
    col1, col2  = st.columns(2)
    
    with col1:
        agrupamento_selecionado_ind = st.selectbox('Selecione o  agrupamento dos dados:', 
                                           lista_agrupamento, 
                                           index = 0, 
                                           key='selectbox_agrupamento_ind'
                                           )
        sem_dados = False
        
        try:
            df_selecionado_ind = indicadores_vol_cus_func(
                    agrupamento_selecionado_ind,
                    ano_selecionado_ind,
                    mes_selecionado_ind,
                    dict_dataframes)
          
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
            
        except:
            st.caption('Dados inexistentes para o local/ano/mês selecionado')
            sem_dados = True
        
        
            
    
                     
    
    
    
         
    if sem_dados == True:
        pass
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        st.markdown(
                    """
                <style>
                [data-testid="stMetricValue"] {
                    font-size: 25px;
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )
        
        with col1:      
                textov0 = (f'{volume_mes:,.0f} m³').replace(",", "_").replace(".", ",").replace("_", ".")
                textov1 = (f'{volume_variacao_abs:,.0f} m³').replace(",", "_").replace(".", ",").replace("_", ".")
                textov2 = (f'{volume_variacao_per*100:,.0f} %').replace(",", "_").replace(".", ",").replace("_", ".")
                
                #if volume_variacao_abs>0: 
                  #  delta_color_t1 = 'inverse'
                #else:
                 #   delta_color_t1 = 'normal'
                
                
                st.metric("Volume no mês/ano selecionados", 
                          textov0, 
                          border=True)
        
        with col2:
                textoc0 = (f'R$ {custo_mes:,.2f}').replace(",", "_").replace(".", ",").replace("_", ".")
                textoc1 = (f'{custo_variacao_abs:,.2f}').replace(",", "_").replace(".", ",").replace("_", ".")
                textoc2 = (f'{custo_variacao_per*100:,.0f} %').replace(",", "_").replace(".", ",").replace("_", ".")
                st.metric("Custo no mês/ano selecionados",
                          textoc0,  
                          border=True, delta_color="inverse")
      
        with col3:      
                texto = (f'{volume_media:,.0f} m³').replace(",", "_").replace(".", ",").replace("_", ".")
                st.metric("Volume médio dos últimos 6 meses", texto , border=True)
        
        with col4:
                texto = (f'R$ {custo_media:,.2f}').replace(",", "_").replace(".", ",").replace("_", ".")
                st.metric("Custo médio dos últimos 6 meses", texto, border=True)
    
        st.caption('Variações de volume e custo em relação à média dos últimos 6 meses')
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
                st.metric("Volume variação absoluta", 
                          "", textov1, 
                          border=True, delta_color="inverse")
                st.metric("Volume variação percentual", 
                          "", textov2, 
                          border=True, delta_color="inverse")
                
        with col2:
                st.metric("Custo variação absoluta", 
                          "", textoc1, 
                          border=True, delta_color="inverse")
                st.metric("Custo variação percentual", 
                          "", textoc2, 
                          border=True, delta_color="inverse")
        
        
        
        
    #trat_acum_func = trat_acumulado_por_ano_func (dict_dataframes, agrupamento_selecionado)
        
    #volume_faturado_por_ano = trat_acum_func[0]
    #custo_faturado_por_ano = trat_acum_func[1]
    #df_selecionado_dataframe = trat_acum_func[2]
    
#MAPA CADASTRAL E INFORMAÇÕES   ----------------------------------

with tab2:
            
    col1, col2, col3, col4 = st.columns(4)
    with col1:     
        ano_selecionado_mapa = st.selectbox('Selecione o ano', anos , index = index_ano, key='selectbox_mapa_ano')
    with col2:
        mes_selecionado_mapa = st.selectbox('Selecione o mes', meses, index = index_mes, key='selectbox_mapa_mes')
    
    with col3:
        st.caption(f'Último ano/mês com dados disponível: {maior_ano}/{maior_mes}')
        st.caption(f'Primeiro ano/mês com dados disponível: {menor_ano}/{menor_mes}')
        
            
    col1, col2 = st.columns(2)
    
    with col1:
        
        funcao = lista_cidades_index_func(cadastro_hidrometros_df)
        lista_cidades = funcao[0]
        index_cidades = funcao[1]
        selecao_cidade = st.selectbox('Selecione o campi/unidade', lista_cidades, index = index_cidades , key='selectbox_mapa_cidades')        
        
    with col2: 
        
        funcao = gerador_lista_uc_local_por_campi_func (cadastro_hidrometros_df , selecao_cidade)
        lista_uc_local = funcao[0]
        index_visao_geral = funcao[1]
    
        selecao_uc_mapa = st.selectbox('Selecione a unidade consumidora', 
                                       lista_uc_local, 
                                       index = index_visao_geral , 
                                       key='selectbox_mapa_uc'
                                       )        
        
        
        if selecao_uc_mapa == lista_uc_local[index_visao_geral]:
            map = folium.Map(width = 950, height=750, location=[-27.6, -48.52], zoom_start=15.5)
            uc_selecionada = selecao_uc_mapa
        else: 
            
            try:
                dict_saida = localiza_lat_long_hidrometro_func(cadastro_hidrometros_df, selecao_uc_mapa, hidrometros_shp)
                lat = dict_saida['lat']
                long = dict_saida['long']
                uc_selecionada = dict_saida['hid_sel']
                map = folium.Map(width = 950, height=750, location=[lat, long], zoom_start=18)
                verificador_mapa  = True
            except:
                verificador_mapa  = False
                pass
    
    tab2_1, tab2_2, tab2_3 = st.tabs(["Mapa", 
                          'Dados agrupados anuais da UC selecionada',
                          'Dados mensais da UC selecionada',
                                     ])
    
    with tab2_1:
        st.caption("Mapa de hidrômetros, redes e subsetores de Água da UFSC")
        st.caption('Os subsetores correspondem a área estimada que cada hidrômetro abastece.' 
                   'O mapa apresenta os subsetores com o consumo do mês selecionado ao lado.'
                   ' Também pode ser visualizado as redes da UFSC e da concessionária e os reservatórios. '
                   ' Clique nas camadas do mapa, como hidrômetros, redes e área de subsetores para visualizar maiores informações.'
                    ' Clique nos pontos de localização dos hidrômetros para visualizar imagem do local')
        
        try:
            dados_agua_df_ano_mes_selecionado_mapa = dados_agua_df_sHU[(dados_agua_df_sHU['ANO'] == ano_selecionado_mapa) & (dados_agua_df_sHU['MES_N'] == mes_selecionado_mapa)]
            dados_agua_df_ano_mes_selecionado_mapa = dados_agua_df_ano_mes_selecionado_mapa.sort_values(by=['VOLUME_FATURADO'], ascending=False).reset_index(drop=True)
            dados_agua_df_ano_mes_selecionado_mapa.index = np.arange(1, len(dados_agua_df_ano_mes_selecionado_mapa) + 1)
                     
            chropleth_subsetores_agua_func(dados_agua_df_ano_mes_selecionado_mapa, filtered_subsetores_agua)
            #NÃO UTILIZADO - classificar_hidrometros_volume_func(hidrometros_shp_filtered, dados_agua_df_ano_mes_selecionado)
                   
            camadas_shapes_func(reservatorios, redes_CASAN, rede_interna_UFSC, limite_UFSC, hidrometros_shp_merge, uc_selecionada)
                            
            adicionar_camadas_de_fundo_func(map)
                
            folium_static(map, width=1000, height=800)
            verificador_dados = True
        except:
            verificador_dados = False
            st.caption('UC sem dados georreferenciados')
            
    
    
        
        
    with tab2_2:
        tab2_2_1, tab2_2_2 = st.tabs(['Volume',
                              'Custo'
                              ])  
        funcao_graf_uc_ano = funcao_graf_uc_ano_func(dados_agua_df_sHU, uc_selecionada)
        
        with tab2_2_1:
            if selecao_uc_mapa == lista_uc_local[index_visao_geral]:
                st.caption('Selecione uma unidade consumidora para mostrar gráfico.')   
            else:
                st.caption(f'Volume da UC {selecao_uc_mapa} agrupado por ano.')   
                st.write(funcao_graf_uc_ano[0])
                                        
        with tab2_2_2:
            if selecao_uc_mapa == lista_uc_local[index_visao_geral]:
                st.caption('Selecione uma unidade consumidora para mostrar gráfico.')
            else:        
                st.caption(f'Custo da UC {selecao_uc_mapa} agrupado por ano.')   
                st.write(funcao_graf_uc_ano[1])
                
    if verificador_dados == False:
        st.caption('UC sem dados disponíveis no mês e ano')
        pass
    else:
        
        with tab2_3:
            tab2_3_1, tab2_3_2, tab2_3_3 = st.tabs(['Volume',
                                  'Custo', 'Fatura no mês e ano selecionados'
                                  ])  
            
                   
            with tab2_3_1:
                if selecao_uc_mapa == lista_uc_local[index_visao_geral]:
                    st.caption('Selecione uma unidade consumidora para mostrar gráfico.')   
                else:
                    st.caption(f'Volume da UC {selecao_uc_mapa} distribuído por mês.')   
                    funcao_graf_uc_mes = funcao_graf_uc_mes_func(dados_agua_df_sHU, uc_selecionada)
                    st.write(funcao_graf_uc_mes[0])
                                            
            with tab2_3_2:
                if selecao_uc_mapa == lista_uc_local[index_visao_geral]:
                    st.caption('Selecione uma unidade consumidora para mostrar gráfico.')
                else:        
                    st.caption(f'Custo da UC {selecao_uc_mapa} distribuído por mês.')   
                    funcao_graf_uc_mes = funcao_graf_uc_mes_func(dados_agua_df_sHU, uc_selecionada)
                    st.write(funcao_graf_uc_mes[1])
    
            with tab2_3_3:
                st.caption(f'Fatura da UC {selecao_uc_mapa} no mês e ano selecionado.')   
                st.caption('Indisponível no momento')
            
with tab3:
    
    st.caption("Escolha o mês e ano para visualizar distribuição do consumo mensal. Por padrão o último mês com dados disponíveis está filtrado.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:     
        ano_selecionado_dados_mensais = st.selectbox('Selecione o ano', anos , index = index_ano, key='selectbox_dados_mensais_ano')
    with col2:
        mes_selecionado_dados_mensais = st.selectbox('Selecione o mes', meses, index = index_mes, key='selectbox_dados_mensais_mes')         
    
    tab3_1, tab3_2, tab3_3 = st.tabs(['Volume',
                          'Custo', 'Tabela'
                          ])    
    dados_agua_df_ano_mes_selecionado_dados_mensais = dados_agua_df_sHU[(dados_agua_df_sHU['ANO'] == ano_selecionado_dados_mensais) & (dados_agua_df_sHU['MES_N'] == mes_selecionado_dados_mensais)]
    dados_agua_df_ano_mes_selecionado_dados_mensais = dados_agua_df_ano_mes_selecionado_dados_mensais.sort_values(by=['VOLUME_FATURADO'], ascending=False).reset_index(drop=True)
    dados_agua_df_ano_mes_selecionado_dados_mensais.index = np.arange(1, len(dados_agua_df_ano_mes_selecionado_dados_mensais) + 1)
         
        # Filter the dataframe based on the selected year
    
    
    with tab3_1:
        st.caption("\n Volume faturado (m³) por unidade consumidora em ordem descrescente no mês e ano selecionados:")
        fig1 = barplot_para_mes_ano_selecionado_func(dados_agua_df_ano_mes_selecionado_dados_mensais)[0]
        st.write(fig1)
    with tab3_2:
        st.caption("\n Custo faturado (R$) por unidade consumidora em ordem descrescente no mês e ano selecionados:")
        fig2 = barplot_para_mes_ano_selecionado_func(dados_agua_df_ano_mes_selecionado_dados_mensais)[1]
        st.write(fig2)
    with tab3_3:
        
        st.caption("\n Relação de unidades consumidoras em ordem descrescente de volume faturado (m³) no mês e ano selecionados:")
        dataframe = dados_agua_df_ano_mes_selecionado_dados_mensais
        dataframe = dataframe.rename(
            columns={
            'VOLUME_FATURADO': 'Volume Faturado m³',
            'VALOR_TOTAL': 'Valor Total R$',
                    }
                                     )
        st.caption('Estatística:')
        st.dataframe(dataframe.describe(), width=1200, height=400)
        st.caption('Dados:')
        st.dataframe(dataframe, width=1200, height=500) # Or any other way you want to display the data

 
with tab4:

    st.caption('Acumulados anuais: Volume e Custo')
    
    
       
    agrupamento_selecionado = st.selectbox('Selecione o  agrupamento dos dados:', 
                                           lista_agrupamento, 
                                           index = 0, 
                                           key='selectbox_agrupamento1'
                                           )
     
    trat_acum_func = trat_acumulado_por_ano_func (dict_dataframes, agrupamento_selecionado)
        
    volume_faturado_por_ano = trat_acum_func[0]
    custo_faturado_por_ano = trat_acum_func[1]
    df_selecionado_dataframe = trat_acum_func[2]
        
        
    tab4_1, tab4_2, tab4_3 = st.tabs(['Volume',
                          'Custo', 'Tabela'
                          ])    
    with tab4_1:
    #Volume Faturado acumulado por ano
        st.caption('Volume acumulado por ano')
        
        fig3 = agrupado_por_ano_func(volume_faturado_por_ano, custo_faturado_por_ano)[0]
        st.write(fig3)
    
    
    with tab4_2:
        
        st.caption('Custo acumulado por ano')
        fig4 = agrupado_por_ano_func(volume_faturado_por_ano, custo_faturado_por_ano)[1]
        st.write(fig4)
    
    
    with tab4_3:
        st.caption("\n Volume e custo acumulado por ano para o agrupamento selecionado:")
                        
        st.caption('Estatística:')
        st.dataframe(df_selecionado_dataframe.describe(), width=1200, height=320)
        st.caption('Dados:')
        st.dataframe(df_selecionado_dataframe, width=1200, height=600) # Or any other way you want to display the data

with tab5:

    st.caption('Gráficos de volumes acumulados por ano para o agrupamento selecionado:')
    
    agrupamento_selecionado2 = st.selectbox('Selecione o  agrupamento dos dados:', 
                                           lista_agrupamento, 
                                           index = 0, 
                                           key='selectbox_agrupamento2'
                                           )
    
    tab5_1, tab5_2, tab5_3 = st.tabs(['ScatterPlot','BoxPlot','LinePlot'])
                           
    with tab5_1:
        
       
        
       
        df_selecionado2 = dict_dataframes[agrupamento_selecionado2] 
        
        df_selecionado2 = df_selecionado2.groupby(['ANO', 'MES_N'])[['VOLUME_FATURADO','VALOR_TOTAL']].sum().reset_index()
        #volume_faturado_pivot = volume_faturado_por_mes_ano.pivot(index='ANO', columns='MES_N', values='VOLUME_FATURADO')
    
        anos_selecionados_fig2 = st.multiselect(    "Selecione os anos desejados no gráfico:",
            options=df_selecionado2['ANO'].unique(),  # Opções do multi-check
            default=df_selecionado2['ANO'].unique(),  # Valores padrão selecionados
            key='multiselect_anos_fig2'
            )
        
            # Filtrar o DataFrame com base nos anos selecionados
        filtered_df_fig2 = df_selecionado2[df_selecionado2['ANO'].isin(anos_selecionados_fig2)]
        
        fig2 = scatter_func_px_vol(filtered_df_fig2)
        st.plotly_chart(fig2, theme="streamlit", use_container_width=True)
    
        filtered_df_fig2 = filtered_df_fig2.rename(columns=
                                                   {'ANO':'Ano',
                                                   'VALOR_TOTAL': 'Custo Total (R$)',
                                                   'VOLUME_FATURADO': 'Volume Faturado (m³)'
                                                   }                                              )
        st.caption('Estatística:')
        st.dataframe(filtered_df_fig2.describe(), width=600, height=320)
        st.caption('Dados:')
        st.dataframe(filtered_df_fig2.sort_values(by='Ano',ascending=False), width=600, height=400)  
     
            
    
    with tab5_2:
    
        anos_selecionados_fig1 = st.multiselect("Selecione os anos desejados no gráfico:",
            options=df_selecionado2['ANO'].unique(),  # Opções do multi-check
            default=df_selecionado2['ANO'].unique(),
            key='multiselect_anos_fig1'
            )
    
        # Filtrar o DataFrame com base nos anos selecionados
        filtered_df_fig1 = df_selecionado2[df_selecionado2['ANO'].isin(anos_selecionados_fig1)]
        fig1 = boxplot_func_px(filtered_df_fig1)
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
        
        filtered_df_fig1 = filtered_df_fig1.rename(columns=
                                                  {'ANO':'Ano',
                                                  'VALOR_TOTAL': 'Custo Total (R$)',
                                                  'VOLUME_FATURADO': 'Volume Faturado (m³)'
                                                  }                                              )
        st.caption('Estatística:')
        st.dataframe(filtered_df_fig1.describe(), width=600, height=320)
        st.caption('Dados:')
        st.dataframe(filtered_df_fig1.sort_values(by='Ano',ascending=False), width=600, height=400)
        

    with tab5_3:
        
        anos_selecionados_fig3 = st.multiselect(    "Selecione os anos desejados no gráfico:",
            options=df_selecionado2['ANO'].unique(),  # Opções do multi-check
            default=df_selecionado2['ANO'].unique(),   # Valores padrão selecionados
            key='multiselect_anos_fig3'
            )
    
        # Filtrar o DataFrame com base nos anos selecionados
        filtered_df_fig3 = df_selecionado2[df_selecionado2['ANO'].isin(anos_selecionados_fig3)]
    
        fig3 = line_func_px(filtered_df_fig3)
        st.plotly_chart(fig3, theme="streamlit", use_container_width=True)
        
        filtered_df_fig3 = filtered_df_fig3.rename(columns=
                                                   {'ANO':'Ano',
                                                   'VALOR_TOTAL': 'Custo Total (R$)',
                                                   'VOLUME_FATURADO': 'Volume Faturado (m³)'
                                                   }                                              )
        st.caption('Estatística:')
        st.dataframe(filtered_df_fig3.describe(), width=600, height=320)
        st.caption('Dados:')
        
        st.dataframe(filtered_df_fig3.sort_values(by='Ano',ascending=False), width=600, height=400)           

   
       

