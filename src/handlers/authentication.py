import re

from bs4 import BeautifulSoup

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
        hpthek_url = "https://a.hpthek.at/lti"
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

        # this request saves the needed cookies in the session object which are needed to view the book
        second_lti_req = session.post(lti_cookie_url, data=payload)

        second_lti_response = second_lti_req.content.decode()

        soup = BeautifulSoup(second_lti_response, 'html.parser')

        # Check for nested books
        if soup.select_one('#content'):
            id_element = soup.select_one('a[href*="index.html"]')
            if id_element:
                id_value = id_element['href'].split('/')[-2]
                return f"{book_display_url + data[0]}/{id_value}"

        # Check for hpthek book
        if second_lti_req.status_code == 403:
            session.post(hpthek_url, data=payload)
            resource_id = payload["resource_link_id"]
            url = "https://a.hpthek.at/ebook/" + resource_id
            return url
        
        # Return Data
        return book_display_url + data[0]
