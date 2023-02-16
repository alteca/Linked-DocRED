"""Module to search wikipedia using Google

---
Linked-DocRED
Copyright (C) 2023 Alteca.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from selenium import webdriver
from bs4 import BeautifulSoup

class WikipediaSearch:
    """Class for wikipedia search
    """

    def __init__(self, url: str):
        """Constructor
        Args:
            url (str): url of the search engine
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('user-data-dir=./chrome-config')

        self.url = url
        self.driver = webdriver.Chrome(options=options)

    def close(self):
        """Close wikipedia search
        """
        self.driver.close()

    def get_search_results(self, keywords: list, num_candidates: int) -> dict:
        """Returns num_candidates search results corresponding to the keywords

        Args:
            keywords (list): list of str keywords
            num_candidates (int): num of candidates to return
        Returns:
            dict: candidates
        """
        url = f"{self.url}&q=site:en.wikipedia.org+{'+'.join(keywords)}"
        self.driver.get(url)

        soup = BeautifulSoup(self.driver.page_source)
        candidates_html = soup.find_all(
            "div", {"class": ["result", "result-default", "google"]})[0:num_candidates]

        # Parse results
        out_candidates = []
        for candidate in candidates_html:
            header = candidate.find_all("h4", {"class": "result_header"})[0]
            title = header.text.replace(" - Wikipedia", "")
            summary = candidate.find_all("p", {"class": "result-content"})
            if len(summary) > 0:
                summary = summary[0].text
            else:
                summary = ""
            url = header.find_all("a")[0].attrs['href']

            out_candidates.append({
                'title': title,
                'summary': summary,
                'url': url
            })

        return out_candidates
