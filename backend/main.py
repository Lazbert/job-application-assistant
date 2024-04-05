# %%
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chromedriver_py import binary_path
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))


def init_driver() -> webdriver.Chrome:
    # initialize Chrome webdriver
    service = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=service)
    return driver


# %%
from abc import ABC, abstractmethod


class AutomationManager(ABC):
    TIMEOUT = 5

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, self.TIMEOUT)

    @property
    @abstractmethod
    def job_board_url(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        self.driver.get(self.job_board_url)
        print(f"Title: {self.driver.title}")

    @abstractmethod
    def get_job_listings(self):
        raise NotImplementedError


class JobBoardAutomationManager(AutomationManager):
    MSFT_LOGIN_TITLE = "Sign in to your account"
    DUO_TITLE = "Duo Security"

    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self._job_board_url = os.getenv("JOB_BOARD_URL")
        self._email = os.getenv("EMAIL")
        self._password = os.getenv("PASSWORD")

    @property
    def job_board_url(self):
        if not self._job_board_url:
            raise ValueError(
                "Unable to retrieve url for job board. Please check environment variables."
            )
        return self._job_board_url

    @property
    def email(self):
        if not self._email:
            raise ValueError(
                "Unable to retrieve email. Please check environment variables."
            )
        return self._email

    @property
    def password(self):
        if not self._password:
            raise ValueError(
                "Unable to retrieve password. Please check environment variables."
            )
        return self._password

    def execute(self):
        super().execute()
        if self.driver.title == self.MSFT_LOGIN_TITLE:
            self.handle_auth()
        self.agree_terms().apply_filters().get_job_listings()

    def handle_auth(self):
        # enter email and click next
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "loginfmt"))
        )
        email_input.send_keys(self.email)
        next_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        next_btn.click()

        # enter password and click sign in
        password_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "i0118"))
        )
        password_input.send_keys(self.password)
        sign_in_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//input[@type="submit"]'))
        )
        sign_in_btn.click()

        # Duo Mobile
        print("Waiting approval from mobile device...")
        my_device_btn = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.ID, "trust-browser-button"))
        )
        print("\u2713 Received approval from mobile device")
        my_device_btn.click()

        return self

    def agree_terms(self):
        # agree the declaration form
        declaration_checkbox = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//input[@type="checkbox"]'))
        )
        declaration_checkbox.click()
        agree_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//input[@value="Agree"]'))
        )
        agree_btn.click()

        # agree disclaimer
        disclaimer_agree_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//input[@type="submit"]'))
        )
        disclaimer_agree_btn.click()
        return self

    def apply_filters(self):
        return self

    def get_job_listings(self):
        return self


manager = JobBoardAutomationManager(driver=init_driver())
manager.execute()
