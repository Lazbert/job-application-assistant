from abc import ABC, abstractmethod
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from interfaces.job import JobOpening, JobSummary


class SinglePageParser(ABC):
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver

    @abstractmethod
    def retrieve_job_openings(self, driver: webdriver.Chrome) -> list[JobOpening]:
        raise NotImplementedError


class JobBoardSinglePageParser(SinglePageParser):
    def __init__(self, driver: webdriver.Chrome) -> None:
        super().__init__(driver)

    def retrieve_job_openings(self):
        job_opening_rows = self.driver.find_elements(
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
