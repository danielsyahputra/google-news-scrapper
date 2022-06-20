import streamlit as st

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from io import BytesIO

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

import warnings
warnings.filterwarnings('ignore')

# Load some functions
def get_data_api(api):
    '''
    Get API result
    '''
    response = requests.get(api)
    return json.loads(response.content)

def scroll(driver, height):
    '''
    Scroll in Selenium
    '''
    driver.execute_script("window.scrollTo(0, {})".format(height))

def get_single_element(driver, xpath):
    '''
    Get single element by xpath in Selenium
    '''
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    return driver.find_element_by_xpath(xpath)


def get_multiple_element(driver, xpath):
    '''
    Get multiple element by xpath in Selenium
    '''
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, xpath)))
    return driver.find_elements_by_xpath(xpath)


def get_text(driver, element):
    '''
    Extract text of an element in Selenium
    '''
    return driver.execute_script("return arguments[0].innerText;", element)


def get_content(xpath):
    '''
    Extract text of an element that is selected by xpath in Selenium
    '''
    return get_text(get_single_element(xpath))

def get_soup(url, verify=True):
    '''
    Parse HTML of a static website 
    '''
    page = requests.get(url, verify=verify)
    soup = BeautifulSoup(page.content)
    return soup


# Page settings
st.set_page_config(
    page_title="Google News Scrapper",
    layout="wide",
    initial_sidebar_state="expanded"
 )

# Title
st.title('Google News Scrapper')

# Input query
query = st.text_input(label='Query', placeholder='Your query')

def load_driver():
    # Load Driver
    # driver_path = "./chromedriver"
    op = webdriver.ChromeOptions()
    # op.add_argument('headless')
    op.add_argument('--headless')
    op.add_argument('--no-sandbox')
    op.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=op)
    return driver

def to_excel(df):
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

def scrape_data(query):
    with st.spinner('Wait for it...'):    
        driver = load_driver()

        # Find query
        url = "https://www.google.com/search?q={}&tbm=nws".format(query)

        driver.get(url=url)

        # Some stuff
        xpath_next = '//*[@id="pnnext"]'
        xpath_div = '//*[@id="rso"]/div'

        df = pd.DataFrame({
            "media": [],
            "judul": [],
            "subtitle": [],
            "tanggal": [],
            "link": []
        })

        while True:
            driver.get(url)
            divs = get_multiple_element(driver, xpath_div)
            for div in divs:
                text = div.text.split("\n")
                link = div.find_element_by_tag_name('a').get_attribute('href')
                data = {
                    "media": text[0],
                    "judul": text[1],
                    "subtitle": text[2],
                    "tanggal": text[-1],
                    "link": link
                }
                df = df.append(data, ignore_index=True)
            try:
                url = get_single_element(driver, xpath_next).get_attribute("href")
            except:
                break
        driver.close()

        st.write("Your query:", query)

        st.write(df)

        
        df_xlsx = to_excel(df)

        st.download_button(
            label='📥 Download data as Excel',
            data=df_xlsx ,
            file_name= f'{query}.xlsx'
            )
    st.success('Done!')
    
st.button(label='Find', on_click=scrape_data, args=(query, ))