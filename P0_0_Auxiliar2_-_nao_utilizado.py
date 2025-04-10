# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 09:50:45 2025

@author: Usuario
"""

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