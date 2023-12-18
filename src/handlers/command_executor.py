import requests

from handlers.authentication import Authentication
from handlers.book_handler import Digi4school
from handlers.config_handler import Config


class Handler:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        })
        self.digi4school = Digi4school()
        self.auth = Authentication(self.session)

    def main(self):
        validconfig = Config().check_config()
        if validconfig:
            login = self.auth.login_user()
            self.session = login[1]
            if login[0]:
                self.handler()
            else:
                print("Invalid user name or password in config")

    def handler(self):
        print("Welcome to Digi4-books!!!\n")
        while True:
            command = input("Enter command >: ")
            if command == "list-books":
                self.list_books()
            elif command.startswith("download"):
                self.download(command)
            else:
                print("Invalid command. Please try again.")

    def list_books(self):
        data = self.digi4school.get_books(self.session)
        if len(data) > 0:
            print("   ID                 Book Name")
            print("-" * 50)
            counter = 1
            for book in data:
                print(f"{str(counter).strip():>4}   {book[2].strip()}")
                counter += 1
            print("-" * 50)
        else:
            print("No data found!!\n")

    def download(self, command):
        args = command.split()
        if len(args) == 3 and args[1] == "book":
            book_id = args[2]
            self.download_book(book_id)
        elif len(args) == 4 and args[1] == "page":
            book_id = args[2]
            page_num = args[3]
            self.download_page(book_id, page_num)
        elif len(args) == 4 and args[1] == "all":
            self.download_all()
        else:
            print("Invalid arguments. Please try again.")

    def download_book(self, book_id):
        if int(book_id) < 0:
            print("Invalid book_id")
            return

        data = self.digi4school.get_books(self.session)[int(book_id)-1]
        self.digi4school.download_book(data, self.session)

    def download_page(self, book_id, page_num):
        # TODO: send book id and page number to the class that handles the download of a selected page
        print("page")
        pass

    def download_all(self):
        data = self.digi4school.get_books(self.session)
        self.digi4school.download_all(data, self.session)
