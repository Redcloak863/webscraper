from bs4 import BeautifulSoup
import requests
import re
import os
import shutil
import string
# import json

"""
Are the functions necessary? Probably not; but, I don't know at the moment how I'm
going to call their code or how many times.
"""

def validCategories(soup):
    """
    Returns a list of valid categories from the site for the user to pick from.
    :param soup:
    :return categories:
    """
    types_ = soup.find_all(class_='c-facet-expander__list-item')
    '''
    The two pull-down forms use this class. We'll pop off the 2 for the 2nd button later.
    '''
    categories = []
    for type_ in types_:
        categories.append(re.sub("[^A-Za-z&\s]", "", type_.get_text().strip()))  # Will leave a trailing space.
    categories.pop()  # Necessary since this is an empty string. Fat fingering the keyboard could pick this!
    categories.pop()  # You could skip this one since it's 'All' again.
    return categories

def CreateDirectories(pp):
    """
    Creates the folders and deletes old ones if necessary.
    :param pp: The number of pages (depth) we'll scrape.
    :return:
    """
    for p in range(pp):
        dir_name = f'./Page_{p + 1}'
        # print(dir_name)  # For testing only.
        if os.path.isdir(dir_name):
            shutil.rmtree(dir_name)
        os.mkdir(dir_name)

def SaveSummaries(soup, folder):
    """
    Takes the output from Beautiful Soup and creates the summary files
    :param soup: The output from Beautiful Soup
    :param folder: the current ./Page_N/ folder
    :return:
    """
    articles = soup.find_all('article')  # These are the article teasers
    links = soup.find_all(class_='c-card__link')  # These are the links to the content pages
    for article, link in zip(articles, links):
        if article.find(class_='c-meta__type').text == category:  # Note that category is still Caps case.
            title = link.get_text()  # These are the page titles
            filename = ""
            for c in title:
                if c not in string.punctuation:
                    filename += c
            filename = folder + filename.replace(" ", "_") + ".txt"
            # print(filename)
            article_page = requests.get(base + link.get("href"))
            article_soup = BeautifulSoup(article_page.text, 'html.parser').find('main')

            try:
                scrape = article_soup.find(class_='article__teaser').text.strip()
                # print('The article is paywalled.')
            except AttributeError:
                scrape = article_soup.find(class_='c-article-teaser-text').text.strip()
                # print('The article isn\'t paywalled.')

            try:
                with open(filename, 'wb') as file:
                    file.write(scrape.encode('utf-8'))
            except IOError as err:
                print(f'Error writing the file: {err}')

if __name__ == "__main__":
    pages = int(input().strip() or "1")  # This is the number of pages to fetch. Default is 1.

    base = "https://www.nature.com/nature"  # All of Nature.com's links are relative.

    url = base + "/articles?sort=PubDate&year=2020&page=" + str(1)  # Wordy because we'll grab this later.
    url = url.lower()  # We need this from outside their server.

    page = requests.get(url)  # This is the digests page
    soup = BeautifulSoup(page.text, 'html.parser')

    category = input()
    if category.lower() + " " not in list(map(lambda x: x.lower(), validCategories(soup))):  # Add the trailing space.
        exit()  # Quit for a bad choice
    '''
    At this point we have page 1 and we've vetted the user's category choice. If pages == 1,
    then we can stop here. Otherwise, we need to continue from 2 to pages.
    '''
    CreateDirectories(pages)
    SaveSummaries(soup, folder='./Page_1/')

    if pages != 1:  # We want more than the first page...
        for depth in range(1, pages):
            url = base + "/articles?sort=PubDate&year=2020&page=" + str(depth + 1)
            page = requests.get(url)  # This is the next digests page
            soup = BeautifulSoup(page.text, 'html.parser')
            SaveSummaries(soup, folder=f'./Page_{depth + 1}/')
    print('Saved all articles.')