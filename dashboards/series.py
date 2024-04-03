import streamlit as st
from streamlit_echarts import st_echarts
import datetime
import pandas as pd
import math
import numpy as np
from streamlit_echarts import JsCode
from loaddata.files import cargar_map_datos_csv
from loaddata.files import cargar_serie_datos_csv
import loaddata.dictionary as dic
import locale
import os
import streamlit.components.v1 as components

#Setear la serie a español
#locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
#control de evento de la serie
in_control=False
# Obtener la fecha actual
fecha_actual = datetime.date.today()


def render_series_arealine():
    #Debe usarse in_control global para poder capturar los eventos de forma correcta
    global in_control
    #Leer datos de la serie
    df = cargar_serie_datos_csv(readfrom3=True)
    indice0 = dic.vars["label"].index(dic.serie["label"][0])
    indice1 = dic.vars["label"].index(dic.serie["label"][1])
    
    # Obtener el tema actual (claro u oscuro)
    tema_actual = st.get_option("theme.base")
    # Definir el color del texto según el tema
    color_texto = "#333" if tema_actual == "light" else "#ddd"

    #Fechas
    fechas_dias = df[dic.vars["date_proc"][0]].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").strftime("%d-%b-%Y").title()).tolist()

    # Datos de deslaves Serie 1
    datos_serie1_max = df[dic.vars["max_proc"][indice0]+'_'+dic.serie["source"][0]].to_numpy()
    datos_serie1_max =[0 if np.isnan(valor) else valor for valor in datos_serie1_max]
    datos_serie1_max = [int(round(valor)) for valor in datos_serie1_max]
    datos_serie1_min = df[dic.vars["min_proc"][indice0]+'_'+dic.serie["source"][0]].to_numpy()
    datos_serie1_min =[0 if np.isnan(valor) else valor for valor in datos_serie1_min]
    datos_serie1_min = [int(round(valor)) for valor in datos_serie1_min]

    # Datos de deslaves Serie 2 
    datos_serie2_max = df[dic.vars["max_proc"][indice1]+'_'+dic.serie["source"][1]].to_numpy()
    datos_serie2_max = [int(round(valor)) if not math.isnan(valor) else valor for valor in datos_serie2_max] # [int(round(valor)) for valor in datos_serie2_max]
    datos_serie2_max =[0 if np.isnan(valor) else valor for valor in datos_serie2_max]
    datos_serie2_min = df[dic.vars["min_proc"][indice1]+'_'+dic.serie["source"][1]].to_numpy()
    datos_serie2_min = [int(round(valor)) if not math.isnan(valor) else valor for valor in datos_serie2_min]  #[int(round(valor)) for valor in datos_serie2_min]
    datos_serie2_min =[0 if np.isnan(valor) else valor for valor in datos_serie2_min]
    

    #Crear los globos de alerta en la serie para valores que estén ubicados en alto riezgo 
    data_markpoint = []
    for indice, valor in enumerate(datos_serie2_max):
        if valor >= int(dic.gauge['values'][-3]*100)  and valor <= int( (dic.gauge['values'][-2])*100) :
            data_markpoint.append({"coord": [indice, valor],"value":str(valor)+'%',"itemStyle": {"color": dic.gauge['color'][-2]}})
        elif valor >= int(dic.gauge['values'][-2]*100) and valor <= int(dic.gauge['values'][-1]*100):
            data_markpoint.append({"coord": [indice, valor], "value":str(valor)+'%',"itemStyle": {"color": dic.gauge['color'][-1]}})


    start_index = max(0, len(fechas_dias) - 12)
    end_index = len(fechas_dias)
    #Se crean los labels del tooltip, se debe hacer en Javascrip
    formater=JsCode(
        "function (params) {"
            +  "const date = ['"+"','".join(map(str, fechas_dias))+"'];"
            +  "const serie1_min = ["+",".join(map(str, datos_serie1_min))+"];"
            +  "const serie2_min = ["+",".join(map(str, datos_serie2_min))+"];"
            +  "const posicion = date.indexOf(params[0].name);"
            +  "var tooltipHtml = params[0].name + '<br/>';"
            +  "params.forEach(function(param) {"
            +  "  if (param.seriesName === '"+dic.serie['label'][0]+"') {"
            +  "   tooltipHtml += '<span style=\"color:#0080FE; font-size: 16px\">&#x25cf;</span> ' + param.seriesName + ' max: <strong>' + param.value + ' mm</strong> <br/>';"
            +  "   tooltipHtml += '<span>&nbsp;&nbsp;&nbsp;</span> ' + param.seriesName + ' min: <strong>' + serie1_min[posicion] + ' mm</strong> <br/>';"
            +  "  } else if (param.seriesName === '"+dic.serie['label'][1]+"') {"
            +  "   tooltipHtml += '<span style=\"color:#00D100;font-size: 16px\">&#x25cf;</span> ' + param.seriesName + ' max: <strong>' + param.value + '%</strong> <br/>';"
            +  "   tooltipHtml += '<span>&nbsp;&nbsp;&nbsp;</span> ' + param.seriesName + ' min: <strong>' + serie2_min[posicion] + '%</strong> <br/>';"
            +  "  }"
            +  "});"
            +  "return tooltipHtml;"
            +"}"
    ).js_code

    option = {'calculable': True,
            'legend': {'data': ['Precipitación', 'Probabilidad_Deslaves'], 'textStyle': {'color': color_texto}, 'top': 'top', 'left': 'center'},
            'xAxis': [{'data': fechas_dias,
                        'type': 'category',
                        'axisLabel': {'color': color_texto}, 
                        'axisLine': {'lineStyle': {'color': color_texto}},
                    },
                    ],

            "yAxis":
                    [
                    {"type": "value", "name": dic.serie['Y_axis_label'][0],"nameLocation": 'middle',"nameGap": 55,
                        'axisLabel': {'formatter':'{value} '+dic.serie['units'][0],'color': dic.serie['color'][0]}, 
                        'axisLine': {'lineStyle': {'color': color_texto}},
                        'min': dic.serie['interval'][0][0], 'max': dic.serie['interval'][0][1], 'interval': dic.serie['interval'][0][1]/10
                        
                    },
                    {"type": "value", "name": dic.serie['Y_axis_label'][1],"nameLocation": 'middle',"nameGap": 45,
                        'axisLabel': {'formatter':'{value}'+dic.serie['units'][1],'color': dic.serie['color'][1]}, 
                        'axisLine': {'lineStyle': {'color': color_texto}},
                        'min': dic.serie['interval'][1][0], 'max': dic.serie['interval'][1][1], 'interval': dic.serie['interval'][1][1]/10
                    },
                    ],
            'series': [
                    {'data':datos_serie1_max,
                            'name': dic.serie['label'][0],
                            "yAxisIndex": 0,
                            'color': dic.serie['color'][0],
                            'type': 'line' if dic.serie['type'][0] == 'area' else dic.serie['type'][0],
                            'areaStyle': {} if dic.serie['type'][0] == 'area' else None,
                        },
                    {'data': datos_serie2_max,
                            'markPoint': {'data': data_markpoint},
                            'name': dic.serie['label'][1],
                            'color': dic.serie['color'][1],
                            "yAxisIndex": 1,
                            'type': 'line' if dic.serie['type'][1] == 'area' else dic.serie['type'][1],
                            'areaStyle': {} if dic.serie['type'][1] == 'area' else None,

                        },
                        ],
            'toolbox': {'feature': {'dataView': {'readOnly': False, 'show': True},
                         'magicType': {'show': True, 'type': ['line', 'bar']},
                         'restore': {'show': True},
                         'saveAsImage': {'show': True}},
                        'show': True},
            'tooltip': {'trigger': 'axis',
                         "formatter":formater
             },
            "dataZoom": [{
                            "type": "slider",
                            #"xAxisIndex": 0,
                            "start": start_index / len(fechas_dias) * 100,  # Comienza en el índice de los últimos 12 datos
                            "end": end_index / len(fechas_dias) * 100,      # Termina en el último dato
                            "minSpan": 7,   # El usuario puede seleccionar un mínimo de 12 datos
                            "bottom": 10,
                            "textStyle": {"color": color_texto}
                        },
                        {
                            "type": "inside",
                            #"xAxisIndex": 0,
                            "start": start_index / len(fechas_dias) * 100,  # Comienza en el índice de los últimos 12 datos
                            "end": end_index / len(fechas_dias) * 100,      # Termina en el último dato
                            "minSpan": 7,
                            "textStyle": {"color": color_texto}
                        },
                     
                        ],  # Agregar dataZoom

            'backgroundColor': "#FFFFFF" if tema_actual == "light" else "#1E1E1E",  # Fondo blanco para el tema claro y negro para el oscuro
    }


    events = {
            "click":"function(params) { return [params.type, params.name, params.value] }"
        }
    bar_events = st_echarts(option, events=events, key="serie")
    state_event=dic.serie_sesion(readfrom3=True)
    
    #Manejar los eventos de la serie de tiempo
    #Se debe jugar con dos eventos extra debido a la falta de soporte directo
    # de Strimlit para limpiar la variable javascript utilizada por el echarts
    if not bar_events == None:
        if state_event and bar_events[0]=='click':     
            place_activo=dic.place(readfrom3=True)
            file_name=dic.vars["file_proc"][1][8:].replace('.nc', '_'+dic.vars["map_source"][1]+'.csv')
            file=os.path.join('data',place_activo,datetime.datetime.strptime(bar_events[1], '%d-%b-%Y').strftime('%Y%m%d')+file_name)
            cargar_map_datos_csv(file,True)
            dic.fecha_usr(bar_events[1])
        dic.serie_sesion('serie',bar_events[1])
 



ST_SERIES_COMPONENTS = {
    "Series: Area & Line": (
        render_series_arealine,
        "https://discuss.streamlit.io/t/streamlit-echarts/3655/57?page=3",
    ),
}
