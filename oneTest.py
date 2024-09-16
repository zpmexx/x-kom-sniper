import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import csv
import subprocess
import base64

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
        print("wchodze")
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
        
        
if __name__ == '__main__':
    links = {}
    testLink = str(input("Podaj link do przedmiotu: "))
    #testPrice = float(input("Podaj cene przedmiotu za jaka maksymalnie mozesz kupic: "))
    testPrice = 1
    links[testLink] = [testPrice,0,0]
    for link, price in links.items():
        scrapePage(link)
        
    for link, price in links.items():
        print(price)
        try:
            if float(price[0]) > float(price[1]):
                if price[2] != 0: #zly link badz zla wartosc w pliku linki.csv
                    print(f'Przedmiot {price[2]} kosztuje mniej o {abs(round(float(price[1]) - float(price[0]),0))} zł od ceny oczekiwanej.')
        except Exception as e:
            print("blad danych")
            print(e)
    kill_command = 'taskkill /F /IM chrome.exe /T'

# Execute the command
    subprocess.run(kill_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

