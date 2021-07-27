#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import datetime
import time

# ---------------------------------------------------    Configuration   ---------------------------------------------------
bgg_username = ""
splits = {"–","("}


last_days = int(input("Look for listings of last x days. x=") or "0")
start_date = datetime.datetime.today() - datetime.timedelta(days=int(last_days))
print()

# ---------------------------------------------------        BGG         ---------------------------------------------------

# get bgg-wishlist page
URL = "https://boardgamegeek.com/wishlist/" + bgg_username
page = requests.get(url=URL).content
soup = BeautifulSoup(page, "html.parser")

# array for all bgg-wishlist games
search_words = []

# iterate through all wishlist entries and add names (each until configured split char)
srchRslts = soup.find("table", "collection_table").find_all("a", "primary")
for srchRslt in srchRslts:
    name = srchRslt.text
    ind = next((i for i, ch  in enumerate(name) if ch in splits),None)
    search_words.append(name[:ind])

# --------------------------------------------------- Ebay Kleinanzeigen ---------------------------------------------------

# format current datetime
now = datetime.datetime.now()
prefix = "[" + now.strftime("%H:%M:%S") + "] - "

# set counter for new listings
counter = 0

# iterate through bgg-wishlist games and scrape ebay kleinanzeigen
for name in search_words:

    print(name + "\n")

    # get ebay kleinanzeigen search results page
    URL = "https://www.ebay-kleinanzeigen.de/s-spielzeug/gesellschaftsspiele/" + name + "/k0c23+spielzeug.art_s:gesellschaftsspiele"
    # avoid blocking the request by setting header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
    }
    page = requests.get(url=URL, headers=headers).content
    soup = BeautifulSoup(page, "html.parser")
    
    # check for search results and continue otherwise
    srchRsltsContent = soup.find("ul", id="srchrslt-adtable")
    if srchRsltsContent is None:
        continue

    # iterate through all search results
    srchRslts = srchRsltsContent.find_all("article")
    for article in srchRslts:

        article_date = article.find("div", "aditem-main--top--right")
        if article_date is not None:

            # check if creation date is before start_date
            article_date = article_date.text.strip()
            # format creation dates of yesterday and today
            if (article_date.find('Gestern,') != -1):
                article_date_formatted = datetime.datetime.today() - datetime.timedelta(days=1)
            elif (article_date.find('Heute,') != -1):
                article_date_formatted = datetime.datetime.today()
            else:
                article_date_formatted = datetime.datetime.strptime(article_date, '%d.%m.%Y')        

            if article_date_formatted >= start_date:

                # increment listings counter
                counter = counter + 1

                # print creation date, price, title and url
                title = article.find("a", "ellipsis").text.strip()
                price = article.find("p", "aditem-main--middle--price").text.strip()

                print("               " + article_date + " | " +  price)
                print("               " + title)
                print("               URL: https://www.ebay-kleinanzeigen.de" + article["data-href"] + "\n")
        
            else:
                break

    # delay of 15 seconds to avoid blocking
    time.sleep(15)

# print listings counter
print("\n" + str(counter) + " new listings")
