import shutil
import time
import os
import re
from requests.exceptions import HTTPError, RequestException
from handlers.authentication import Authentication
from handlers.pdf_convert import Convert

class Download():
    def __init__(self, session) -> None:
        self.session = session
        self.image_url_only = False

    def main(self, data):
        starttime = time.time()
        down_dir = f'download/{data[0]}'
        os.makedirs(down_dir, exist_ok=True)
        print("gettings tokens", end="\r")

        url = Authentication(self.session).get_token(data)

        print("downloading svg files", end="\r")
        if self.get_svg(down_dir, url):
            print("downloading images", end="\r")

            if self.get_images(down_dir, url):
                print("converting to pdf", end="\r")

                Convert().convert_svg_to_pdf(down_dir, data[2])
        else:
            print("Failed to download SVG files.")
        shutil.rmtree(down_dir)
        print(f"took {time.time() - starttime}", end="\r")
        print("\n")        

    def get_svg(self, down_dir, url):
        if not self.hpthek_book:
            response = self.session.get(f"{url}/1.svg", timeout=5)
            if response.status_code != 404:
                file_url = f"{url}/{{}}.svg"
                self.image_url_only = True
            else:
                response = self.session.get(f"{url}/1/1.svg", timeout=5)
                if response.status_code != 404:
                    file_url = f"{url}/{{}}/{{}}.svg"
                    self.image_url_only = False
                else:
                    print("failed to get url")
                    return False
        else:
            response = self.session.get(f"{url}/1.svg", timeout=5)
            if response.status_code != 404:
                file_url = f"{url}/{{}}.svg"
                self.image_url_only = True
            else:
                response = self.session.get(f"{url}1/1.svg", timeout=5)
                if response.status_code != 404:
                    file_url = f"{url}/{{}}/{{}}.svg"
                    self.image_url_only = False
                else:
                    print("failed to get url")
                    return False


        counter = 1
        while True:
            file_url_with_counter = file_url.format(counter, counter)
            try:
                response = self.session.get(file_url_with_counter, timeout=5)
                if response.status_code == 404:
                    if counter == 1:
                        return False
                    break

                response.raise_for_status()
            except (RequestException, HTTPError):
                print(f"Error downloading {file_url_with_counter}")
                return False

            with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as svg_file:
                svg_file.write(response.text)

            counter += 1
        return True


    def get_images(self, svg_dir, url):
        svg_files = os.listdir(svg_dir)

        for file in svg_files:
            with open(f"{svg_dir}/{file}", "rb") as svg_file:
                svg_contents = svg_file.read().decode('utf-8')

            # use a regular expression to extract all xlink:href attribute values from the image tags
            pattern = r'<image\s.*?xlink:href="([^"]*)".*?>'
            matches = re.findall(pattern, svg_contents)

            # print the extracted xlink:href values
            if matches:
                for xlink_href in matches:
                    if self.image_url_only:
                        image_url = f"{url}/{xlink_href}"
                    else:
                        image_url = f"{url}/{os.path.basename(file)}/{xlink_href}"
                    response = self.session.get(image_url, timeout=5)
                    dirname = f"{svg_dir}/{os.path.dirname(xlink_href)}"
                    os.makedirs(dirname, exist_ok=True)

                    if response.status_code == 200:
                        with open(os.path.join(dirname, os.path.basename(xlink_href)), "wb") as img_file:
                            img_file.write(response.content)
                    else:
                        return False
        return True