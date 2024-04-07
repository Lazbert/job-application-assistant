from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TermsAgreementHandler(ABC):
    def __init__(self, wait: WebDriverWait) -> None:
        self.wait = wait

    @abstractmethod
    def handle_terms_agreement(self, driver: webdriver.Chrome, wait: WebDriverWait):
        raise NotImplementedError


class JobBoardTermsAgreementHandler(TermsAgreementHandler):
    def __init__(self, wait: WebDriverWait) -> None:
        super().__init__(wait)

    def handle_terms_agreement(self):
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
