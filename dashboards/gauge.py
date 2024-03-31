import json
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
from loaddata.files import cargar_map_datos_csv
import streamlit as st
import loaddata.dictionary as dic


def render_gauge_streetlights():
    df = cargar_map_datos_csv(readfrom3=True)
    if isinstance(df, str):
        st.write('<div style="font-size: 24px; background-color: yellow; padding: 10px;"><span style="color:red;"><b>'+df+'para crear reloj de alertas</b></span></div>', unsafe_allow_html=True)
        return

    #En caso de que valor necesite ser ajustado 
    valor=round(max(df[dic.vars['name_proc'][1]])*dic.vars['map_factor'][1],1)
    gauge_formater, gauge_color, values_formater = dic.get_gauge_control()
    formatter = JsCode(values_formater).js_code
           
    option = {
        "series": [
            {
                "type": 'gauge',
                "startAngle": 220,
                "endAngle": -40,
                "min": 0,
                "max": 100,
                "splitNumber": 8,
                "radius": '90%', 
                "center": ['50%', '75%'], 
                "axisLine": {
                "lineStyle": {
                    "width":10,
                    "color": gauge_color
                }
                },
                "pointer": {
                    "icon": 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',#'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
                    "length": '12%',
                    "width": 20,
                    "offsetCenter": [0, '-60%'],
                    "itemStyle": {
                        "color": 'auto'
                    }
                },
                "axisTick": {
                    "length": 12,
                    "lineStyle": {
                        "color": 'auto',
                        "width": 2
                    }
                },
                "splitLine": {
                    "length": 25,
                    "lineStyle": {
                        "color": 'auto',
                        "width": 5
                    }
                },
                "axisLabel": {
                    "show": False,
                #    "color": 'auto',
                #    "fontSize": 20,
                #    "distance": -80,
                #    #"formatter": formatter
                }, 
                
                "title": {
                    "offsetCenter": [0, '70%'],
                    "fontSize": 20,
                    "color": '#fff',
                    "fontWeight": 'bolder',
                    "fontStyle": 'italic',
                },
                "detail": {   
                    "fontSize": dic.gauge['text_size'],
                    "offsetCenter": [0, str(dic.gauge['text_pos'])+'%'],
                    "valueAnimation": True,
                    "formatter": formatter,
                    "color": 'auto',
                    "showZero": "true"
                },
                "data": [
                    {
                        "value":valor,
                    }
                ]
            }
        ], 
      }
    st_echarts(option, height="500px")
    #st_echarts(option , height="450%",width="100%")


ST_GAUGES_COMPONENTS = {
    "Gauge: Street Lights": (
        render_gauge_streetlights,
        "https://medium.com/datasciencearth/map-visualization-with-folium-d1403771717",
    ),
}
