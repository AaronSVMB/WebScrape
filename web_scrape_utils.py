"""Functions for Web Scrapping British Library"""

# ============================================================================================
# Imports
# ============================================================================================

from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd

# ============================================================================================
# Constants
# ============================================================================================

s = HTMLSession()

# ============================================================================================
# Functions
# ============================================================================================

# ============================================================================================
# Scraping
# ============================================================================================


def getcurrentpage(url: str):
    """ takes the current html page and saves it as a soup with all content and html tags

    :param url: webpage url as a string
    :return soup: html tags and content to be scraped
    """
    r = s.get(url)
    r.encoding = 'utf-8' # fixes accent issue
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def getnextpageurl(soup):
    """ Scan the current page to find the next button which caches the url
    for the next page to loop

    :param soup: page content with html tags
    :return next_href: url for next page content
    """
    next_img_tag = soup.find('img', {'alt': 'Next Record'})
    if next_img_tag:
        next_a_tag = next_img_tag.find_parent('a')
        if next_a_tag:
            next_href = next_a_tag.get('href')
            return next_href
    else:
        return


# ============================================================================================
# Storing Data
# ============================================================================================


def getdatatable(soup):
    """ takes soup and stores the relevant data table found on the page

    :param soup: page content with html tags
    :return df_transposed: pandas df with columns as the labels with the current
    page data as the row
    """
    # Find the table by its id
    table = soup.find('table', {'id': 'estcdata'})

    # Initialize dictionary to hold table data
    data_dict = {}
    last_key = None

    # Loop through each table row
    for tr in table.find_all('tr'):
        # Initialize empty list for each row
        cells = tr.find_all('td')
        key, value = cells[0].text.strip(), cells[1].text.strip()

        # If key is empty, use the last key
        if not key:
            key = last_key

        # Add data to dictionary
        if key in data_dict:
            if isinstance(data_dict[key], list):
                data_dict[key].append(value)
            else:
                data_dict[key] = [data_dict[key], value]
        else:
            data_dict[key] = value

        last_key = key

    # Convert the data dictionary to a DataFrame
    df = pd.DataFrame([data_dict])

    return df


def remove_xa0_from_list(cell):
    """ xa0_ is an html for a type of page break. Our data set was plagued with these, this code manually replaces it

    :param cell: a cell in our data frame
    :return: cleaned data frame rid of xa0_ tags showing up in the data frame
    """
    if isinstance(cell, list):
        return [s.replace('\xa0', ' ') for s in cell]
    else:
        return cell  # return the original cell if it's not a list

# ============================================================================================
# Crawl
# ============================================================================================


def loopCrawlWhile(url: str):
    """ Performs crawl and web scraping processes. Stores data as big df all columns
    This version uses a while loop so it continues until the stopping condition is
    satisfied. This functions stopping condition is when the next button has no href

    :param url: initial webpage to start crawl from
    :return concatenated_df: df with all webpages scraped.
    """
    list_of_dfs = []
    while True:
        soup = getcurrentpage(url)
        pageDf = getdatatable(soup)
        pageDf.reset_index(inplace=True, drop=True)
        list_of_dfs.append(pageDf)
        url = getnextpageurl(soup)
        if not url:
            break
    concatenated_df = pd.concat(list_of_dfs, ignore_index=True)
    concatenated_df = concatenated_df.applymap(remove_xa0_from_list)

    return concatenated_df


def loopCrawlFor(url: str, iterations: int):
    """ Performs crawl and web scraping processes. Stores data as big df all columns
    This version uses a for loop so it can only collect a subset of the data
    unless ex-ante we know the number of urls / web page links

    :param url: initial webpage to start crawl from
    :param iterations: number of webpages to scrape, less than or equal to total number of book results or else run time error
    :return concatenated_df: df with all webpages scraped.
    """
    list_of_dfs = []
    for i in range(iterations):
        soup = getcurrentpage(url)
        pageDf = getdatatable(soup)
        pageDf.reset_index(inplace=True, drop=True)
        list_of_dfs.append(pageDf)
        url = getnextpageurl(soup)

    concatenated_df = pd.concat(list_of_dfs, ignore_index=True)
    concatenated_df = concatenated_df.applymap(remove_xa0_from_list)

    return concatenated_df


# Test

"""url = 'http://estc.bl.uk/F/KHD1ITQBVJIQ6D4SCYGX9LDVKAE5TSCGI45ML8MEN3GBJJNKFB-05975?func=full-set-set&set_number=080885&set_entry=000001&format=999'

loopfor = loopCrawlFor(url, 100)
print(loopfor)"""
