from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TermsAgreementHandler(ABC):
    @abstractmethod
    def handle_terms_agreement(self, driver: webdriver.Chrome, wait: WebDriverWait):
        raise NotImplementedError


class JobBoardTermsAgreementHandler(TermsAgreementHandler):
    def handle_terms_agreement(self, wait: WebDriverWait):
        # agree the declaration form
        declaration_checkbox = wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//input[@type="checkbox"]'))
        )
        declaration_checkbox.click()
        agree_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//input[@value="Agree"]'))
        )
        agree_btn.click()

        # agree disclaimer
        disclaimer_agree_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//input[@type="submit"]'))
        )
        disclaimer_agree_btn.click()
