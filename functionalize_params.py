"""Code to Functionalize Selenium reading of British Library Website"""

# ============================================================================================
# Imports
# ============================================================================================

from selenium import webdriver
from selenium.webdriver.common.by import By  # Importing By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import chromedriver_autoinstaller
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

import pandas as pd

# Combine
from web_scrape_utils import loopCrawlWhile

# ============================================================================================
# Driver
# ============================================================================================

options = Options()
options.add_argument("--window-size=1920,1080")

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(options=options)

# ============================================================================================
# Params
# ============================================================================================

url = 'http://estc.bl.uk/F/N1AAPMB44PEFES2BHRCSTEL8I9V2UFCS59GGTRU6LMRT5YYJAH-00493?func=file&file_name=find-d'

search_params_common = {'filter_request_1': 'eng', 'filter_request_4': 'enk'}

year_list = [year for year in range(1500, 1801)]

logical_params_trials = ['alldocuments AND London', 'alldocuments NOT London']

added_logical_params = ['alldocuments AND London AND be', 'alldocuments AND London NOT be', 'alldocuments NOT London']

# ============================================================================================
# Functions
# ============================================================================================


def advanced_search_interface(url: str, year: int,
                              search_params_common: dict, current_logic: str):
    """ Interacts with the advanced search interface on the British Library page and gets us to the relevant page
    for our BS4 webscraping code

    :param url: the url for the advanced search page of the British Library website
    :param year: The current year we want to search for and enter as a search parameter
    :param search_params_common: Search parameters used in all searches (english and GB)
    :param current_logic: the logic parameter we are utilizing to reduce the searches to get more data // avoid 1001 cap
    :return: the start_url for my BeautifulSoup4 webscraping code aka the first search result of our request
    """
    driver.get(url)

    # Common Features – England and English
    for param, value in search_params_common.items():
        select_element = driver.find_element(By.NAME, param)  # Using By.NAME here
        select = Select(select_element)
        select.select_by_value(value)

    # Input Current Iteration Year
    text_entry_element = driver.find_element(By.NAME, 'filter_request_2')
    text_entry_element.clear()
    text_entry_element.send_keys(str(year))

    # Input Current Entry Logical Param
    logical_entry_element = driver.find_element(By.NAME, 'request')
    logical_entry_element.clear()
    logical_entry_element.send_keys(current_logic)

    # With all current iteration parameters filled, click search button
    search_button = driver.find_element(By.XPATH, '//*[@alt="Go"]')
    search_button.click()

    # Establish code pause (good practice) – better to use wait, but excessive in our case
    time.sleep(2)

    try:
        search_result_link = driver.find_element(By.XPATH, '//a[contains(@href, "func=short-0")]')
    except NoSuchElementException:
        print("The element was not found")
        search_result_link = None
        # If a hyperlink is found, click it
    if search_result_link:
        search_result_link.click()
    else: # Handle the case where no search results are found
        print(f"No search results found for {year} with {current_logic}")
        return

    # Now I'm on the new page. With this, I now want to click on the table's first row hyperlink
    first_table_link = driver.find_element(By.XPATH, '//table//a[contains(@href, "set_entry=000001")]')
    first_table_link.click()

    current_url = driver.current_url
    return current_url


# ============================================================================================
# Pair with web scrape
# ============================================================================================


def interface_and_scrape_iteration(search_url: str, year: int,
                              search_params_common: dict, current_logic: str):
    """ Provides one iteration of the advanced search page interaction, and BS4 webscraping code that produces one df

    :param search_url: the url for the advanced search page
    :param year: the current year we are interested in
    :param search_params_common: England and English parameters, common to all iterations
    :param current_logic: the current logical argument (x AND y ... // x NOT y // ... )
    :return: a df for the current year, and current logic of all the documents satisfying said conditions
    """
    result_url = advanced_search_interface(search_url, year, search_params_common, current_logic)
    if not result_url:  # Handles 0 results case as to not raise an error
        return
    df = loopCrawlWhile(result_url)
    return df


# ============================================================================================
# Loop for Iterations
# ============================================================================================


def search_and_scrape_loop(search_url: str, year_list: list,
                           search_params_common: list, logic_list: list):
    """ Performs the advanced search page process into the BS4 scraping code for number of years times

    :param search_url: the url for the advanced search page
    :param year_list: list from starting year to stopping year for the current iterations
    :param search_params_common: England and English, common search parameters across all iterations
    :param logic_list: the list of possible logical pairings
    :return: df from all iterations, each year and each logical pairings
    """
    df_list = []
    for year in year_list:
        for logic in logic_list:
            df = interface_and_scrape_iteration(search_url, year, search_params_common, logic)
            df_list.append(df)
    final_df = pd.concat(df_list, ignore_index=True)

    return final_df

# Test

year_list_subset = [i for i in range(1500,1526)]

data_1500_to_1525_three_logic = search_and_scrape_loop(url, year_list_subset, search_params_common, added_logical_params)
data_1500_to_1525_three_logic.to_csv('data_1500_to_1525_three_logic.csv')

# Important to close chrome driver after testing :D
driver.quit()
