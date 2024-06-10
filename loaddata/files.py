
import pandas as pd
import os
import loaddata.dictionary as dic
from netCDF4 import Dataset
import numpy as np
import geopandas as gpd
import streamlit as st
import xarray as xr
import random
from datetime import datetime

datos_csv_map_cargado = None
datos_csv_serie_cargado = None
datos_nc_map_cargado = None
datos_nc_map_heat_cargado = None
datos_nc_scatterbar_cargado = None
archivo_csv = "data/pepe.csv"
archivo_nc = "data/pepe.nc"

def julian_to_gregorian(jd):
    # Calculamos los valores A, B y C según la fórmula de conversión
    A = jd + 32044
    B = int((4 * A + 3) / 146097)
    C = A - int((146097 * B) / 4)

    # Calculamos los valores D, E y F según la fórmula de conversión
    D = int((4 * C + 3) / 1461)
    E = C - int((1461 * D) / 4)
    F = int((5 * E + 2) / 153)

    # Calculamos el día, mes y año gregoriano
    day = E - int((153 * F + 2) / 5) + 1
    month = F + 3 - 12 * int(F / 10)
    year = 100 * B + D - 4800 + int(F / 10)

    return year, month, day

def cargar_scatter_bar_data(path=archivo_nc,
                     reload=False,readfrom3=False):
    
    global datos_nc_scatterbar_cargado
    group_1 = [str(name) for name, in_group in zip(dic.scatter_bar["data_set_name"], dic.scatter_bar["in_group_1"]) if in_group]

    # Definir las columnas del DataFrame con sus tipos de datos
    columnas = {
        "fecha": pd.to_datetime([]),           # Columna de tipo fecha
        "precipitacion": pd.Series([], dtype='float'),  # Columna de tipo float
        "prob_deslaves": pd.Series([], dtype='int'),    # Columna de tipo int
        "categorias": pd.Series([], dtype='str')        # Columna de tipo string
    }

    data=[]
    if os.path.exists(path) :
        for index in range(len(group_1 )): 
            #print(dic.scatter_bar["data_set_name"][index])
            ds = xr.open_dataset(os.path.join(path,dic.scatter_bar["data_set_name_file"][index]))
            T_grid=ds[dic.scatter_bar["data_set_time"][index]].values
            var=ds[dic.scatter_bar["data_set_var"][index]].values

            for j, date in enumerate(T_grid):
                if dic.scatter_bar["data_set_type_calendar"][index]=='julian_day':
                    year, month, day = julian_to_gregorian(int(date))
                    data_date=pd.to_datetime(f"{2000}-{month:02d}-{day:02d}", format="%Y-%m-%d")
                elif dic.scatter_bar["data_set_type_calendar"][index]=='days since 1960-01-01':
                        fecha_hora = datetime.fromisoformat(str(date))
                        data_date=pd.to_datetime(f"{2000}-{fecha_hora.month:02d}-{fecha_hora.day:02d}", format="%Y-%m-%d")

                data.append({
                        dic.scatter_bar["scatter_vars"][0]: data_date,
                        dic.scatter_bar["scatter_vars"][1]: round(var[j],1),
                        dic.scatter_bar["scatter_vars"][2]: random.randint(0, 100),
                        dic.scatter_bar["scatter_vars"][3]: dic.scatter_bar["data_set_name"][index]
                })            
        datos_nc_scatterbar_cargado=pd.DataFrame(data)
        return datos_nc_scatterbar_cargado
    elif readfrom3:
        if datos_nc_scatterbar_cargado is None:
            return 'No se encontraron los datos asociados '
        else:
            return datos_nc_scatterbar_cargado
    else:
        datos_nc_scatterbar_cargado= None
        return 'No se encontraron los datos asociados '
    

def cargar_serie_datos_csv(archivo=archivo_csv,
                     reload=False,readfrom3=False):
    global datos_csv_serie_cargado
    place_activo=dic.activos['var'].index(dic.place(readfrom3=True))

    if os.path.exists(archivo) :
        if datos_csv_serie_cargado is None or reload:
            #print('Recarga Serie')
            #print(place_activo)
            try:
                with open(archivo, 'r') as file:
                    datos_csv_serie_cargado = None
                    datos_csv_serie_cargado = pd.read_csv(archivo)
                    #print('Leo los datos Serie')
            except Exception as e:
                print("Error al abrir el archivo CSV:", e)
        return datos_csv_serie_cargado
    elif readfrom3:
        if datos_csv_serie_cargado is None:
            return 'No se encontraron los datos asociados '
        else:
            return datos_csv_serie_cargado
    else:
        datos_csv_serie_cargado = None
        return 'No se encontraron los datos asociados '

def cargar_map_datos_csv(archivo=archivo_csv,
                     reload=False,readfrom3=False):
    global datos_csv_map_cargado
    place_activo=dic.activos['var'].index(dic.place(readfrom3=True))
    
    if os.path.exists(archivo) :
        if datos_csv_map_cargado is None or reload:
            #print('Recarga')
            #print(place_activo)
            try:
                with open(archivo, 'r') as file:
                    datos_csv_map_cargado = None
                    datos_csv_map_cargado = pd.read_csv(archivo)
                    #Esto es solo para el caso de Linea Ferrea Peru 
                    #Porque el shape esta mal ordenado en su construccion
                    datos_csv_map_cargado=datos_csv_map_cargado.drop_duplicates().reset_index(drop=True)
                    df1=datos_csv_map_cargado.head(111).iloc[::-1].reset_index(drop=True)
                    df2=datos_csv_map_cargado.iloc[-244:-1].reset_index(drop=True).iloc[::-1].reset_index(drop=True)
                    datos_csv_map_cargado=datos_csv_map_cargado.iloc[111:-244].reset_index(drop=True)
                    datos_csv_map_cargado = pd.concat([datos_csv_map_cargado, df2], ignore_index=True)
                    datos_csv_map_cargado = pd.concat([datos_csv_map_cargado, df1], ignore_index=True)
                    del df1,df2
                    precision = 6

                    # Crear la máscara utilizando la precisión de las coordenadas
                    datos_csv_map_cargado=datos_csv_map_cargado[datos_csv_map_cargado['Longitud'].between(dic.activos['east'][place_activo], dic.activos['west'][place_activo]) &
                                                          datos_csv_map_cargado['Latitud'].between(dic.activos['south'][place_activo], dic.activos['north'][place_activo])
                                                          ].reset_index(drop=True)

                    #print('Leo los datos')
            except Exception as e:
                print("Error al abrir el archivo CSV:", e)
        return datos_csv_map_cargado
    elif readfrom3:
        if datos_csv_map_cargado is None:
            return 'No se encontraron los datos asociados '
        else:
            return datos_csv_map_cargado
    else:
        datos_csv_map_cargado = None
        return 'No se encontraron los datos asociados '

from shapely.ops import unary_union
@st.cache_data
def cargar_map_datos_layer_csv(archivo=archivo_nc.replace('.nc','.csv'),
                     reload=False,readfrom3=False,
                     var=dic.vars["var_proc"][0],
                     label=dic.vars["label"][0],
                     json_file=dic.vars['file_proc'][0].replace('.nc','.geojson')

                     ):
    global datos_nc_map_cargado
    if datos_nc_map_cargado is None or reload:
        gdf = gpd.read_file(json_file)
        if var in gdf.columns:
            # Eliminar la columna 'daily_rain'
            gdf = gdf.drop(columns=[var])
        datos_nc_map_cargado_aux = pd.read_csv(archivo)
        datos_nc_map_cargado= gdf.join(datos_nc_map_cargado_aux)
        
        datos_nc_map_cargado[var]=round(datos_nc_map_cargado[var],2)

        grouped = datos_nc_map_cargado.groupby(var)
        geometries = []
        daily_rain_values = []

        # Itera sobre cada grupo y fusiona las geometrías
        for rain, group in grouped:
            geometries.append(unary_union(group['geometry']))
            daily_rain_values.append(rain)
        # Crea un nuevo GeoDataFrame con las geometrías fusionadas y los valores de daily_rain
        datos_nc_map_cargado = gpd.GeoDataFrame({'geometry': geometries, var: daily_rain_values})
        #Verificar shapes que pueden superponerse:
        for i, polygon1 in datos_nc_map_cargado.iterrows():
            for j, polygon2 in datos_nc_map_cargado.iterrows():
                # Saltar si estamos comparando el mismo polígono
                if i == j:
                    continue
                # Verificar si los polígonos se solapan
                if polygon1['geometry'].intersects(polygon2['geometry']):
                    # Calcular la diferencia entre los polígonos para eliminar la porción superpuesta
                    #difference = polygon1['geometry'].difference(polygon2['geometry'])
                    # Actualizar la geometría del polígono i con la diferencia
                    datos_nc_map_cargado.loc[datos_nc_map_cargado.index[i],"geometry"] = datos_nc_map_cargado.geometry[datos_nc_map_cargado.index[i]]- datos_nc_map_cargado.geometry[datos_nc_map_cargado.index[j]]
        
        datos_nc_map_cargado.crs = gdf.crs
        del datos_nc_map_cargado_aux, gdf

        datos_nc_map_cargado['popup']=label+': <strong>' + round(datos_nc_map_cargado[var],2).astype(str)+' mm </strong>'

        return datos_nc_map_cargado
    elif readfrom3:
        if datos_nc_map_cargado is None:
            return 'No se encontraron los datos asociados '
        else:
            return datos_nc_map_cargado
    else:
        datos_nc_map_cargado = None
        return 'No se encontraron los datos asociados ' 

@st.cache_data
def cargar_map_datos_layer_nc(archivo=archivo_nc,
                     reload=False,readfrom3=False,
                     var=dic.vars["var_proc"][0],
                     ):
    global datos_nc_map_heat_cargado 

    if datos_nc_map_heat_cargado is None or reload:
        nc_data =  xr.open_dataset(archivo) 
        data_lon= nc_data[dic.vars['var_proc_latlon'][1]].values
        data_lat= nc_data[dic.vars['var_proc_latlon'][0]].values
        data_var= nc_data[var].values
        data=[]
        longitud=[]
        latitud=[]
        
        for j, lats in enumerate(data_lat):
            for i, lons in enumerate(data_lon): 
                longitud.append(round(lons,2))
                latitud.append(round(lats,2))
                data.append(round(data_var[0,j,i],1))
 
        #Crea un dataframe:
        df = pd.DataFrame({
             'Latitud':latitud,
             'Longitud':longitud,
            dic.vars["var_proc"][0]:data
        })
        del nc_data
        datos_nc_map_heat_cargado = df
        return datos_nc_map_heat_cargado 
    elif readfrom3:
        if datos_nc_map_heat_cargado  is None:
            return 'No se encontraron los datos asociados '
        else:
            return datos_nc_map_heat_cargado 
    else:
        datos_nc_map_heat_cargado  = None
        return 'No se encontraron los datos asociados ' 
    
    



