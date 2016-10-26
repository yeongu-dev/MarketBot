# 중고장터 모니터링 텔레그램 Bot 만들기

- 텔레그램의 Bot을 통해서 중고장터에 지정된 키워드로 새로운 매물이 올라올 경우 Bot이 알려준다.

## TelegramBot 등록

- 블로그 [박연오: 텔레그램 로봇, 공식 API로 만들기 (파이썬, 구글 앱 엔진)](http://bakyeono.net/post/2015-08-24-using-telegram-bot-api.html) 참고
- [공식 Telegram Bot API](https://core.telegram.org/bots) 참고

## python 패키지 설치

`pip install -r requirements.txt`

## 설정

- `MarketBot/settings/__init__.py` 파일 수정

```python
slrclub = [
    {
        "chat_id": "12345678",               # Telegram 사용자 ID:
                                             # TelegramBotAPI getUpdates를 통해 얻은 ID
        "user_id": "slrclub_my_user",        # SRLClub 중고장터 ID
        "password": "slrclub_my_password",   # SRLClub 중고장터 비밀번호
        "keywords": ["sample_keyword", "sample_keyword"], # 검색 키워드
    },
  {
      ....
  }
]

token = "AbcdEfg..." # Telegram Bot Token
```

## 실행

```bash
cd MarketBot
python main.py
```

## 주의사항
- 순전히 개인용도로 사용하려고 만들었습니다.
- 설정`settings/__init__.py` 를 보면 알겠지만 암호화 그런거 없으니 유념하세요.