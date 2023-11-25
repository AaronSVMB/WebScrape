"""First Strides at Selenium code with interface of British Website"""

from selenium import webdriver
from selenium.webdriver.common.by import By  # Importing By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import chromedriver_autoinstaller
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


options = Options()
options.add_argument("--window-size=1920,1080")

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(options=options)

# print the available methods and attributes of the driver
#print(dir(driver))

url = 'http://estc.bl.uk/F/KHD1ITQBVJIQ6D4SCYGX9LDVKAE5TSCGI45ML8MEN3GBJJNKFB-42326?func=file&file_name=find-d'
driver.get(url)
time.sleep(2)

search_params_common = {'filter_request_1': 'eng', 'filter_request_4': 'enk'}

for param, value in search_params_common.items():
    select_element = driver.find_element(By.NAME, param)  # Using By.NAME here
    select = Select(select_element)
    select.select_by_value(value)

year_list = [year for year in range(1600, 1601)]

for year in year_list:
    text_entry_element = driver.find_element(By.NAME, 'filter_request_2')
    text_entry_element.clear()
    text_entry_element.send_keys(str(year))

logical_params_trials = ['alldocuments AND London', 'alldocuments NOT London']

for trial in logical_params_trials:
    logical_entry_element = driver.find_element(By.NAME, 'request')
    logical_entry_element.clear()
    logical_entry_element.send_keys(trial)

search_button = driver.find_element(By.XPATH, '//*[@alt="Go"]')
search_button.click()

wait = WebDriverWait(driver, 2)

try:
    # Wait for a search result hyperlink to be present, adjust the locator as needed
    search_result_link = wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "func=short-0")]')))
    # If a hyperlink is found, click it
    search_result_link.click()
except TimeoutException:
    # Handle the case where no search results are found
    print("No search results found.")

# now i'm on the new page and i want to click on the first book href, store that, then this feeds
# perfectly into the scraping code that i have and i just need to functionalize teh above, and work on
# the logical arguments

try:
    # Wait for the first hyperlink in the table to be present
    first_table_link = wait.until(EC.presence_of_element_located((By.XPATH, '//table//a[contains(@href, "set_entry=000001")]')))
    # If the hyperlink is found, click it
    first_table_link.click()
except TimeoutException:
    # Handle the case where no such hyperlink is found
    print("No hyperlink found in the table.")

# Now I'm on the page where my scraper can work. I have 2 options | either save this url and make a list of
# urls to give to my scraper, OR start scraping one at a time. Will think on this.

current_url = driver.current_url

# Feed into scrapper :D

#TODO Functionalize this code


time.sleep(4)
driver.quit()

