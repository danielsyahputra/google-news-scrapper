import streamlit as st

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
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

def scroll(height):
    '''
    Scroll in Selenium
    '''
    driver.execute_script("window.scrollTo(0, {})".format(height))

def get_single_element(xpath):
    '''
    Get single element by xpath in Selenium
    '''
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    return driver.find_element_by_xpath(xpath)


def get_multiple_element(xpath):
    '''
    Get multiple element by xpath in Selenium
    '''
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, xpath)))
    return driver.find_elements_by_xpath(xpath)


def get_text(element):
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

# Load Driver
driver_path = "./chromedriver"
op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome(driver_path, options=op)

# Title
st.title('Google News Scrapper')

# Input query
query = st.text_input(label='Query', placeholder='Algoritma Data Science School')

# Find query
url = "https://www.google.com/search?q={}&tbm=nws".format(query)

driver.get(url=url)

# Some stuff
xpath_next = '//*[@id="pnnext"]'
xpath_prev = '//*[@id="pnprev"]'
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
    divs = get_multiple_element(xpath_div)
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
        url = get_single_element(xpath_next).get_attribute("href")
    except:
        break

st.write("Your query:", query)

st.write(df)

@st.cache
def convert_df(df):
    return df.to_csv(f"{query}.csv").encode('utf-8')

st.download_button(
    label="Download data as CSV",
    data=df,
    file_name=f'{query}.csv',
    mime='text/csv',
)