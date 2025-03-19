# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 15:14:22 2025

@author: Usuario
"""

import os
import pandas as pd
#from datetime import date
#import numpy as np
#import geopandas as gpd
#import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker

#import folium
#import folium.plugins as plugins
#import base64
#import matplotlib.pyplot as plt
#import matplotlib.cm as cm
#import matplotlib.colors as colors
#import matplotlib.ticker as ticker
#import mapclassify as mc
#import streamlit as st
#import altair as alt
#import plotly.express as px
#from streamlit_folium import folium_static
#import plotly.express as px

pasta_projeto = os.path.dirname(os.path.abspath('__file__'))
print(pasta_projeto)
caminho_dados_agua_csv = os.path.join(pasta_projeto, 'Dados', 'Produtos', 'dados_agua_df.csv')
dados_agua_df = pd.read_csv(caminho_dados_agua_csv)
dados_agua_df['ANO'] = dados_agua_df['ANO'].astype('int')
dados_agua_df = dados_agua_df.rename(columns={'COD_HIDROMETRO': 'HIDROMETRO'})
dados_agua_df.info()

anos = dados_agua_df['ANO'].unique()
meses = dados_agua_df['MES_N'].unique() 
ultimo_dtime = dados_agua_df['Dtime'].


dados_agua_df = dados_agua_df.rename(columns={'HIDROMETRO': 'Hidrometro'})

#remove o Hospital Universitário da análise
dados_agua_df_sHU = dados_agua_df[dados_agua_df['Hidrometro']!='H014']

