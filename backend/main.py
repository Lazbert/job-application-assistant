# %%
from selenium import webdriver
from chromedriver_py import binary_path
from services.manager import JobBoardAutomationManager


def init_driver() -> webdriver.Chrome:
    # initialize Chrome webdriver
    service = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=service)
    return driver


# %%
manager = JobBoardAutomationManager(driver=init_driver(), filter="IT/")
manager.execute()

# %%
all_openings = manager.get_job_listings()

# %%
all_openings
