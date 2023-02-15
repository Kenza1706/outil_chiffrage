# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import streamlit as st
import time
import plotly.express as px
import plotly.graph_objects as go
warnings.filterwarnings('ignore')
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from user import *
import streamlit.components.v1 as stc
from streamlit_option_menu import option_menu

st.set_page_config(
        page_title="RATP",
        page_icon="chart_with_upwards_trend",
        layout="wide",
    )

if "qte" not in st.session_state:
        myFile = open("quantite_projet.xlsx", "w+")
        dataframe=pd.DataFrame(columns=['Sous Système', 'N° préstation', 'Désignation','Travaux','Quantité','Taux forfaitaire unitaire JOUR',"Taux forfaitaire unitaire NUIT LONGUE","Fournitures unitaires","CMP"])
        st.session_state.qte = dataframe
        dataframe.to_excel("quantite_projet.xlsx",index=False)
        

if "data" not in st.session_state:
        st.session_state.data = load_data("BPU.xlsx")

if "eq" not in st.session_state:
        st.session_state.eq = load_data("Equipements.xlsx")
if "syst" not in st.session_state:
    st.session_state.syst = load_data("Sous_Systeme.xlsx")
if "soc" not in st.session_state:
        st.session_state.soc = load_data("prestation_equipement.xlsx")

        
    
HTML_BANNER = """
    <div style="background-color:#034980;padding:10px;border-radius:15px">
    <h1 style="color:white;text-align:center;">Outil de chiffrage détaillé RATP </h1>
    <p style="color:white;text-align:center;">Courants faibles et télécom</p>
    </div>
    """        
def main() :   
    stc.html(HTML_BANNER)
    t1, t2 = st.columns((1,1)) 
    t1.image('./RATP1.jpg', width = 300)
    t2.markdown(""" <style> .font {
    font-size:18px ; font-family: 'Cooper Black'; color: #000080;} 
    </style> """, unsafe_allow_html=True)
    t2.markdown('<p class="font">Outil de chiffrage CFA</p>', unsafe_allow_html=True)
    #t2.title("Outil de chiffrage CFA")
    t2.markdown(" TEL:  01 58 78 33 33 " )
    t2.markdown("WEBSITE:  https://www.ratp.fr/ ")
    menu = ['Base des prix unitaires', 'Equipements','Quantités du projet','Estimation des couts',"Association"]
    st.sidebar.image("R.png", use_column_width=True)
    with st.sidebar:
        res = option_menu("MENU", ['BPU', 'EQUIPEMENTS','QUANTITES DU PROJET','ESTIMATION DES COUTS',"ASSOCIATION"],
                         icons=['house', 'list-task', 'kanban', 'bi bi-currency-euro','gear'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#5cb8a7"},
        "icon": {"color": "blue", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#c8dfe3"},
        "nav-link-selected": {"background-color": "#034980"},
              }
        )
    
   
    if res=='BPU':
            st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #95c2a9;} 
    </style> """, unsafe_allow_html=True)
            st.markdown('<p class="font">BASE DES PRIX UNITAIRES</p>', unsafe_allow_html=True)
            f1()
        
    elif res=='EQUIPEMENTS':
                st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #95c2a9;} 
    </style> """, unsafe_allow_html=True)
                st.markdown('<p class="font">EQUIPEMENTS</p>', unsafe_allow_html=True)
                f2()
    elif res=='QUANTITES DU PROJET':
                st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #95c2a9;} 
    </style> """, unsafe_allow_html=True)
                st.markdown('<p class="font">QUANTITES DU PROJET</p>', unsafe_allow_html=True)
                manage_quantite()
        
    elif res=='ESTIMATION DES COUTS':
                st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #95c2a9;} 
    </style> """, unsafe_allow_html=True)
                st.markdown('<p class="font">ESTIMATION DES COUTS</p>', unsafe_allow_html=True)
                estimation_totale()
    elif res=='ASSOCIATION':
                st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #95c2a9;} 
    </style> """, unsafe_allow_html=True)
                st.markdown('<p class="font">PRESTATION - EQUIPEMENT</p>', unsafe_allow_html=True)
                association(st.session_state.data,st.session_state.eq)
    else:
        pass
                            
    
    
if __name__ == '__main__' :
    main()