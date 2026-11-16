from abc import ABC, abstractmethod


class BaseTemplate(ABC):

    @abstractmethod
    def generate(self, document, data) -> None:
        """
        Generate document using template structure and style engine.
        """
        pass
