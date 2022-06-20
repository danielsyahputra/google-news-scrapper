import streamlit as st

# Page settings
st.set_page_config(
    page_title="About App",
    layout="wide",
    initial_sidebar_state="expanded"
 )

st.title("About this App")

st.write("This google news scrapper app allows you to scrape all the news that Google shows based on your input query. This app will enable you to find out about your company's exposure or the information regarding the trend that may catch your eyes.")

st.write("For more information about this app, you can find out more on this link [Github](https://github.com/danielsyahputra13/google-news-scrapper)")
