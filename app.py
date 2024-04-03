import inspect
import textwrap

import streamlit as st
#Extras
import pandas as pd
import numpy as np
#import snowflake.connector
#import streamlit_option_menu
from streamlit_option_menu import option_menu

from dashboards import ST_COMPONENT
from dashboards.map import ST_MAPS_COMPONENTS
from dashboards.gauge import ST_GAUGES_COMPONENTS
import loaddata.dictionary as dic
from loaddata.files import cargar_serie_datos_csv
from loaddata.files import cargar_map_datos_csv
from loaddata.files import cargar_map_datos_layer_csv
from loaddata.files import cargar_map_datos_layer_nc
import os
import base64
from pathlib import Path
#import locale

#locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
import datetime



def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def img_to_html(img_path,size,link_url,text):
    img_html = "<img src='data:image/png;base64,{}' width={}  class='img-fluid' title='{}'>".format(
      img_to_bytes(img_path),size,text
    )
    link_html = f"<div>{text}</div>"
    return f"<a href='{link_url}' target='_blank'>{img_html}</a>"

def banner(img_path,div_class,text):
    img_html = "<div class='{}'> <img src='data:image/png;base64,{}' class='img-fluid' title='{}'> </div>" .format(
      div_class,img_to_bytes(img_path),text
    )
    return img_html


# Define la función para manejar el cambio de selección
def get_place(value):
    dic.place(place=dic.ferrovias[value])

#Barra lateral de control
def main():   
    #Siempre cargar los estilos al principio de la creación de la página
    st.markdown(dic.css, unsafe_allow_html=True)
        
    with st.sidebar:
        #Sección de logos
        st.markdown(
                f"""
                    <div style="display: flex;">
                    <div style="flex: 45%;">
                    {img_to_html(dic.cliente['icon'],100,dic.cliente['url'],dic.cliente['desc'])}
                    </div>
                    <div style="flex: 10%;">
                    </div>
                    <div style="flex: 45%;">
                    {img_to_html(dic.alisios['icon'],75,dic.alisios['url'],dic.alisios['desc'])}
                    </div>
                    </div>
                    """,
        unsafe_allow_html=True
        )

        #st.header("Botoneria")
        st.header(" ")

        #control de combo box de opciones de mapas 
        map_options = (
            list(ST_MAPS_COMPONENTS.keys())
        )
        #control de combo box de opciones de lugares (activos) 
        place_options =(
            dic.activos['name']
        )

        #Combo box de lugraes (activos)
        selected_place = st.selectbox(
            label="Activos",
            options=place_options,  
        )

        #Se activa el lugar y se carga la serie de tiempo 
        dic.place(place=dic.activos['var'][dic.activos['name'].index(selected_place)])
        place_activo=dic.place(readfrom3=True)
        file=os.path.join('data',place_activo,dic.serie['file'])
        df = cargar_serie_datos_csv(file,True)
        #df = cargar_serie_datos_csv(readfrom3=True)
        fechas_dias = df[dic.vars["date_proc"][0]].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").strftime("%Y/%m/%d")).tolist()
        del df
        
        #Combo box de opciones de mapas
        selected_map = st.selectbox(
            label="Opciones de Mapa",
            options=map_options,
        )

        #Calendario:
        #  Primera inicialización (En búsqueda del día actual)
        if dic.fecha_usr(readfrom3=True)=='Initial':
            # Verificación de que "hoy" esté como dato en la serie
            #   Si "Hoy" no está en mi serie de datos uso por defecto el primer día 
            #     en la serie, que normalmente es el día en que se produjo la serie
            if not datetime.date.today().strftime('%Y%m%d') in fechas_dias:
                date=st.date_input('',
                      format="YYYY/MM/DD",
                      value=datetime.datetime.strptime(fechas_dias[0], "%Y/%m/%d"),
                      min_value=datetime.datetime.strptime(fechas_dias[0], "%Y/%m/%d"), 
                      max_value=datetime.datetime.strptime(fechas_dias[-1],"%Y/%m/%d"),
                      )
            #   Si "Hoy" está en la serie entonces lo despliego para darle al usuario como
            #     primera vista el día actual 
            else:
                date=st.date_input('',
                      format="YYYY/MM/DD",
                      min_value=datetime.datetime.strptime(fechas_dias[0], "%Y/%m/%d"), 
                      max_value=datetime.datetime.strptime(fechas_dias[-1],"%Y/%m/%d"),
                      )
        # Al no ser la primera inicializaión entonces se establece una comunicación entre los
        #  evento de doble clic sobre la serie y el calendario
        else:
            #Se garantiza que el formato de fechas de la serie sea compatible con el de calendario
            usr_selction=datetime.datetime.strptime(dic.fecha_usr(readfrom3=True), '%d-%b-%Y').strftime('%Y/%m/%d')
            date=st.date_input('',
                      format="YYYY/MM/DD",
                      value=datetime.datetime.strptime(usr_selction, "%Y/%m/%d"),
                      min_value=datetime.datetime.strptime(fechas_dias[0], "%Y/%m/%d"), 
                      max_value=datetime.datetime.strptime(fechas_dias[-1],"%Y/%m/%d"),
                      )
            del usr_selction
        #Se ubica el archivo de carga
        file_name=dic.vars["file_proc"][1][8:].replace('.nc', '_'+dic.vars["map_source"][1]+'.csv')
        file=os.path.join('data',place_activo,date.strftime('%Y%m%d')+file_name)
        #Se activa semaforo de exclusion de evento para la serie (* importante para controlar los eventos de clic)
        dic.serie_sesion('calendar',date.strftime('%d-%b-%Y'))
        #Se le avisa a los componentes de mapa y gauge qué deben cargar 
        cargar_map_datos_csv(file,True)
        dic.fecha_usr(date.strftime('%d-%b-%Y'))
        #Cargar NC de layer
        file_name=dic.vars["file_proc"][0][8:]
        file=os.path.join('data',place_activo,date.strftime('%Y%m%d')+file_name)
        layer = dic.get_layers()
        if layer is not None:
            var = dic.vars["var_proc"][layer]
            json_file=os.path.join('data',place_activo,dic.vars['file_proc'][layer].replace('.nc','.geojson'))
            cargar_map_datos_layer_csv(file.replace('.nc','.csv'),reload=True,var=var, json_file=json_file)
            cargar_map_datos_layer_nc(file,reload=True,var=var)
            del var 

    #Dsitribución del canvas
    #st.title("Deslaves")
    # Banner superior
    st.markdown(banner(dic.alisios['banner_top'],'banner',dic.alisios['url']), unsafe_allow_html=True)
    #Las Columnnas y sus proporciones
    c3, c1= st.columns([2, 4],gap="large")
    c4, c2= st.columns([2, 4],gap="large")

    #Los container
    with st.container():
        c1.write("") #c1
        c2.write("") #c2

    with st.container():
        c3.write("") #c3
        c4.write("c4") #c4

    #Siempre cargar la serie primero porque me permite controlar el resto de componentes
    with c2:
        dasboardC2, url = (
            ST_COMPONENT['Series: Area & Line']
        )
        dasboardC2()

    with c1:
        dasboardC1, url = (
            ST_COMPONENT[selected_map]
        )
        dasboardC1()

    with c3:
        dasboardC3, url = (
            ST_GAUGES_COMPONENTS['Gauge: Street Lights']
        )
        st.markdown('<br><br>', unsafe_allow_html=True)
        dasboardC3()  

    st.markdown('<br><br>', unsafe_allow_html=True)

    # Banner inferior
    st.markdown(banner(dic.alisios['banner_bottom'],'banner',dic.alisios['url']), unsafe_allow_html=True)

    #sourcelines, _ = inspect.getsourcelines(demo)
    #with st.expander("Source Code"):
    #    st.code(textwrap.dedent("".join(sourcelines[1:])))
    #st.markdown(f"Credit: {url}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Deslaves", page_icon=":chart_with_upwards_trend:",
        layout="wide"
    )
    main()
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<h6>Copyright © 2024,  <a href="'+dic.alisios['url']+'">ALISIOS CORP</a></h6>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="info@alisioscorporation.com">@xchourio  &  @alicios_corp</a></h6>',
            unsafe_allow_html=True,
        )
        
