from datetime import date
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from wordcloud import WordCloud

def generate_grid_options_builder(df):
    gb = GridOptionsBuilder.from_dataframe(df[['Trend','Frequency']])

    cellsytle_jscode = JsCode("""
    function(params) {
        return {
            'fontSize': '125%'
        }
    };
    """)

    #Infer basic colDefs from dataframe types
    gb.configure_default_column(resizable=False, cellStyle=cellsytle_jscode)
    gb.configure_column("Trend", type="string", minWidth=320)
    gb.configure_column("Frequency", minWidth=100)
    gb.configure_selection(selection_mode='single', pre_selected_rows=[0])
    gb.configure_pagination(paginationAutoPageSize=True)
    gridOptions = gb.build()

    grid_response = AgGrid(
        df , 
        gridOptions=gridOptions, 
        theme="streamlit", 
        data_return_mode=DataReturnMode.AS_INPUT, 
        fit_columns_on_grid_load=True, 
        allow_unsafe_jscode=True
        )

    df = grid_response["data"]

@st.cache(suppress_st_warning=True)
def filter_json(df,amount):
    df = df[df['Frequency'] >= df.iloc[amount-1]['Frequency']]
    return df.set_index('Trend').T.to_dict('index')

def generate_wordcloud(df):
    trend = filter_json(df, 10)
    wc = WordCloud(
        width=1320,
        height=720,
        font_path='./assets/font/THSarabunNew.ttf',
        background_color="white",
        regexp=r"[\u0E00-\u0E7Fa-zA-Z']+",
        scale=1
    )
    wc.fit_words(trend['Frequency'])
    st.image(wc.to_array(),use_column_width=True)

st.set_page_config(layout='wide')
st.title('Thai Trending Phrase Analysis on Online News')

c1,c2,c3,c4 = st.columns((2,2,2,2))
############################################

with c1:
    st.subheader('Select Date')
    st.date_input(label='Select Date',min_value= date(2021,10,1),max_value= date(2021,12,31),value=date(2021,10,1),key='ndate')
    news = '_'.join(str(st.session_state.ndate).split('-'))
    df = pd.read_csv('./assets/TrendSelect - Ground_Truth.csv')
    st.subheader("Ground Truth")
    df = df[df["date"] == st.session_state.ndate.strftime("%m-%d-%Y")]
    for i in range(1,4):
        if pd.notna(df[f"trend{i}"].iloc[0]):
            st.write(f'<p style="font-size:25px"> - {df[f"trend{i}"].iloc[0]} </p>', unsafe_allow_html=True)
        else:
            break

############################################

with c2:
    df = pd.read_json('./assets/SMA/'+news+'.json',encoding="utf8")
    df.rename(columns = {'LCS':'Trend', 'frequency':'Frequency'}, inplace = True)
    st.subheader('Longest Common Substring')
    generate_wordcloud(df)
    generate_grid_options_builder(df)
    
############################################

with c3:
    df = pd.read_json('./assets/Twitter/'+news+'.json',encoding="utf8")
    df.rename(columns = {'word':'Trend', 'frequency':'Frequency'}, inplace = True)
    st.subheader('Twitter Reference Method')
    generate_wordcloud(df)
    generate_grid_options_builder(df)
############################################

with c4:
    df = pd.read_json('./assets/Facebook/'+news+'.json',encoding="utf8")
    df.rename(columns = {'Key':'Trend', 'Value':'Frequency'}, inplace = True)
    st.subheader('Facebook Reference Method')
    generate_wordcloud(df)
    generate_grid_options_builder(df)
############################################