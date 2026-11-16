from abc import ABC, abstractmethod
from pathlib import Path


class BaseHandler(ABC):
    """Base class for all document handlers."""

    @abstractmethod
    def write(
        self,
        path: Path,
        content: str,
        overwrite: bool = False,
    ) -> dict:
        """Write a document."""
        pass

    @abstractmethod
    def read(
        self,
        path: Path,
    ) -> str:
        """Read a document."""
        pass
