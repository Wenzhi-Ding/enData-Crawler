import os
import re
import urllib.request

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

path = os.getcwd() + os.sep


class MovieInfo(object):
    """
    This is a class for enquirying a specific movie, which is also the parent classes. Now supporting:
        - Douban
        - IMDb

    The driving factor for this class is the ID of each movies on different platforms.

    Adding a new source is easy through creating new sub-class and reload the relevant functions.
        - get_detail(self, code)
            To get detail information of a specific movie.
            Should indicate certain platform by sub-class.

        - search(self, name_in)
            To search movie's ID.
            Should indicate certain platform by sub-class.

        - get_code(self)
            To get the movie ID in the top list of a platform.
            Should indicate certain platform by sub-class.

        - get(self, obj_in)
            The leading function in parent class to manage enquiry and output.

        - output(self, code)
            Enquiry information and output.

        - search_body(self, url, pattern)
            To search by the url and to match information by pattern.
            All arguments should be assigned.
    """

    def get(self, obj_in):
        if isinstance(obj_in, list):
            for code in obj_in:
                self.output(code)
        elif isinstance(obj_in, str):
            self.output(obj_in)
        return 0

    def output(self, code):
        df = self.get_detail(code)
        if len(df) != 0:
            df.to_csv('%s%s.csv' % (path, df.iloc[0, 0]), header=False, encoding='utf_8_sig')
            print("Finish output of: %s" % df.iloc[0, 0])
        else:
            print("Fail to get detail.")
        return 0

    def search_body(self, url, pattern):
        """Due to the anti-scripting design of Douban Search, headless mode can not be used."""
        browser = webdriver.Chrome()
        browser.get(url)
        WebDriverWait(browser, 3)
        page = browser.page_source
        code = re.compile(pattern).findall(page)[0]
        print("Start getting: %s" % code)
        return code


class DoubanInfo(MovieInfo):

    def get_detail(self, code):
        index = ["Chinese_Name", "Douban_Release_Date", "Douban_Rating", "Director_CHN", "Actors_CHN", "Douban_Votes",
                 "Douban_Intro", "Douban_Rank", "IMDb_Name", "IMDb_Rating_DB"]
        url = "https://movie.douban.com/subject/%s/" % code
        print(url)
        try:
            db_page = urllib.request.urlopen(url).read().decode('utf-8')
        except:
            print("No such code from thie source.")
            return pd.DataFrame()
        soup_db = BeautifulSoup(db_page, "html5lib")
        data = [""] * 10
        data[0] = str(soup_db.find_all(property="v:itemreviewed")[0].string)
        data[1] = str(soup_db.find_all(property="v:initialReleaseDate")[0].string)
        data[2] = str(soup_db.find_all(property="v:average")[0].string)
        data[3] = str(soup_db.find_all(rel="v:directedBy")[0].string)
        actor = soup_db.find_all(rel="v:starring")
        data[4] = ', '.join(map(lambda x: str(x.string), actor))
        try:
            data[5] = str(soup_db.find_all(property="v:votes")[0].string)
        except:
            data[5] = 0
        data[6] = str(soup_db.find_all(property="v:summary")[0].get_text())[35:-25].replace('\n', " ").replace(' ',
                                                                                                               '').replace(
            "\u3000", '')
        try:
            data[7] = int(re.compile(r'(?<=<span class="top250-no">No.)[0-9]*?(?=</span>)').findall(db_page)[0])
        except:
            data[7] = int("")
        imdb_url = re.compile(r'http://www.imdb.com/title/.*?(?=")').findall(db_page)[0]
        imdb_page = urllib.request.urlopen(imdb_url).read().decode('utf-8').replace('&nbsp;', '')
        soup_imdb = BeautifulSoup(imdb_page, "html5lib")
        try:
            data[8] = re.compile(r'(?<=<h1 class="">).*?(?=<span id="titleYear">)').findall(imdb_page)[0]
        except:
            data[8] = re.compile(r'(?<=<h1 class="long">).*?(?=<span id="titleYear">)').findall(imdb_page)[0]
        data[9] = str(soup_imdb.find_all(itemprop="ratingValue")[0].string)

        df_in = pd.DataFrame(data, index=index)
        return df_in

    def search(self, name_in):
        db_search = "https://movie.douban.com/subject_search?search_text=%s&cat=1002" % name_in
        db_code = self.search_body(db_search, r'(?<=/subject/)[0-9]*?(?=/)')
        self.get(db_code)
        return 0

    def get_code(self):
        code_lst_in = []
        for index in range(10):
            search_page = urllib.request.urlopen(
                "https://movie.douban.com/top250?start=%d&filter=" % (index * 25)).read().decode('utf-8')
            for item in re.compile(r'(?<=/subject/)[0-9]*?(?=/)').findall(search_page):
                code_lst_in.append(item)
            print("Fetching codes: %d%%" % ((index + 1) * 10))
        return code_lst_in


class IMDbInfo(MovieInfo):

    def get_detail(self, code):
        index = ["IMDb_Name", "IMDb_Release_Date", "Director_EN", "Actors_EN", "IMDb_Rating_IM", "IMDb_Votes",
                 "IMDb_Intro", "IMDb_Rank"]
        url = "https://www.imdb.com/title/tt%s/" % code
        print(url)
        try:
            imdb_page = urllib.request.urlopen(url).read().decode('utf-8').replace('&nbsp;', '')
        except:
            print("No such code from thie source.")
            return pd.DataFrame()
        data = [""] * 8
        soup_imdb = BeautifulSoup(imdb_page, "html5lib")
        try:
            data[0] = re.compile(r'(?<=<h1 class="">).*?(?=<span id="titleYear">)').findall(imdb_page)[0]
        except:
            data[0] = re.compile(r'(?<=<h1 class="long">).*?(?=<span id="titleYear">)').findall(imdb_page)[0]
        data[1] = str(soup_imdb.find_all(title="See more release dates")[0].string).replace('\n', "")
        data[2] = str(soup_imdb.find_all(attrs={"class": "credit_summary_item"})[0].find_all("a")[0].string)
        actor = soup_imdb.find_all(attrs={"class": "credit_summary_item"})[2].find_all("a")
        actor.pop()
        data[3] = ', '.join(map(lambda x: str(x.string), actor))
        data[4] = str(soup_imdb.find_all(itemprop="ratingValue")[0].string)
        data[5] = str(soup_imdb.find_all(itemprop="ratingCount")[0].string)
        data[6] = str(soup_imdb.find_all(attrs={"class": "summary_text"})[0].get_text())[21:-13].replace('\n', "")
        try:
            data[7] = int(re.compile(r'(?<=Top Rated Movies #)[0-9]*').findall(imdb_page)[0])
        except:
            data[7] = int("")

        df_in = pd.DataFrame(data, index=index)
        return df_in

    def search(self, name_in):
        try:
            imdb_search = "https://www.imdb.com/find?q=%s&s=tt&ttype=ft&ref_=fn_ft" % name_in
            imdb_code = self.search_body(imdb_search, r'(?<=<td class="result_text"> <a href="/title/tt)[0-9]*?(?=/)')
            self.get(imdb_code)
        except:
            print("Invalid input for IMDb.")
        return 0

    def get_code(self):
        search_page = urllib.request.urlopen('https://www.imdb.com/chart/top?ref_=nv_mv_250_6').read().decode('utf-8')
        code_lst_in = re.compile(r'(?<=<a href="/title/tt)[0-9]*?(?=/)').findall(search_page)
        return list(set(code_lst_in))
