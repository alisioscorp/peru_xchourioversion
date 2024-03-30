import json
from streamlit_echarts import Map
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import xarray as xr
import numpy as np
import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
from loaddata.files import cargar_map_datos_csv
import loaddata.dictionary as dic
from geopy.distance import geodesic
from streamlit_folium import folium_static




bounds_peru = [[-18.3496, -81.3261], [0.2295, -68.6521]] 

color_scale_heatmap = dic.get_bar_color()

# Definir una función para mapear los valores de probabilidad a colores
def color_producer(probability):
    for i in range(len(color_scale_heatmap) - 1):
        if color_scale_heatmap[i][0] <= probability <= color_scale_heatmap[i+1][0]:
            return color_scale_heatmap[i][1]


def render_heatmap_latlon():
    place_activo=dic.activos['var'].index(dic.place(readfrom3=True))
    fecha=dic.fecha_usr(readfrom3=True)
    #Crear la instancia del mapa
    mapObj = folium.Map([dic.activos['center_lat'][place_activo], 
                         dic.activos['center_lon'][place_activo]],
                         zoom_start=10, max_zoom=10, min_zoom=10,
                         control_scale=True )
    mapObj.max_bounds = bounds_peru

    # Leer el archivo CSV en un DataFrame de pandas
    df = cargar_map_datos_csv(readfrom3=True)
    #En caso de que no haya archivo asociado se muestra mensaje de alerta 
    if isinstance(df, str):
        st.write('<div style="font-size: 24px; background-color: yellow; padding: 10px;"><span style="color:red;"><b>'+df+'para crear mapa</b></span></div>', unsafe_allow_html=True)
        return

    # Convertir NaN a cero en el DataFrame
    df.fillna(0.0, inplace=True)

    # Convertir el DataFrame a una lista de listas
    data = df.values.tolist()


    # Eliminar puntos aislados basados en distancia umbral
    threshold_distance = 3.3  # Umbral de distancia en grados (ajustar según necesidad)
    filtered_data = [df.iloc[0]]
    for i in range(1, len(df)):
        distancia = geodesic((df.iloc[i-1]['Latitud'], df.iloc[i-1]['Longitud']), (df.iloc[i]['Latitud'], df.iloc[i]['Longitud'])).kilometers
        if distancia <= threshold_distance and distancia!=0.0:
            filtered_data.append(df.iloc[i])

          
    # Crear una lista de coordenadas para la línea continua
    coordinates = [[row[0], row[1]] for row in filtered_data]

    # Añadir segmentos de la línea continua al mapa con colores correspondientes
    for i in range(len(coordinates) - 1):
        folium.PolyLine(locations=[coordinates[i], coordinates[i+1]], 
                        color=color_producer(df[dic.vars['name_proc'][1]][i]),
                         weight=7, opacity=0.7
                        ).add_to(mapObj)
    
    folium.LayerControl().add_to(mapObj)

    st.markdown(
        """
        <style>
        .center {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 90vh; /* Altura del 90% del viewport */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    fecha_title= str(fecha).split('-')[0]+' '+dic.meses_espanol[str(fecha).split('-')[1].lower()] +' '+str(fecha).split('-')[2]
    
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>"+
            "Probabilidad de deslaves en "+ dic.get_place_name() +
            " <br> "+fecha_title+
            "</h1>", unsafe_allow_html=True)

    # Convertir la escala de colores en un string CSS
    css_gradient = "background: linear-gradient(to right, "
    for stop in color_scale_heatmap:
        css_gradient += f"{stop[1]} {stop[0] * dic.vars['map_factor'][1] }%, "
    css_gradient = css_gradient[:-2] + "); width: 500px; height: 30px; margin-top: 0px; margin-bottom: 0px; margin-left: auto; margin-right: auto;"
    # Agregar valores debajo de la barra de colores
    css_gradient += "text-align: center; margin-top: 10px;"
    css_gradient += "position: relative;"
    css_gradient += "font-size: 14px;"
    css_gradient += "display: flex;"
    css_gradient += "justify-content: space-between;"
    
    st_folium(mapObj, width=1050, height=450, use_container_width=True)#, width=800, height=450
    
    # Mostrar la barra de colores con valores multiplicados por 100
    bar_range=dic.vars['map_color_bar'][1]
    st.markdown(f'<div style="{css_gradient}; position: relative; width: 100%;">' +
           ''.join([f'<span style="position: absolute; left: {stop[0] * dic.vars["map_factor"][1] }%; top: 100%; transform: translateX(-50%);">{int(stop[0] * dic.vars["map_factor"][1] )}%</span>' for stop in color_scale_heatmap 
                    if stop[0] == dic.color_bar_adjust(0.0,bar_range[0],bar_range[1]) 
                    or stop[0] == dic.color_bar_adjust(0.25,bar_range[0],bar_range[1]) 
                    or stop[0] == dic.color_bar_adjust(0.50,bar_range[0],bar_range[1]) 
                    or stop[0] == dic.color_bar_adjust(0.75,bar_range[0],bar_range[1]) 
                    or stop[0] == dic.color_bar_adjust(1,bar_range[0],bar_range[1])
                    ]) +
           '</div>', unsafe_allow_html=True)
    
    st.markdown('<br><br>', unsafe_allow_html=True)
    


ST_MAPS_COMPONENTS = {
    "Heatmap: Ferrovía": (
        render_heatmap_latlon,
        "https://medium.com/datasciencearth/map-visualization-with-folium-d1403771717",
        #https://discuss.streamlit.io/t/streamlit-folium-update-more-dynamic-maps/35149/3
        #https://folium.streamlit.app/dynamic_map_vs_rerender
    ),
}
