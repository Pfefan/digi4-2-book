import os

import requests
from bs4 import BeautifulSoup as bs
from requests.utils import cookiejar_from_dict

from handlers.config_handler import Config


class Digi4school:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        })
        self.login_url = "https://digi4school.at/br/xhr/login"
        self.books_list_url = "https://digi4school.at/ebooks"
        self.book_url = "https://a.digi4school.at/ebook/"
        self.token_url = "https://a.digi4school.at/lti"

        os.makedirs('download', exist_ok=True)


    def login_user(self):
        payload = {
            'email': 'email',
            'password': 'password'
        }
        data = Config().get_config()
        payload["email"] = data["email"]
        payload["password"] = data["password"]
        response = self.session.post(self.login_url, data=payload, timeout=5)
    
        if str(response.content, 'utf-8') == "OK":
            return True
        elif str(response.content, 'utf-8') == "KO":
            return False

    def get_page(self):
        books = []
        if self.session is None:
            raise ValueError("Session is not initialized.")

        response = self.session.get(self.books_list_url, timeout=5)

        soup = bs(response.content, 'html.parser')

        shelf_div = soup.find('div', {'id': 'shelf'})

        a_tags = shelf_div.find_all('a')

        for a_tag in a_tags:
            href = a_tag.get('href')

            data_id = a_tag['data-id']
            data_code = a_tag['data-code']
            h1_text = a_tag.find('h1').text
            books.append((data_id, data_code, h1_text, href))

        return books

    def get_token(self):
        cookies = self.session.cookies.get_dict()
        update_cookie = self.session.get("https://digi4school.at/", cookies=self.session.cookies).cookies.get_dict()

        print(update_cookie["digi4s"])
        print(cookies["digi4s"])
        

        print("----------------------------------------------------------------------------")
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "474",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": 'ad_session_id={ad_session_id}; digi4s={digi4s}'.format(ad_session_id=cookies["ad_session_id"], digi4s=update_cookie["digi4s"]),
            "Host": "a.digi4school.at",
            "Origin": "https://kat.digi4school.at",
            "Referer": "https://kat.digi4school.at/",
            "sec-ch-ua": "\"Google Chrome\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
       
        payload = {
            "resource_link_id": 7553,
            "lti_version": "LTI-1p0",
            "lti_message_type": "basic-lti-launch-request",
            "user_id": "urn:digi4school.at/lti/user/252212",
            "oauth_callback": "about:blank",
            "oauth_nonce": "FC91D38DE",
            "oauth_version": "1.0",
            "oauth_timestamp": 1681389330,
            "oauth_consumer_key": "digi4s-katalog",
            "oauth_signature_method": "HMAC-SHA1",
            "context_id": "",
            "context_type": "",
            "roles": "urn:lti:role:ims/lis/Learner",
            "custom_code": "22s5bzuagyky",
            "custom_download": 0,
            "custom_warn": 0,
            "oauth_signature": "sS7I2Hmw/oPAk5EHrurx1rcaELg="
        }

        response = self.session.post(self.token_url, headers=headers, data=payload, timeout=5)

        print(response.status_code) # prints the HTTP status code
        print(response.headers) # prints the response headers
        with open("response.html", "w+", encoding="utf-8") as f:
            f.write(response.text)

        print("----------------------------------------------------------------------------")


    def download_book(self, data):
        print(data)
        url = self.book_url + book_id
        down_dir = f'download/{book_id}'

        self.session.get(url, timeout=5)

        cookies = self.session.cookies.get_dict()
        digi4b = "2299266513%2c7553%2c22s5bzuagyky%2c252212%20{982%201681475730%20B895BAA86447BB34B758579E37D1E600BB67619A}"

        headers = {
            'Cookie': 'digi4b="{digi4b}"; ad_session_id={ad_session_id}; digi4s={digi4s}'.format(digi4b=digi4b, ad_session_id=cookies["ad_session_id"], digi4s=cookies["digi4s"]),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }

        counter = 1

        os.makedirs(down_dir)


        while True:
            file_url = f"{url}/{counter}.svg"
            response = self.session.get(file_url, headers=headers, timeout=10)

            if response.status_code == 404:
                break

            with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as f:
                f.write(response.text)

            counter += 1

        print(f"All SVG files for book {book_id} have been downloaded to {down_dir}.")
