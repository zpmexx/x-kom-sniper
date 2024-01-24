import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import csv

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
            except:
                print("Nie znaleziono ceny")
        links[link][1] = price.text[:-3].replace(',','.').replace(" ","")
        links[link][2] = name.text
        try:
            regularPrice = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[1]/div[2]/span/span') #cena regularna przed przecena
            print(f'{name.text}: {price.text} / {regularPrice.text}')
        except:
            print(f'{name.text}: {price.text}')
        driver.close()
        driver.quit()      
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
                except:
                    print("Nie znaleziono ceny")
            links[link][1] = price.text[:-3].replace(',','.').replace(" ","")
            links[link][2] = name.text
            try:
                regularPrice = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[1]/div[2]/span/span') #cena regularna przed przecena
                print(f'{name.text}: {price.text} / {regularPrice.text}')
            except:
                print(f'{name.text}: {price.text}')
            driver.close()
            driver.quit() 
        except:
            print("Nie znaleziono przedmiotu") 
            driver.close()
            driver.quit()  
        
        
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
