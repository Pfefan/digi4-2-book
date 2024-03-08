from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config_handler import ConfigHandler

class Executor():
    LOGIN_URL = "https://digi4school.at/"
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")  # Run in headless mode
        self.options.add_argument("--no-sandbox")  # Bypass OS security model
        self.options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        self.options.add_argument("--disable-renderer-backgrounding")  # Ensure Renderer process never throttles its priority
        self.options.add_argument("--disable-background-timer-throttling")  # Disable task throttling of timer tasks from background pages
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.minimize_window()

    def login(self):
        config_data = ConfigHandler().get_config()
        self.driver.get(self.LOGIN_URL)
        self.driver.find_element(By.ID, 'email').send_keys(config_data["email"])
        self.driver.find_element(By.ID, 'password').send_keys(config_data["password"])
        self.driver.find_element(By.CSS_SELECTOR, 'form#login button').click()

    def execute_js(self, url, js_code):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        result = self.driver.execute_script(js_code)
        print(result)

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    js_code = """
    var pageNumbers = [];
    $("#goBtn").children().each(function() {
        pageNumbers.push(parseInt($(this).val()));
    });
    return pageNumbers.length;
    """

    executor = Executor()
    executor.login()
    executor.execute_js("https://digi4school.at/ebook/10vqygp964ze", js_code)
    executor.quit()