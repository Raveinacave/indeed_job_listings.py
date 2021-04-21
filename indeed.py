import http.cookiejar as cookielib
import os
import urllib
import re
import string
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import date
from time import sleep
import pandas as pd
import re

cookie_filename = "parser.cookies.txt"

# Companies you want to scrape and their name used in the indeed URL bar
ID_companies = {
'TSLA':'Tesla'}

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
delay = 100

class IndeedParser(object):

    def ID_Extract(company,data=None):
        companyID = ID_companies[company]
        url = f'https://www.indeed.com/jobs?q={companyID}&l='
        options = Options()
        browser = webdriver.Firefox(options=options)
        browser.get(url)
        try:
            WebDriverWait(browser, delay).until(
            EC.presence_of_element_located((By.ID, "searchCountPages")))
        except TimeoutException:
            print(f'Loading took too much time for {company}!')
            pass
        else:
            html = browser.page_source
            browser.quit()
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup
        except UnboundLocalError:
            print("Something went wrong, attempting extraction again")
            self.ID_Extract(company,country)
                
    def ID_Transform_and_save(soup,company,country,save=True):
        listings = soup.find('div',{"id": "searchCountPages"})
        if listings is None:
            listings = 0
        else:
            listings = str(listings.text)
            listings_numbers = re.findall('[0-9]+', listings)
            listings = ''.join(map(str, listings_numbers))
        filename = 'INDEED-%s-data.csv' % (company)
        datapath = 'data'
        filename = os.path.join(".." + os.sep, datapath + os.sep, filename)
        if os.path.isfile(filename): data_df = pd.read_csv(filename)
        else: data_df = pd.DataFrame()
        data = pd.DataFrame({'date':[date.today()],'company':[company],'country':[country],'listings':[listings]})
        if len(data_df) > 0:
            data_df = pd.concat([data_df, data],join="outer",ignore_index=True)
            data_df.drop_duplicates(subset=['date','company','country'])
        else: data_df = data
        data_df.set_index('date', inplace=True)
        if save: data_df.to_csv(filename)
        print('All caught up on ' + company + " in " + country + "!" )


#List of companies you want to scrape
companies = ['TSLA']

#List of countries you want to scrape in
countries = ['US']

for company in companies:
    for country in countries:
        soup = IndeedParser.ID_Extract(company,country)
        IndeedParser.ID_Transform_and_save(soup,company,country)
        sleep(2)


