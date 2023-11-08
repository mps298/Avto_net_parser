import time
from copy import deepcopy
from bs4 import BeautifulSoup
from selenium import webdriver
import random
from aiogram.types import ReplyKeyboardMarkup

all_brands = {}
all_models = {}

headers = {
    "Accept": "ext/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
}


def get_url(brand='', model="", price_min='0', price_max='999999', year_min='0', year_max='2090', fuel='0', km_min='0',
            km_max='999999', location='0', transmission='0', page=1):
    # fuel codes: 202 - diesel, 201 - petroleum, 0 - any
    # location codes; 0 - any, 1 - LJ, 2 - Mb, etc.
    # transmission codes: 0 - any, 1 - Automatic, 2 - Manual

    result_url = (f'https://www.avto.net/Ads/results.asp?znamka={brand}&model={model}&modelID=&tip=&znamka2='
                  f'&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin={price_min}&cenaMax={price_max}'
                  f'&letnikMin={year_min}&letnikMax={year_max}&bencin={fuel}&starost2=999&oblika='
                  f'&ccmMin=0&ccmMax=99999&mocMin=&mocMax=&kmMin={km_min}&kmMax={km_max}&kwMin=0'
                  f'&kwMax=999&motortakt=&motorvalji=&lokacija={location}&sirina=&dolzina='
                  f'&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer='
                  f'&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&doseg=&EQ1=1000000000'
                  f'&EQ2=1000000000&EQ3=1000000000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000'
                  f'&EQ7=1110100020&EQ8=101000000&EQ9=1000000020&KAT=1012000000&PIA=&PIAzero=&PIAOut='
                  f'&PSLO=&akcija=&paketgarancije=0&broker=&prikazkategorije=&kategorija=&ONLvid=&ONLnak='
                  f'&zaloga=10&arhiv=&presort=&tipsort=&stran={page}&subTRANS={transmission}')

    return result_url


def get_data(brand="", model="", price_min='0', price_max='999999', year_min='0', year_max='2090', fuel='0', km_min='0',
             km_max='999999', location='0', transmission='0', page=1):
    try:
        options = webdriver.FirefoxOptions()
        options.set_preference("general.useragent.override",
                               headers["User-Agent"])
        driver = webdriver.Firefox(options=options)
        url = get_url(brand, model, price_min, price_max, year_min, year_max,
                      fuel, km_min, km_max, location, transmission, page)
        driver.get(url=url)
        time.sleep(random.randint(6, 10))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_links = soup.find_all("div", class_="row bg-white position-relative GO-Results-Row GO-Shadow-B")

        driver.close()
        driver.quit()

    except Exception as exception:
        print(exception)

    #  Checking if there are more pages in pagination

    page_exists = True
    previous_links = deepcopy(all_links)
    next_page_number = 2

    while page_exists:
        try:
            options = webdriver.FirefoxOptions()
            options.set_preference("general.useragent.override",
                                   headers["User-Agent"])
            driver = webdriver.Firefox(options=options)
            url = get_url(brand, model, price_min, price_max, year_min, year_max,
                          fuel, km_min, km_max, location, transmission, page=next_page_number)
            driver.get(url=url)
            time.sleep(random.randint(6, 10))
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            driver.close()
            driver.quit()

        except Exception as exception:
            print(exception)

        current_links = soup.find_all("div", class_="row bg-white position-relative GO-Results-Row GO-Shadow-B")

        # checking pages for repetition
        first_a_in_current_links = BeautifulSoup(str(current_links), 'html.parser').find('a')
        first_a_in_previous_links = BeautifulSoup(str(previous_links), 'html.parser').find('a')

        if len(current_links) == 0 or len(previous_links) == 0 or first_a_in_current_links == first_a_in_previous_links:
            page_exists = False
        else:
            print('page' + str(next_page_number))
            for link in current_links:
                all_links.append(link)

            previous_links = current_links
            next_page_number += 1

    soup = BeautifulSoup(str(all_links), 'html.parser')

    result_urls = []
    result_titles = []
    result_images = []
    result_prices = []

    # parsing urls
    urls = BeautifulSoup(str(soup.find_all('div', class_="col-auto p-3 GO-Results-Photo")),
                         'html.parser').find_all('a')
    counter = 1
    for link in urls:
        url = link.get("href")
        url = url.replace("..", "https://www.avto.net")
        result_urls.append(url)
        print(f"{counter} url = {url}")
        counter += 1
    print(f"-----------------------------------\n{len(result_urls)} urls\n")

    # parsing images
    images = BeautifulSoup(str(soup.find_all('div', class_="col-auto p-3 GO-Results-Photo")),
                           'html.parser').find_all('img')
    counter = 1
    for link in images:
        image = link.get("src")
        if not '.jpg' or ".." in image:
            continue
        result_images.append(image)
        print(f"{counter} image = {image}")
        counter += 1
    print(f"-----------------------------------\n{len(result_images)} images\n")

    # parsing texts
    titles = BeautifulSoup(str(soup.find_all('div', class_="col-auto p-3 GO-Results-Photo")),
                           'html.parser').find_all('img')
    counter = 1
    for link in titles:
        title = link.get("title")
        if title:
            result_titles.append(title)
            print(f"{counter} title = {title}")
            counter += 1
    print(f"-----------------------------------\n{len(result_titles)} titles\n")

    # getting prices

    prices = (BeautifulSoup(str(BeautifulSoup(str(all_links), 'html.parser').find_all("div",
        class_='d-none d-sm-block col-auto px-sm-0 pb-sm-3 GO-Results-PriceLogo')), 'html.parser').find_all
        ('div', {'class': ['GO-Results-Price-TXT-Regular', 'GO-Results-Price-TXT-AkcijaCena']}))


    counter = 1
    for link in prices:
        price = link.text
        if price:
            result_prices.append(price)
            print(f"{counter} price = {price}")
            counter += 1
    print(f"-----------------------------------\n{len(result_prices)} prices\n")


    if len(result_titles) == len(result_urls) == len(result_images) == len(result_prices):
        results = []
        for i in range(len(result_images)):
            results.append([result_images[i], result_titles[i], result_urls[i], result_prices[i]])
        return results
    else:
        return f"Something went wrong... /start to try another search"


def get_keyboard(buttons_to_add, columns=3):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    counter = 1
    for button in buttons_to_add:
        keyboard.insert(button)
        if not counter % columns:
            keyboard.row()

    return keyboard


def get_all_brands():
    all_brands_found = {}

    all_cars_url = "https://www.avto.net/Ads/search_makes.asp"

    options = webdriver.FirefoxOptions()
    options.set_preference("general.useragent.override",
                           headers["User-Agent"])
    driver = webdriver.Firefox(options=options)
    driver.get(url=all_cars_url)
    # time.sleep(random.randint(6, 10))
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.close()
    driver.quit()



    all_links = soup.find_all("a", class_="stretched-link font-weight-bold text-decoration-none text-truncate d-block")
    for link in all_links:
        tmp_key = link.string
        brand_key = ""
        brand_key = brand_key.join(c for c in tmp_key if c.isalnum() or c == ' ' or c == '(' or c == ')' or c == '-')
        brand_key = brand_key.strip()
        brand_value = "https://www.avto.net/Ads/" + link["href"]

        all_brands_found[brand_key] = brand_value

    return all_brands_found


def get_all_models(url):
    all_models_found = []

    options = webdriver.FirefoxOptions()
    options.set_preference("general.useragent.override",
                           headers["User-Agent"])
    driver = webdriver.Firefox(options=options)
    driver.get(url=url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_links = soup.find_all("div", class_="col-12 px-0")
    soup = BeautifulSoup(str(all_links), 'html.parser')
    all_links = soup.find_all("span", class_="text-truncate")

    for link in all_links:
        tmp_key = link.string
        model = ""
        model = model.join(c for c in tmp_key if c.isalnum() or c == ' ' or c == '(' or c == ')' or c == '-')
        model = model.strip()

        if 'ostali modeli' in model:
            continue
        all_models_found.append(model)

    return all_models_found
