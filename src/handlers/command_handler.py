import requests

from handlers.authentication import AuthAndTokenHandler
from handlers.book_fetcher import BookDataRetriever
from handlers.config_handler import ConfigHandler


class CommandHandler:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        })
        self.digi4school = BookDataRetriever()
        self.auth = AuthAndTokenHandler()

        self.commands = {
            "list-books": self.list_books,
            "download": self.download,
            "help": self.help,
        }

    def main(self):
        validconfig = ConfigHandler().check_config()
        if validconfig:
            login_success = self.auth.login_user(self.session)
            if login_success:
                self.handler()
            else:
                print("Invalid user name or password in config")

    def handler(self):
        print("Welcome to Digi4-books!!!\n")
        while True:
            command = input("Enter command >: ")
            self.execute_command(command)

    def execute_command(self, command):
        command_name, *args = command.split()
        if command_name in self.commands:
            try:
                self.commands[command_name](*args)
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Invalid command. Please try again.")

    def help(self):
        print("List of available commands:")
        print("- list-books - List all available books")
        print("- download book <book_id> - Download a specific book")
        print("- download all - Download all books")
        print("- download book <book_id> page <page> - Download a specific page from a book")
        print("- download book <book_id> page <start_page> <end_page> - Download a specific range of pages from a book")
        print("- help - Display this help message \n")

    def list_books(self):
        data = self.digi4school.get_book_list(self.session)
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

    def download(self, *args):
        if args[0] == "book" and len(args) == 2:
            book_id = args[1]
            self.download_book(book_id)
        elif args[0] == "book" and args[2] == "page" and len(args) == 4:
            book_id = args[1]
            start_page = args[3]
            self.download_page(book_id, start_page)
        elif args[0] == "book" and args[2] == "page" and len(args) == 5:
            book_id = args[1]
            start_page = args[3]
            end_page = args[4]
            self.download_page(book_id, start_page, end_page)
        elif args[0] == "all" and len(args) == 1:
            self.download_all_books()
        else:
            print("Invalid arguments. Please try again.")

    def download_book(self, book_id):
        if int(book_id) < 0:
            print("Invalid book_id")
            return

        data = self.digi4school.get_book_list(self.session)[int(book_id)-1]
        self.digi4school.download_single_book(data, self.session)

    def download_all_books(self):
        data = self.digi4school.get_book_list(self.session)
        self.digi4school.download_all_books(data, self.session)

    def download_page(self, book_id, start_page, end_page=None):
        if int(book_id) < 0:
            print("Invalid book_id")
            return

        # TODO: Add check for valid page numbers
        data = self.digi4school.get_book_list(self.session)[int(book_id)-1]
        self.digi4school.download_page(data, self.session, int(start_page), int(end_page) if end_page else None)
