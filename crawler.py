from scraper.scraper import Scraper

sc = Scraper("https://www.amazon.ca", "mechanical keyboard")

sc.open_page()
sc.get_products()

page_len = int(sc.get_last_page_numer())

for page in range(2, page_len+1):
    sc.open_page(page)
    sc.get_products()

sc.create_excel_file("keyboards")

sc.close_page()