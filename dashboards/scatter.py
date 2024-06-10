import altair as alt
import streamlit as st
from vega_datasets import data
import pandas as pd
import numpy as np
from loaddata.files import cargar_scatter_bar_data
import loaddata.dictionary as dic
from streamlit_echarts import JsCode

def scatter_bars():

    #Traer los datos en el formato requerido por este componente 
    df=cargar_scatter_bar_data(readfrom3=True)

    #Traer los labels y colores asociados desde el diccionario
    group_1 = [str(name) for name, in_group in zip(dic.scatter_bar["data_set_name"], dic.scatter_bar["in_group_1"]) if in_group]
    color_group_1 = [str(name) for name, in_group in zip(dic.scatter_bar["data_set_color"], dic.scatter_bar["in_group_1"]) if in_group]

    scale = alt.Scale(
        domain=group_1,
        range=color_group_1,
    )
    color = alt.Color(dic.scatter_bar["scatter_vars"][3]+":N", scale=scale)

    # We create two selections:
    # - a brush that is active on the top panel
    # - a multi-click that is active on the bottom panel
    brush = alt.selection_interval(encodings=["x"])
    click = alt.selection_point(encodings=["color"])

    # Top panel is scatter plot of temperature vs time
    points = (
        alt.Chart()
        .mark_point()
        .encode(
            alt.X("monthdate(fecha):T", title="Date"),
            alt.Y(
                dic.scatter_bar["scatter_vars"][1]+":Q",
                title=f"{dic.scatter_bar['scatter_y_title']} ({dic.scatter_bar['scatter_y_units']})",
                scale=alt.Scale(domain=dic.scatter_bar['scatter_y_range']),
            ),
            color=alt.condition(brush, color, alt.value("lightgray")),
            size=alt.Size(dic.scatter_bar["scatter_vars"][2]+":Q", 
                          scale=alt.Scale(bins=[0.01,40, 60, 90, 100]),
                          title=dic.scatter_bar['group_labels_names'][1].split('\n')
                          ),
        )
        .properties(width=1200, height=500)
        .add_params(brush)
        .transform_filter(click)
    )

    # Bottom panel is a bar chart of weather type
    bars = (
        alt.Chart()
        .mark_bar()
        .encode(
            alt.X("sum("+dic.scatter_bar["scatter_vars"][1]+")", title=f"{dic.scatter_bar['bar_x_title']} ({dic.scatter_bar['bar_x_units']})"),
            alt.Y(dic.scatter_bar["scatter_vars"][3]+":N"),
            color=alt.condition(click, color, alt.value("lightgray")),
        )
        .transform_filter(brush)
        .properties(
            width=1200,
            height=300
        )
        .add_params(click)
    )

    chart = alt.vconcat(points, bars, data=df, title="")

    st.altair_chart(chart, theme="streamlit", use_container_width=True)

ST_SCATTERS_COMPONENTS = {
    "Scatters & Bars": (
        scatter_bars,
        "https://echarts.apache.org/examples/",
        #"https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart"
        #"https://altair-viz.github.io/altair-tutorial/notebooks/03-Binning-and-aggregation.html"
    ),
}
