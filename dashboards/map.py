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
from loaddata.files import cargar_map_datos_layer_nc
from loaddata.files import cargar_map_datos_layer_csv
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

    #Preguntar si hay que activar un layer
    layer = dic.get_layers() 
    #Contruir la barra de colores para el layer
    colormap = dic.get_color_extra_layer('BrBG',dic.vars["map_color_bar"][layer][0],dic.vars["map_color_bar"][layer][1])

    #********************************
    #         RASTER-SHAPE          *
    #********************************
    #Pedir los datos para raster:
    df_raster = cargar_map_datos_layer_csv(readfrom3=True)
    df_raster = df_raster[~df_raster.geometry.is_empty]
    df_raster.reset_index(drop=True, inplace=True)
    #Se crean los popups por separado para mayor control
    popup = folium.GeoJsonPopup(
                    fields= ['popup'] , #Colummna que está en el df_raster
                    labels=False,
                    max_width=800,
                    parse_html=True, 
                    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    
    )
    folium.GeoJson(df_raster,
                   name=dic.vars['map_label_layer'][0]+' (raster)',
                   show=dic.vars['map_layer_activate'][0],
                   style_function=lambda x: {
                                "fillColor": colormap(x["properties"][dic.vars['var_proc'][0]])
                                if x["properties"][dic.vars['var_proc'][0]] is not None
                                else "transparent",
                                "color": colormap(x["properties"][dic.vars['var_proc'][0]]) if x["properties"][dic.vars['var_proc'][0]] is not None else "transparent",
                                "weight": 0.0001,
                                "dashArray": "5, 5",
                                "fillOpacity": dic.vars['map_layer_opacity'][0],
                                },
                    popup=popup,   
                   ).add_to(mapObj)  

    #********************************
    #           HEATMAP             *
    #********************************
    #Pedir los datos para Heatmap:
    df_heat=cargar_map_datos_layer_nc(readfrom3=True)
    #Se descomponen los colores en valores de 0 a 1 por exigencia del Heatmap:
    pasos = [0 + i * ((1 - 0) / (len(colormap.colors)-1)) for i in range(len(colormap.colors))] 
    #Se crea la barra de colores para el Heatmap
    gradient = {p: dic.rgba_to_hex(colormap.colors[i]) for i, p in enumerate(pasos)}
    del pasos
    #Se debe normalizar los datos para expresarlos entre 0 y 1 
    data_normalized = [(x - dic.vars["map_color_bar"][layer][0]) / (dic.vars["map_color_bar"][layer][1]-dic.vars["map_color_bar"][layer][0]) for x in df_heat[dic.vars['var_proc'][0]]]
    #Crear el Heatmap
    HeatMap(list(zip(df_heat['Latitud'], df_heat['Longitud'], data_normalized)), 
            scale_radius=True,    #Ajuste de Radio segun el zoom activo 
            gradient = gradient ,  #Barra de colores siempre debe estar expresada en diccionario con valor ente 0 y 1 
            radius=10, 
            min_opacity=0.8,
            max_opacity=0.9,
            name=dic.vars['map_label_layer'][0]+' (heatmap)',
            show=True,             #Se activa el layer por defecto.
            ).add_to(mapObj)
    
    #********************************
    #          LINEA SHAPE          *
    #********************************
    # Crear una lista de coordenadas para la línea continua
    # Como la linea se construlle punto a punto se añade a un grupo comun para poder
    #  agregarla como un todo a los layers del folium
    coordinates = [[row[0], row[1]] for row in filtered_data]
    feature_group = folium.FeatureGroup(name=dic.vars['map_label_layer'][1])
    # Añadir segmentos de la línea continua al mapa con colores correspondientes
    for i in range(len(coordinates) - 1):
        folium.PolyLine(locations=[coordinates[i], coordinates[i+1]], 
                        color=color_producer(df[dic.vars['name_proc'][1]][i]),
                         weight=7, opacity=0.7
                        ).add_to(feature_group)
    feature_group.add_to(mapObj)
    
    #Para poder tener mayor control del control-layer es mejor agregarlo como un child
    mapObj.add_child( folium.LayerControl(position='topleft', autoZIndex=True) )

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
    
    #***********************************
    # BARRA DE COLORESS PROBABILIDADES *
    #***********************************   
    # Mostrar la barra de colores con valores multiplicados por 100
    # Los valores extremos deben ponerse en codigo HTML al igual que si se quiere agregar un espacio
    # Ejemplo '≤'(&#8804;) ' '(&nbsp;), entonces es camobinacion '≤ ' se escribe '&#8804;&nbsp;'
    bar_range=dic.vars['map_color_bar'][1]
    st.markdown(f'<div style="{css_gradient}; position: relative; width: 100%;">' +
           ''.join([
                    f'<span style="position: absolute; left: {stop[0]}%; top: 100%; transform: translateX(-50%);">'
                    f'{ "&#8804;&nbsp;5" if stop[0] <= 5 else ("&#8805;&nbsp;95" if stop[0] >= 95 else int(stop[0] * dic.vars["map_factor"][1]) )}%'
                        '</span>'
                    for stop in color_scale_heatmap
                        if stop[0] == dic.color_bar_adjust(0.0,bar_range[0],bar_range[1]) 
                        or stop[0] == dic.color_bar_adjust(0.25,bar_range[0],bar_range[1]) 
                        or stop[0] == dic.color_bar_adjust(0.50,bar_range[0],bar_range[1]) 
                        or stop[0] == dic.color_bar_adjust(0.75,bar_range[0],bar_range[1]) 
                        or stop[0] == dic.color_bar_adjust(1,bar_range[0],bar_range[1])
                    ]) +
          '</div>' +
           '<br>'+
           '<div style="margin: 0 auto; width: 100%; text-align: center;">' +
           '<span style="font-size: 20px;">'+dic.vars['map_title_color_bar'][1]+'</span>' +
           '</div>', unsafe_allow_html=True)
    
    
    #************************************
    #  BARRA DE COLORESS PRECIPITACION  *
    #************************************
    #Se Descomponen los colores y se llevan a HEX
    lista_colores_rgba = list(zip(range(len(colormap.colors)), colormap.colors))
    lista_colores_hex = [[((i-dic.vars["map_color_bar"][0][0])/(dic.vars["map_color_bar"][0][1]-dic.vars["map_color_bar"][0][0]))*100,
                           '#' + ''.join([f'{int(color * 255):02x}' for color in rgba[1][:3]])] for i, rgba in enumerate(lista_colores_rgba)]
    del lista_colores_rgba
    #La mejor forma de crear la Barra usando los colores formateados para CSS
    css_gradient =dic.colorbar_to_css(lista_colores_hex,layer,dic.vars['units'][layer])
    bar_range=dic.vars['map_color_bar'][layer]
    st.markdown(f'<div style="{css_gradient}; position: relative; width: 100%;">' +
           ''.join([f'<span style="position: absolute; left: {stop[0]}%; top: 100%; transform: translateX(-50%);">{int((stop[0]/100) * (bar_range[1] - bar_range[0])) + bar_range[0]  }mm</span>' for stop in lista_colores_hex 
                    if int((stop[0]/100) * (bar_range[1] - bar_range[0])) + bar_range[0] == dic.color_bar_adjust(0.0,bar_range[0],bar_range[1]) 
                    or int((stop[0]/100) * (bar_range[1] - bar_range[0])) + bar_range[0] == dic.color_bar_adjust(0.2,bar_range[0],bar_range[1]) 
                    or int((stop[0]/100) * (bar_range[1] - bar_range[0])) + bar_range[0] == dic.color_bar_adjust(0.4,bar_range[0],bar_range[1])
                    or int((stop[0]/100) * (bar_range[1] - bar_range[0])) + bar_range[0] == dic.color_bar_adjust(0.6,bar_range[0],bar_range[1]) 
                    or int((stop[0]/100) * (bar_range[1] - bar_range[0])) + bar_range[0] == dic.color_bar_adjust(0.8,bar_range[0],bar_range[1]) 
                    or int((stop[0]/100) * (bar_range[1] - bar_range[0])) + bar_range[0] == dic.color_bar_adjust(1,bar_range[0],bar_range[1])
                    ]) +
           '</div>' +
           '<br>'+
           '<div style="margin: 0 auto; width: 100%; text-align: center;">' +
           '<span style="font-size: 20px;">'+dic.vars['map_title_color_bar'][0]+'</span>' +
           '</div>', unsafe_allow_html=True)
    st.markdown('<br><br>', unsafe_allow_html=True)     


ST_MAPS_COMPONENTS = {
    "Heatmap: Ferrovia": (
        render_heatmap_latlon,
        "https://medium.com/datasciencearth/map-visualization-with-folium-d1403771717",
        #https://discuss.streamlit.io/t/streamlit-folium-update-more-dynamic-maps/35149/3
        #https://folium.streamlit.app/dynamic_map_vs_rerender
    ),
}
