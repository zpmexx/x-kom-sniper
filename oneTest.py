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
        driver.get(link)    
        image_element = driver.find_element(By.CSS_SELECTOR, '.sc-1tblmgq-1.fIFmvE')
        image_src = image_element.get_attribute('src')
        category = driver.find_element(By.CSS_SELECTOR, '.sc-10anzls-2.kfrpkf')

        # Process the image URL or base64 data
        if image_src.startswith('http'):
            # If the src is a URL, download the image using requests
            response = requests.get(image_src)
            if response.status_code == 200:
                with open('downloaded_image.jpg', 'wb') as file:
                    file.write(response.content)
                print("Image downloaded successfully.")
            else:
                print("Failed to download the image.")
        elif image_src.startswith('data:image'):
            # If the src is a base64 encoded image, decode and save it directly
            base64_data = image_src.split(',', 1)[1]
            with open('downloaded_image.jpg', 'wb') as file:
                file.write(base64.b64decode(base64_data))
            print("Base64 image decoded and saved successfully.")
        else:
            print("Image source format not recognized.")
    #     print(image)
    #     print(image.text)
    #     print("E")
    #     image_url = image.get_attribute('src')
    #     print('f')
    #     import base64
    #     base64_data = image_url.split(',', 1)[1]
    #     image_data = base64.b64decode(base64_data)
    #     print(image_url)
    #     response = requests.get(image_url)
    #     print('g')
    #     current_directory = os.getcwd()
        
    #     image_filename = os.path.join(current_directory, 'downloaded_image.jpg')  # Update the path and filename as needed

    # # Save the image
    #     if response.status_code == 200:
    #         with open(image_filename, 'wb') as f:
    #             f.write(image_data)   
                               
        name = driver.find_element(By.CSS_SELECTOR, 'h1[data-name="productTitle"]')  
        print(name.text)       
        print(category.text)
        elements = category.text.splitlines()
        print(elements)
        print(elements[-1])
        try:
                                                    #sc-fzqAbL VtZxm sc-o28yi1-2 fPROAJ
                                                    #sc-fzqAbL iHxQAy sc-11gqal2-1 kreaNb
                                                    
            price1 = driver.find_element(By.CSS_SELECTOR, ".sc-fzqMAW.gHIvzZ.sc-o28yi1-2.huvLfx")     #cena standardowa
            print('cena standardowa:')
            print(price1.text)
            price = price1.text.split('zł')[0].replace(',','.').replace(' ','')
            
            try:
                                                         # to na pewno do dodania /html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[3]/div[2]/div/div[2]/p/span
                                                         #/html/body/div[1]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/p/span
                                                         #sc-fzqAbL iHxQAy sc-11gqal2-1 kreaNb
                                                        # sc-fzqAbL.cIgqIB

                price2 =  driver.find_element(By.CSS_SELECTOR, ".sc-1qdf3pj-0.jrtOIu")  #kilka css selectorw wyzej, dalej usuwa sie reszte
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
        except Exception as e:
            print("blad danych")
            print(e)
    kill_command = 'taskkill /F /IM chrome.exe /T'

# Execute the command
    subprocess.run(kill_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

