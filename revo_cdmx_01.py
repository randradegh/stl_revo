# Bibliotecas
import pandas as pd
import plotly.express as px
import streamlit as st
import pydeck as pdk
import geopandas as gpd
import numpy as np
from urllib.error import URLError



low_memory=False

"""
### Gráficos y Mapa acerca de la revocación de mandato.
#### El caso de la CDMX.


“Una imagen vale más que mil palabras”. En la actualidad cuando las empresas cuentan 
con una gran cantidad de datos que deben transformar en información relevante.

Así, cada vez es más importante tener la capacidad de examinar la información para comprender 
qué es importante y qué no lo es.

Las imágenes hacen que el análisis sea mucho más fácil y rápido, y ofrecen la posibilidad 
de ver de un vistazo lo que importa. 

Este es solamente un ejercicio de análisis construído con algunas librerías de funciones de Pyton.


#### La revocación 
Es el instrumento de participación solicitado por la ciudadanía para determinar la conclusión anticipada en el desempeño de la persona titular de la Presidencia de la República, a partir de la pérdida de la confianza.

Se llevó a cabo en todo México el 10 de abril de 2022.

En este ejercicio se mostrarán solamente los resultados para la Ciudad de México.
"""

# Datos de shape de alcaldías
#shape = gpd.read_file('/run/media/randrade/ADATAHV100/respaldos/rsync/randrade/capacitacion/python/curso_stl/app_test_01/data/limites_alcaldias_cdmx.geojson')
shape = gpd.read_file('data/limites_alcaldias_cdmx.geojson')
shape.rename(columns = {'nomgeo':'alcaldía'}, inplace = True)
#st.write(shape)
"""
### Algunos datos que usaremos

- Datos de la población de las alcaldías de la CDMX.
"""
# Leemos los datos de población

df_pob = pd.read_csv('data/población_alcaldías_cdmx.csv')

with st.expander("Visualizar/Ocultar Población por alcaldía", expanded=False):
    #### Población de las diversas alcaldías de la Ciudad de México, ordenadas alfabéticamente
    # Datos de población de alcaldías de CDMX
    st.write(df_pob)

# 
# Interamos los datos geográficos, población y votos en un solo dataframe
#

# Join entre población y shape de alcaldías
df_full = pd.merge(shape, df_pob, on='alcaldía')
#st.write(df_full)

# Datos de votaciones en la CDMX
df_actas = pd.read_csv('data/20220411_1845_REVOCACION_MANDATO_2022/20220411_1845_COMPUTOS_RM2022_utf-8.csv', sep=',', skiprows=6)
df_actas_cdmx = df_actas[df_actas.ENTIDAD=='CIUDAD DE MÉXICO'][['ID_ENTIDAD','ID_DISTRITO_FEDERAL','DISTRITO_FEDERAL','QUE_SE_LE_REVOQUE_EL_MANDATO_POR_PÉRDIDA_DE_LA_CONFIANZA','QUE_SIGA_EN_LA_PRESIDENCIA_DE_LA_REPÚBLICA','NULOS','TOTAL_VOTOS_CALCULADOS']]
# """
# Votaciones
# """
#st.write(df_actas_cdmx.tail(70))

# Homogeneizamos los nombres de las alcaldías
df_actas_cdmx.loc[(df_actas_cdmx['DISTRITO_FEDERAL'] == 'ALVARO OBREGON'), 'DISTRITO_FEDERAL'] = 'Álvaro Obregón'
df_actas_cdmx.loc[(df_actas_cdmx['DISTRITO_FEDERAL'] == 'BENITO JUAREZ'), 'DISTRITO_FEDERAL'] = 'Benito Juárez'
df_actas_cdmx.loc[(df_actas_cdmx['DISTRITO_FEDERAL'] == 'COYOACAN'), 'DISTRITO_FEDERAL'] = 'Coyoacán'
df_actas_cdmx.loc[(df_actas_cdmx['DISTRITO_FEDERAL'] == 'CUAUHTEMOC'), 'DISTRITO_FEDERAL'] = 'Cuauhtémoc'
df_actas_cdmx.loc[(df_actas_cdmx['DISTRITO_FEDERAL'] == 'TLAHUAC'), 'DISTRITO_FEDERAL'] = 'Tláhuac'
df_actas_cdmx.loc[(df_actas_cdmx['DISTRITO_FEDERAL'] == 'ALVARO OBREGON'), 'DISTRITO_FEDERAL'] = 'Álvaro Obregón'

# Corregimos nombres del resto de las Alcaldías
df_actas_cdmx['DISTRITO_FEDERAL'] = df_actas_cdmx['DISTRITO_FEDERAL'].str.title()

# Arreglamos a Cuajimalpa
df_actas_cdmx.replace('Cuajimalpa De Morelos','Cuajimalpa de Morelos', inplace=True)

# Renombramos la columna a alcaldía
df_actas_cdmx.rename(columns = {'DISTRITO_FEDERAL':'alcaldía'}, inplace = True)


# Datasets por tipo de voto
df_actas_cdmx_alcaldias_nulos = df_actas_cdmx.groupby(['alcaldía'])['NULOS'].sum().reset_index(name='count_nulos')
df_actas_cdmx_alcaldias_fuera = df_actas_cdmx.groupby(['alcaldía'])['QUE_SE_LE_REVOQUE_EL_MANDATO_POR_PÉRDIDA_DE_LA_CONFIANZA'].sum().reset_index(name='count_fuera')
df_actas_cdmx_alcaldias_siga = df_actas_cdmx.groupby(['alcaldía'])['QUE_SIGA_EN_LA_PRESIDENCIA_DE_LA_REPÚBLICA'].sum().reset_index(name='count_siga')

# Integramos los votos al df general (full)
df_full = pd.merge(df_full, df_actas_cdmx_alcaldias_nulos, on='alcaldía', how='left')
df_full = pd.merge(df_full, df_actas_cdmx_alcaldias_fuera, on='alcaldía', how='left')
df_full = pd.merge(df_full, df_actas_cdmx_alcaldias_siga, on='alcaldía', how='left')

# Agregamos una columna con la relación de votos 'siga' por habitante
df_full['count_siga/habitantes'] = round(df_full['count_siga']*100/df_full['habitantes'],2)

# """
# Votaciones
# """
"""
- Datos Integrados (geográficos, población, votación.

"""
with st.expander("Visualizar/Ocultar Datos integrados", expanded=False):
    st.write(df_full)

#
# Gráfico de barras de 'siga'
#
"""
- Gráfico de barras «QUE SIGA EN LA PRESIDENCIA DE LA REPÚBLICA» con datos absolutos.
"""
with st.expander("Visualizar/Ocultar Gráfico de Barras, datos absolutos", expanded=False):

    fig_a = px.bar(df_full.sort_values(by=['count_siga'], ascending = False), x="alcaldía", y='count_siga',
                title = "Votos de «QUE SIGA EN LA PRESIDENCIA DE LA REPÚBLICA» en la CDMX por Alcaldía.", 
                color="alcaldía", 
                labels={ # Replaces default labels by column name
                    "alcaldía": "Alcaldía",
                    "count_siga": "Votos"
                    },
                width = 900, 
                height = 900
        )
        
    BGCOLOR = "#A9BCF5"
        
    fig_a.update_layout({
        'plot_bgcolor': BGCOLOR,
        'paper_bgcolor': BGCOLOR,
        'font_family':"Cantarell",
        'font_size': 14,
        'font_color' :"#0B2161",
        'title_font_family':"Cantarell",
        'title_font_color':"black",
        'legend_title_font_color':"black"    
    })

    fig_a

"""
- Gráfico de barras «QUE SIGA EN LA PRESIDENCIA DE LA REPÚBLICA» con datos relativos.
"""
with st.expander("Visualizar/Ocultar Gráfico de Barras, datos relativos", expanded=False):

    fig_b = px.bar(df_full.sort_values(by=['count_siga/habitantes'], ascending = False), x="alcaldía", y='count_siga/habitantes',
                title = "Porcentaje de Habitantes que votaron <br>«QUE SIGA EN LA PRESIDENCIA DE LA REPÚBLICA»<br>en la CDMX por Alcaldía.", 
                color="alcaldía", 
                labels={ # Replaces default labels by column name
                    "alcaldía": "Alcaldía",
                    "count_siga/habitantes": "Votos*100/Habitantes"
                    },
                width = 900, 
                height = 900
        )
        
    BGCOLOR = "#A9BCF5"
        
    fig_b.update_layout({
        'plot_bgcolor': BGCOLOR,
        'paper_bgcolor': BGCOLOR,
        'font_family':"Cantarell",
        'font_size': 14,
        'font_color' :"#0B2161",
        'title_font_family':"Cantarell",
        'title_font_color':"black",
        'legend_title_font_color':"black"    
    })

    fig_b

#
# Mapa
#

"""
- Mapa interactivo. Se pueden seleccionar la visualización de los votos absolutos y relativos.

Pase el puntero del mouse sobre las diversas alcaldías para mostrar los resultados de la revocación.

Haga click en las pequeñas flechas en el extremo superior derecho del mapa para visualizarlo en pantalla completa.

---

Herramientas: Fedora Linux, Python, Pandas, pydeck, Mapbox, OpenStreetMap, Streamlit.

---

¿Comentarios? randradedev@gmail.com

Roberto Andrade F. (c)
"""

# st.write(salida)
with st.sidebar:

    modo = st.selectbox(
        'Seleccione el tipo de valor de los votos',
        ('Absoluto', 'Relativo'))

    if (modo == 'Absoluto'):
        fill_color = ['count_siga/2000', 0, 0, 'count_siga/1000']
    else:
        fill_color = ['(count_siga*50)/habitantes', 5, 226, 'count_siga*1000/habitantes']

    #st.write('You selected:', modo)

try:
    ALL_LAYERS = {
        "Álvaro Obregón": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Álvaro Obregón'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Azcapotzalco": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Azcapotzalco'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Benito Juárez": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Benito Juárez'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Coyoacán": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Coyoacán'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Cuajimalpa de Morelos": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Cuajimalpa de Morelos'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Cuauhtémoc": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Cuauhtémoc'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Gustavo A. Madero": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Gustavo A. Madero'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Miguel Hidalgo": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Miguel Hidalgo'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Iztacalco": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Iztacalco'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            #color = lambda : [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            get_fill_color=fill_color,
            #get_fill_color=[200,  200, 200, 40],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Iztapalapa": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Iztapalapa'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            #get_fill_color=fill_color,
            get_fill_color=fill_color,
            #get_fill_color=[200,  200, 200, 40],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "La Magdalena Contreras": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='La Magdalena Contreras'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Milpa Alta": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Milpa Alta'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            #color = lambda : [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            get_fill_color=fill_color,
            #get_fill_color=[200,  200, 200, 40],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Tláhuac": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Tláhuac'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Tlalpan": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Tlalpan'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Venustiano Carranza": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Venustiano Carranza'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            get_fill_color=fill_color,
            #get_fill_color=[200,  'random.randint(0, 255),random.randint(0, 255), random.randint(0, 255)', 'random.randint(0, 255)'],
            #get_fill_color=[33, 97, 140, 150],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
        "Xochimilco": pdk.Layer(
            "GeoJsonLayer",
            data=df_full[df_full.alcaldía=='Xochimilco'],
            opacity=0.8,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            get_elevation=0,
            #color = lambda : [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            get_fill_color=fill_color,
            #get_fill_color=[200,  200, 200, 40],
            pointType= 'circle',
            lineWidthScale= 20,
            lineWidthMinPixels= 50,
            get_line_color=[164, 64, 0],
            getPointRadius= 100,
            getLineWidth= 20,    
        ),
    }

    my_tooltip={
    "html": 
    "<b><p style='color:#AEB6BF;font-size:16px;'>Votos en la CDMX por Revocación de Mandato</p></b>"
    "<b><p style='color:#A9CCE3;font-size:16px;'>{alcaldía}</p></b>"
    "«Que siga al mando»:</b> {count_siga}"
    "<br><b>% de habitantes por «Que siga al mando»:</b> {count_siga/habitantes}"
    "<br><b>«Que se le revoque el mandato»:</b> {count_fuera}"
    "<br><b>«Nulos»:</b> {count_nulos}",    
    "style": {"color": "#FAFAFA", 
            "background-color":"#34495E",
            "z-index":2,}
}
    selected_layers = [
        layer for layer_name, layer in ALL_LAYERS.items()
        if st.sidebar.checkbox(layer_name, True)]
    if selected_layers:
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={"latitude": 19.3266,
                                "longitude": -99.1490, 
                                "zoom": 9.2, 
                                "pitch": 0,                                
                                },
            tooltip=my_tooltip,
            layers=selected_layers,
            width=1200,
            height=900
        ))
    else:
        st.error("Please choose at least one layer above.")


except URLError as e:
    st.error("""
        **This demo requires internet access.**

        Connection error: %s
    """ % e.reason)
