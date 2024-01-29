import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import csv
import subprocess

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
        print(name.text)       
        try:
            price1 = driver.find_element(By.CSS_SELECTOR, ".sc-n4n86h-1.hYfBFq")     #cena standardowa
            print(price1.text)
            price = price1
            
            try:
                                                         # to na pewno do dodania /html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[3]/div[2]/div/div[2]/p/span
                price2 =  driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[2]/p/span')
                print(price2.text)
                price1value = price1.text[:-3].replace(',','.').replace(" ","")
                price2value = price2.text[:-3].replace(',','.').replace(" ","")
                price = price1 if price1value < price2value else price2
                print(f'cena finalna: {price.text}')
            except Exception as e:
                print(e)
                print("Brak ceny promocyjnej")
                with open ('logfile.log', 'a') as file:
                    file.write(f"""Brak ceny promocyjnej {link}\n""")
            
            links[link][1] = price.text[:-3].replace(',','.').replace(" ","")
            links[link][2] = name.text

            print(f'{name.text}: {price.text}')
            driver.close()  
            
        except Exception as e:
            print(e)
            print("ceny nie znaleziono")  
            with open ('logfile.log', 'a') as file:
                file.write(f"""Nie znaleziono ceny {link}\n""") 

        #driver.quit()                      
    except:
        print("Brak produktu")
        with open ('logfile.log', 'a') as file:
            file.write(f"""Nie znaleziono przedmiotu {link}\n""")
        
        
if __name__ == '__main__':
    links = {}
    testLink = str(input("Podaj link do przedmiotu: "))
    testPrice = float(input("Podaj cene przedmiotu za jaka maksymalnie mozesz kupic: "))
    links[testLink] = [testPrice,0,0]
    for link, price in links.items():
        scrapePage(link)
        
    for link, price in links.items():
        print(price)
        try:
            if float(price[0]) > float(price[1]):
                if price[2] != 0: #zly link badz zla wartosc w pliku linki.csv
                    print(f'Przedmiot {price[2]} kosztuje mniej o {abs(round(float(price[1]) - float(price[0]),0))} zł od ceny oczekiwanej.')
        except:
            print("blad danych")
    kill_command = 'taskkill /F /IM chrome.exe /T'

# Execute the command
    subprocess.run(kill_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

