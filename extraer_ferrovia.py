import geopandas as gpd
from netCDF4 import Dataset
import pandas as pd
import os
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point
from shapely.geometry import MultiPoint
from shapely.ops import split
import loaddata.dictionary as dic
import sys
import re
from datetime import datetime
import glob
import shutil

stop='NO SE PUEDE CONTINUAR'
# Patrón regex para verificar el formato YYYYMMDD
patron_fecha = re.compile(r'^\d{8}_')
patron_folders= re.compile(r'\d{4}-\d{2}-\d{2}')

# Función para verificar si una fecha es válida en el calendario gregoriano
def fecha_valida(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, '%Y%m%d')
        return True
    except ValueError:
        return False

def validar(dir,create):
    # Verificar si el directorio existe
    if create and not os.path.exists(dir):
        # Crear el directorio si no existe
        os.makedirs(dir)
        print(f"El directorio '{dir}' ha sido creado.")
    elif not create and not os.path.exists(dir):
        print("\033[48;5;0m\033[38;5;214m" + f"El directorio/archivo '{dir}' No existe, hasta que '{dir}' exista NO SE PUEDE CONTINUAR, por favor verifique" + "\033[0m")
        sys.exit()
    else:
        print(f"El directorio '{dir}' ya existe.")    

# Definir función para calcular la distancia entre dos puntos
def calculate_distance(point1, point2):
    # Conversión de grados a metros (aproximación)
    distancia_en_grados = point1.distance(point2)
    distancia_en_metros = distancia_en_grados * 111000  # Aproximadamente 111,000 metros por grado en latitud o longitud
    return distancia_en_metros

def geometrias_to_puntos(gdf):
    # Convertir geometrías de LineString a puntos
    points = []
    #Comentado pero funciona
    for line in gdf.geometry:
        if isinstance(line, LineString):
            points.extend(list(line.coords))
        else:
            for linestring in line:
                points.extend(list(linestring.coords))

    # Crear un nuevo GeoDataFrame con los puntos
    gdf_points = gpd.GeoDataFrame(geometry=[Point(x, y) for x, y in points], crs=gdf.crs)
    # Liberar memoria
    del gdf

    # Extraer las coordenadas del shapefile
    x_destino = gdf_points.geometry.x
    y_destino = gdf_points.geometry.y

    return x_destino,y_destino


def get_coords_shape(nc_files,nc_dir,out_dir,x_destino,y_destino,var,name,min_name,max_name,fecha_name,is_layer):
# Encontrar los índices correspondientes a las coordenadas del shapefile en el NetCDF
    # (Se asume que las coordenadas son las mismas y están en el mismo sistema de coordenadas)
    # Si no es así se puede usar nearest neighbor, interpolación, etc., dependiendo de tus necesidades.

    # Iterar sobre cada punto de las coordenadas del shapefile

    min1=[]
    min2=[]
    max1=[]
    max2=[]
    fecha=[]
    for nc_file in nc_files:
        # Verificar si ya existe un archivo CSV correspondiente al archivo NetCDF actual
        csv_filename = os.path.splitext(nc_file)[0] + '_shape.csv'
        if csv_filename in os.listdir(nc_dir):
            print(f"El archivo CSV correspondiente a {nc_file} ya existe. Saltando al siguiente archivo.")
            continue

        # Cargar el archivo NetCDF
        nc_path = os.path.join(nc_dir, nc_file)
        nc_data = Dataset(nc_path)
        #Obtener la fecha
        fecha.append(nc_file[:8])
        # Obtener las variables necesarias del archivo NetCDF
        variable1 = nc_data.variables[var][:]
        min1.append(variable1.min())
        max1.append(variable1.max())
        #print()
        dimensiones = np.shape(variable1)

        # Contar el total de datos
        total_datos = dimensiones[0] * dimensiones[1] * dimensiones[2]

        #print("El total de datos en la variable es:", total_datos)
        

        longitudes = nc_data.variables['lon'][:] 
        latitudes = nc_data.variables['lat'][:]
        #print(longitudes)
        #print(xandre)

        max_length = max(longitudes.shape[0], latitudes.shape[0])

        # Calcular la cantidad de faltantes a agregar al final de cada matriz para que tengan la misma longitud
        pad_longitudes = max_length - longitudes.shape[0]
        pad_latitudes = max_length - latitudes.shape[0]

        # Añadir falatntes  al final de la matriz más corta
        longitudes_padded = np.pad(longitudes, (0,pad_longitudes), mode='constant', constant_values=-999)
        latitudes_padded = np.pad(latitudes, (0, pad_latitudes), mode='constant', constant_values=-999)

        #Liberar Memoria
        del longitudes, latitudes
        longitudes=longitudes_padded
        latitudes=latitudes_padded 
        #Liberar Memoria
        del longitudes_padded,latitudes_padded 

        # Crear un árbol KD para búsqueda rápida del vecino más cercano
        points_origen = np.column_stack((longitudes[:].ravel(), latitudes[:].ravel()))
        tree = cKDTree(points_origen)

        # Encontrar el índice del vecino más cercano en el conjunto de datos de origen para cada punto de destino
        # Para este caso origen es el archivo NC mienstras que el destino corresponde a el shape y/o csv 
        indices_vecinos = tree.query(np.column_stack((x_destino, y_destino)), k=1)[1]

        # Asignar los valores correspondientes a los índices de los vecinos más cercanos
        values_variable1 = variable1.ravel()[indices_vecinos]
        #values_variable2 = variable2.ravel()[indices_vecinos]

        min2.append(values_variable1.min())
        max2.append(values_variable1.max())

        # Crear un DataFrame con los valores y las coordenadas
        df = pd.DataFrame({'Latitud': y_destino, 'Longitud': x_destino, name: values_variable1})

        # Guardar el DataFrame como un archivo CSV
        csv_path = os.path.join(out_dir, csv_filename)
        df.to_csv(csv_path, index=False)
        #if is_layer:
        #    shutil.copy(nc_path, out_dir) 

        print(f"\033[32m\033[40mArchivo CSV guardado exitosamente: {csv_path}\t[*] \033[0m")

    #Hacer un dataframe:
    min1 = [valor if valor != 'masked' else np.nan for valor in min1]
    max1 = [valor if valor != 'masked' else np.nan for valor in max1]
    min2 = [valor if valor != 'masked' else np.nan for valor in min2]
    max2 = [valor if valor != 'masked' else np.nan for valor in max2]
    data = {
    fecha_name:fecha,
    min_name+'_grid': min1,
    max_name+'_grid': max1,
    min_name+'_shape':min2,
    max_name+'_shape':max2
    }
    
    df1 = pd.DataFrame(data)
    #darele formato a colummna fecha
    df1['fecha'] = pd.to_datetime(df1['fecha'], format='%Y%m%d')
    #ordenarlo por fecha
    df1 = df1.sort_values(by='fecha', ascending=True).reset_index(drop=True)
    return df1

def produce_files(nc_dir,out_dir,sub_folder=''):
    print('en funcion')
    df_final = pd.DataFrame()
    # Directorio que contiene los archivos NetCDF (en este caso uso el mismo directorio que el script)
    validar(nc_dir,False) 
    #Directorio donde se guardan las salidas
    validar(out_dir,True) 

    # Lista todos los archivos .csv en el directorio
    archivos_csv = glob.glob(os.path.join(out_dir, '*.csv'))
    for archivo in archivos_csv:
        os.remove(archivo)

    
    # Cargar el archivo shapefile
    if dic.activos['shape'][place]:
        shp_filename = os.path.join(nc_dir,dic.activos['shape'][place])
        validar(shp_filename,False)
        gdf = gpd.read_file(shp_filename)

        x_destino,y_destino = geometrias_to_puntos(gdf)
        del gdf

    # Obtener la lista de archivos NetCDF en el directorio
    nc_files = [f for f in os.listdir(os.path.join(nc_dir,sub_folder)) if f.endswith('.nc')]
    #print(nc_files)
    if not nc_files:
        print("\033[48;5;0m\033[38;5;214m" + f"No hay ningún archivo .nc en '{os.path.join(nc_dir,sub_folder)}', por lo tanto no hay nada que procesar" + "\033[0m")
        sys.exit()
#Se verifica que no se contamine el proceso con arcchivos que no cumplen con el formato
# de nombres adecuado (se verifica fechas, patron de nombre para cada archivo y que sean pares)
# es decir se debe tener la misma cantidad de archivos por día (1 por variable)
#Primer filtro formato de fechas YYYYMMDD
    nc_files = [archivo for archivo in nc_files if patron_fecha.match(archivo) and fecha_valida(archivo[:8])]
    #Segundo filtro patron de nombres 
    # Lista de cadenas a incluir
    incluir = [archivo[8:] for archivo in dic.vars['file_proc']] 
    nc_files = [archivo for archivo in nc_files if patron_fecha.match(archivo) and any(archivo.endswith(s) for s in incluir)]
    #Tercer filtro , deben estar la misma cantidad de archivos para cada variable
    for i in range(len(incluir)-1):
        var1= sum(archivo.count(incluir[i]) for archivo in nc_files) 
        var2= sum(archivo.count(incluir[i+1]) for archivo in nc_files) 
        if var1 != var2:
            if var1 ==min(var1, var2):
                index=i
            else:
                index=i+1
            print("\033[48;5;0m\033[38;5;214m" + f" no existe la cantidad suficiente de archivos de '{incluir[index]}' por lo que  NO SE PUEDE CONTINUAR, por favor verifique "+sub_folder+ "\033[0m")
            sys.exit()
    del var1,var2
    if dic.activos['shape'][place]:
        for i in range(len(incluir)):
            files = [archivo for archivo in nc_files if patron_fecha.match(archivo) and any(archivo.endswith(s) for s in [incluir[i]])]
            var=dic.vars['var_proc'][i]
            name=dic.vars['name_proc'][i]
            min_name=dic.vars['min_proc'][i]
            max_name=dic.vars['max_proc'][i]
            fecha_name=dic.vars['date_proc'][0]
            is_layer=dic.vars['var_is_layer'][i]
            df_aux=get_coords_shape(files,os.path.join(nc_dir,sub_folder),out_dir,x_destino,y_destino,var,name,min_name,max_name,fecha_name,is_layer)
            # Concatena solo las nuevas columnas al DataFrame df_final
            df_final = pd.concat([df_final, df_aux.iloc[:, 1:]], axis=1) 
    return df_final,df_aux,fecha_name,out_dir


for place in range(len(dic.activos['name'])):
    nc_dir=os.path.join(dic.activos['home_path'][place])
    subcarpetas = [] #Carpetas que tienen datos, se supone la carpeta es el start time
    for nombre in os.listdir(nc_dir):
        if os.path.isdir(os.path.join(nc_dir, nombre)):
            if patron_folders.match(nombre):
                subcarpetas.append(nombre)
    subcarpetas = sorted(subcarpetas)
    subcarpetas=[]
    if subcarpetas: 
        for carpeta in subcarpetas:
            out_dir = os.path.join('data',dic.activos['var'][place],carpeta)
            df_final,df_aux,fecha_name,out_dir=produce_files(nc_dir,out_dir,carpeta)
            # Garantizar que la columna 'fecha' esté en df_final
            df_final[fecha_name] = df_aux[fecha_name]
            # Reordena las columnas del DataFrame final moviendo 'fecha' al principio
            columnas = list(df_final.columns)
            columnas.remove(fecha_name)  # Elimina 'fecha' de la lista de columnas
            columnas.insert(0, fecha_name)  # Agrega 'fecha' al principio de la lista de columnas
            df_final = df_final.reindex(columns=columnas) 
            df_final.to_csv(os.path.join(out_dir,dic.serie['file']), index=False)
            print(df_final)

        print(subcarpetas)
    else:
        out_dir = os.path.join('data',dic.activos['var'][place])
        df_final,df_aux,fecha_name,out_dir=produce_files(nc_dir,out_dir)
        # Garantizar que la columna 'fecha' esté en df_final
        df_final[fecha_name] = df_aux[fecha_name]
        # Reordena las columnas del DataFrame final moviendo 'fecha' al principio
        columnas = list(df_final.columns)
        columnas.remove(fecha_name)  # Elimina 'fecha' de la lista de columnas
        columnas.insert(0, fecha_name)  # Agrega 'fecha' al principio de la lista de columnas
        df_final = df_final.reindex(columns=columnas) 
        df_final.to_csv(os.path.join(out_dir,dic.serie['file']), index=False)

        print(df_final)