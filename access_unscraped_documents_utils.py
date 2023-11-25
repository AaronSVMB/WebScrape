"""Code to access documents on the British Library that our current
scraping code and logical parameters cannot reach by the 1001 capacity per search
that the British Library website allows a user to view"""

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

url = 'http://estc.bl.uk/F/T73SLDT1IQYIGAPLANDL93JQUXE7MCA67GGQ15A2FR9VYSJF41-02131?func=file&file_name=find-d'

search_params_common = {'filter_request_1': 'eng', 'filter_request_4': 'enk'}

year_list = [year for year in range(1500, 1801)]

added_logical_params = ['alldocuments AND London AND be', 'alldocuments AND London NOT be', 'alldocuments NOT London']

logic_to_try_list = ['an', 'and']

logic_and = ' AND '
logic_not = ' NOT '

# ============================================================================================
# Functions
# ============================================================================================

# Better Idea

def advanced_search_interface_added_logic_level_one(url: str, year: int, search_params_common: dict,
                                          current_logic: str, logic_to_try: str,
                                          and_or_not: str):
    """ Modifies the advanced search interface function to accomodate multiple strings of logic level additions

    :param url: url for the advanced search page
    :param year: the current year that is going to be scraped for
    :param search_params_common: English and England parameters that are constants across all requests
    :param current_logic: the base logic that we are going to be modifying
    :param logic_to_try: logical argument to append to current_logic to try to get more data points
    :param and_or_not: AND or NOT respectively
    :return: a tuple of (num_results, added_logic, current_search_urls) names reveal their purpose
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

    # Above code comes directly from advanced_search_interface from functionalize_params.py
    # Below adds the new logical steps

    # Store the displayed output of 'total number of records'
    try:
        link_element = driver.find_element(By.XPATH, '//a[contains(@href, "func=short-0")]')
    except NoSuchElementException:
        print('The element was not found')
        link_element = None
    if link_element:
        num_results = int(link_element.text.strip())
    else:
        print(f'Initial Search for {year} and {current_logic} already has 0 results')
        return None, None, None

    if num_results > 1001:
        # Revise current logical entry
        added_logic_first_level = current_logic + and_or_not + logic_to_try
        # Refind Logic area
        logical_entry_element = driver.find_element(By.NAME, 'request')
        logical_entry_element.clear()
        logical_entry_element.send_keys(added_logic_first_level)

        # Search again
        search_button = driver.find_element(By.XPATH, '//*[@alt="Go"]')
        search_button.click()

        # Proceed
        try:
            search_result_link = driver.find_element(By.XPATH, '//a[contains(@href, "func=short-0")]')
        except NoSuchElementException:
            print("The element was not found")
            search_result_link = None
            # If a hyperlink is found, click it
        if search_result_link:
            # update num_results to use to decide if a second logic level is needed in another function
            num_results = int(search_result_link.text.strip())
            search_result_link.click()
        else:  # Handle the case where no search results are found
            print(f"No search results found for {year} with {added_logic_first_level}")
            return None, None, None

        # Now I'm on the new page. With this, I now want to click on the table's first row hyperlink
        first_table_link = driver.find_element(By.XPATH, '//table//a[contains(@href, "set_entry=000001")]')
        first_table_link.click()

        current_url_first_level = driver.current_url  # First Level case

        return num_results, added_logic_first_level, current_url_first_level
    else:
        print(f'year {year} with logic {current_logic} does not need additional scraping')
        return None, None, None

# Test

"""test_num_results, test_added_logic, test_url = advanced_search_interface_added_logic_level_one(url, 1793, search_params_common, added_logical_params[0], logic_to_try_list[0], logic_and)
print(test_num_results, test_added_logic, test_url)"""

def switch_last_and_to_not(added_logic_any_level: str):
    """ Takes a logical statement of ANDs and NOTs and switches the final AND to a NOT to get all cases for a sub logical argument class

    :param added_logic_any_level: logical statement that ends with an AND
    :return: the added_logic_any_level with the final AND as a NOT
    """
    words = added_logic_any_level.split()
    reversed_words = words[::-1]

    # Find the index of the first 'AND' in the reversed list and replace it with 'NOT'
    for i, word in enumerate(reversed_words):
        if word == 'AND':
            reversed_words[i] = 'NOT'
            break  # Break out of the loop once the first 'AND' is found and replaced

    # Reverse the list back and join to form the final string
    added_logic_any_level_opposite = ' '.join(reversed_words[::-1])

    return added_logic_any_level_opposite


def advanced_search_interface_added_logic_any_level_reverse(url: str, year: int,
                                                            search_params_common: dict,
                                                            added_logic_any_level_opposite: str):
    """ Performs the NOT operation or AND depending on what is set as the base case. Produces url for this case

    :param url: url for the advanced search page
    :param year: the current year that is going to be scraped for
    :param search_params_common: English and England parameters that are constants across all requests
    :param added_logic_any_level_opposite: final AND is a NOT in the logical string
    :return: num_results for this search, current_url to scrape (tuple)
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
    logical_entry_element.send_keys(added_logic_any_level_opposite)

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
        # update num_results to use to decide if a second logic level is needed in another function
        num_results = int(search_result_link.text.strip())
        search_result_link.click()
    else: # Handle the case where no search results are found
        print(f"No search results found for {year} with {added_logic_any_level_opposite}")
        return

    # Now I'm on the new page. With this, I now want to click on the table's first row hyperlink
    first_table_link = driver.find_element(By.XPATH, '//table//a[contains(@href, "set_entry=000001")]')
    first_table_link.click()

    current_url = driver.current_url
    return num_results, current_url


def advanced_search_interface_added_logic_level_two(url: str, year: int, search_params_common: dict,
                                          current_logic: str, logic_to_try: str,
                                          and_or_not: str):
    """ Interact with the advanced search interface for any case of the added second logic level
    (AND AND, AND NOT, NOT NOT, NOT AND)

    :param url: url for the advanced search page
    :param year: the current year that is going to be scraped for
    :param search_params_common: English and England parameters that are constants across all requests
    :param current_logic: the level one logic
    :param logic_to_try: statement to append to current_logic
    :param and_or_not: logical operator AND or NOT
    :return: the url to scrape for the second level logic advanced search
    """
    # Revise current logical entry
    added_logic_second_level = current_logic + and_or_not + logic_to_try

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
    logical_entry_element.send_keys(added_logic_second_level)

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
    else:  # Handle the case where no search results are found
        print(f"No search results found for {year} with {added_logic_second_level}")
        return

    # Now I'm on the new page. With this, I now want to click on the table's first row hyperlink
    first_table_link = driver.find_element(By.XPATH, '//table//a[contains(@href, "set_entry=000001")]')
    first_table_link.click()

    current_url = driver.current_url
    return current_url



def interface_and_scrape_one_iteration(search_url: str, year: int, search_params_common: dict,
                                       base_logic: str, logic_to_try_list: list,
                                       logic_and: str, logic_not: str):
    """

    :param search_url: url for the advanced search page
    :param year: the current year that is going to be scraped for
    :param search_params_common: English and England parameters that are constants across all requests
    :param base_logic: starting logical argument to append logical level one and two to
    :param logic_to_try_list: logical statements to be added
    :param logic_and: AND
    :param logic_not: NOT
    :return: dataframe for the current year | first and second level logic only
    """
    # Create a list to store the dfs to
    df_list = []

    # Always start with AND, and do NOT on second time through
    num_results_and_level_one, logic_level_one_and, logic_level_one_and_result_url = advanced_search_interface_added_logic_level_one(search_url, year, search_params_common, base_logic, logic_to_try_list[0], logic_and)
    if not logic_level_one_and_result_url:  # Handles 0 results case
        return
    df_level_one_and = loopCrawlWhile(logic_level_one_and_result_url)
    df_list.append(df_level_one_and)

    # Create logic level one NOT case

    logic_level_one_not = switch_last_and_to_not(logic_level_one_and)

    num_results_not_level_one, logic_level_one_not_result_url = \
        advanced_search_interface_added_logic_any_level_reverse(search_url, year, search_params_common,
                                                                logic_level_one_not)

    df_level_one_not = loopCrawlWhile(logic_level_one_not_result_url)
    df_list.append(df_level_one_not)

    # Check if Logic level 2 is needed for AND case

    if num_results_and_level_one > 1001:
        # AND, AND
        and_and_level_two_url = advanced_search_interface_added_logic_level_two(search_url, year, search_params_common,
                                                                                logic_level_one_and,
                                                                                logic_to_try_list[1],
                                                                                logic_and)
        df_level_two_and_and = loopCrawlWhile(and_and_level_two_url)
        df_list.append(df_level_two_and_and)

        # AND, NOT

        and_not_level_two_url = advanced_search_interface_added_logic_level_two(search_url, year, search_params_common,
                                                                                logic_level_one_and,
                                                                                logic_to_try_list[1],
                                                                                logic_not)

        df_level_two_and_not = loopCrawlWhile(and_not_level_two_url)
        df_list.append(df_level_two_and_not)

    if num_results_not_level_one > 1001:

        # NOT, AND
        not_and_level_two_url = advanced_search_interface_added_logic_level_two(search_url, year, search_params_common,
                                                                                logic_level_one_not,
                                                                                logic_to_try_list[1],
                                                                                logic_and)

        df_level_two_not_and = loopCrawlWhile(not_and_level_two_url)
        df_list.append(df_level_two_not_and)

        # NOT, NOT
        not_not_level_two_url = advanced_search_interface_added_logic_level_two(search_url, year, search_params_common,
                                                                                logic_level_one_not,
                                                                                logic_to_try_list[1],
                                                                                logic_not)

        df_level_two_not_not = loopCrawlWhile(not_not_level_two_url)
        df_list.append(df_level_two_not_not)

    final_df = pd.concat(df_list, ignore_index=True)

    return final_df


def search_and_scrape_all_logic_levels_loop(search_url: str, year_list: list,
                                            search_params_common: dict, logic_list: list,
                                            logic_to_try_list: list, logic_and: str, logic_not: str):
    """

    :param search_url: url for the advanced search page
    :param year_list: list of all years to analyze
    :param search_params_common: English and England parameters that are constants across all requests
    :param logic_list: list of base logical arguments
    :param logic_to_try_list: logical statements to be added
    :param logic_and: AND
    :param logic_not: NOT
    :return: dataframe across all years | first and second order logic only
    """
    all_year_df_list = []
    for year in year_list:
        for logic in logic_list:
            df = interface_and_scrape_one_iteration(search_url, year, search_params_common,
                                                    logic, logic_to_try_list, logic_and, logic_not)
            if df is not None and not df.empty:
                all_year_df_list.append(df)

    final_df = pd.concat(all_year_df_list, ignore_index=True)

    return final_df


# Test

year_list_subset = [i for i in range(1500,1661)]

data_1550_to_1660_two_levels_of_logic = search_and_scrape_all_logic_levels_loop(url, year_list_subset,
                                                                        search_params_common, added_logical_params,
                                                                        logic_to_try_list, logic_and, logic_not)
data_1550_to_1660_two_levels_of_logic.to_csv('data_1550_to_1660_two_levels_of_logic.csv')

# Important to close chrome driver after testing :D
driver.quit()


