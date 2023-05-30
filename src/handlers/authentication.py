import re
from handlers.config_handler import Config

class Authentication:
    def __init__(self, session):
        self.session = session
        self.login_url = "https://digi4school.at/br/xhr/login"

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
            return (True, self.session)
        elif str(response.content, 'utf-8') == "KO":
            return (False, self.session)

    def get_token(self, data):
        # right now firstly the list-files has to be executed to get the cookies, i will change that in the future i am just
        # trying to implement the feature right now, the request with the id needs the digi4s cookie from the home page
        payload = {}
        book_code_url = "https://digi4school.at/ebook/" + data[1]
        lti_ad_session_url = "https://kat.digi4school.at/lti"
        lti_cookie_url = "https://a.digi4school.at/lti"
        hpthek_url = "https://a.hpthek.at/lti"

        book_code_req = self.session.get(book_code_url)

        book_code_response = book_code_req.content.decode()
        # gets all the data from the first lti response using regular expressions
        for match in re.findall(r"<input name='(\w+)' value='(.*?)'>", book_code_response):
            payload[match[0]] = match[1]

        # this request takes the cookie and the response data from the book id request to get a new ad_session_id token
        first_lti_req = self.session.post(lti_ad_session_url, data=payload)

        first_lti_response = first_lti_req.content.decode()
        payload.clear()

        # gets all the data from the first lti response using regular expressions
        for match in re.findall(r"<input name='(\w+)' value='(.*?)'>", first_lti_response):
            payload[match[0]] = match[1]

        # this request gets the cookies which are needed for reading out book data using the data from the first lti response
        second_lti_req = self.session.post(lti_cookie_url, data=payload)
        if second_lti_req.status_code == 403:
            hpthek_resp = self.session.post(hpthek_url, data=payload)
            self.hpthek_book = True
            return "https://a.hpthek.at/ebook/164"   # actually return the right book id
        return self.book_display_url + data[0]
