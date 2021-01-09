import fire
import time
from decouple import config
from bs4 import BeautifulSoup
from notion.client import NotionClient
from notion.block import QuoteBlock
from notion.block import SubheaderBlock
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class HighlightsUploader(object):

    def __init__(self, book_name=''):
        self.book_name = book_name
        if self.book_name:
            self.upload()
        else:
            raise Exception("Enter a book name")

    def upload(self):
        NOTION_TOKEN = config('NOTION_TOKENV2')
        GOODREADS_URL = config('GOODREADS_NOTES_URL')
        NOTION_BOOKS_LIST = config('NOTION_BOOKS_LIST_URL')
        try:
            highlights = self.scrape(GOODREADS_URL)
            if highlights == None:
                raise Exception(f"{self.book_name} not found in Goodreads")

            client = NotionClient(token_v2=NOTION_TOKEN)
            books_collection = client.get_collection_view(NOTION_BOOKS_LIST)
            book_searched_id = ""

            for book_row in books_collection.collection.get_rows():
                if self.book_name.lower() in book_row.title.lower():  # Check if book exists in Notion books list
                    book_searched_id = book_row.id
                    break

            if not book_searched_id:
                raise Exception(f"{self.book_name} not found in Notion")

            book_page = client.get_block(book_searched_id)
            book_page.children.add_new(SubheaderBlock, title="Highlights")

            for h in highlights:  # Add blockquotes for every highlight in its respective note
                book_page.children.add_new(QuoteBlock, title=h)

            print("Note updated successfully")
            return True

        except Exception as e:
            print(e)

    def get_webdriver(self):
        options = Options()
        options.headless = True
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        driver = webdriver.Firefox(
            options=options, firefox_profile=firefox_profile)

        return driver

    def scrape(self, goodreads_url):
        driver = self.get_webdriver()
        highlights = ''
        try:
            driver.get(goodreads_url)
            time.sleep(2)
            books_list = driver.find_elements_by_class_name(
                "annotatedBookItem")
            for book in books_list:
                book_name = book.find_element_by_class_name(
                    "annotatedBookItem__bookInfo__bookTitle").text

                if self.book_name.lower() in book_name.lower():  # Check if book name is in goodreads books list
                    book_notes_url = book.find_element_by_class_name(
                        "annotatedBookItem__knhLink")
                    book_notes_url.click()  # Click the box of the book searched

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    highlights = soup.select(
                        '.noteHighlightTextContainer__highlightText > span')
                    highlights = [h.text for h in highlights]
                    break

            driver.close()
            return highlights

        except Exception as e:
            driver.close()
            print(e)


if __name__ == '__main__':
    fire.Fire(HighlightsUploader)
