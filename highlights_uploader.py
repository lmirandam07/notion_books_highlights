import os
import fire
import notion
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class HighlightsUploader(object):

    def __init__(self, book_name=''):
        self.book_name = book_name

    def upload(self):
        load_dotenv()
        notes_url = os.getenv('GOODREADS_NOTES_URL')
        highlights = self.scrape(notes_url)

    def get_webdriver(self):
        options = Options()
        options.headless = True
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        driver = webdriver.Firefox(options=options, firefox_profile=firefox_profile)

        return driver

    def scrape(self, notes_url):
        driver = self.get_webdriver()

        try:
            driver.get(notes_url)
            time.sleep(2)
            books_list = driver.find_elements_by_class_name("annotatedBookItem")
            for book in books_list:
                book_name = book.find_element_by_class_name("annotatedBookItem__bookInfo__bookTitle").text

                if self.book_name.lower() in book_name.lower(): # Check if book name is in goodreads books list
                    book_notes_url = book.find_element_by_class_name("annotatedBookItem__knhLink")
                    book_notes_url.click() # Click the box of the book searched

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    highlights = soup.select('.noteHighlightTextContainer__highlightText > span')
                    highlights = [h.text for h in highlights]
                    driver.close()

                    return highlights

        except Exception as e:
            driver.close()
            print(e)



    def update_notion(highlights_list):
        pass

if __name__ == '__main__':
    # fire.Fire(HighlightsUploader)
    uploader = HighlightsUploader('motivation hacker')
    uploader.scrape('https://www.goodreads.com/notes/114436946-luis-miranda-m')
