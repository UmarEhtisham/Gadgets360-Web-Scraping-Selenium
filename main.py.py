import logging
import time
import os

import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException,
)

class DataScraping:

    def __init__(self, clicks_input, driver_path, website_url) -> None:

        self.max_clicks = clicks_input
        self.driver_path = driver_path
        self.website_url = website_url
        self.driver = None
        self.old_clicks = 0
        self.load_click = 0
        self.variable_elements = 0
        self.main_df = pd.DataFrame()
        self.specs_dict = {} 
        self.dict_collection_list = []
        self.popup_closed = False
        self.model_data = []
        self.released_date_data = []
        self.full_price_data = []
        self.discounted_price_data = []

    def start(self):

        logging.info("Initializing the Chrome driver and opening the website.")
        # Set the different otpions for the browser
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Ignore the certificate and SSL errors
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')

        # Maximize the browser window
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument('--incognito')

        # define the driver path
        service = Service(self.driver_path)

        # Define the driver and open the browser
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(self.website_url)

        try:

            time.sleep(10)
            logging.info("Website loaded successfully.")

        except TimeoutException:
            logging.error("Timeout waiting for website to load.")

    def dataset_info(self):

        try:
            
            data_file = "dataset.csv"

            if not os.path.exists(data_file):
                logging.info("No dataset file detected")

            else:
                df = pd.read_csv(data_file)
                self.variable_elements = len(df)
                self.main_df = df
                self.old_clicks = (len(df) - 20) // 20

                if self.old_clicks:    
                    logging.info("Old clicks have been re-assigned")
                else:
                    logging.info("Dataset exists but no old clicks found")
                
        except Exception as e:
            logging.error(f"Error reading the data file: {e}")

    def load_data(self):

        counter = 0

        try:

            if self.load_click != self.old_clicks:
                logging.info("Retreiving old data")
                
            while self.load_click != self.old_clicks:
                
                self.click_and_click()
                time.sleep(2)
                self.load_click += 1
            
            if counter != self.max_clicks:
                logging.info("New data is being fetched")

            while counter != self.max_clicks:      
                self.click_and_click()
                counter += 1

        except Exception as e:
            print("Some problem found in while loops")

    def click_and_click(self):

        temp_counter = 0

        try:

            load_more_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, './/span[@class="load-more _btn"]'))
                )     
            self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button) 

            time.sleep(1)
            if not self.popup_closed:
                self.close_popup()
                self.popup_closed = True

            temp_counter += 1
            time.sleep(1)  
            load_more_button.click()

            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, './/div[contains(@class,"_flx _lpbwg")]')) > temp_counter * 20
            )

            time.sleep(1)

        except ElementClickInterceptedException:
            logging.warning("Click intercepted, scrolling and retrying...")
            self.driver.execute_script("window.scrollBy(0, 200);")  # Scroll by a larger amount to avoid interception
        

        except TimeoutException:
            logging.warning("Timeout occurred while clicking 'Load More' button.")
        

        except NoSuchElementException:
            logging.warning("No more 'Load More' button or elements found.")
        

    def close_popup(self):
          
        try:
        # Wait for the popup to appear and close it
                popup_close_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, 'btnClosenotify'))  # Adjust the ID accordingly
                )
                popup_close_button.click()
                logging.info("Popup closed.")
        
        except TimeoutException:
                logging.info("No popup to close.")
    
        except Exception as e:
                logging.error(f"Error while closing popup: {e}")

    def extract_data(self):
            
        try:

            wait = WebDriverWait(self.driver, 10)
            parent_elements = wait.until(EC.presence_of_element_located((By.ID, 'allplist')))

            child_elements = parent_elements.find_elements(By.XPATH, './/div[contains(@class, "_flx _lpbwg")]')
            
            new_elements = len(child_elements) - self.variable_elements
        
            logging.info(f"{new_elements} Items loaded")
            self.variable_elements += new_elements
            if not new_elements:
                return {}, []

            self.specs_dict.clear()
            self.dict_collection_list.clear()
            inner_specs_dict = {}   

            loop = 1

            logging.info("Item-wise Data scraping is starting now")
            print("-" * 50)

            for element in child_elements[-new_elements:]:
                attempt = 0

                while attempt < 3:

                    try:
    
                        self.modify_data(element)

                        anchor_tag = element.find_element(By.XPATH, './/a[@class="_lpimga"]')
                        url = anchor_tag.get_attribute("href")
                        
                        self.driver.execute_script("window.open('');")

                        self.driver.switch_to.window(self.driver.window_handles[1])

                        self.driver.get(url)

                        wait = WebDriverWait(self.driver, 10)
                        specs = wait.until(EC.presence_of_element_located((By.XPATH, './/div[@class="_pdswrp"]')))

                        key_data = specs.find_elements(By.CLASS_NAME, '_ttl')
                        value_data = specs.find_elements(By.CLASS_NAME, '_vltxt')

                        for key, value in zip(key_data,value_data):
                            inner_specs_dict.update({key.text:value.text})
                        self.dict_collection_list.append(inner_specs_dict)  
                        inner_specs_dict = {}

                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])

                        logging.info(f"Loop-number {loop}, Data Scraping - Done")
                        loop += 1
                        break

                    except (NoSuchElementException, TimeoutException) as e:
                        logging.error(f"Failed: Problem raised while fetching inner specs data: {e}")
                        attempt += 1
                else:
                    logging.error(f"Failed to fetch data for element after {attempt} attempts")

            self.specs_dict.update({
                'model':self.model_data, 
                'released_date': self.released_date_data, 
                'full_price' : self.full_price_data, 
                'discounted_price' : self.discounted_price_data
                })
            
            return self.specs_dict, self.dict_collection_list

        except WebDriverException as e:
            logging.error(f"WebDriverException occurred: {e}")
            return {}, []
        
    def modify_data(self, element):
        
        operations = {"model_number":(By.CLASS_NAME,"_hd", self.model_data),
                      "released":(By.CLASS_NAME,"_dtli", self.released_date_data),
                      "f_price":(By.CLASS_NAME,"_lpcprc", self.full_price_data),
                      "d_price":(By.CSS_SELECTOR,"a._lprc > span", self.discounted_price_data)
                      }
     
        for key, (by, value, data_list) in operations.items():
           
            try:
                outer_data = element.find_element(by, value)
                data_list.append(outer_data.text.strip() if outer_data else np.nan)
                
            except NoSuchElementException:
                data_list.append(np.nan)

    def build_dataframe(self, specs_dict, dict_collection_list):

        print("-" * 50)
        logging.info("Dataset making is starting now")
        print("-" * 50)

        try:

            outer_df = pd.DataFrame(specs_dict)
            inner_df = pd.DataFrame(dict_collection_list)
        
            final_df = pd.concat([outer_df, inner_df], axis=1)

            self.main_df = pd.concat([self.main_df, final_df])

            self.main_df.to_csv(f'dataset.csv', index=False)

            logging.info(f"Dataset has been updated")
            print("-" * 50)

        except Exception as e:
            logging.error("An error occurred while building DataFrame:", e)

    def run(self):
        try:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

            self.start()
            self.dataset_info()
            
       
            while True:
                
                self.load_data()
                self.specs_dict, self.dict_collection_list = self.extract_data()
                
                if self.specs_dict and self.dict_collection_list:
                    
                    self.build_dataframe(self.specs_dict, self.dict_collection_list)
                
                if not self.specs_dict and not self.dict_collection_list:
                    logging.warning("No more data available. Exiting...")
                    break
                
        except Exception as e:
            logging.error("An error occured: %s", e)

        finally:
            if self.driver:
                self.driver.quit()
                logging.warning("Scraping process finished. Browser closed.")

if __name__ == "__main__":

    user_input = int(input("Enter the max clicks size: "))
    chrome_driver_path = "chromedriver.exe"
    website_address =   "https://www.gadgets360.com/mobiles/phone-finder"

    scrape = DataScraping(user_input, chrome_driver_path, website_address)
    scrape.run()
   

 

  
            

