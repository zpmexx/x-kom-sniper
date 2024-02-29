import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import csv


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import subprocess
import json

options = webdriver.ChromeOptions()
options.add_argument("disable-infobars")
options.add_argument("start-maximized")
options.add_argument("disable-dev-shm-usage")
options.add_argument("no-sandbox")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("disable-blink-features=AutomationControlled")


def scrapePage(link):
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(link)                      
        name = driver.find_element(By.CSS_SELECTOR, 'h1[data-name="productTitle"]')  
        try:
            category = driver.find_element(By.CSS_SELECTOR, '.sc-10anzls-2.kfrpkf')
            elements = category.text.splitlines()
            print("kategoria ze strony:")
            print(elements[-1])
            print("kategoria z bazy danych: ")
            print(links[link][5])
            if links[link][5] == '': #no category
                print("brak kategori")
                cursor.execute("UPDATE xkom_itemmodel set category = ? where id = ?", elements[-1], links[link][3])
                cnxn.commit()
        except Exception as e:
            print(e)
            print("Brak kategori na stronie")
            with open ('logfile.log', 'a') as file:
                file.write(f"""Brak kategorii {link}\n""")
        print("przed zmiana name")
        print(links[link][4])
        if links[link][4] == '': #no name
            print("brak nazwy updatuje")
            cursor.execute("UPDATE xkom_itemmodel set name = ? where id = ?", name.text, links[link][3])
            cnxn.commit()
            
    except:
        print("Brak produktu")
        with open ('logfile.log', 'a') as file:
            file.write(f"""Nie znaleziono przedmiotu {link}\n""")
   
if __name__ == '__main__':  
    links = {}      
    driver = webdriver.Chrome(options=options) 
    try:
        now = datetime.now()
        formatDateTime = now.strftime("%d/%m/%Y %H:%M")
        with open ('nodiscountfile.log', 'a') as file:
            file.write(f"""{formatDateTime}\n""")    
    except:
        pass
    try:   
        #with open('test_linki.csv') as csv_file:
        import pyodbc
        load_dotenv()
        db_password = os.getenv('db_password')
        db_user = os.getenv('db_user')
        db_server = os.getenv('db_server')
        db_driver = os.getenv('db_driver')
        db_db = os.getenv('db_db')


        cnxn = pyodbc.connect(f'Driver={db_driver};;Server={db_server};Database={db_db};User ID={db_user};Password={db_password}')

        cursor = cnxn.cursor()

        cursor.execute("SELECt id,name,link,target_price,category FROM xkom_itemmodel  where name = '' or category = ''") 
        x = cursor.fetchall()
        for i in x:
            id = i[0]
            name = i[1]
            category = i[4]
            links[i[2]] = [i[3],0,0,id,name,category]

        for link, price in links.items():
            scrapePage(link)
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""Wystapil problem z otwarciem pliku linki.csv\n{str(e)}\n""")
    cnxn.close()




kill_command = 'taskkill /F /IM chrome.exe /T'

# Execute the command
subprocess.run(kill_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
