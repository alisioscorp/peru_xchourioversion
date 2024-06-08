
activos={
        'name':['Ferrovia 1'],#'Ferrovia 2'], #Nombre de los activos
        'var':['FerVia1'],#'FerVia2'], #Nombre de variables internas asociada con el activo (Nunca usar espacios en este campo)
        'shape':['Callao_LaOroya.shp'],#''], #Si usa shape agruege el nombre del archivo , sino solo use ''
        'shape_order':['Peru'],#''], #Las opciones en este item son 'Peru' o 'None' , 
                                     #El caso 'Peru' es porque la líneas está desordenada, entonces comienza en un punto y luego salta al otro extremo
                                     #   y siguen los puntos hasta el punto incial de donde saltó. 
        'home_path':['Peru_Varios'],#'Peru_Varios'], #Directorios donde están los archivos a procesar (ahí debe estar los nc y shapes - defina un directorio por activo), 
        #'out_path':['pepe1','pepo1'], #Directorio donde se guardan los datos procesados
        "source":['shape'],
        'north':[-10.5 ],# -10.5],
        'south':[-12.5 ],# -12.5],
        'east': [-85   ],# -76.5],
        'west': [-76.5 ],# -74  ],
        'center_lat':[-12.06210],#-11.562107],
        'center_lon':[-77.00],#-76.036526],
    
}


serie={
    "label" : ['Precipitación','Probabilidad_Deslaves'], # Label superior de la series de datos
    "color": ['#556FC6','#91CC74'], # Colores en que se muestran las series de datos usar siempre codigos hex puede ubicar colores en (https://htmlcolorcodes.com/es/tabla-de-colores/) 
    "Y_axis_label":['Precipitación','Probabilidad de deslaves'], #Label en los ejes 
    "units":['mm','%'], # unidades de cada serie
    "type":['bar','bar'], # Puede ser line, bar, area
    "source":['grid','shape'],
    "shade":50, # Corresponde a la tonalidad con la que se muestran los valores minimos en una barra (50% mas claro que el color original)
    "file":'serie.csv', #Solo se define un archivo que va a contener los datos de las serie de todas las variables
    "interval":[[0,10],[0,100]], #Ajustar los intervalos minimo y máximo de la serie

}
vars={
    "label" : ['Precipitación','Probabilidad_Deslaves'],
    # Las siguientes lineas solo son vinculante para la creacion de archivos (el procesado)
    "name_proc":['precip(mm)','deslaves(%)'], # nombre con el que se guardaran los valores procesados para archivos visualizados en el mapa
    "file_proc":['20240307_Peru_rain.nc','20240307_Peru_lndslides.nc'], # nombre de archivos-> coloque el nombre completo de un archivo, 
                                                                          # recuerde debe comenzar con fecha en formato YYYYMMDD luego un '_'
                                                                          # y alfinal el nombre que desee colocarle seguido de la extención 
                                                                          # por ejemplo 19850115_pepe.nc
    "var_proc":['daily_rain','p_landslide'], #variables dentro de archivo nc
    "var_proc_latlon":['lat','lon'], #nombre de variable de longitud y latitud dentro de archivo nc
    "units":['mm','%'], #Unidades de los datos
    "var_is_layer":[True,False],  #Indicar cual es la variable de grid layer 
    "min_proc":['precip_min','deslaves_min'],#nombre de va con los que se guardan los valores mínimos
    "max_proc":['precip_max','deslaves_max'], #nombre de va con los que se guardan los valores máximos
    "date_proc":['fecha'], # En este caso solo se define una vez porque es un campo común para todas las variables
    "map_factor":[1,1],
    "map_label_layer":['precipitación','Ferrovia'], #Label que saldrá en la lista layer del mapa folium
    "map_layer_activate":[False,True], #Activar por defecto si se muestra el layer la primera vez (valore True o False) 
                                       # Se recomienda al menos dejar un layer en True
    "map_layer_opacity":[0.8,0.7],  #Transparencia del layer en el mapa (valores de 0 a 1)
    "map_color_bar":[[0,10],[0,100]], #Rango de la barra de colores 
    "map_title_color_bar":['Precipitación','Probabilidad'], #Titulo de la barra de colores
    "map_source":['shape','shape'], #Esto solo afecta la linea, shape significa que hay una archivo con ese sufijo donde estan los datos 
                                    # procesados por el shape en este caso de Peru para construir la linea ferrea 
    
}


alisios ={
    'icon':'icons/alisios.png',
    'url':'https://alisioscorporation.com/',
    'desc':'Alisios Corp.',
    'banner_bottom':'icons/banner_bottom.png',
    'banner_top':'icons/deslaves.png'
}

cliente ={
    'icon':'icons/LOGO-KERA-BLANCO-300x256.png',
    'url':'https://keraunos.co/',
    'desc':'keraunos'
}

gauge={
    "label" : ['Sin alertas','Atención','Alerta naranja','Alerta roja'],#['BAJO', 'MEDIO', 'ALTO'], #Nombre de categorías
    "values": [0.35,0.62,0.87,1],#[0.33,0.66,1], #Valores hasta donde llegará cada categoría por defecto arrnaca en 0 así que no debe definir 0 como inicio
    "location": [0.125,0.375,0.625,0.875], #[0,50,62.5,100],#[12.5,37.5,62.5,87.5], #[0,50,100], #Posición del label en el gauge
    "color": ['#7CFFB2','#58D9F9','#FFA500','#FF6E76'],#['#7CFFB2','#FDDD60','#FF6E76'] #Colores de cada caetgoría siempre deben ser valores hexagesimales 
    "text_size":40, #Tamaño del texto que indica el valor del gauge
    "text_pos":-15   #Posión en gauge del texto que indica el valor del gauge (el valor debe ir en porcentaje )
}
map={
    "label" : ['Precipitación','Probabilidad_Deslaves'],
    "color": [[],['#7CFFB2','#58D9F9','#FFA500','#FF6E76']], #Se recomienda usar los mismos colores que en el gauge
    "values": [[],[0.35,0.62,0.87,1]],
    "color_bar":[[],[7,5,5,4]] # cantidad de colores que quiere generar a parir del color definido
}


############################### ALERTA NO MODIFICAR NADA LUEGO DE ESTA LINEA #########################

meses_espanol = {
    'jan': 'Enero',
    'ene': 'Enero',
    'feb': 'Febrero',
    'mar': 'Marzo',
    'apr': 'Abril',
    'abr': 'Abril',
    'may': 'Mayo',
    'jun': 'Junio',
    'jul': 'Julio',
    'aug': 'Agosto',
    'ago': 'Agosto',
    'sep': 'Septiembre',
    'oct': 'Octubre',
    'nov': 'Noviembre',
    'dec': 'Diciembre',
    'dic': 'Diciembre'
}

css='''
        <style>
            section.main > div {max-width: 100%} 
            .banner_bottom {
                    width: 160%;
                    height: 200px;
                    overflow: hidden;
            }
            .banner_bottom img {
                    width: 65%;
                    object-fit: cover;
            }
            .banner {
                    width: 100%;
                    height: 300px;
                    overflow: hidden;
                    position: relative;
                    display: flex; /* Hacer que el contenedor sea un contenedor flex */
                    justify-content: center; /* Centrar horizontalmente */
                    align-items: center; 
            }
            .banner img {
                width: 100%; /* Ajustar la imagen al ancho completo del contenedor */
                height: auto; /* Ajustar la altura automáticamente para mantener la relación de aspecto */
                position: absolute; /* Posicionar la imagen de manera absoluta dentro del contenedor */
                top: 50%; /* Posicionar la imagen en el 50% de la parte superior del contenedor */
                left: 50%; /* Posicionar la imagen en el 50% de la parte izquierda del contenedor */
                transform: translate(-50%, -50%);
            }
            
        </style>
        '''

import numpy as np
from branca.colormap import linear



active_place = None
fecha_actual = None
place_name = None
                #'FerVia1'
def place(place=activos['var'][0],readfrom3=False):
    global active_place
    global place_name
    
    if readfrom3 and active_place is not None:
        return active_place
    else:
        active_place=place
        index = activos['var'].index(active_place)
        place_name = activos['name'][index]
        return active_place

def fecha_usr(fecha='Initial',readfrom3=False):
    global fecha_actual
    if readfrom3 and fecha_actual is not None:
        return fecha_actual
    else:
        fecha_actual=fecha
        return fecha_actual

def get_place_name():
    return place_name

def get_gauge_control():
    formater="function (value) {"
    value="function (value) {"
    color=[]
    for i in range(len(gauge['label'])):
        if i ==0:
            formater=formater+"if (value === "+str(gauge['location'][i])+") {"+"  return '"+str(gauge['label'][i])+"'; }"
        else:
            formater=formater+"else if (value === "+str(gauge['location'][i])+") {"+"  return '"+str(gauge['label'][i])+"';}"
        color.append( [ gauge['values'][i] , gauge['color'][i] ] )
    formater=formater+"return '';}"

    for i in range(len(gauge['label'])):
        if i ==0:
            value=value+"if (-0.1 < value && value <= "+str((gauge['values'][i]*100))+" ) {"+"  return value + '%\\n\\n' + '"+str(gauge['label'][i])+"'; }"
        else:
            value=value+"else if ("+str((gauge['values'][i-1]*100))+" < value && value <= "+str((gauge['values'][i]*100))+" ) {"+"  return value + '%\\n\\n' + '"+str(gauge['label'][i])+"'; }"
    value=value+"return '';}"
    #print(formater)
    return formater,color,value

def hex_to_rgba(hex_color, alpha):

    # Eliminar el carácter '#' si está presente
    hex_color = hex_color.lstrip('#')
    alpha = alpha * 255 
    # Convertir los valores hexadecimales en valores decimales
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    # Calcular el valor alfa en el rango de 0 a 1
    a = alpha / 255
    # Retornar la cadena en formato rgba
    return f"rgba({r}, {g}, {b}, {a})"

def rgba_to_hex(rgba_color):
    # Convertir los valores RGBA en el rango de 0 a 255
    r = int(rgba_color[0] * 255)
    g = int(rgba_color[1] * 255)
    b = int(rgba_color[2] * 255)
    # Convertir el valor de alfa en el rango de 0 a 255
    a = int(rgba_color[3] * 255)
    # Formatear los valores en formato hexadecimal
    hex_color = "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a)
    # Retornar el valor hexadecimal
    return hex_color

def lighten_color(hex_color, factor):
    # Eliminar el carácter '#' si está presente
    hex_color = hex_color.lstrip('#')
    # Convertir los valores hexadecimales en valores decimales
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    # Aplicar el factor de claridad
    r = min(255, r + factor)
    g = min(255, g + factor)
    b = min(255, b + factor)
    # Retornar el color en formato hexadecimal
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def color_bar_adjust(valor_original,min_nuevo,max_nuevo):
    min_original=0
    max_original=1
    valor_reescalado = (valor_original - min_original) * ((max_nuevo - min_nuevo) / (max_original - min_original)) + min_nuevo
    return valor_reescalado


def get_bar_color(factor=15,bar_range=vars['map_color_bar'][1]):
    ini=0
    colors = []
    for i in range(len(map['values'][1])+1):
        if i==len(map['values'][1]):
            ini=map['values'][1][-1]
            end=1
            color = map['color'][1][-1]
        else:
            end=map['values'][1][i]
            color=map['color'][1][i]
        if ini==end:
            break
        step=(end-ini)/map['color_bar'][1][i]
        for index,value in enumerate(np.arange(ini, end, step)):
            if value >= map['values'][1][i]:
                break 
            hex_color = color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            r = max(0, min(255, r - (factor * index)))
            g = max(0, min(255, g - (factor * index)))
            b = max(0, min(255, b - (factor * index)))

            colors.append([ color_bar_adjust(round(value,2),bar_range[0],bar_range[1]), #round(value,2)*map_factor,
                           "#{:02x}{:02x}{:02x}".format(r, g, b)])
        ini=map['values'][1][i]
    
    seen = set()
    colors= [x for x in colors if tuple(x) not in seen and not seen.add(tuple(x))]
    colors[-1][-2] = bar_range[1] #1.0*map_factor
    for target_value in [color_bar_adjust(0.0,bar_range[0],bar_range[1]),
                         color_bar_adjust(0.25,bar_range[0],bar_range[1]),
                         color_bar_adjust(0.50,bar_range[0],bar_range[1]),
                         color_bar_adjust(0.75,bar_range[0],bar_range[1])
                         ]:
        closest_value = min(colors, key=lambda x: abs(x[0] - target_value))
        index_of_closest_value = colors.index(closest_value)
        colors[index_of_closest_value][0] = target_value
    return colors

def obtener_mes_en_espanol(mes_ingles):
    return meses_espanol.get(mes_ingles, mes_ingles)

def get_color_extra_layer(color,min,max):
    if color=='BrBG':
        colormap = linear.BrBG_11.scale(
                    min, max
                    )
    else:
        colormap = linear.YlGn_09.scale(
                    min, max
                    )
    return colormap

layer_index = None
def get_layers():
    global layer_index
    layers = sum(valor == True for valor in vars["var_is_layer"])
    if layers == 1:
        layer_index =[i for i, valor in enumerate(vars["var_is_layer"]) if valor][0]
    return layer_index

def colorbar_to_css(color_scale,index,units):
    css_gradient = "background: linear-gradient(to right, "
    for stop in color_scale:
        css_gradient += f"{stop[1]} {stop[0] * vars['map_factor'][index] }%, "
    css_gradient = css_gradient[:-2] + "); width: 500px; height: 30px; margin-top: 0px; margin-bottom: 0px; margin-left: auto; margin-right: auto;"
    # Agregar valores debajo de la barra de colores
    css_gradient += "text-align: center; margin-top: 10px;"
    css_gradient += "position: relative;"
    css_gradient += "font-size: 14px;"
    css_gradient += "display: flex;"
    css_gradient += "justify-content: space-between;"
    return css_gradient

date_activate =None
calendar_date=None
serie_date=None
state_event=True
def serie_sesion(control='', date_select='',readfrom3=False): 
    global date_activate
    global calendar_date
    global serie_date
    global state_event
    #print('pepe es pepa')
    #print(date_select)
    if control =='calendar' and calendar_date != date_select:
        calendar_date = date_select
        date_activate = date_select
        state_event=False
    elif control =='serie' and serie_date != date_select:
        serie_date = date_select
        date_activate = date_select
        state_event=True
    elif readfrom3: 
        return state_event



