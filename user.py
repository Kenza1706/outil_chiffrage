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
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import plotly.figure_factory as ff
import plotly.express as px
import streamlit.components.v1 as components
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


if "qte" not in st.session_state:
        myFile = open("quantite_projet.xlsx", "w+")
        dataframe=pd.DataFrame(columns=['Sous Système', 'N° préstation', 'Désignation','Travaux','Quantité','Taux forfaitaire unitaire JOUR',"Taux forfaitaire unitaire NUIT LONGUE","Fournitures unitaires","CMP"])
        st.session_state.qte = dataframe
        dataframe.to_excel("quantite_projet.xlsx",index=False)



#@st.experimental_memo
def load_data(text):
    df = pd.read_excel(text)
    return df

#@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode("utf-8")


def show_grid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True)
    grid_table = AgGrid(
        df,
        height = "800px", 
        width='100%',
        gridOptions=gb.build(),
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
    )
    return grid_table


def update(df):
    grid_table=show_grid(df)
    grid_table_df = pd.DataFrame(grid_table['data'])
    return grid_table_df
    
   




def f2() :   
    data=st.session_state.eq
    res = st.sidebar.radio("Choisir : ", ('Consulter 🔎', 'Rechercher 🕵️‍♂️','Ajouter 👈','Modifier ✍🏻','Supprimer ❌'))
    if (res=='Consulter 🔎'):
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('disabled', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()
        grid_response = AgGrid(
            data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            theme='alpine', #Add theme color to the table
            enable_enterprise_modules=True,
            height = "800px", 
            width='100%',
            reload_data=False
        )

        data = grid_response['data']
        selected = grid_response['selected_rows'] 
        df = pd.DataFrame(selected)
    elif (res=='Ajouter 👈'):
               with st.container():
                   data=user_add_eq(data)
                   st.session_state.eq = data
                   (st.session_state.eq).to_excel('Equipements.xlsx',index=False)
             
    elif (res=='Rechercher 🕵️‍♂️'):
           st.dataframe(filter_dataframe(data))  
    elif (res=='Modifier ✍🏻'):
             data=update(data)
             st.session_state.eq = data 
             (st.session_state.eq).to_excel('Equipements.xlsx',index=False)
    else :
            data=user_supp_eq(data)
            st.session_state.eq = data 
            (st.session_state.eq).to_excel('Equipements.xlsx',index=False)
        
        
        

def table_interactive(text):
        data = load_data(text)
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()
        grid_response = AgGrid(
            data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            theme='alpine', #Add theme color to the table
            enable_enterprise_modules=True,
            height = "800px", 
            width='100%',
            reload_data=False
        )

        data = grid_response['data']
        selected = grid_response['selected_rows'] 
        df = pd.DataFrame(selected)
        return df
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.checkbox("Add filters")
    if not modify:
        return df
    df = df.copy()
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df
        
        
        
        
        
def f1() :   
    data=st.session_state.data
    res = st.sidebar.radio("Choisir : ", ('Consulter 🔎', 'Rechercher 🕵️‍♂️','Ajouter 👈','Modifier ✍🏻','Supprimer ❌'))
    if (res=='Consulter 🔎'):
        tab1, tab2,tab3= st.tabs(["Préstations", "Consultation des Sous Systèmes","Mise a jour des Sous Systèmes"])
        dat=st.session_state.syst
        with tab1:
                gb = GridOptionsBuilder.from_dataframe(data)
                gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
                gb.configure_side_bar() #Add a sidebar
                gb.configure_selection('disabled', use_checkbox=True, groupSelectsChildren="Group checkbox select children") 
                gridOptions = gb.build()
                grid_response = AgGrid(
                    data,
                    gridOptions=gridOptions,
                    data_return_mode='AS_INPUT', 
                    update_mode='MODEL_CHANGED', 
                    fit_columns_on_grid_load=False,
                    enable_enterprise_modules=True,
                    theme='alpine',
                    height = "800px", 
                    width='100%',
                    reload_data=False
                )

                data = grid_response['data']
                selected = grid_response['selected_rows'] 
                df = pd.DataFrame(selected)
                df_xlsx = to_excell(data)
                st.download_button(label='📥 Télécharger',
                                        data=df_xlsx ,
                                        file_name= 'BPU.xlsx')
        with tab2:
                gb = GridOptionsBuilder.from_dataframe(dat)
                gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
                gb.configure_side_bar() #Add a sidebar
                gb.configure_selection('disabled', use_checkbox=True, groupSelectsChildren="Group checkbox select children") 
                gridOptions = gb.build()
                grid_response = AgGrid(
                    dat,
                    gridOptions=gridOptions,
                    data_return_mode='AS_INPUT', 
                    update_mode='MODEL_CHANGED', 
                    fit_columns_on_grid_load=False,
                    enable_enterprise_modules=True,
                    theme='alpine',
                    height = "800px", 
                    width='100%',
                    reload_data=False
                )

                data = grid_response['data']
                selected = grid_response['selected_rows'] 
                df = pd.DataFrame(selected)
                df_xlsx = to_excell(dat)
                st.download_button(label='📥 Télécharger',
                                        data=df_xlsx ,
                                        file_name= 'SOUS_SYSTEMES.xlsx')
        with tab3: 
                dat = dat.astype(str)
                res = st.radio("Choisir : ", ('Rechercher 🕵️‍♂️','Ajouter 👈'))
                if res=='Rechercher 🕵️‍♂️': 
                    st.dataframe(filter_dataframe(dat))
                else:
                    d=dict()
                    num=st.text_input("N°Sous Système :")
                    des=st.text_input("Désignation :")
                    d["N°Sous Système"]=str(num)
                    d["Désignation"]=des
                    df_dictionary = pd.DataFrame([d])
                    if st.button("Ajouter"):
                        s=st.session_state.syst
                        s = s.astype(str)
                        if str(num) not in (s["N°Sous Système"].unique()):
                                dat = pd.concat([dat, df_dictionary], ignore_index=True)
                                st.session_state.syst = dat
                                dat.to_excel("Sous_Systeme.xlsx",index=False)
                                st.success('Ajout éffectué avec succés!!!')
                        else:
                            st.error('Numero de sous système déja existant!!!')
                    
    elif (res=='Ajouter 👈'):
                   data=user_add_pres(data)
                   st.session_state.data = data
                   (st.session_state.data).to_excel('BPU.xlsx',index=False)
             
    elif (res=='Rechercher 🕵️‍♂️'):
           st.dataframe(filter_dataframe(data))  
    elif (res=='Modifier ✍🏻'):
             data=update(data)
             st.session_state.data = data 
             (st.session_state.data).to_excel('BPU.xlsx',index=False)
    else :
            data=user_supp_pres(data)
            st.session_state.data = data 
            (st.session_state.data).to_excel('BPU.xlsx',index=False)
    
            
def user_add_pres(data):
    with st.container():
        st.subheader("Ajouter une préstation")
        col1,col2 = st.columns(2)
        dd = st.session_state.syst
        d=dict()
        with col1:
                sys=st.selectbox('Sous système:',data["Sous Système"].unique())
                des=dd[dd["N°Sous Système"]==sys]
                des=(des["Désignation"].unique())[0]
                st.write('Sous système concerné :' ,des)
                liste=((data[data['Sous Système']==sys])["Type préstation"]).unique()
                prestation=st.selectbox('Type de la préstation:',liste)
                num_prix= st.text_input("N°préstation :")
                designation= st.text_input("Désignation :")
                unite=st.text_input("Unité:",'u')
                
        with col2:
                fourniture= st.number_input('Fournitures(€):')
                mo= st.number_input("Temps de main d'oeuvre (heures):")
                mo_jour_h= st.number_input("Prix unitaire MO JOUR |Taux horaire (€):")
                mo_nuit_ch= st.number_input("Prix unitaire MO NUIT COURTE |Taux horaire (€):")
                mo_nuit_lh= st.number_input("Prix unitaire MO NUIT LONGUE |Taux horaire (€):")
        d["N° de prix "]=num_prix
        d["Désignation"]=designation
        d["Unité"]=unite
        d["Sous Système"]=sys
        d["Type préstation"]=prestation
        d['Fournitures \nP.U en euros']=fourniture
        d["Temps Main d'œuvre en heures"]=mo
        d['Prix unitaire MO JOUR (hors fourniture)|Taux horaire']=mo_jour_h
        v1=float(mo)*float(mo_jour_h)
        d['Prix unitaire MO JOUR (hors fourniture)|Taux forfaitaire']=float(mo)*float(mo_jour_h)
        d['Prix unitaire MO NUIT COURTE (hors fourniture)|Taux horaire']=mo_nuit_ch
        v2=float(mo)*float(mo_nuit_ch)
        d['Prix unitaire MO NUIT COURTE (hors fourniture)|Taux forfaitaire']=float(mo)*float(mo_nuit_ch)
        d['Prix unitaire MO NUIT LONGUE (hors fourniture)|Taux horaire']=mo_nuit_lh
        v3=float(mo)*float(mo_nuit_lh)
        d['Prix unitaire MO NUIT LONGUE (hors fourniture)|Taux forfaitaire']=float(mo)*float(mo_nuit_lh)
        if st.button('Ajouter ✅'):
            t=data.astype(str)
            if str(num_prix) not in (t["N° de prix "].unique()):
                st.success('Ajout éffectué avec succés!!!')
                df_dictionary = pd.DataFrame([d])
                data = pd.concat([data, df_dictionary], ignore_index=True)
                data.reset_index(drop=True, inplace=True)
                st.write(data)
                return data  
            else:
                st.error('Numéro de préstation déja éxistant!!!')
                return data
        else:
            return data
def user_add_eq(data):
        st.subheader("Ajouter un équipement")
        col1,col2 = st.columns(2)
        d=dict()
        with col1:
                ref=st.text_input("Référence Article:")
                d["Référence Article"]=ref
                designation= st.text_input("Libellé Article :")
                d["Libellé Article"]=designation
                catalogue= st.text_input("Catalogue :")
                d["Catalogue"]=catalogue
                famille= st.text_input("Famille :")
                d["Famille"]=famille
                ssfamille= st.text_input("Sous Famille :")
                d["Sous-Famille"]=ssfamille
                usage= st.text_input("Usage :")
                d["Usage"]=usage
                delai= st.number_input("Délai d'approvisionnement (jours):")
                d["Délai d'appro(jours)"]=delai
                cmp= st.number_input("CMP (€):")
                d["CMP (€)"]=cmp
        with col2:
                
                fournisseur= st.text_input("Fournisseur :")
                d["Fournisseur"]=fournisseur
                marche= st.text_input("N° de marché :")
                d["N° de marché"]=marche
                fabricant= st.text_input("Fabricant :")
                d["Fabricant"]=fabricant
                comment= st.text_area("Commentaire achat:")
                d["libelleAchat"]=comment
                dd =st.session_state.syst
                sys=st.selectbox('Sous système:',dd['N°Sous Système'].unique())
                des=dd[dd["N°Sous Système"]==sys]
                des=(des["Désignation"].unique())[0]
                st.write('Sous système concerné :' ,des)
                d["Sous Système"]=sys
        if st.button('Ajouter ✅'):
            res =data.astype(str)
            if str(ref) not in res["Référence Article"].unique():
                st.success('Ajout éffectué avec succés!!!')
                df_dictionary = pd.DataFrame([d])
                data = pd.concat([data, df_dictionary], ignore_index=True)
                data.reset_index(drop=True, inplace=True)
                st.write(data)
                return data  
            else:
                st.error('Référence article déja éxistante!!!')
                return data
        else:
            return data

        
def user_supp_pres(data):
        st.subheader("Supprimer des préstations")
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()
        grid_response = AgGrid(
            data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=True,
            theme='alpine', #Add theme color to the table
            enable_enterprise_modules=True,
            height = "800px", 
            width='100%',
            reload_data=False
        )

        data = grid_response['data']
        selected = grid_response['selected_rows'] 
        df_selected = pd.DataFrame(selected)
        if st.button('Supprimer ❌'):
                df_selected=df_selected.set_index("N° de prix ")
                for elem in list(df_selected.index):
                        data=data[data["N° de prix "]!=elem]
                st.success('Suppression éffectuée avec succés!!!')
        else:
            pass
            
        return data
def user_supp_eq(data):
        st.subheader("Supprimer des équipements")
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()
        grid_response = AgGrid(
            data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            theme='alpine', #Add theme color to the table
            enable_enterprise_modules=True,
            height = "800px", 
            width='100%',
            reload_data=False
        )

        data = grid_response['data']
        selected = grid_response['selected_rows'] 
        df_selected = pd.DataFrame(selected)
        if st.button('Supprimer ❌'):
                df_selected=df_selected.set_index("Référence Article")
                for elem in list(df_selected.index):
                        data=data[data["Référence Article"]!=elem]
                st.success('Suppression éffectuée avec succés!!!')
        else:
            pass
            
        return data
def user_supp_qte():
        data=st.session_state.qte
        st.subheader("Supprimer des quantités")
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
        gridOptions = gb.build()
        grid_response = AgGrid(
                data,
                gridOptions=gridOptions,
                data_return_mode='AS_INPUT', 
                update_mode='MODEL_CHANGED', 
                fit_columns_on_grid_load=True,
                theme='alpine',
                enable_enterprise_modules=True,
                height = "800px", 
                width='100%',
                reload_data=False
                )
        data= grid_response['data']
        selected = grid_response['selected_rows']        
        df_selected = pd.DataFrame(selected)
        if st.button('Supprimer ❌'):
                df_selected=df_selected.set_index("N° préstation")
                for elem in list(df_selected.index):
                        data=data[data["N° préstation"]!=elem]
                st.success('Suppression éffectuée avec succés!!!')
                return data
        else:
            return data
def association():
                data=st.session_state.data
                eq=st.session_state.eq
                res = st.sidebar.radio("Choisir : ", ('Consulter 🔎', 'Rechercher 🕵️‍♂️','Ajouter 👈','Supprimer ❌'))
                if res=='Consulter 🔎':
                    mdata=st.session_state.soc
                    if (mdata.shape[0] > 0):
                            d1=st.session_state.data
                            d2=st.session_state.eq
                            ll=[]
                            for i in range(len(mdata)):
                                    d=dict()
                                    d["N° prix"]=mdata["N° de prix "][i]
                                    d["Préstation"]=(((d1[d1["N° de prix "]==d["N° prix"]])["Désignation"]).unique())[0]
                                    d["Référence Article"]=mdata["Référence Article"][i]
                                    d["Equipement"]=(((d2[d2["Référence Article"]==d["Référence Article"]])["Libellé Article"]).unique())[0]
                                    ll.append(d)
                            ll=pd.DataFrame(ll)
                            st.dataframe(filter_dataframe(ll)) 
                            df_xlsx = to_excell(ll)
                            st.download_button(label='📥 Télécharger',
                                        data=df_xlsx ,
                                        file_name= 'PRESTATION-EQUIPEMENT.xlsx')
                            agree = st.checkbox('Filtrage par préstation',key='teest')
                            if agree:
                                prestation=st.selectbox('Préstation:',ll["Préstation"].unique())
                                if st.button("OK"):
                                    st.dataframe(ll[ll["Préstation"]==prestation])
                            
                    else:
                        st.warning('Aucune association trouvée!!!')
                        
                            
                        
                         
                elif res=='Rechercher 🕵️‍♂️':
                    
                    mdata=st.session_state.soc
                    if (mdata.shape[0] > 0):
                        st.dataframe(filter_dataframe(st.session_state.soc))
                    else:
                        st.warning('Aucune association trouvée!!!')
                elif res =='Ajouter 👈':
                        dd = st.session_state.syst
                        sys=st.selectbox('Sous systeme:',data["Sous Système"].unique())
                        des=dd[dd["N°Sous Système"]==sys]
                        des=(des["Désignation"].unique())[0]
                        st.write('Sous système concerné :' ,des)
                        liste=((data[data['Sous Système']==sys])["Désignation"]).unique()
                        prestation=st.selectbox('Prestation:',liste)
                        ll=(data[data['Désignation']==prestation])
                        ll=(ll["N° de prix "].unique())[0]
                        eqq=eq[eq['Sous Système']==sys]
                        gb = GridOptionsBuilder.from_dataframe(eqq)
                        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
                        gb.configure_side_bar() #Add a sidebar
                        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") 
                        gridOptions = gb.build()
                        grid_response = AgGrid(
                        eqq,
                        gridOptions=gridOptions,
                        data_return_mode='AS_INPUT', 
                        update_mode='MODEL_CHANGED', 
                        fit_columns_on_grid_load=False,
                        theme='alpine', #Add theme color to the table
                        enable_enterprise_modules=True,
                        height = "800px", 
                        width='100%',
                        reload_data=False
                )

                        eqq = grid_response['data']
                        selected = grid_response['selected_rows'] 
                        df = pd.DataFrame(selected)
                        dd = pd.read_excel("prestation_equipement.xlsx")
                        if st.button("Associer ✅"):
                            l1=[]
                            l2=[]
                            if (df.shape[0]) >0 :
                                    for elem in df['Référence Article'] :
                                        if (ll,elem) not in zip(dd["N° de prix "],dd['Référence Article']):
                                          l1.append(elem)
                                          l2.append(ll)
                                        else:
                                                st.warning('Association '+str(ll)+ " - "+str(elem)+ " déja éxistante!!!")
                                    zipped = list(zip(l2, l1))
                                    df = pd.DataFrame(zipped, columns=["N° de prix ", 'Référence Article'])
                                    dd = pd.concat([dd, df], ignore_index=True)
                                    dd.to_excel('prestation_equipement.xlsx',index=False)
                                    st.success('Association éffectuée avec succés!!!')
                                    st.write(dd)
                                    st.session_state.soc=dd
                                    df_xlsx = to_excell(dd)
                                    st.download_button(label='📥 Télécharger',
                                        data=df_xlsx ,
                                        file_name= 'PRESTATION_EQUIPEMETS.xlsx')
                            else:
                                    st.warning("Aucun équipement a associer")
                else :
                    res=st.session_state.soc
                    liste=res["N° de prix "].unique()
                    num=st.selectbox('Référence préstation:',liste)
                    if st.button("Supprimer cette association"):
                            st.session_state.soc=res[(res["N° de prix "]!=num) ]
                            st.success('Association supprimée avec succés!!!')
                            (res).to_excel('prestation_equipement.xlsx',index=False)
def manage_quantite():
        res = st.sidebar.radio("Choisir : ", ('Consulter 🔎', 'Rechercher 🕵️‍♂️','Ajouter 👈','Modifier ✍🏻','Supprimer ❌'))
        fusion=st.session_state.qte
        if res =='Consulter 🔎':
            if fusion.shape[0] >0:
                   st.write(fusion) 
            else:
                st.error("Aucune quantité trouvée")
                    
        elif res=='Rechercher 🕵️‍♂️':
            if fusion.shape[0] >0:
                 st.dataframe(filter_dataframe(fusion))
            else:
                st.error("Aucune quantité trouvée")
        elif res=='Ajouter 👈':
                quantite(fusion)
        elif res=='Modifier ✍🏻':
            if fusion.shape[0] >0:
                fusion=update(fusion)
                st.session_state.qte = fusion
                (st.session_state.qte).to_excel('quantite_projet.xlsx',index=False)
            else:
                st.error("Aucune quantité trouvée")
        else:
                if fusion.shape[0] >0:
                    d=st.session_state.qte.copy()
                    d=user_supp_qte()
                    st.session_state.qte=d.copy()
                    (d).to_excel('quantite_projet.xlsx',index=False)
                else:
                        st.error("Aucune quantité trouvée!!")
                       
def quantite(fusion):
                dictionnaire=dict()
                data=st.session_state.data
                eq=st.session_state.eq
                dd = st.session_state.syst
                sys=st.selectbox('Sous système:',data["Sous Système"].unique())
                des=dd[dd["N°Sous Système"]==sys]
                des=(des["Désignation"].unique())[0]
                st.write('Sous système concerné :' ,des)
                liste=((data[data['Sous Système']==sys])["Désignation"]).unique()
                prestation=st.selectbox('Préstation:',liste)
                travaux=st.selectbox('Travaux:',['JOUR','NUIT COURTE','NUIT LONGUE'])
                qt= st.number_input("Quantité:",min_value=0)
                ll=(data[data['Désignation']==prestation])
                num_prestation=(ll["N° de prix "].unique())[0]
                dictionnaire["Sous Système"]=sys
                dictionnaire["N° préstation"]=num_prestation
                dictionnaire["Désignation"]=prestation
                dictionnaire["Travaux"]=travaux
                dictionnaire["Quantité"]=qt
                dictionnaire["Taux forfaitaire unitaire JOUR"]=(ll["Prix unitaire MO JOUR (hors fourniture)|Taux forfaitaire"].unique())[0]
                dictionnaire["Taux forfaitaire unitaire NUIT COURTE"]=(ll["Prix unitaire MO NUIT COURTE (hors fourniture)|Taux forfaitaire"].unique())[0]
                dictionnaire["Taux forfaitaire unitaire NUIT LONGUE"]=(ll["Prix unitaire MO NUIT LONGUE (hors fourniture)|Taux forfaitaire"].unique())[0]
                dictionnaire["Fournitures unitaires"]=(ll["Fournitures \nP.U en euros"].unique())[0]
                dictionnaire= pd.DataFrame([dictionnaire])
                #fusion=pd.read_excel("quantite_projet.xlsx")
                eqq=eq[eq['Sous Système']==sys]                        
                gb = GridOptionsBuilder.from_dataframe(eqq)
                gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
                gb.configure_side_bar() #Add a sidebar
                gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
                gridOptions = gb.build()
                grid_response = AgGrid(
                eqq,
                gridOptions=gridOptions,
                data_return_mode='AS_INPUT', 
                update_mode='MODEL_CHANGED', 
                fit_columns_on_grid_load=True,
                theme='alpine',
                enable_enterprise_modules=True,
                height = "800px", 
                width='100%',
                reload_data=False
                )
                eqq = grid_response['data']
                selected = grid_response['selected_rows'] 
                df = pd.DataFrame(selected)
                dictionnaire["CMP"]=0
                if st.button("Valider ✅"):
                    s=df.shape
                    if (s[0] >0):
                        dictionnaire["CMP"]=(df["CMP (€)"]).sum()
                    fusion= pd.concat([fusion,dictionnaire], ignore_index=True)
                    
                    fusion.to_excel('quantite_projet.xlsx',index=False)
                    st.success('Quantité ajoutée avec succés!!!')
                    st.session_state.qte=fusion
                    st.write(fusion)
                    df_xlsx = to_excell(fusion)
                    st.download_button(label='📥 Télécharger',
                                data=df_xlsx ,
                                file_name= 'QUANTITE PROJET.xlsx')
def to_excell(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_dataframe(res):
                                my_list=res["N°Sous Système"].unique()
                                dd = st.session_state.syst
                                ll=[]
                                for elem in my_list:
                                    d=dict()
                                    my_data=res[res["N°Sous Système"]==elem]
                                    d["N°Sous Système"]=elem
                                    des=dd[dd["N°Sous Système"]==elem]
                                    des=(des["Désignation"].unique())[0]
                                    d["Désignation"]=des
                                    d["COUT FOURNITURE"]=my_data["COUT FOURNITURE"].sum()
                                    d["COUT MO"]=my_data["COUT MO"].sum()
                                    d["COUT TOTAL"]=my_data["COUT TOTAL"].sum()
                                    ll.append(d)
                                dataframe=pd.DataFrame(ll)
                                return dataframe

def estimation_totale():
    if st.button("Estimer"):
            df=pd.read_excel("quantite_projet.xlsx")
            ll=[]
            s=df.shape
            if (s[0] >0):
                        for i in range(len(df)):
                            d=dict()
                            d["N°Sous Système"]=df["Sous Système"][i]
                            d["Désignation"]=df["Désignation"][i]
                            d["Travaux"]=df["Travaux"][i]
                            d["CMP préstation unitaire"]=df["CMP"][i]
                            d["Fournitures préstation unitaire"]=df["Fournitures unitaires"][i]
                            if (df["Travaux"][i])== 'JOUR' :
                                d["COUT MO"]=(int(df["Quantité"][i]))*(float(df["Taux forfaitaire unitaire JOUR"][i]))
                            elif (df["Travaux"][i])== 'NUIT COURTE':
                                d["COUT MO"]=(int(df["Quantité"][i]))*(float(df["Taux forfaitaire unitaire NUIT COURTE"][i]))
                            else:
                                d["COUT MO"]=(int(df["Quantité"][i]))*(float(df["Taux forfaitaire unitaire NUIT LONGUE"][i]))
                            d["COUT FOURNITURE"] =(int(df["Quantité"][i]))*(float(df["Fournitures unitaires"][i])+float(df["CMP"][i]))
                            d["COUT TOTAL"]=d["COUT MO"]+d["COUT FOURNITURE"]
                            ll.append(d)
                        res=pd.DataFrame(ll)
                        tab1, tab2, tab3,tab4 = st.tabs(["Estimation générale", "Estimations par préstation", "Estimations par sous système","Visualisations"])
                        with tab1:
                                st.markdown("""
                <style>
                div[data-testid="metric-container"] {
                   background-color: rgba(28, 151, 225, 0.1);
                   border: 10px solid rgba(28, 151, 225, 0.1);
                   padding: 1% 1% 1% 1%;
                   border-radius: 5px;
                   color: rgb(30, 103, 119);
                   overflow-wrap: break-word;
                }

                /* breakline for metric text         */
                div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
                   overflow-wrap: break-word;
                   white-space: break-spaces;
                   color: green;
                }
                </style>
                """, unsafe_allow_html=True)
                                a=res["COUT TOTAL"].sum()
                                st.metric('COUT TOTAL',a)
                                b=res["COUT FOURNITURE"].sum()
                                st.metric('COUT DE FOURNITURE',b)
                                c=res["COUT MO"].sum()
                                st.metric("COUT DE MAIN D'OEUVRE",c)
                        with tab2:
                                st.write(res)
                                res.to_excel("Estimation.xlsx",index=False)
                                df_xlsx = to_excell(res)
                                st.download_button(label='📥 Télécharger',
                                                data=df_xlsx ,
                                                file_name= 'ESTIMATION.xlsx')
                        with tab3:
                                my_list=res["N°Sous Système"].unique()
                                dd = st.session_state.syst
                
                                ll=[]
                                for elem in my_list:
                                    d=dict()
                                    my_data=res[res["N°Sous Système"]==elem]
                                    d["N°Sous Système"]=elem
                                    des=dd[dd["N°Sous Système"]==elem]
                                    des=(des["Désignation"].unique())[0]
                                    d["Désignation"]=des
                                    d["COUT FOURNITURE"]=my_data["COUT FOURNITURE"].sum()
                                    d["COUT MO"]=my_data["COUT MO"].sum()
                                    d["COUT TOTAL"]=my_data["COUT TOTAL"].sum()
                                    ll.append(d)
                                dataframe=pd.DataFrame(ll)
                                st.write(dataframe)
                                df_xlsx = to_excell(dataframe)
                                st.download_button(label='📥 Télécharger',
                                                data=df_xlsx ,
                                                file_name= 'ESTIMATION-PRESTATION.xlsx')
                        with tab4:
                                 m=get_dataframe(res)
                                 col1, col2= st.columns(2)
                                 with col1:
                                       fig = px.bar(m, x = 'Désignation',y = 'COUT FOURNITURE',title = 'Cout Fourniture par sous système' )
                                       st.plotly_chart(fig)
                                       fig = px.bar(m, x = 'Désignation',y = 'COUT MO',title = 'Cout MO par sous système' )
                                       st.plotly_chart(fig)  
                                       
                                        
                                 with col2:
                                       fig = px.bar(res, x = 'Désignation',y = 'COUT FOURNITURE',title = 'Cout Fourniture par préstation' )
                                       st.plotly_chart(fig)
                                       fig = px.bar(res, x = 'Désignation',y = 'COUT MO',title = 'Cout MO par préstation' )
                                       st.plotly_chart(fig)
                                
                                
                                    
            
            else:
                st.error('Aucune quantité saisie!!!')         
                
            
                