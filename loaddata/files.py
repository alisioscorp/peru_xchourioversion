
import pandas as pd
import os
import loaddata.dictionary as dic

datos_csv_map_cargado = None
datos_csv_serie_cargado = None
archivo_csv = "data/pepe.csv"

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


    
    



