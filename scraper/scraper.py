from math import prod
from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import pandas as pd

# Amazon Product Scraper class
class Scraper():
    def __init__(self, base_url, keyword) -> None:
        self.__base_url = base_url
        self.__keyword = keyword.replace(' ', '+')
        self.__soup = None
        self.__options = webdriver.FirefoxOptions()
        self.__options.headless = True
        self.__driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=self.__options)
        self.__products = []

    def url_builder(self, page_num=None):
        url = f"{self.__base_url}/s?k={self.__keyword}"
        if page_num != None:
            url += f"&page={page_num}"
        return url

    def open_page(self, page_num=None):
        url = self.url_builder(page_num=page_num)
        self.__driver.get(url)
        self.__soup = BeautifulSoup(self.__driver.page_source, 'html.parser')
    
    def close_page(self):
        self.__driver.quit()
    
    def get_last_page_numer(self):
        return self.__soup.select("span.s-pagination-item.s-pagination-disabled")[-1].get_text()

    def get_product_detail_page(self, element):
        return f"https://www.amazon.ca{element.find('a')['href']}"

    def get_product_image_src(self, element):
        src_set = element.find('img')['srcset'].split(',')
        return src_set[-1][:-3]

    def get_product_name(self, element):
        return element.find('h2').get_text()

    def get_product_rating(self, element):
        return element.select('span.a-icon-alt')[0].get_text() if element.select('span.a-icon-alt') else "N/A"

    def get_product_price(self, element) -> str:
        return element.select('span.a-price>span')[0].get_text().replace(',', '') if element.select('span.a-price') else "N/A"

    def get_original_price(self, element) -> str:
        return element.select('span.a-price.a-text-price>span')[0].get_text().replace(',', '') if element.select('span.a-price.a-text-price') else "N/A"

    def get_sale_percent(self, prd) -> str:
        original = self.get_original_price(prd)
        current = self.get_product_price(prd)

        org = float(original.replace("$", "")) if original != "N/A" else None
        curr = float(current.replace("$", "")) if current != "N/A" else None

        if curr != None and org != None:
            diff = org - curr
            return f"{round((diff/org)*100)}%"

        return "N/A"

    def get_products(self):
        products = self.__soup.select('div.sg-col-4-of-12.s-result-item.s-asin.sg-col-4-of-16.sg-col.s-widget-spacing-small.sg-col-4-of-20')
        
        for prd in products:
            self.__products.append({'prod_url': self.get_product_detail_page(prd), 
            'prod_img': self.get_product_image_src(prd), 
            'prod_name': self.get_product_name(prd), 
            'prod_rating': self.get_product_rating(prd),
            'prod_price': self.get_product_price(prd),
            'prod_org_price': self.get_original_price(prd),
            'prod_sale': self.get_sale_percent(prd)
            })

    def create_excel_file(self, file_name):
        df = pd.DataFrame(self.__products)
        df.to_excel(f"{file_name}.xlsx")
