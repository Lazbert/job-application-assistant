# %%
from selenium import webdriver
from chromedriver_py import binary_path
from services.manager import AutomationManagerFactory, JobWebsite


def init_driver() -> webdriver.Chrome:
    # initialize Chrome webdriver
    service = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=service)
    return driver


# %%
manager = AutomationManagerFactory.create_manager(
    source=JobWebsite.JOB_BOARD, driver=init_driver(), filter="IT/"
)
all_openings = manager.execute()
print(f"\u2713 Completed scraping {len(all_openings)} job openings.")

# %%
all_openings
