from handlers.config_handler import Config
from handlers.digi4school_handler import Digi4school
from logging_formater import ConfigLogger


class Handler:
    def __init__(self) -> None:
        self.config = ConfigLogger().setup()
        self.digi4school = Digi4school()
        self.bookdata = []

    def main(self):
        validconfig = Config().check_config()
        if validconfig:
            if self.digi4school.login_user():
                self.handler()
            else:
                self.config.warning("Invalid user name or password in config")


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

    def download(self, command):
        args = command.split()
        if len(args) == 3 and args[1] == "book":
            book_id = args[2]
            self.download_book(book_id)
        elif len(args) == 4 and args[1] == "page":
            book_id = args[2]
            page_num = args[3]
            self.download_page(book_id, page_num)
        else:
            print("Invalid arguments. Please try again.")

    def list_books(self):
        data = self.digi4school.get_page()
        if len(data) > 0:
            print("   ID                 Book Name")
            print("-" * 50)
            counter = 1
            for book in data:
                print(f"{str(counter).strip():>4}   {book[2].strip()}")
                counter += 1
            print("-" * 50)
            self.bookdata = data
        else:
            print("No data found!!\n")

    def download_book(self, book_id):
        if int(book_id) < 0:
            print(len(self.bookdata))
            print("Invalid book_id")
            return
        
        data = self.bookdata[int(book_id)-1]
        self.digi4school.download_book(data)

    def download_page(self, book_id, page_num):
        # TODO: send book id and page number to the class that handles the download of a selected page
        print("page")
        pass