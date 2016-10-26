# -*- coding: utf-8 -*-

import urllib
from bs4 import BeautifulSoup
import requests
import time
from base import BotBase, ArticleBase
from settings import slrclub, token


class SLRClubBot(BotBase):
    def authentication(self):
        """Overrides method in BotBase"""
        url = "https://www.slrclub.com/login/auth.php"
        url2 = "http://www.slrclub.com/login/login_center.php"
        user_data = {'user_id': self.user_id, 'password': self.password}
        with requests.session() as s:
            # first auth
            r = s.post(url, data=user_data, verify=False)
            soup = BeautifulSoup(r.text, 'html.parser')
            code_value = soup.find("input", {"name": "code"})['value']
            data = {'code': code_value}
            # second auth
            s.post(url2, data=data)
            self.session = s
        return self.session

    def _search_new_article(self, keyword):
        """Overrides method in BotBase"""
        time.sleep(2)
        data = {"keyword": keyword}
        url = "http://www.slrclub.com/service/search/local?id=used_market&category=1&setsearch=subject&{0}".format(urllib.urlencode(data))
        try:
            r = self.session.get(url)
        except requests.exceptions.ConnectionError as e:
            message = 'connection to {0} failed. \n {1}'
            print e
            return []
      
        html_doc = r.text
        lam = self.load_latest_article_number(keyword)

        # get article on 1 page
        soup = BeautifulSoup(html_doc, 'html.parser')
        bbs_list = soup.find(id='bbs_list')
        if bbs_list is None:
            print "bbs_list is None!!"
            print soup
            return []
        else:
            tbody = bbs_list.find('tbody')

        articles = []
        tr_soup = tbody.find_all('tr')
        for i, tr in enumerate(tr_soup):
            list_num = int(tr.find("td", {"class": "list_num"}).text)
            if i == 0:
                new_lam = list_num
                self.save_latest_article_number(keyword, new_lam)
            if list_num > lam:
                # subj text and url
                alink = tr.find("td", {"class": "sbj"}).find("a")
                subject = alink.text
                url = "http://www.slrclub.com" + alink['href']
                # date no
                reg_date = tr.find("td", {"class": "list_date"}).text
                article = ArticleBase(list_num, subject, url, reg_date)
                articles.append(article)
            if lam == 0:
                break
        return articles


def main():
    process = []
    session = None
    for s in slrclub:
        user_id = s["user_id"]
        password = s["password"]
        chat_id = s["chat_id"]
        keywords = s["keywords"]
        if session is None:
            bot = SLRClubBot(user_id, password, chat_id, token, 1, keywords)
            session = bot.authentication()
        else:
            bot = SLRClubBot(user_id, password, chat_id, token, 1, keywords, session)

        process.append(bot)

    while True:
        for bot in process:
            messages = bot.new_messages()
            for msg in messages:
                bot.api_send_message(msg)

            from datetime import datetime
            if len(messages) == 0:
                print datetime.now(), "no messages"
            else:
                print datetime.now(), "success"
        time.sleep(60)


if __name__ == "__main__":
    main()

