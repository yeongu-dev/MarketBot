# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import requests
import shelve

__author__ = 'yg-park'


class ArticleBase(object):
    """Market Article Class"""
    def __init__(self, number, subject, url, reg_date):
        self.number = number
        self.subject = subject
        self.url = url
        self.reg_date = reg_date

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)

    def to_string(self):
        return u"{0}\n{1}\n{2}\n\n".format(self.subject, self.url, self.reg_date)


class BotBase(object):
    """Telegram Bot Base Class"""
    __metaclass__ = ABCMeta

    def __init__(self, user_id, password, chat_id, bot_token, market_uid, search_keywords, session=None, delay=60):
        """
        :param user_id:  (string) 회원계정
        :param password: (string) 계정 비밀번호
        :param chat_id:  (string) 텔레그램 ID
        :param bot_token: (string) 텔레그램 bot token
        :param market_uid: (string) 장터 고유 ID
        :param search_keywords: (list-string) 검색 키워드
        :param delay: (integer) 검색 주기 시간 초
        """
        self.user_id = user_id
        self.password = password
        self.chat_id = chat_id
        self.token = bot_token
        self.base_url = 'https://api.telegram.org/bot{0}/'.format(bot_token)
        self.market_uid = market_uid
        self.keywords = search_keywords
        self.delay = delay
        self.session = session
        self.latest_article_number = None

    # --------------- CMD Method ----------------- #
    def cmd_start(self):
        pass

    def cmd_end(self):
        pass

    def cmd_set_keyword(self):
        pass

    # --------------- Telegram APIs ----------------- #
    def _api(self, api, params=None):
        """_api: 텔레그램 API 호출
        :param api: (string) Telegram API method
        :param params: (dictionary) API parameters
        :return: http response
        """
        base_url = self.base_url
        response = requests.post(base_url + api, data=params)
        return response

    def api_send_message(self, text):
        """api_send_msg: 메시지 발송
        :param chat_id: (integer) 메시지를 보낼 채팅 ID
        :param text:    (string)  메시지 내용
        :return: http response
        """
        params = {
            'chat_id': str(self.chat_id),
            'text': text.encode('utf-8'),
        }
        return self._api('sendMessage', params=params)

    def api_get_me(self):
        """api_get_me: 텔레그램 봇 확인
        :return: http response
        """
        return self._api('getMe')

    # --------------- Abstract Method ----------------- #
    @abstractmethod
    def authentication(self):
        """authentication: 인증
        :return: (requests) session
        """
        return self.session

    @abstractmethod
    def _search_new_article(self, keyword):
        """_search: 키워드 단위의 article 검색

        :param keyword:
        :return:
        """
        pass

    # --------------- Base Method ----------------- #
    def fetch_new_articles(self):
        """
        새로운 게시물 수집
        :return: articles 리스트
        """
        articles = []
        for kw in self.keywords:
            article = self._search_new_article(kw)
            articles += article
        return list(set(articles))

    def save_latest_article_number(self, keyword, number):
        """
        shelve 파일에 키워드의 가장 최근 게시물 번호를 저장한다.
        :param keyword: 검색 키워드 문자열
        :param number:
        :return:
        """
        # save new last list num
        filename = '{0}-{1}'.format(self.market_uid, self.chat_id)
        fdb = shelve.open(filename, 'c')
        fdb[keyword] = number
        fdb.close()

    def load_latest_article_number(self, keyword):
        """
        shelve 파일에서 가장 최근에 기록된 키워드의 게시물 번호를 로드한다
        :param keyword: 검색 키워드 문자열
        :return:
        """
        # get a saved last list number
        filename = '{0}-{1}'.format(self.market_uid, self.chat_id)
        fdb = shelve.open(filename, 'c')
        if len(fdb) == 0:
            lam = 0
            fdb[keyword] = lam
        elif keyword not in fdb:
            lam = 0
            fdb[keyword] = lam
        else:
            lam = fdb[keyword]
        fdb.close()
        return lam

    def new_messages(self):
        """
        텔레그램 Bot이 사용자에게 보내는 메세지 생성
        :return: 메세지 문자열 리스트
        """
        max_len = 4096
        articles = self.fetch_new_articles()
        message_doc = self.make_message(articles)
        msg_list = []
        if message_doc is None:
            return msg_list
        size_msg = len(message_doc)

        if size_msg > max_len:
            loop = size_msg / max_len
            for i in range(loop + 1):
                if size_msg > max_len * (i + 1):
                    msg = message_doc[max_len * i:max_len * (i + 1)]
                else:
                    msg = message_doc[max_len * i:]
                msg_list.append(msg)
        else:
            msg_list.append(message_doc)
        return msg_list

    # --------------- Utility Method ----------------- #
    @staticmethod
    def make_message(articles):
        """
        make_message: 텔레그램 챗 메시지 텍스트 생성
        :param articles: (list-ArticleBase) articles
        :return: (string) message
        """
        message = ""
        for a in articles:
            message += a.to_string()

        if message != "":
            return message
        else:
            return None

