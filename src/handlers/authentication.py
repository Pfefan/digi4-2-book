import re

from bs4 import BeautifulSoup
import urllib.parse
from handlers.config_handler import Config


class Authentication:
    def __init__(self):
        self.login_url = "https://digi4school.at/br/xhr/login"

    def login_user(self, session):
        payload = {
            'email': 'email',
            'password': 'password'
        }
        data = Config().get_config()
        payload["email"] = data["email"]
        payload["password"] = data["password"]
        response = session.post(self.login_url, data=payload, timeout=5)

        if str(response.content, 'utf-8') == "OK":
            return (True, session)
        elif str(response.content, 'utf-8') == "KO":
            return (False, session)

    def get_token(self, data, session):
        payload = {}
        book_code_url = "https://digi4school.at/ebook/" + data[1]
        lti_ad_session_url = "https://kat.digi4school.at/lti"
        lti_cookie_url = "https://a.digi4school.at/lti"
        hpthek_lti = "https://a.hpthek.at/lti"
        scook_lti = "https://www.scook.at/lti"
        book_display_url = "https://a.digi4school.at/ebook/"

        book_code_req = session.get(book_code_url)

        book_code_response = book_code_req.content.decode()
        # gets all the data from the first lti response using regular expressions
        for match in re.findall(r"<input name='(\w+)' value='(.*?)'>", book_code_response):
            payload[match[0]] = match[1]

        # this request takes the cookie and the response data from the book id request to get a new ad_session_id token
        first_lti_req = session.post(lti_ad_session_url, data=payload)
        payload.clear()

        first_lti_response = first_lti_req.content.decode()

        # gets all the data from the first lti response using regular expressions
        for match in re.findall(r"<input name='(\w+)' value='(.*?)'>", first_lti_response):
            payload[match[0]] = match[1]
        
        action_lti = re.search(r"<form[^>]*action='(.*?)'", first_lti_response)
        if action_lti:
            action_lti = action_lti.group(1)

        print(session.cookies)
        # requests the cookies needed to view the book
        headers = {
            "Host": "kat.digi4school.at",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://digi4school.at/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(urllib.parse.urlencode(payload).encode('utf-8'))),
            "Origin": "https://digi4school.at",
            "Connection": "keep-alive",
            "Cookie": session.cookies.get("digi4s") + "; " + session.cookies.get("ad_session_id"),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
        }

        second_lti_req = session.post(action_lti, headers=headers, data=payload)

        second_lti_response = second_lti_req.content.decode()

        soup = BeautifulSoup(second_lti_response, 'html.parser')

        print(second_lti_req.headers)

        # Check for nested books
        if soup.select_one('#content'):
            id_element = soup.select_one('a[href*="index.html"]')
            if id_element:
                id_value = id_element['href'].split('/')[-2]
                return f"{book_display_url + data[0]}/{id_value}"

        # Check for hpthek book
        """if second_lti_req.status_code == 403:
            session.post(hpthek_lti, data=payload)
            resource_id = payload["resource_link_id"]
            url = "https://a.hpthek.at/ebook/" + resource_id

            # validate if its a hpthek book
            hpthek_req = session.get(url, data=payload)
            print(url)
            if hpthek_req.status_code == 200:
                return url
            else:
                lti_req = session.post(scook_lti, data=payload)
                print(lti_req.headers)"""
        
        # Return Data
        return book_display_url + data[0]
