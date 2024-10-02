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
        category = driver.find_element(By.CSS_SELECTOR, '.parts__BreadcrumbsWrapper-sc-67f74feb-2.bKRaiX')
        print(f"kategoria: {category.text}")                
        name = driver.find_element(By.CSS_SELECTOR, 'h1[data-name="productTitle"]')  
        print(f"nazwa: {name.text}") 
        elements = category.text.splitlines()
        #print(elements)
        print(elements[-4])
        try:
                                                    #sc-fzqAbL VtZxm sc-o28yi1-2 fPROAJ
                                                    #sc-fzqAbL iHxQAy sc-11gqal2-1 kreaNb
                                                    
            price1 = driver.find_element(By.CSS_SELECTOR, ".sc-emqRaN.cfSJSM.parts__Price-sc-53da58c9-2.hbVORa")     #cena standardowa
            print('cena standardowa:')
            print(price1.text)
            price = price1.text.split('zł')[0].replace(',','.').replace(' ','')
            
            try:
                                                         # to na pewno do dodania /html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[3]/div[2]/div/div[2]/p/span
                                                         #/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/p/span
                                                         #sc-fzqAbL iHxQAy sc-11gqal2-1 kreaNb
                                                        # sc-fzqAbL.cIgqIB

                price2 =  driver.find_element(By.CSS_SELECTOR, ".parts__PriceWrapper-sc-b4da89df-0.rRpBl")  #kilka css selectorw wyzej, dalej usuwa sie reszte
                print("cena promocyjna:")
                print(price2.text)
                price1value = price1.text.split('zł')[0].replace(',','.').replace(' ','')
                print(f'wartosc price1value: {price1value}')
                price2value = price2.text.split('zł')[0].replace(',','.').replace(' ','')
                print(f'wartosc price2value: {price2value}')
                price = price1value if float(price1value) < float(price2value) else price2value
                print(f'cena finalna: {price}')
            except Exception as e:
                print(e)
                print("Brak ceny promocyjnej")
                with open ('logfile.log', 'a') as file:
                    file.write(f"""Brak ceny promocyjnej {link}\n""")
            
            links[link][1] = price
            #links[link][1] = price.text[:-3].replace(',','.').replace(" ","")
            links[link][2] = name.text

            print(f'{name.text}: {price}')
            driver.close()  
            
        except Exception as e:
            print(e)
            print("ceny nie znaleziono")  
            with open ('logfile.log', 'a') as file:
                file.write(f"""Nie znaleziono ceny {link}\n""") 
                
        #driver.quit()                      
    except Exception as e:
        print("Brak produktu")
        print(e)
        with open ('logfile.log', 'a') as file:
            file.write(f"""Nie znaleziono przedmiotu {link}\n""")

def writeResultToFile(links):
    with open ('results.txt', 'w') as file:
        for link, price in links.items():
            try:
                if float(price[0]) >= float(price[1]):
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
    my_address = os.getenv('my_address')
    
    now = datetime.now()
    formatDateTime = now.strftime("%d/%m/%Y %H:%M")
    formatReportDateTime = now.strftime("%Y/%m/%d %H:%M")
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
    resultList = []
    for link, price in links.items():
        try:
            if float(price[0]) >= float(price[1]):
                if price[2] != 0: #zly link badz zla wartosc w pliku linki.csv
                    body += f'''<h1 style="color:red">Przedmiot: {price[2]}</h1>\n
        <h2>Link: {link}</h2>\n
        <h3>Cena startowa: {price[6]} zł</h3>\n
        <h3>Cena za która chcieliśmy kupić: {price[0]} zł</h3>\n
        <h3>Cena przedmiotu obecnie: {price[1]} zł</h3>\n
        <h2>Różnica: {abs(round(float(price[6]) - float(price[0]),0))}/{abs(round(float(price[1]) - float(price[0]),0))} zł.</h2>\n\n
        '''
                    resultList.append([price[2],link,price[0],price[1],abs(round(float(price[1]) - float(price[0]),0))])
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
        try: #update bazy raportu na stronie
            for row in resultList:
                print(row)
                cursor.execute("insert into xkom_reportelement(item_name, link,target_price,current_price,difference,creation_date) values (?,?,?,?,?,?)",row[0],row[1],row[2],row[3],row[4],formatReportDateTime)
                cnxn.commit()
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} Problem z wgraniem raportu do bazy danych {str(e)}\n""")
    else:
        sum = 0
        try:
            for link, price in links.items():
                print(link, price)
                sum += float(price[0])
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} Problem z sumowaniem elementów {str(e)}\n""")
            
        body = f"""Brak przedmiotów przecenionych. Liczba przedmiotów {len(links)}, łączna cena: {sum} """
        msg.attach(MIMEText(body, 'html'))
        try:
            server = smtplib.SMTP('smtp-mail.outlook.com', 587)
            server.starttls()
            server.login(from_address, password)
            text = msg.as_string()
            server.sendmail(from_address, my_address, text)
            server.quit()               
        except Exception as e:
            with open ('logfile.log', 'a') as file:
                file.write(f"""{formatDateTime} Problem z wysłaniem na maile\n{str(e)}\n""")
        with open ('emptyresult.txt', 'a') as file:
            file.write(f"""{formatDateTime} - Brak przedmiotow\n""")
            


if __name__ == '__main__':  
    links = {}      
    driver = webdriver.Chrome(options=options) 
    try:
        now = datetime.now()
        formatDateTime = now.strftime("%d/%m/%Y %H:%M")
        with open ('nodiscountfile.log', 'a') as file:
            file.write(f"""{formatDateTime}\n""")  
            
        with open ('logfile.log', 'a') as file:
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

        cursor.execute("SELECt id,name,link,target_price,category,current_price FROM xkom_itemmodel where status = 0") 
        x = cursor.fetchall()
        for i in x:
            id = i[0]
            name = i[1]
            category = i[4]
            current_price = i[5]
            links[i[2]] = [i[3],0,0,id,name,category,current_price]

        for link, price in links.items():
            scrapePage(link)
    except Exception as e:
        with open ('logfile.log', 'a') as file:
            file.write(f"""Wystapil problem z otwarciem pliku linki.csv\n{str(e)}\n""")

    writeResultToFile(links=links)
    sendResultViaEmail(links=links)
    cnxn.close()




kill_command = 'taskkill /F /IM chrome.exe /T'

# Execute the command
subprocess.run(kill_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
