from abc import ABC, abstractmethod
from sankalit_mcp.brand.models import BrandRule, ValidationResult
from sankalit_mcp.brand.context import ValidationContext


class BaseRule(ABC):

    @property
    @abstractmethod
    def metadata(self) -> BrandRule:
        """
        Return the rule metadata definition.
        """
        pass

    @abstractmethod
    def validate(self, context: ValidationContext) -> ValidationResult:
        """
        Perform validation check on the context.
        """
        pass

    @abstractmethod
    def fix(self, context: ValidationContext) -> None:
        """
        Apply automatic corrections to correct the violation.
        """
        pass
