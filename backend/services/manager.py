import os
import time
import random
from enum import Enum, auto
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from interfaces.manager import AutomationManager
from interfaces.job import JobOpening

from services.utils.auth import JobBoardAuthenticationHandler
from services.utils.terms import JobBoardTermsAgreementHandler
from services.utils.parser import JobBoardSinglePageParser
from services.utils.retriever import JobBoardSingleDetailsRetriever


class JobBoardAutomationManager(AutomationManager):
    MSFT_LOGIN_TITLE = "Sign in to your account"
    DUO_TITLE = "Duo Security"
    SORT_BY_DESC_DEADLINE = "&sort=deadline&order=desc"

    def __init__(self, driver: webdriver.Chrome, filter: str):
        super().__init__(driver)
        self._job_board_url = os.getenv("JOB_BOARD_URL")
        self.auth_handler = JobBoardAuthenticationHandler(
            driver=self.driver, wait=self.wait
        )
        self.terms_handler = JobBoardTermsAgreementHandler(wait=self.wait)
        self.single_page_parser = JobBoardSinglePageParser(driver=self.driver)
        self.filter = filter
        self.job_openings = list[JobOpening]()
        self.single_detail_retriever = JobBoardSingleDetailsRetriever(
            driver=self.driver
        )

    @property
    def job_board_url(self) -> str:
        if not self._job_board_url:
            raise ValueError(
                "Unable to retrieve url for job board. Please check environment variables."
            )
        return self._job_board_url

    def execute(self):
        super().execute()
        if self.driver.title == self.MSFT_LOGIN_TITLE:
            self.handle_auth()
        return self.agree_terms().apply_filters().get_job_listings()

    def handle_auth(self):
        self.auth_handler.handle_auth()
        return self

    def agree_terms(self):
        self.terms_handler.handle_terms_agreement()
        return self

    # TODO: Implement multi-filter
    # TODO: separate this into another class
    def apply_filters(self):
        # select filter from dropdown
        job_nature_filter = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, r'//span[starts-with(@class,"select2-selection")]')
            )
        )
        job_nature_filter.click()
        job_nature_input = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, r'//input[@placeholder="All Job Natures"]')
            )
        )
        job_nature_input.send_keys(self.filter)
        job_nature_input.send_keys(Keys.ENTER)

        # search with filter
        search_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//button[@type="submit"]'))
        )
        search_btn.click()
        print(f"Applied filters: {self.filter}")
        return self

    def get_job_listings(self, pages=3):
        # set results with descending deadline, i.e furthest deadline goes first
        base_url = self.driver.current_url + self.SORT_BY_DESC_DEADLINE
        self.driver.get(base_url)
        all_job_openings = list[JobOpening]()
        for page in range(pages):
            time.sleep(random.randrange(1, 3))
            print("Screening page ", page + 1)
            self.driver.get(base_url + f"&page={page + 1}")
            all_job_openings.extend(self.single_page_parser.retrieve_job_openings())
        self.job_openings = all_job_openings
        print(f"\u2713 Completed scraping {len(self.job_openings)} job openings.")
        return self

    def get_job_details(self):
        pass


class JobWebsite(Enum):
    JOB_BOARD = auto()


class AutomationManagerFactory:
    @staticmethod
    def create_manager(
        source: JobWebsite, driver: webdriver.Chrome, filter: str
    ) -> AutomationManager:
        products = {
            JobWebsite.JOB_BOARD: JobBoardAutomationManager(driver, filter="IT/")
        }
        if source in products:
            return products[source]
        raise NotImplementedError(f"Unsupported source: {source}")
