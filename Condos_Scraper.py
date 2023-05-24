from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.select import Select
import time
import csv
import os
import pandas as pd
import warnings
import shutil
import requests
import getpass_ak
from termcolor import colored
import sys
warnings.filterwarnings('ignore')

def initialize_bot():

    ## Setting up chrome driver for the bot
    chrome_options  = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    #chrome_options.add_argument('--headless')
    driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(driver_path, options=chrome_options)
    driver.set_page_load_timeout(60)
    ######################################################
    #chrome_options = uc.ChromeOptions()
    #chrome_options.add_argument('--headless')
    #driver = uc.Chrome(options=chrome_options)
    #driver.maximize_window()
    return driver

def scrape_torontomls_data(driver, scraped, URL, output):

    if 'End of listings' in scraped:
        return

    #URL = "http://v3.torontomls.net/Live/Pages/Public/Link.aspx?Key=55013c7770a643d882e94ffcf8a1f633&App=TREB"
    driver.get(URL)
    time.sleep(5)
    height = driver.execute_script("return document.body.scrollHeight")
    y = 0
    # scrolling to the end of the page
    while True:
        y += 700
        driver.execute_script(f"window.scrollTo(0, {y})")
        time.sleep(2)
        end_height = driver.execute_script("return document.body.scrollHeight")
        if y > height*2 or y >= end_height:
            break
    try:
        div = wait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.reports.view-clf")))
    except:
        div = wait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.reports.view-pm")))

    elems = wait(div, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.formitem.legacyBorder.formgroup.vertical")))
    #(len(elems))
    nelem = len(elems)
    for m, elem in enumerate(elems):
        house = {}
        row = []
        house['features'] = set()
        spans = wait(elem, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.formitem.formfield")))
        try:
            house['address'] = spans[0].text
            if house['address'] in scraped: continue
        except:
            house['address'] = 'Unknown'
            line = f"Warning: failed to correctly scrape the address of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow'))         
            
        try:
            house['condo#'] = str(spans[1].text)
            if len(house['condo#']) == 0:
                house['condo#'] = '-1'
        except:
            house['condo#'] = '0'
            line = f"Warning: failed to correctly scrape the condo number of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow')) 

        ################################################################
        # for debugging purpose
        #if house['address'] != '4870 Elgin Mills Rd E':
        #    continue
        #################################################################
        try:    
            house['area'] = spans[2].text        
        except:
            house['area'] = 'Unknown'
            line = f"Warning: failed to correctly scrape the area of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow'))  
        try:
            house['city'] = spans[3].text
            #print('City: ', house['city'])  
        except:
            house['city'] = 'Unknown'           
            line = f"Warning: failed to correctly scrape the city of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow')) 
        try:    
            house['zip'] = spans[4].text
            #print('Zip Code: ', house['zip'])    
        except:
            house['zip'] = 'Unknown'
            line = f"Warning: failed to correctly scrape the zip code of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])    
            print(colored(line, 'yellow'))          
        try:
            house['price'] = spans[5].text.split('$')[-1].replace(',', '')
            #print('Price: ', house['price'])
        except:
            house['price'] = '0'
            line = f"Warning: failed to correctly scrape the price of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow')) 
        try:
            house['district'] = spans[8].text
            #print('District: ', house['district'])  
        except:
            house['district'] = 'Unknown'
            line = f"Warning: failed to correctly scrape the district of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow'))  
        ind = 0
        start = 8
        n = len(spans)                        
        # checking for the start of the features tab
        for k in range(8, n):
            if 'Taxes:' in spans[k].text.strip():
                try:
                    house['tax'] = spans[k].text.split('$')[-1].replace(',', '')  
                except:
                    house['tax'] = '0'
                    line = f"Warning: failed to correctly scrape the tax of listing '{house['address']}',\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow')) 
                try:
                    house['tax_year'] = spans[k+1].text   
                except:
                    house['tax_year'] = '0'   
                    line = f"Warning: failed to correctly scrape the tax year of listing '{house['address']}',\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])  
                    print(colored(line, 'yellow'))               
                    
            if 'Maint:' in spans[k].text.strip():
                try:
                    house['fee'] = spans[k].text.split('$')[-1].replace(',', '')  
                except:
                    house['fee'] = '0'
                    line = f"Warning: failed to correctly scrape the condo fee of listing '{house['address']}',\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow')) 
                   
            if 'Front On:' in spans[k].text.strip() or 'Fronting On:' in spans[k].text.strip():
                try:
                    house['style'] = spans[k-1].text 
                    for i in range(1, 5):
                        if ":" in house['style']:
                            house['style'] = spans[k-i].text 
                        else:
                            break
                    house['type'] = 'Residential'
                    house['fee'] = '-1'
                    house['unit#'] = '-1'
                    house['level'] = '-1'
                except:
                    house['type'] = 'Residential'
                    house['fee'] = '-1'
                    house['unit#'] = '-1'
                    house['level'] = '-1'
                    house['style'] = 'Other'
                    line = f"Warning: failed to correctly scrape the style of listing '{house['address']}',\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow')) 

                if len(house['style']) == 0:
                    house['style'] = 'Other'             
                    
            if 'Last Status' in spans[k].text.strip() or 'DOM:' in spans[k].text.strip():
                try:
                    house['type'] = spans[k+1].text 
                    if 'Condo' in house['type']:
                        house['type'] = 'Condominium'
                    else:
                        house['type'] = 'Residential'                    
                        
                    if 'Town' in spans[k+2].text or 'Town' in spans[k+1].text:
                        house['style'] = 'Townhouse'
                    else:
                        house['style'] = 'Apartment'
                except:
                    house['type'] = 'Residential'
                    house['style'] = 'Other'
                    line = f"Warning: failed to correctly scrape the style of listing '{house['address']}',\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow')) 
                # no lot data for condos
                house['lot1'] = '-1'     
                house['lot2'] = '-1'

                if len(house['style']) == 0:
                    house['style'] = 'Other'               
                    
            if 'Bedrooms:' in spans[k].text.strip():
                try:
                    house['bedrooms'] = spans[k].text.split('+')[0].split(':')[-1]   
                    if len(house['bedrooms']) == 0:
                        house['bedrooms'] = '0'  
                except:
                    house['bedrooms'] = '0'
                    line = f"Warning: failed to correctly scrape the number of bedrooms of listing '{house['address']}',\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow')) 
                    
            if 'Washrooms:' in spans[k].text.strip():
                try:
                    house['washrooms'] = spans[k].text.split('+')[0].split(':')[-1]   
                    if len(house['washrooms']) == 0:
                        house['washrooms'] = '0'  
                except:
                        house['washrooms'] = '0' 
                        line = f"Warning: failed to correctly scrape the number of washrooms of listing '{house['address']}',\n please update manually"
                        #print(COLOR["YELLOW"], line, COLOR["ENDC"])   
                        print(colored(line, 'yellow'))             
                        
            if 'Unit#:' in spans[k].text.strip():
                try:
                    house['unit#'] = spans[k].text.split(':')[-1]   
                except:
                        house['unit#'] = '0' 
                        line = f"Warning: failed to correctly scrape the unit number of listing '{house['address']}',\n please update manually"
                        #print(COLOR["YELLOW"], line, COLOR["ENDC"])   
                        print(colored(line, 'yellow'))               
                        
            if 'Level:' in spans[k].text.strip() and ' Level:' not in spans[k].text.strip():
                try:
                    house['level'] = spans[k].text.split(':')[-1]   
                except:
                        house['level'] = '0' 
                        line = f"Warning: failed to correctly scrape the floor of listing '{house['address']}',\n please update manually"
                        #print(COLOR["YELLOW"], line, COLOR["ENDC"])   
                        print(colored(line, 'yellow'))              
                        
            if 'MLS#:' in spans[k].text.strip():
                try:
                    house['MLS'] = spans[k].text.split(':')[-1]   
                except:
                        house['MLS'] = '0' 
                        line = f"Warning: failed to correctly scrape the floor of listing '{house['address']}',\n please update manually"
                        #print(COLOR["YELLOW"], line, COLOR["ENDC"])   
                        print(colored(line, 'yellow'))    
                        
            if 'Lot:' in spans[k].text.strip():
                lot = spans[k].text
                try:
                    lot1 = lot.split(' ')[0].split(':')[-1]
                except:
                    lot1 = 0
                    line = f"Warning: Lot data is missing for listing '{house['address']}'"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow'))
                try:
                    lot2 = lot.split(' ')[2]    
                except:
                    lot2 = 0
                    line = f"Warning: Lot data is missing for listing '{house['address']}'"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow'))
                house['lot1'] = lot1     
                house['lot2'] = lot2
          
            if 'Basement:' in spans[k].text.strip():
                try:
                    house['basement'] = spans[k].text.split(':')[-1].strip()
                    if len(house['basement']) == 0:
                        house['basement'] = 'None'
                except:
                        house['basement'] = 'None'
                        line = f"Warning: failed to correctly scrape the basement of listing '{house['address']}',\n please update manually"
                        #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
                        print(colored(line, 'yellow'))  
            elif 'Tot Prk Spcs:' in spans[k].text.strip() or 'Tot Pk Spcs:' in spans[k].text.strip():
                try:
                    house['park_places'] = spans[k].text.split(':')[-1].strip()
                    if len(house['park_places']) == 0:
                        house['park_places'] = 'None'
                except:
                        house['park_places'] = 'None'
                        line = f"Warning: failed to correctly scrape the park places of listing '{house['address']}',\n please update manually"
                        #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
                        print(colored(line, 'yellow'))
            elif 'Oth Struct:' in spans[k].text.strip():
                start = k+9
                step = 8
            elif 'Prop Feat:' in spans[k].text.strip() or 'Bldg Amen:' in spans[k].text.strip():
                start = k+8
                step = 8
                #break
            elif 'Client Remks:' in spans[k].text.strip():
                try:
                    des = spans[k].text.replace('Client Remks:', '')  
                except:
                    des = ''
                    line = f"Warning: failed to correctly scrape the description of listing '{house['address']}',\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
                    print(colored(line, 'yellow'))
                try:
                    extra = spans[k+1].text.replace('Client Remks:', '')
                except:
                    extra = ''
                try:
                    house['des'] = des + ' ' + extra.replace("Extras:", "") + ' ' + 'Listing Courtesy of: ' + spans[k+2].text.split(':')[-1].title() + '. Contact Alex Now To Book A Showing'
                    #print('Description: \n', house['des'])
                except:
                    house['des'] = ''
                    line = f"Warning: failed to correctly scrape the description of listing '{house['address']}',\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
                    print(colored(line, 'yellow'))
        done = False
        # condition for houses with no features
        if start >= n:
            start -= 9
        for i in range(start, n-3, step):
            try:
                f1 = spans[i].text
                f2 = spans[i+1].text
                f3 = spans[i+2].text
            except:
                continue

            # conditions for the description section start
            for j in range(9):
                try:
                    if 'Client Remks:' in spans[i+j].text:
                        ind = i+j
                        done = True
                        break
                except:
                    continue

            if done: break
            if 'Client Remks:' in f1:
                ind = i
                break
            elif 'Client Remks:' in f2: 
                if len(f1.strip()) > 0:
                    house['features'].add(f1)
                ind = i+1
                break
            elif 'Client Remks:' in f3:
                if len(f1.strip()) > 0:
                    house['features'].add(f1)
                if len(f2.strip()) > 0:
                    house['features'].add(f2)
                ind = i+2
                break

            if len(f1.strip()) > 0:
                house['features'].add(f1)
            if len(f2.strip()) > 0:
                house['features'].add(f2)
            if len(f3.strip()) > 0:
                house['features'].add(f3)
            #print(f1, f2, f3)
        #try:
        #    des = spans[ind].text.replace('Client Remks:', '')  
        #except:
        #    des = ''
        #    line = f"Warning: failed to correctly scrape the description of listing '{house['address']}',\n please update manually"
        #    #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
        #    print(colored(line, 'yellow'))
        #try:
        #    extra = spans[ind+1].text.replace('Client Remks:', '')
        #except:
        #    extra = ''
        #try:
        #    house['des'] = des + ' ' + extra.replace("Extras:", "") + ' ' + 'Listing Courtesy of: ' + spans[ind+2].text.split(':')[-1].title() + '. Contact Alex Now To Book A Showing'
        #    #print('Description: \n', house['des'])
        #except:
        #    house['des'] = ''
        #    line = f"Warning: failed to correctly scrape the description of listing '{house['address']}',\n please update manually"
        #    #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
        #    print(colored(line, 'yellow'))

        # scraping the house images
        img_path = os.getcwd() + '\\Images\\' + house['address']
        if os.path.exists(img_path):
            shutil.rmtree(img_path) 
        os.makedirs(img_path)
        try:
            info = wait(elem, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.info"))).text.split('of')[-1]
            info = int(info)
            # limit the maximum number of images by 20
            #if info > 20:
            #    info = 20
        except:
            info = 1

        # clicking on images to display it in the full size
        try:
            img = wait(elem, 60).until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            driver.execute_script("arguments[0].click();", img)
            time.sleep(3)
        except:
            press = False
        for i in range(info):
            try:
                img_url = wait(driver, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.lg-object.lg-image")))[i].get_attribute("src")
                response = requests.get(img_url)
                with open(img_path + f'\\img{i+1}.png', 'wb') as file:
                    file.write(response.content)
            except:
                break

            if info > 1:
                try:
                    button = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.lg-next.lg-icon")))
                    driver.execute_script("arguments[0].click();", button)  
                    time.sleep(3)
                except:
                    press = False
        try:
            button = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.lg-close.lg-icon")))
            driver.execute_script("arguments[0].click();", button)
            time.sleep(2)
        except:
            press = False

        row = [house['features'], house['address'], house['area'], house['city'], house['zip'], house['price'], house['district'], house['tax'], house['tax_year'], house['type'], house['style'], house['bedrooms'], house['washrooms'], house['lot1'], house['lot2'], house['fee'], house['basement'], house['park_places'], house['unit#'], house['level'], house['MLS'], house['condo#'], house['des']]

        with open(output, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)  

        line = f"Listing {m+1} of {nelem} is scraped successfully!"
        #print(COLOR["GREEN"], line, COLOR["ENDC"])
        print(colored(line, 'green'))
    # outputting the end data to a csv file
    row = []
    for k in range(23):
        row.append('End of listings')
    with open(output, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)  
        
def scrape_realmmlp_data(driver, scraped, URL, output):

    if 'End of listings' in scraped:
        return

    driver.get(URL)
    time.sleep(2)

    try:
        # getting the number of listings 
        text = wait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.sc-ikZpkk.jatHPM.chakra-text.sc-cLFqLo.kFppvC"))).text
        if text.find('of') != -1:
            text = text.split('of')[-1].split(' ')[1]
        else:
            text = text.split(' ')[0]

        nlist = int(text)
    except:
        line = f"Error: Failed to get the number of listings, exiting ..."
        print(colored(line, 'red'))
        input('Press any key to exit')
        sys.exit(1)

    # clicking on the first listing
    try:
        div = wait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='card-container__CardContainer-sc-ec1j2-0 gZLJBU']/div")))[0]
        button = wait(div, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))[-1]
        driver.execute_script("arguments[0].click();", button)
    except Exception as err:
        print(f'Error: {str(err)}')

    keys = ['features', 'address', 'area', 'city', 'zip', 'price', 'district', 'tax', 'tax_year', 'type', 'style', 'bedrooms', 'washrooms', 'lot1', 'lot2', 'fee', 'basement', 'park_places', 'unit#', 'level', 'MLS', 'condo#', 'des']    
    num_keys = ['lot1', 'lot2', 'fee', 'park_places']
    for ilist in range(nlist):
        house = {}
        row = []
        house['features'] = set()
        div = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.report-TREB")))
        add_div = wait(div, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.addr")))
        price_div = wait(div, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.price")))
        info_div = wait(div, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.data-section.section.collapsible")))
        dts = wait(info_div, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "dt")))
        dds = wait(info_div, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "dd")))
        info_table = wait(div, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.short-details")))
        info_tds = wait(info_table, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "td")))
        details_div = wait(div, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@id='section-property']")))
        det_dts = wait(details_div, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "dt")))
        det_dds = wait(details_div, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "dd")))
        des_div = wait(div, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.data-row.data-section.section.noborder")))
        extra_divs = wait(div, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.data-row.data-section.section.collapsible")))
        contact_divs = wait(div, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.data-row.data-section.section")))
        features_divs = wait(div, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.data-section.section.collapsible")))
        try:
            img_div = wait(div, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.image-gallery-content")))
        except:
            line = f"Warning: No images are found for listing {ilist+1}, skipping ...."
            print(colored(line, 'yellow')) 
            get_next_listing(driver, ilist, nlist)
            continue

        try:
            house['address'] = wait(add_div, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text.split(',')[0]
            if house['address'] in scraped: continue
        except:
            house['address'] = 'Unknown'
            line = f"Warning: failed to correctly scrape the address of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow'))         
            
        try:
            condo = house['address'].split(' ')[-1]
            if condo.isnumeric():
                house['condo#'] = condo
            else:
                house['condo#'] = '-1'
        except:
            house['condo#'] = '0'
            line = f"Warning: failed to correctly scrape the condo number of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow')) 

        try:    
            house['area'] = wait(add_div, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text.split(',')[-1]     
        except:
            house['area'] = 'Unknown'
            line = f"Warning: failed to correctly scrape the area of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow'))  
        try:
            house['city'] = wait(add_div, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h3"))).text.split(',')[3].split(' ')[1]
            #print('City: ', house['city'])  
        except:
            house['city'] = 'Unknown'           
            line = f"Warning: failed to correctly scrape the city of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow')) 
        try:    
            code = wait(add_div, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h3")))
            house['zip'] = wait(code, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.zip"))).text 
        except:
            house['zip'] = 'Unknown'
            line = f"Warning: failed to correctly scrape the zip code of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])    
            print(colored(line, 'yellow'))          
        try:
            house['price'] = wait(price_div, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "span")))[0].text.split('$')[-1]#.replace(',', '')
            #print('Price: ', house['price'])
        except:
            house['price'] = '0'
            line = f"Warning: failed to correctly scrape the price of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow')) 
        try:
            house['district'] = wait(add_div, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h3"))).text.split(',')[1].strip()
            #print('District: ', house['district'])  
        except:
            house['district'] = 'Unknown'
            line = f"Warning: failed to correctly scrape the district of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow'))  

        try:
            for i, dt in enumerate(dts):
                if dt.text.lower() == 'taxes':
                    house['tax'] = dds[i].text.split('$')[-1].replace(',', '')
                    break
        except:
            house['tax'] = '0'
            line = f"Warning: failed to correctly scrape the tax of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow')) 
        try:
            for i, dt in enumerate(dts):
                if dt.text.lower() == 'tax year':
                    house['tax_year'] = dds[i].text
                    break
        except:
            house['tax_year'] = '0'   
            line = f"Warning: failed to correctly scrape the tax year of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])  
            print(colored(line, 'yellow'))               
            
        try:
            for i, dt in enumerate(dts):
                if dt.text.lower() == 'maintenance':
                    house['fee'] = dds[i].text.split('$')[-1].replace(',', '')  
                    break
        except:
            house['fee'] = '0'
            line = f"Warning: failed to correctly scrape the condo fee of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow')) 
                   
        try:
            house['style'] = wait(add_div, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text.split(' ')[-1]

            if 'town' in house['style'].lower():
                house['style'] = 'Townhouse'
            if len(house['style']) == 0:
                house['style'] = 'Other' 

        except:
            house['style'] = 'Other'
            line = f"Warning: failed to correctly scrape the style of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow')) 
                    
        try:
            house['type'] = wait(add_div, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text.split(' ')[0].split('/')[-1]

            if 'condo' in house['type'].lower():
                house['type'] = 'Condominium'
            if 'house' in house['type'].lower():
                house['type'] = 'Townhouse'                    
            if len(house['type']) == 0:
                house['type'] = 'Residential'                         
        except:
            house['type'] = 'Residential'
            line = f"Warning: failed to correctly scrape the style of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow')) 
                 
        try:
            for td in info_tds:
                if 'bed'in td.text.lower():
                    house['bedrooms'] = td.text.lower().replace('\n', '').split('bed')[0].split('+')[0]
                    break
            if len(house['bedrooms']) == 0:
                house['bedrooms'] = '0'  
        except:
            house['bedrooms'] = '0'
            line = f"Warning: failed to correctly scrape the number of bedrooms of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow')) 
                    
        try:
            for td in info_tds:
                if 'bath'in td.text.lower():
                    house['washrooms'] = td.text.lower().replace('\n', '').split('bath')[0].split('+')[0]
                    break  
            if len(house['washrooms']) == 0:
                house['washrooms'] = '0'  
        except:
                house['washrooms'] = '0' 
                line = f"Warning: failed to correctly scrape the number of washrooms of listing '{house['address']}',\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])   
                print(colored(line, 'yellow'))             
                        
        try:
            for i, dt in enumerate(det_dts):
                if dt.text.lower() == 'unit #':
                    house['unit#'] = det_dds[i].text 
                    break
        except:
                house['unit#'] = '0' 
                line = f"Warning: failed to correctly scrape the unit number of listing '{house['address']}',\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])   
                print(colored(line, 'yellow'))               
                        
        try:
            for i, dt in enumerate(det_dts):
                if dt.text.lower() == 'level':
                    house['level'] = det_dds[i].text 
                    break
        except:
                house['level'] = '0' 
                line = f"Warning: failed to correctly scrape the floor of listing '{house['address']}',\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])   
                print(colored(line, 'yellow'))              
                        
        try:
            house['MLS'] = wait(price_div, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h3"))).text
        except:
                house['MLS'] = '0' 
                line = f"Warning: failed to correctly scrape the floor of listing '{house['address']}',\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])   
                print(colored(line, 'yellow'))    
                        
        try:
            for i, dt in enumerate(det_dts):
                if dt.text.lower() == 'lot size':
                    house['lot1'] = det_dds[i].text.split(' ')[0] 
                    house['lot2'] = det_dds[i].text.split(' ')[3] 
                    break
        except:
            house['lot1'] = 0
            house['lot2'] = 0
            line = f"Warning: Lot data is missing for listing '{house['address']}'"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow'))
                
        try:
            for i, dt in enumerate(det_dts):
                if dt.text.lower() == 'basement':
                    house['basement'] = det_dds[i].text 
                    break
            if len(house['basement']) == 0:
                house['basement'] = 'None'
        except:
                house['basement'] = 'None'
                line = f"Warning: failed to correctly scrape the basement of listing '{house['address']}',\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
                print(colored(line, 'yellow'))  
        try:
            for i, dt in enumerate(det_dts):
                if dt.text.lower() == 'total parking spaces':
                    house['park_places'] = det_dds[i].text 
                    break
            if len(house['park_places']) == 0:
                house['park_places'] = 'None'
        except:
                house['park_places'] = 'None'
                line = f"Warning: failed to correctly scrape the park places of listing '{house['address']}',\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
                print(colored(line, 'yellow'))
        try:
            des = des_div.text.replace('Description', '').replace('\n', '')
        except:
            des = ''
            line = f"Warning: failed to correctly scrape the description of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow'))

        extra = ''  
        try:
            for extra_div in extra_divs:
                if 'Extras' in extra_div.text:
                    extra = extra_div.text.replace('Extras', '')
                    break
        except:
            pass
            
        # listing Courtesy
        #contact = ''
        #try:
        #    for contact_div in contact_divs:
        #        if 'Contracted With' in contact_div.text:
        #            contact = contact_div.text.replace('Contracted With', '').split('BROKERAGE')[0] + 'BROKERAGE'
        #            break
        #except:
        #    pass

        try:
            #house['des'] = des + ' ' + extra + ' ' + 'Listing Courtesy of: ' + contact + '. Contact Alex Now To Book A Showing'
            house['des'] = des + ' ' + extra + '. Contact Alex Now To Book A Showing'

        except:
            house['des'] = ''
            line = f"Warning: failed to correctly scrape the description of listing '{house['address']}',\n please update manually"
            #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            print(colored(line, 'yellow'))

        # features
        try:
            for features_div in features_divs:
                if 'Features' in features_div.text:
                    lis = wait(features_div, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
                    for li in lis:
                        house['features'].add(li.text)
                    break
        except:
            pass

        # removing the suit number from condo address
        if house['type'] == 'Condominium':
            add = house['address'].split(' ')[:-1]
            house['address'] = ' '.join(add)
            house['condo#'] = house['address'].split(' ')[-1]

        # scraping the house images
        img_path = os.getcwd() + '\\Images\\' + house['address'] + '_' + house['MLS']
        if os.path.exists(img_path):
            shutil.rmtree(img_path) 
        os.makedirs(img_path)

        try:
            # viewing images in full screen mode
            try:
                # for dark windows theme
                button = wait(img_div, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.sc-jSMfEi.kvDFEK.chakra-button.sc-bUbCnL.sc-kIKDeO.sc-hNKHps.eXMndt.hrWNNq.jvmDOS")))
            except:
                # for light windows theme
                button = wait(img_div, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.sc-jSMfEi.cFedwT.chakra-button.sc-bUbCnL.sc-kIKDeO.sc-hNKHps.eXMndt.hrWNNq.jvmDOS")))
            driver.execute_script("arguments[0].click();", button)
            time.sleep(2)
            n = int(button.text)
            #####################################
            # capping the number of images to 20
            if n > 20:
                n = 20
            ####################################
            imgs = []
            for i in range(n):
                try:
                    # getting the link of each image
                    img_url = wait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='lg-toolbar lg-group']/a")))[-1].get_attribute("href")
                    if img_url[:4] != 'http':
                        img_url += 'https://app.realmmlp.ca/'
                    imgs.append(img_url)
                    # pressing on next image
                    button = wait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//button[@class='lg-next lg-icon']")))[-1]
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(3)
                except:
                    continue

            # opening second tab 
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            # downloading images
            for i, img in enumerate(imgs):           
                try:
                    driver.get(img)
                    response = requests.get(driver.current_url)
                    #driver.save_screenshot(img_path + f'\\img{i+1}.png')
                    with open(img_path + f'\\img{i+1}.png', 'wb') as file:
                        file.write(response.content)
                except:
                    continue
            driver.close()
            # back to tab 1 in the browser
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)
            # closing the images window
            button = wait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.lg-close.lg-icon")))[-1]
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)
        except Exception as err:
            line = f"Warning: Failed to scrape all the images for listing '{house['address']}'"
            print(colored(line, 'yellow'))

        # checking for unassigned keys
        for key in keys:
            if house.get(key, -1) == -1:
                house[key] = -1

        # overriding non numeric values for numeric keys
        for key in num_keys:
            if not isinstance(house[key], int) and not isinstance(house[key], float) and not house[key].isnumeric():
                house[key] = -1


        row = [house['features'], house['address'], house['area'], house['city'], house['zip'], house['price'], house['district'], house['tax'], house['tax_year'], house['type'], house['style'], house['bedrooms'], house['washrooms'], house['lot1'], house['lot2'], house['fee'], house['basement'], house['park_places'], house['unit#'], house['level'], house['MLS'], house['condo#'], house['des']]

        with open(output, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)  

        line = f"Listing {ilist+1} of {nlist} is scraped successfully!"
        print(colored(line, 'green'))

        # clicking on the next listing
        get_next_listing(driver, ilist, nlist)


def get_next_listing(driver, ilist, nlist):
    if ilist < nlist - 1: # condition not to click next after last listing
        try:
            # for dark Windows theme
            button = wait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//button[@class='sc-jSMfEi dqisxW chakra-button sc-brCFrO sc-gITdmR dFiDPF cEqlF listing-view__NavigationButton-sc-gf6j0o-0 TEtJK listing-view__NavigationButton-sc-gf6j0o-0 TEtJK']")))        
        except:
            # for light Windows theme
            button = wait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//button[@class='sc-jSMfEi gxDBFX chakra-button sc-brCFrO sc-gITdmR dFiDPF cEqlF listing-view__NavigationButton-sc-gf6j0o-0 TEtJK listing-view__NavigationButton-sc-gf6j0o-0 TEtJK']")))

        driver.execute_script("arguments[0].click();", button)
        time.sleep(5)

def p2h_login(driver, name, pwd):
    print('Signing in Point2homes....')
    print('-'*100)
    #login
    url = "https://www.point2homes.com/Help/advertising-for-agents.html"
    driver.get(url)
    time.sleep(3)
    try:
        button = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-ghost-primary")))
        driver.execute_script("arguments[0].click();", button)
        time.sleep(3)
        driver.execute_script(f"document.getElementById('Username').value='{name}'")
        time.sleep(2)
        driver.execute_script(f"document.getElementById('Password').value='{pwd}'")
        time.sleep(2)
        button = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and @value='Sign in']")))
        driver.execute_script("arguments[0].click();", button)
        time.sleep(5)
    except:
        line = f"Warning: failed to login to the Point2homes account! Exiting the program ..."
        #print(COLOR["RED"], line, COLOR["ENDC"]) 
        print(colored(line, 'red'))
        input('Press any key to exit')
        sys.exit()
        

def create_listing(df, name, pwd, driver):

    p2h_login(driver, name, pwd)

    url = 'https://www.point2homes.com/Account/MyListings'
    driver.get(url)
    # clicking on active listings
    buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    for button in buttons:
        if 'Active' in button.text:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)
            break
    #########################################################################
    print('Checking Existing Listings in P2H ....')
    print('-'*100)
    # checking for added listings
    completed = []
    try:
        while True:
            # getting the address of the active listings
            act_div = wait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='activeListingsContainer' and @class='tabContent']")))
            elems = wait(act_div, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='item-cnt clearfix  none']")))
            for elem in elems:
                try:
                    add = wait(elem, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.address-container"))).text.split(',')[0].strip()
                    beds = wait(elem, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "strong")))[0].text.strip()
                    baths = wait(elem, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "strong")))[1].text.strip()
                    price = wait(elem, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.green"))).text.replace('$','').replace('CAD','').strip()
                    completed.append(add + '_'+ str(beds) + '_' + str(baths)+ '_' + str(price))
                except:
                    continue

            # moving to the next page of the active listings+
            button = wait(act_div, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@class='pager-next']")))
            driver.execute_script("arguments[0].click();", button)
    except:
        pass
    #####################################################################
    # Deleting all the active listings
    #print('Deleting all active Listings in P2H ....')
    #print('-'*100)
    #url = 'https://www.point2homes.com/Account/MyListings'
    #driver.get(url)
    ## clicking on active listings
    #buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    #for button in buttons:
    #    if 'Active' in button.text:
    #        driver.execute_script("arguments[0].click();", button)
    #        time.sleep(3)
    #        break

    #done = False
    #while True:
    #    try:
    #        if done: break
    #        # getting the address of the active listings
    #        act_div = wait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='activeListingsContainer' and @class='tabContent']")))
    #        try:
    #            elems = wait(act_div, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='item-cnt clearfix  none']")))
    #        except:
    #            break
    #        nelem = len(elems)
    #        for i in range(nelem):
    #            act_div = wait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='activeListingsContainer' and @class='tabContent']")))
    #            try:
    #                elems = wait(act_div, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='item-cnt clearfix  none']")))
    #            except: 
    #                done = True
    #                break
    #            try:
    #                buttons = wait(elems[0], 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    #                for button in buttons:
    #                    if button.text.strip() == 'Archive':
    #                        driver.execute_script("arguments[0].click();", button)
    #                        time.sleep(2)
    #                        break
    #                popup = wait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.psrk-popup.visible")))
    #                button = wait(popup, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-primary")))
    #                driver.execute_script("arguments[0].click();", button)
    #                time.sleep(5)
    #            except:
    #                continue

    #    except:
    #        driver.quit()
    #        driver = initialize_bot()
    #        p2h_login(driver, name, pwd)
    #        print('Deleting all active Listings in P2H ....')
    #        print('-'*100)
    #        url = 'https://www.point2homes.com/Account/MyListings'
    #        driver.get(url)
    #        # clicking on active listings
    #        buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    #        for button in buttons:
    #            if button.text.strip() == 'Active':
    #                driver.execute_script("arguments[0].click();", button)
    #                time.sleep(3)
    #                break


    #print('Deleting all archived Listings in P2H ....')
    #print('-'*100)
    #url = 'https://www.point2homes.com/Account/MyListings'
    #driver.get(url)
    #time.sleep(3)
    ## clicking on archive listings
    #buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    #for button in buttons:
    #    if 'Archived' in button.text:
    #        driver.execute_script("arguments[0].click();", button)
    #        time.sleep(3)
    #        break

    #done = False
    #while True:
    #    try:
    #        if done: break
    #        # getting the address of the active listings
    #        arc_div = wait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='archivedListingsContainer' and @class='tabContent']")))
    #        try:
    #            elems = wait(arc_div, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='item-cnt clearfix']")))
    #        except:
    #            break
    #        nelem = len(elems)
    #        for i in range(nelem):
    #            arc_div = wait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='archivedListingsContainer' and @class='tabContent']")))
    #            try:
    #                elems = wait(arc_div, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='item-cnt clearfix']")))
    #            except:
    #                done = True
    #                break
    #            try:
    #                buttons = wait(elems[0], 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    #                for button in buttons:
    #                    if button.text.strip() == 'Delete':
    #                        driver.execute_script("arguments[0].click();", button)
    #                        time.sleep(2)
    #                        break
    #                popup = wait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.psrk-popup.visible")))
    #                button = wait(popup, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-primary")))
    #                driver.execute_script("arguments[0].click();", button)
    #                time.sleep(5)
    #            except:
    #                continue
    #    except:
    #        driver.quit()
    #        driver = initialize_bot()
    #        p2h_login(driver, name, pwd)
    #        print('Deleting all archive Listings in P2H ....')
    #        print('-'*100)
    #        url = 'https://www.point2homes.com/Account/MyListings'
    #        driver.get(url)
    #        # clicking on archive listings
    #        buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    #        for button in buttons:
    #            if button.text.strip() == 'Archived':
    #                driver.execute_script("arguments[0].click();", button)
    #                time.sleep(3)
    #                break

    #sys.exit()
    ############################################################################
    #ncomp = len(completed)
    #print(f'Total number of existing listings: {ncomp}')
    # reading exclusions list
    try:
        df_ex = pd.read_csv('exclusions.csv', encoding = 'unicode_escape', engine ='python')
        exc = df_ex['name'].tolist()
    except:
        exc = []
        line = 'Warning: No brokerage exclusion file is found or file is corrupted, all the listings will be included'
        #print(COLOR["YELLOW"], line, COLOR["ENDC"])
        print(colored(line, 'yellow'))    
        
    print('Creating Listings in Point2homes....')
    print('-'*100)
    # creating the listings
    inds = df.index
    total = len(inds)
    url = "https://www.point2homes.com/Account/AddAListing"
    for m, ind in enumerate(inds):

        try:
            driver.get(url)
            alert = wait(driver, 3).until(EC.alert_is_present())
            # Press the OK button
            alert.accept()
            current_page = driver.current_url
        except:
            # Wait for the alert to be displayed and store it in a variable
            current_page = driver.current_url

        time.sleep(3)  
        if current_page != url:
            line = f"Warning: failed to login to the Point2homes, Please make sure to provide correct credentials! Exiting the program ..."
            print(colored(line, 'red'))
            input('Press any key to exit')
            sys.exit()
        try:
            skip = False
            house = df.iloc[ind]
            # skip listings already added to the site
            for elem in completed:
                add = elem.split('_')[0]
                beds = elem.split('_')[1]
                baths = elem.split('_')[2]
                price = elem.split('_')[3]
                # if address, baths, beds and price matches then skip
                if house['address'].strip() == add and str(house['bedrooms']).strip() == beds and str(house['washrooms']).strip() == baths and str(house['price']).strip() == price: 
                    skip = True
                    break

            if skip: continue

            # skip listings in the exclusion list based on BROKERAGE 
            skip = False
            for elem in exc:
                if elem.lower() in house['des'].lower(): 
                    print(f"Skipping listing '{house['address']}' for being in the exclusion list")
                    skip = True
                    break
            if skip: continue

            # Address input
            try:
                address = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@id='Address' and @name='Address']")))
                address.send_keys(house['address'])
                #driver.execute_script(f"document.getElementById('AddressLocation_Address').value='{house['address']}'")
                time.sleep(1)   
            except:
                line = f"Warning: failed to correctly add the address of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
                print(colored(line, 'yellow'))        
            
            # unit number input
            #try:
            #    unit = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@id='AddressLocation_AddressSuite' and @name='AddressLocation.AddressSuite']")))
            #    if house['condo#'] != '-1':
            #        unit.send_keys(str(house['condo#']))
            #    elif str(house['condo#']) == '-1' and house['type'] == 'Condominium':
            #        num = str(house['level']) + '-' + str(house['unit#'])
            #        unit.send_keys(num)
            #    time.sleep(2)   
            #except:
            #    line = f"Warning: failed to correctly add the unit number of listing '{house['address']}' in point2homes,\n please update manually"
            #    #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
            #    print(colored(line, 'yellow'))

            # city input
            try:
                city_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='citySelector' and @name='CityGeoId']")))
                sel = Select(city_menu)
                options = wait(city_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))
                city = house['area'].strip()
                for option in options:
                    if option.text == city:
                        sel.select_by_visible_text(city)  
                        break
                time.sleep(1)
            except:
                line = f"Warning: failed to correctly add the city of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow')) 

            # Neighborhood input
            try:
                nei_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='neighborhoodSelector' and @name='NeighborhoodGeoId']")))
                sel = Select(nei_menu)
                options = wait(nei_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))
                nei = house['district'].strip()
                for option in options:
                    if option.text == nei:
                        sel.select_by_visible_text(nei)  
                        break
                time.sleep(1)
            except:
                line = f"Warning: failed to correctly add the neighborhood of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"]) 
                print(colored(line, 'yellow'))

            # zip code input
            try:
                driver.execute_script(f"document.getElementById('ZipCode').value='{house['zip']}'")
                time.sleep(1)
            except:
                line = f"Warning: failed to correctly add the zip code of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))
              
            # MLS num input            
            #try:
            #    house['MLS'] = str(house['MLS'])
            #    driver.execute_script(f"document.getElementById('AddressLocation_MLSNumber').value='{house['MLS']}'")
            #    time.sleep(2)
            #except:
            #    line = f"Warning: failed to correctly add the MLS number of listing '{house['address']}' in point2homes,\n please update manually"
            #    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            #    print(colored(line, 'yellow'))

            # price input
            try:
                house['price'] = str(house['price'])
                driver.execute_script(f"document.getElementById('Price').value='{house['price']}'")
                time.sleep(1)  
            except:
                line = f"Warning: failed to correctly add the price of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))

            # description input
            try:
                frame = wait(driver, 60).until(EC.presence_of_element_located((By.ID, "Description_ifr")))
                driver.switch_to.frame(frame)
                time.sleep(2)
                des = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//body[@id='tinymce']")))
                des.send_keys(house['des'])
                #driver.execute_script("arguments[0].value = arguments[1]", des, house['des'])
                time.sleep(1)
            except:
                line = f"Warning: failed to correctly add the description of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))

            driver.switch_to.default_content()

            # type input
            try:
                type_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='BuildingDetails_Type' and @name='BuildingDetails.Type']")))
                sel = Select(type_menu)
                options = wait(type_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))

                for option in options:
                    if option.text == 'Residential':
                        sel.select_by_visible_text(option.text)  
                        break
                time.sleep(1)
            except:
                line = f"Warning: failed to correctly add the type of listing '{house['address']}' in point2homes,\n please update manually"

            # style input
            try:              
                style_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='residentialSubTypes' and @name='BuildingDetails.SubType']")))
                sel = Select(style_menu)
                options = wait(style_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))
  
                if int(house['fee']) == -1:
                    style = house['type'].strip()
                else:
                    style = house['style'].strip()

                selected = False
                for option in options:
                    if option.text == style:
                        sel.select_by_visible_text(style)
                        selected = True
                if not selected:
                    sel.select_by_visible_text("Single family")
                time.sleep(1)  
            except:
                line = f"Warning: failed to correctly add the style of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))        
   
            # ownership input
            try:
                own_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='BuildingDetails_OwnershipType' and @name='BuildingDetails.OwnershipType']")))
                sel = Select(own_menu)
                options = wait(own_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))

                for option in options:
                    if option.text == 'Condominium':
                        sel.select_by_visible_text(option.text)  
                        break
                time.sleep(1)
            except:
                line = f"Warning: failed to correctly add the ownership of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))

            # type and stories inputs for listing only not condo
            if house['type'] != 'Condominium':
                try:              
                    type_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='BuildingDetails_BuildingUnitType' and @name='BuildingDetails.BuildingUnitType']")))
                    sel = Select(type_menu)
                    options = wait(type_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))
                    type_name = house['type'].strip().replace('-', ' ')

                    for option in options:
                        if option.text == type_name:
                            sel.select_by_visible_text(type_name)
                            break
                    time.sleep(1)  
                except:
                    line = f"Warning: failed to correctly add the type of listing '{house['address']}' in point2homes,\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow'))                 
 
                # stories input
                try:              
                    story_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='BuildingDetails_Stories' and @name='BuildingDetails.Stories']")))
                    sel = Select(story_menu)
                    options = wait(story_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))
                    story = house['style'].strip().split('-')[0]               
                    for option in options:
                        if option.text == story:
                            sel.select_by_visible_text(story)
                            break
                    time.sleep(1)  
                except:
                    line = f"Warning: failed to correctly add the stories of listing '{house['address']}' in point2homes,\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow'))   

            # bedrooms and bathrooms inputs
            try:
                bed = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@id='BuildingDetails_Bedrooms' and @name='BuildingDetails.Bedrooms']")))
                bed.send_keys(str(house['bedrooms']).strip()) 
                #house['bedrooms'] =  str(house['bedrooms']).strip()
                #driver.execute_script(f"document.getElementById('BuildingDetails_BedroomCount').value='{house['bedrooms']}'")
                time.sleep(1)  
            except:
                line = f"Warning: failed to correctly add the number of bedrooms of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))
            try:
                #bath = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@id='BuildingDetails_BathroomCount' and @name='BuildingDetails.BathroomCount']")))
                #bath.send_keys(str(house['washrooms']))
                house['washrooms'] =  str(house['washrooms'])
                driver.execute_script(f"document.getElementById('BuildingDetails_Bathrooms').value='{house['washrooms']}'")
                time.sleep(1)  
            except:
                line = f"Warning: failed to correctly add the number of washrooms of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))

            # basement and parking inputs
            if house['park_places'] >= 0:
                try:
                    house['park_places'] =  str(house['park_places'])
                    driver.execute_script(f"document.getElementById('BuildingDetails_GarageStalls').value='{house['park_places']}'")
                    time.sleep(1)  
                except:
                    line = f"Warning: failed to correctly add the parking of listing '{house['address']}' in point2homes,\n please update manually"
                    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                    print(colored(line, 'yellow'))
            try:        
                basement_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='BuildingDetails_HasBasement' and @name='BuildingDetails.HasBasement']")))
                sel = Select(basement_menu)
                options = wait(basement_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))
                basement = house['basement']
                if basement == 'None':
                    basement = 'No'
                else:
                    basement = 'Yes'
                for option in options:
                    if option.text == basement:
                        sel.select_by_visible_text(basement)
                time.sleep(1)  
            except:
                line = f"Warning: failed to correctly add the basement of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))

            # lot inputs
            try:                      
                if house['lot2'] > 0 and house['lot1'] > 0:
                    house['lot2'] =  str(house['lot2'])
                    driver.execute_script(f"document.getElementById('Lot_DimensionLength').value='{house['lot2']}'")

                    house['lot1'] =  str(house['lot1'])
                    driver.execute_script(f"document.getElementById('Lot_DimensionWidth').value='{house['lot1']}'")

                    unit_menu = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//select[@id='Lot_LotMeasurementUnit' and @name='Lot.LotMeasurementUnit']")))
                    sel = Select(unit_menu)
                    options = wait(unit_menu, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))
                    for option in options:
                        if option.text == 'feet':
                            sel.select_by_visible_text(option.text)  
                            break
                    time.sleep(1)
            except:
                line = f"Warning: failed to correctly add the lot data of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))

            # taxes and year inputs
            #try:
            #    #tax = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@id='TaxesFees_Tax' and @name='TaxesFees.Tax']")))
            #    #tax.send_keys(str(house['tax']))        
            #    house['tax'] =  str(house['tax'])
            #    driver.execute_script(f"document.getElementById('TaxesFees_Tax').value='{house['tax']}'")
            #    #year = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@id='TaxesFees_TaxYear' and @name='TaxesFees.TaxYear']")))
            #    #year.send_keys(str(house['tax_year']))
            #except:
            #    line = f"Warning: failed to correctly add the tax of listing '{house['address']}' in point2homes,\n please update manually"
            #    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            #    print(colored(line, 'yellow'))
            #try:
            #    house['tax_year'] =  str(house['tax_year'])
            #    driver.execute_script(f"document.getElementById('TaxesFees_TaxYear').value='{house['tax_year']}'")
            #except:
            #    line = f"Warning: failed to correctly add the tax year of listing '{house['address']}' in point2homes,\n please update manually"
            #    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            #    print(colored(line, 'yellow'))        
            #try:
            #    house['fee'] =  str(house['fee'])
            #    if house['fee'] != '-1':
            #        driver.execute_script(f"document.getElementById('TaxesFees_CondoFee').value='{house['fee']}'")
            #except:
            #    line = f"Warning: failed to correctly add the condo fee of listing '{house['address']}' in point2homes,\n please update manually"
            #    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            #    print(colored(line, 'yellow'))

            # uploading house images
            try:           
                # uploading first image
                imgs_path = os.getcwd() + '\\Images\\' + house['address'] + '_' + house['MLS']
                files = os.listdir(imgs_path)
                if len(files) > 0:
                    button = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@id='AddPhotoBtn']")))
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(2)
                    img_path = imgs_path + f'\\img1.png'
                    div2 = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.fileupload-buttonbar")))
                    upload = wait(div2, 60).until(EC.presence_of_element_located((By.TAG_NAME, "input")))
                    upload.send_keys(img_path)
                    time.sleep(2)
                    # click on upload button
                    div2 = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.fileupload-buttonbar")))
                    button = wait(div2, 60).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(5)

                if len(files) > 1:
                    # uploading other images
                    button = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@id='AddPhotoBtn']")))
                    driver.execute_script("arguments[0].click();", button)  
                    time.sleep(3)
                    for file in files:
                        if file == 'img1.png': continue
                        img_path = imgs_path + '\\' + file
                        div2 = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.fileupload-buttonbar")))
                        upload = wait(div2, 60).until(EC.presence_of_element_located((By.TAG_NAME, "input")))
                        upload.send_keys(img_path)
                        time.sleep(0.5)
                    # click on upload button
                    div2 = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.fileupload-buttonbar")))
                    button = wait(div2, 60).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(60)
            except:
                line = f"Warning: failed to correctly add all the images of listing '{house['address']}' in point2homes,\n please update manually"
                #print(COLOR["YELLOW"], line, COLOR["ENDC"])
                print(colored(line, 'yellow'))

            ## features input
            #try:
            #    div = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.account-section")))
            #    elems = wait(div, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.form-group")))
            #    for elem in elems:
            #        items = wait(elem, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "label.lbl-cr.features-checkbox")))
            #        features = house['features']
            #        features = features.replace('"', '').replace("'", '').replace('{', '').replace('}', '').split(',')
            #        for item in items:
            #            for feature in features:
            #                if len(feature.strip()) == 0: continue
            #                feature = feature.strip().replace('Floor', 'Floors')
            #                feature = feature.replace('Laminate', 'Laminate Floors')
            #                if feature.strip() == item.text.strip():
            #                #if feature.strip() in item.text.strip() or item.text.strip() in feature.strip():
            #                    button = wait(item, 60).until(EC.presence_of_element_located((By.TAG_NAME, "input")))
            #                    driver.execute_script("arguments[0].click();", button)
            #                    break
            #    time.sleep(2)
            #except:
            #    line = f"Warning: failed to correctly add the features of listing '{house['address']}' in point2homes,\n please update manually"
            #    #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            #    print(colored(line, 'yellow'))

            # Saving the setting
            try:
                buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "button")))
                for button in buttons:
                    if button.text.strip() == 'Save':
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(5)
                        break

                # getting the current page url
                try:
                    current_page = driver.current_url
                except:
                    # Wait for the alert to be displayed and store it in a variable
                    alert = wait(driver, 3).until(EC.alert_is_present())
                    # Press the OK button
                    alert.accept()
                    current_page = driver.current_url


                # listing is not saved successfully
                if current_page == url:
                    line = f"Warning: failed to correctly save the listing '{house['address']}' in point2homes, skipping listing ..."
                    print(colored(line, 'yellow'))
                    continue
                # listing is saved successfully
                else:
                    buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
                    for button in buttons:
                        if 'Drafts' in button.text:
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                            break
                    div = wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@id='draftListingsContainer']")))
                    divs = wait(div, 60).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='item-cnt clearfix']")))
                    for div in divs:
                        buttons = wait(div, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
                        for button in buttons:
                            if button.text.strip() == 'Activate':
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(1)
                                break                                         
                        buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, "button")))
                        for button in buttons:
                            if button.text.strip() == 'Activate now':
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(10)
                                break
            except:
                line = f"Warning: failed to correctly save the listing '{house['address']}' in point2homes, skipping listing ..."
                print(colored(line, 'yellow'))

            line = f'Listing {m+1} of {total} is added successfully'
            print(colored(line, 'green'))
        except:
            line = f"Warning: Unknown failure ocurred, restarting the session ..."
            print(colored(line, 'yellow'))
            print('-'*100)
            driver.quit()
            time.sleep(5)
            driver = initialize_bot()
            p2h_login(driver)
            continue


def initialize_output():

    path = os.getcwd()
    # removing the previous output files
    if os.path.exists(path + '\\Images'):
        shutil.rmtree(path + '\\Images')  

    files = os.listdir(path)
    for file in files:
        if file == 'houses.csv':
            os.remove(file)

    header = ['features', 'address', 'area', 'city', 'zip', 'price', 'district', 'tax', 'tax_year', 'type', 'style', 'bedrooms', 'washrooms', 'lot1', 'lot2', 'fee', 'basement', 'park_places',  'unit#', 'level', 'MLS', 'condo#', 'des']


    filename = 'houses.csv'

    if path.find('/') != -1:
        output = path + "/" + filename
    else:
        output = path + "\\" + filename

    with open(output, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)    
        
    return output
  
def resume_output():

    found = False
    path = os.getcwd()
    files = os.listdir(path)
    for file in files:
        if file == 'houses.csv':
            found = True
            if path.find('/') != -1:
                output = path + "/" + file
            else:
                output = path + "\\" + file
            break

    if found:
        return output
    else:
        return 'N/A'

def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux
    else:
        _ = os.system('clear')

if __name__ == '__main__':

    os.system("color")              
    ## point2homes credentials input
    while True:
        name = input('Please enter P2H username: ')
        if len(name) > 0:
            break
        else:
            print('Invalid username, please try again!')
            print('-'*100)
            continue    

    print('-'*100)    
    while True:
        #pwd = input('Please enter the password: ')
        pwd = (getpass_ak.getpass('Please enter the password: '))
        if len(pwd) > 0:
            break
        else:
            print('Invalid password, please try again!')
            print('-'*100)
            continue

    # mode input
    mode = ''
    while True:
        print('-'*100)
        mode = input('Do you wish to start a new scraping session or resume the last one? \n 1: New Session \n 2: Resume Current Session \n')
        try:
            mode = int(mode)
        except:
            print('Invalid input, please try again!')
            continue

        if mode == 1 or mode == 2:
            break
        else:
            print('Invalid input, please try again!')
            continue

    url = ''
    if mode == 1:
        print('-'*100)
        # MLS link input
        while True:
            url = input('Please enter the link of the listings: \n')
            if 'torontomls.net' in url or 'realmmlp' in url:
                break
            else:
                print('Invalid MLS link, please try again!')
                print('-'*100)
                continue  

    if mode == 1:
        try:
            output = initialize_output()
        except:
            line = 'Error: Failure in deleting the previous output file or creating the new one!  Existing the program ...'
            print(colored(line, 'red'))
            input('Press any key to exit')
            sys.exit()
            
    else:
        # if no images folder is found then start a new session
        if not os.path.exists(os.getcwd() + '\\Images'):
            line = "Error: couldn't locate the listings images folder, Existing the program ..."
            print(colored(line, 'red'))
            input('Press any key to exit')
            sys.exit()
            
        else:
            try:
                output = resume_output()
            except:
                line = 'Error: Failure in accessing the previous output file! Existing the program ...'
                print(colored(line, 'red'))
                input('Press any key to exit')
                sys.exit()


    # if no csv file is found then start a new session
    if output == 'N/A':
        line = "Error: couldn't locate the input file 'houses.csv', Existing the program ..."
        print(colored(line, 'red'))
        input('Press any key to exit')
        sys.exit()

        
    start_time = time.time()
    # initializing web driver
    driver = initialize_bot()
    clear_screen()
    ###################################################
    # user inputs
    #name = ""
    #pwd = ""
    #url = 'https://app.realmmlp.ca/shared/portal/k99qVym8bbI5kwQ34731/bjZNGj95YRhV8M8M9AnbFM5yReXRKNunE8n9J2N5uAKpMgy5yqImoQRylb12f2pEe1Azrrt8AOWRL5K4S3NgVJRwyLUemQk7z8p9IMnDr6ajPKteAlw9wRA4CJpmM2NRB2SzA4rBn3BZt48nV3J?%24orderby=modified+desc%2C+price&active&is_map_search=true&mode=card&ne_lat=45.12387363842464&ne_lng=-77.34393480015373&offset=1&q=treb%2FlistingID%3AN5625215%2CN5619566%2CN5611882%2CN5598844%2CN5619093%2CN5625529%2CN5628733%2CN5582804%2CN5591551%2CN5608185%2CN5584811%2CN5628601%2CN5624992%2CN5594260%2CN5626500%2CN5603604%2CN5571328%2CN5508352%2CN5587919%2CN5614366%2CN5606448%2CN5614886%2CN5631482%2CN5621988%2CN5582397%2CN5622673%2CN5625859%2CN5630996%2CN5627860%2CN5632370%2CN5609839%2CN5589768%2CN5579227%2CN5618776%2CN5619953%2CN5571433%2CN5603133%2CN5618558%2CN5629291%2CN5619235%2CN5622814%2CN5614464%2CN5629799%2CN5630786%2CN5627585%2CN5630150%2CN5630891%2CN5629642%2CN5609715%2CN5617495%2CN5610993%2CN5623119%2CN5624147%2CN5615648%2CN5597475%2CN5622419%2CN5631633%2CN5601229%2CN5627469%2CN5627160%2CN5632038%2CN5600846%2CN5579492%2CN5623476%2CN5624140%2CN5621327%2CN5591323%2CN5605523%2CN5581315%2CN5619522%2CN5541923%2CN5609163%2CN5626342%2CN5624579%2CN5556621%2CN5615652%2CN5603285%2CN5617064%2CN5624773%2CN5572502%2CN5609112%2CN5625399%2CN5531729%2CN5511147%2CN5618614%2CN5622975%2CN5546397%2CN5611809%2CN5608044%2CN5591700%2CN5615858%2CN5624242%2CN5602530%2CN5600499%2CN5627584%2CN5609956%2CN5585625%2CN5626680%2CN5620549%2CN5604708&sw_lat=42.74695474460297&sw_lng=-82.04608323765373&z=8'
    #mode = 2
    #if mode == 2:
    #    output = resume_output()
    ####################################
    while True:
        try:
            print('-'*100)
            print('Scraping Listings Details....')
            print('-'*100)
            # processing scraped listings
            df = pd.read_csv(output)
            scraped = df['address'].values.tolist()
            if 'torontomls' in url and mode == 1:
                scrape_torontomls_data(driver, scraped, url, output)            
            elif 'realmmlp' in url and mode == 1:
                scrape_realmmlp_data(driver, scraped, url, output)
            df_listings = pd.read_csv('houses.csv')
            print('-'*100)
            create_listing(df_listings, name, pwd, driver)          
            break
        except SystemExit:
            input('Press any key to exit')
            sys.exit()

        except Exception as err:
            print(err)
            line = 'Warning: Unknown failure ocurred, restarting the session ...'
            #print(COLOR["YELLOW"], line, COLOR["ENDC"])
            print(colored(line, 'yellow'))
            print('-'*100)
            driver.quit()
            time.sleep(3)
            driver = initialize_bot()
            clear_screen()

    driver.quit()
    # removing the output files
    #path = os.getcwd()
    #if os.path.exists(path + '\\Images'):
    #    shutil.rmtree(path + '\\Images')     
    #if os.path.exists(path + '\\houses.csv'):
    #    os.remove(path + '\\houses.csv') 
    print('-'*100)
    print('Process Completed successfully! Total Elapsed time is {:.1f} mins'.format((time.time() - start_time)/60))
    print('-'*100)
    input('Press any key to exit')
