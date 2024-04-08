from abc import ABC, abstractmethod


class SingleDetailsRetriever(ABC):
    def __init__(self, driver) -> None:
        self.driver = driver

    @abstractmethod
    def retrieve_details(self, job_id: str):
        raise NotImplementedError


class JobBoardSingleDetailsRetriever(SingleDetailsRetriever):
    def __init__(self, driver) -> None:
        super().__init__(driver)

    def retrieve_details(self, job_id: str):
        pass
