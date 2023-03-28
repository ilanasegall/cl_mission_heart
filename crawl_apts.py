from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time, random, re, csv
#
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options

OUTPUT_FILE = "./cl_apts.csv"
HEART_PHRASES = ["heart of the mission", "heart of mission", "corazon de la mision"]

def is_next_page(driver):
    page_numbers_element_list = driver.find_elements_by_xpath('//body//span[@class="cl-page-number"]')
    page_numbers_text = page_numbers_element_list[0].text
    (page_start, page_end, total) = map(lambda x: int(x), re.findall(r'\d+', page_numbers_text))
    if(page_end < total):
        return True
    return False

def go_to_next_page(driver):
    next_buttons = driver.find_elements_by_xpath('//button[@class="bd-button cl-next-page icon-only"]')
    next_button = next_buttons[0]
    next_button.click()

def get_page_apt_urls(driver):
    links = driver.find_elements_by_xpath('//body/div/main/div[@class="cl-search-results"]/div[@class="results cl-results-page cl-search-view-mode-list"]/ol//li//div//a')
    page_apt_urls = []
    for link in links:
        apt_url = link.get_attribute("href")
        page_apt_urls.append(apt_url)
    return(page_apt_urls)

def process_page(html_soup):
    title = html_soup.find(id="titletextonly").get_text()
    body = html_soup.find(id="postingbody").get_text()
    location = html_soup.find(id="map")
    lat = location.get("data-latitude")
    long = location.get("data-longitude")
    heart_flag = False

    content = (title + body).lower()
    if any([x in content for x in HEART_PHRASES]):
        heart_flag = True

    return(heart_flag, lat, long)

# def write_to_file(heart_flag, lat, long):
#     heart_flag,lat,long

def main():
    apt_urls = []
    heart_list = []

    url_base = "https://sfbay.craigslist.org/search/sfc/apa?nh=18#search=1~list~0~0"

    driver = webdriver.Firefox()
    driver.get(url_base)

    while(True):
        time.sleep(random.random())
        apt_urls.extend(get_page_apt_urls(driver))
        if is_next_page(driver):
            go_to_next_page(driver)
        else:
            break

    #remove duplicates
    apt_urls = list(set(apt_urls))

    for link in apt_urls:
        time.sleep(random.random())
        driver.get(link)
        page_source = driver.page_source
        html_soup = BeautifulSoup(page_source, 'html.parser')
        (heart_flag, lat, long) = process_page(html_soup)
        heart_list.append({"heart": heart_flag, "lat": lat, "long": long})

    with open(OUTPUT_FILE, "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["heart", "lat", "long"])
        for apt in heart_list:
            writer.writerow([apt["heart"], apt["lat"], apt["long"]])
    driver.quit()



if __name__ == "__main__":
    main()



# open('heart_map.csv')


# for apt in apts:
#     link = apt.find("a")["href"]
#     links.append(link)
# print(links)
