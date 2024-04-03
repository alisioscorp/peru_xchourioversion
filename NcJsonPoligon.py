import geojson
import xarray as xr
import numpy as np
import loaddata.dictionary as dic
import os
import sys
import pandas as pd
import sys
import shutil

def netcdf_to_geojson(nc_file, lon_variable, lat_variable, data_variable, geojson_name,parametro):
    valores=[]
    ids=[]
    ds = xr.open_dataset(nc_file)
    

    print(nc_file)
    
    # Extraer coordenadas longitudinales y latitudinales
    lons = ds[lon_variable].values
    lats = ds[lat_variable].values
    
    # Extraer los datos de interés
    data = ds[data_variable].values
    
    # Calcular la diferencia entre las coordenadas longitudinales y latitudinales
    lon_diff = np.diff(lons)[0] / 2
    lat_diff = np.diff(lats)[0] / 2
    
    # Crear una lista para almacenar los polígonos GeoJSON con sus valores asociados
    features = []
    
    # Iterar sobre todas las celdas en el archivo NetCDF
    geometry_id = 0
    for i in range(len(lats) - 1):
        for j in range(len(lons) - 1):
            # Definir los vértices del polígono
            vertices = [
                (lons[j] - lon_diff, lats[i] - lat_diff),
                (lons[j] + lon_diff, lats[i] - lat_diff),
                (lons[j] + lon_diff, lats[i + 1] + lat_diff),
                (lons[j] - lon_diff, lats[i + 1] + lat_diff),
                (lons[j] - lon_diff, lats[i] - lat_diff)  # Repetir el primer vértice para cerrar el polígono
            ]
            
            # Obtener el valor asociado a la celda actual
            #print(data.ndim)
            if data.ndim == 3:
                value = round(float(data[0,i, j]),4)
            elif data.ndim == 2:
                value = round(float(data[i, j]),4)
            if  np.isnan(value):
                value = None
            
            # Crear el polígono GeoJSON con su valor asociado
            polygon = geojson.Polygon([vertices])
            feature = geojson.Feature(geometry=polygon, id=geometry_id,properties={data_variable: value})
            
            # Agregar la característica a la lista de características
            features.append(feature)
            valores.append(value)
            ids.append(geometry_id)
            geometry_id = geometry_id+1
            
    
    #Crea un dataframe:
    df = pd.DataFrame({
         "id":ids,
         data_variable:valores
    })
    df.to_csv(geojson_name.replace(".geojson",".csv"), index=False)
    # Crear una colección de características GeoJSON
    feature_collection = geojson.FeatureCollection(features)
    
    # Escribir la colección de características en un archivo GeoJSON
    if parametro == 'first':
        with open(geojson_name, "w") as f:
            geojson.dump(feature_collection, f)

# Llamar a la función para convertir el archivo NetCDF a GeoJSON
#netcdf_to_geojson("20240129_Peru_lndslides.nc", "lon", "lat", "p_landslide", "20240129_Peru_lndslides_poligon.geojson")
#netcdf_to_geojson("data.nc", "X", "Y", "precipitation", "data_poligon.geojson")

if len(sys.argv) < 2:
    print("\033[91m Se requiere al menos un argumento. \033[0m")
    #print(" Ejemplo ")

    sys.exit()
    
parametro = sys.argv[1]
var_json=dic.vars["var_proc"][0]

if parametro == 'first':
    file_in=os.path.join(dic.activos['home_path'][0],dic.vars['file_proc'][0])
    file_out=os.path.join('data',dic.activos['var'][0], dic.vars['file_proc'][0].replace(".nc", ".geojson"))

    if not os.path.exists(file_in):
        print("\033[48;5;0m\033[38;5;196m"+f" No existe el archivo '{file_in}', no se puede continuar"+"\033[0m")
        sys.exit()
    netcdf_to_geojson(file_in, dic.vars['var_proc_latlon'][1], dic.vars['var_proc_latlon'][0],var_json, file_out,parametro)

elif parametro == 'all':
    
    nc_files = [f for f in os.listdir(os.path.join(dic.activos['home_path'][0])) if f.endswith(dic.vars['file_proc'][0][8:])]

    for files in nc_files:
        file_out=os.path.join('data',dic.activos['var'][0], files.replace(".nc", ".geojson"))
        file_in=os.path.join(dic.activos['home_path'][0],files)
        netcdf_to_geojson(file_in, dic.vars['var_proc_latlon'][1], dic.vars['var_proc_latlon'][0],var_json, file_out,parametro)
        shutil.copy(file_in, file_out.replace(".geojson",".nc"))
        #print(file_in)
    
