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
    TIMEOUT = 3

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


class USTJobBoardAutomationManager(AutomationManager):
    MSFT_LOGIN_TITLE = "Sign in to your account"

    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self._job_board_url = os.getenv("HKUST_JOB_BOARD_URL")
        self._hkust_email = os.getenv("HKUST_EMAIL")
        self._hkust_password = os.getenv("HKUST_PASSWORD")

    @property
    def job_board_url(self):
        if not self._job_board_url:
            raise ValueError(
                "Unable to retrieve url for HKUST Job Board. Please check environment variables."
            )
        return self._job_board_url

    @property
    def hkust_email(self):
        if not self._hkust_email:
            raise ValueError(
                "Unable to retrieve HKUST email. Please check environment variables."
            )
        return self._hkust_email

    @property
    def hkust_password(self):
        if not self._hkust_password:
            raise ValueError(
                "Unable to retrieve HKUST password. Please check environment variables."
            )
        return self._hkust_password

    def execute(self):
        super().execute()
        self.driver.implicitly_wait(self.TIMEOUT)
        if self.driver.title == self.MSFT_LOGIN_TITLE:
            self.handle_auth()
        self.apply_filters().get_job_listings()

    def handle_auth(self):
        return self

    def apply_filters(self):
        return self

    def get_job_listings(self):
        return self


manager = USTJobBoardAutomationManager(driver=init_driver())
manager.execute()
