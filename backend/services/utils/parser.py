from abc import ABC, abstractmethod
import re
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
                link_tag = row.find_element(
                    by=By.XPATH, value=r'.//a[@class="job-post"]'
                )
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
                details_href = link_tag.get_attribute("href")
                if not details_href:
                    raise ValueError(
                        f"Unable to retrieve job id for opening {ind + 1}."
                    )
                match = re.search(r".*?jp=(\d*)", details_href)
                if not match:
                    raise ValueError(
                        f"Unable to match regex pattern for opening {ind + 1}."
                    )
                job_id = match.group(1)
                company, job_title, job_nature = [
                    str(ele.get_attribute("innerText")).strip() for ele in summary
                ]
                job_opening = JobOpening(
                    id=job_id,
                    summary=JobSummary(
                        company=company,
                        job_title=job_title,
                        job_nature=job_nature,
                        posting_date=posting_date,
                        deadline=deadline,
                    ),
                )
                res.append(job_opening)

            except ValueError as e:
                print(e)
                continue
        return res
