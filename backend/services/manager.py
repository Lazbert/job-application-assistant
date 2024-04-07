import os
from datetime import datetime
import time
import random
from enum import Enum, auto
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from interfaces.manager import AutomationManager
from interfaces.job import JobOpening, JobSummary
from services.utils.auth import JobBoardAuthenticationHandler


class JobBoardAutomationManager(AutomationManager):
    MSFT_LOGIN_TITLE = "Sign in to your account"
    DUO_TITLE = "Duo Security"
    SORT_BY_DESC_DEADLINE = "&sort=deadline&order=desc"

    def __init__(self, driver: webdriver.Chrome, filter: str):
        super().__init__(driver)
        self._job_board_url = os.getenv("JOB_BOARD_URL")
        self.auth_handler = JobBoardAuthenticationHandler()
        self.filter = filter

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
        self.auth_handler.handle_auth(self.driver, self.wait)
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

    # TODO: Implement multi-filter
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

    def get_job_listings(self, pages=5) -> list[JobOpening]:
        # set results with descending deadline, i.e furthest deadline goes first
        base_url = self.driver.current_url + self.SORT_BY_DESC_DEADLINE
        self.driver.get(base_url)

        def get_single_page_jobs(driver: webdriver.Chrome) -> list[JobOpening]:
            job_opening_rows = driver.find_elements(
                by=By.XPATH, value=r'//tr[@class="job-item"]'
            )
            print(f"Found {len(job_opening_rows)} job openings")

            res = list[JobOpening]()
            for ind, row in enumerate(job_opening_rows):
                try:
                    summary = row.find_elements(
                        by=By.XPATH,
                        value=r'.//td[@class="small-middle-view"]//td//font[@class="font2"]',
                    )
                    dates = row.find_elements(
                        by=By.XPATH,
                        value=r'.//td[@style="color:#336C99;"]',
                    )
                    if len(summary) != 3 or len(dates) != 2:
                        raise ValueError(
                            f"Expected 5 elements for each job opening. Got {len(summary) + len(dates)} instead at opening {ind + 1}."
                        )
                    posting_date, deadline = [
                        datetime.strptime(
                            str(ele.get_attribute("innerText")).strip(), r"%Y-%m-%d"
                        )
                        for ele in dates
                    ]
                    if deadline < datetime.now():
                        print(
                            f"Deadline {deadline} has passed for opening {ind + 1}. Skipping."
                        )
                        continue
                    company, job_title, job_nature = [
                        str(ele.get_attribute("innerText")).strip() for ele in summary
                    ]
                    job_opening = JobOpening(
                        summary=JobSummary(
                            company=company,
                            job_title=job_title,
                            job_nature=job_nature,
                            posting_date=posting_date,
                            deadline=deadline,
                        )
                    )
                    res.append(job_opening)

                except ValueError as e:
                    print(e)
                    continue
            return res

        all_job_openings = list[JobOpening]()
        for page in range(pages):
            time.sleep(random.randrange(1, 3))
            print("Screening page ", page + 1)
            self.driver.get(base_url + f"&page={page + 1}")
            all_job_openings.extend(get_single_page_jobs(self.driver))
        return all_job_openings


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
