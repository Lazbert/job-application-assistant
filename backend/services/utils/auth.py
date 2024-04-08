from abc import ABC, abstractmethod
import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv

load_dotenv()


class AuthenticationHandler(ABC):
    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait) -> None:
        self.driver = driver
        self.wait = wait

    @abstractmethod
    def handle_auth(self, driver: webdriver.Chrome, wait: WebDriverWait):
        raise NotImplementedError


class JobBoardAuthenticationHandler(AuthenticationHandler):
    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait) -> None:
        super().__init__(driver, wait)
        self._email = os.getenv("EMAIL")
        self._password = os.getenv("PASSWORD")

    @property
    def email(self) -> str:
        if not self._email:
            raise ValueError(
                "Unable to retrieve email. Please check environment variables."
            )
        return self._email

    @property
    def password(self) -> str:
        if not self._password:
            raise ValueError(
                "Unable to retrieve password. Please check environment variables."
            )
        return self._password

    def handle_auth(self):
        # enter email and click next
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "loginfmt"))
        )
        email_input.send_keys(self.email)
        next_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        next_btn.click()

        # enter password and click sign in
        password_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "i0118"))
        )
        password_input.send_keys(self.password)

        sign_in_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, r'//input[@type="submit"]'))
        )
        sign_in_btn.click()

        # Mobile Authenticator
        print("Waiting approval from mobile device...")
        my_device_btn = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.ID, "trust-browser-button"))
        )
        print("\u2713 Received approval from mobile device")
        my_device_btn.click()
