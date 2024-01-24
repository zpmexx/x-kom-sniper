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
        name = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/h1') #nazwa przedmiotu                      
        try:
            price1 = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[2]/p/span') #cena z kodem rabatowym, czasem niestety klasyczna gdy przecena
            price2 = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[1]/div/div') #cena klasyczna
            price1value = price1.text[:-3].replace(',','.').replace(" ","")
            price2value = price2.text[:-3].replace(',','.').replace(" ","")
            price = price1 if price1value < price2value else price2
        except:   
            try:                                       
                price = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[1]/div/div') #cena klasyczna
            except Exception as e:
                    with open ('logfile.log', 'a') as file:
                        file.write(f"""Nie znaleziono ceny {name}\n""")
                # print("Nie znaleziono ceny")
        links[link][1] = price.text[:-3].replace(',','.').replace(" ","")
        links[link][2] = name.text
        try:
            regularPrice = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[1]/div[2]/span/span') #cena regularna przed przecena
            # print(f'{name.text}: {price.text} / {regularPrice.text}')
        except:
            pass
            # print(f'{name.text}: {price.text}')
        driver.close()
        # driver.quit()      
    except: #wydluzony czas dostawy zmienia sciezki
        try:
            driver.get(link)                      
            name = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[3]/div[1]/div/div[1]/h1') #nazwa przedmiotu                      
            try:
                price1 = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div[2]/div/div[2]/p/span') #cena z kodem rabatowym, czasem niestety klasyczna gdy przecena
                price2 = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div[2]/div/div[1]/div/div') #cena klasyczna
                price1value = price1.text[:-3].replace(',','.').replace(" ","")
                price2value = price2.text[:-3].replace(',','.').replace(" ","")
                price = price1 if price1value < price2value else price2
            except:   
                try:                              
                    price = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div[2]/div/div[1]/div/div') #cena klasyczna
                except Exception as e:
                    with open ('logfile.log', 'a') as file:
                        file.write(f"""Nie znaleziono ceny {name}\n""")
            links[link][1] = price.text[:-3].replace(',','.').replace(" ","")
            links[link][2] = name.text
            try:
                regularPrice = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[1]/div[2]/span/span') #cena regularna przed przecena
                #print(f'{name.text}: {price.text} / {regularPrice.text}')
            except:
                pass
                #print(f'{name.text}: {price.text}')
            driver.close()
            # driver.quit() 
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""Nie znaleziono przedmiotu {link}\n""")
            
            driver.close()
            # driver.quit()  

def writeResultToFile(links):
    with open ('results.txt', 'w') as file:
        for link, price in links.items():
            try:
                if float(price[0]) > float(price[1]):
                    if price[2] != 0: #zly link badz zla wartosc w pliku linki.csv
                        file.write(
f'''Przedmiot: {price[2]}
Link: {link}
Cena za która chcieliśmy kupić: {price[0]} zł
Cena przedmiotu obecnie: {price[1]} zł
Różnica: {abs(round(float(price[1]) - float(price[0]),0))} zł.\n
''')
                        # print(f'Przedmiot {price[2]} kosztuje mniej o {abs(round(float(price[1]) - float(price[0]),0))} zł od ceny oczekiwanej.')
            except:
                pass   
                 
                 
def sendResultViaEmail(links):
    load_dotenv()
    from_address = os.getenv('from_address_cdrl')
    to_address_str = os.getenv('to_address')
    #app_password = os.getenv('app_password_gmail')
    password = os.getenv('password')
    
    now = datetime.now()
    formatDateTime = now.strftime("%d/%m/%Y %H:%M")
    print(to_address_str)
    try:
        to_address = json.loads(to_address_str)
        print(to_address)
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg["To"] = ", ".join(to_address)
        msg['Subject'] = f"Raport x-kom {formatDateTime}."
        print(", ".join(to_address))
        
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""{formatDateTime} Problem z wczytaniem maili\n{str(e)}\n""")
            return True
    # Create MIME object


    # Email body
    body = ""
    for link, price in links.items():
        try:
            if float(price[0]) > float(price[1]):
                if price[2] != 0: #zly link badz zla wartosc w pliku linki.csv
                    body += f'''<h1 style="color:red">Przedmiot: {price[2]}</h1>\n
        <h2>Link: {link}</h2>\n
        <h3>Cena za która chcieliśmy kupić: {price[0]} zł</h3>\n
        <h3>Cena przedmiotu obecnie: {price[1]} zł</h3>\n
        <h2>Różnica: {abs(round(float(price[1]) - float(price[0]),0))} zł.</h2>\n\n
        '''
                    # print(f'Przedmiot {price[2]} kosztuje mniej o {abs(round(float(price[1]) - float(price[0]),0))} zł od ceny oczekiwanej.')
        except:
            pass
    if body:        
        msg.attach(MIMEText(body, 'html'))
        try:
            server = smtplib.SMTP('smtp-mail.outlook.com', 587)
            server.starttls()
            server.login(from_address, password)
            text = msg.as_string()
            server.sendmail(from_address, to_address, text)
            server.quit()               
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} Problem z wysłaniem na maile\n{str(e)}\n""")
    else:
        with open ('emptyresult.txt', 'a') as file:
            file.write(f"""{formatDateTime} - Brak przedmiotow\n""")
            


if __name__ == '__main__':  
    links = {}      
    driver = webdriver.Chrome(options=options)                     
    try:   
        with open('linki.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            next(csv_reader)
            for row in csv_reader:
                if row[1]:
                    links[row[0]] = [row[1],0,0]

        for link, price in links.items():
            scrapePage(link)
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""Wystapil problem z otwarciem pliku linki.csv\n{str(e)}\n""")

    writeResultToFile(links=links)
    sendResultViaEmail(links=links)


kill_command = 'taskkill /F /IM chrome.exe /T'

# Execute the command
subprocess.run(kill_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
