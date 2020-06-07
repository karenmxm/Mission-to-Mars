# Import Splinter, BeautifulSoup and Pandas
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time


def scrape_all():
    
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "high_resolution_image": high_resolution_image (browser)
    }

    browser.quit()
    return data

# Set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': 'chromedriver'}
browser = Browser('chrome', **executable_path)

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
    

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        news_title

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
        news_p

    except AttributeError:
        return None, None

    return news_title, news_p



def featured_image(browser):

    # Featured Images
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try: 
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url


def mars_facts():
    
    try:
    # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]    
    
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


def high_resolution_image (browser):
    
    # Visit High Resolution Images url
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    time.sleep(1)


    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # Get the average temps
    images = soup.find_all('div', class_ ='description')
    
    high_res_img = []
    # Iterate through each image
    for image in images:
        # Use Beautiful Soup's find() method to navigate and retrieve attributes
        link = image.find('a')
        h3 = link.find('h3')
        href = link['href']
        title = h3.text
        
        mars_img = f'https://astrogeology.usgs.gov{href}'
        browser.visit(mars_img)
             
        # Scrape page into Soup
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
        
        img_url_item = soup.select_one('img.wide-image').get('src')
     
        img_url = f'https://astrogeology.usgs.gov{img_url_item}'
               
        high_resolution_img = {
            "high_resolution_img": img_url,
            "title": title}
        
        high_res_img.append(high_resolution_img)

    # Close the browser after scraping
    browser.quit()

    # Return results
    return high_res_img 

browser.quit()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
