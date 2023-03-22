from config_handler import Config

class Handler:
    def __init__(self) -> None:
        pass

    def main(self):
        validconfig = Config().check_config()
        if validconfig:
            self.handler()

    def handler(self):
        print("Welcome to Digi4-books!!!\n")
        while True:
            value = input("Enter 1 to download a selected page and 2 for the whole book: ")
            if value == "1":
                self.handle_selected_page()
                break
            elif value == "2":
                self.handle_whole_book()
                break
            else:
                print("Invalid input. Please try again.")

    def handle_selected_page(self):
        book_name = input("Enter the book name: ")
        page_number = input("Enter the page number: ")
        # TODO: send book name and page number to the class that handles the download

    def handle_whole_book(self):
        book_name = input("Enter the book name: ")
        # TODO: send book name to the class that handles the download
