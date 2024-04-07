from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from interfaces.job import JobOpening


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
    def execute(self) -> list[JobOpening]:
        self.driver.get(self.job_board_url)
        print(f"Title: {self.driver.title}")

    @abstractmethod
    def get_job_listings(self):
        raise NotImplementedError
