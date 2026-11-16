from typing import List
from sankalit_mcp.brand.models import ComplianceReport
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.registry import RuleRegistry


class BrandFixer:

    def __init__(self, registry: RuleRegistry):
        self.registry = registry

    def fix(self, context: ValidationContext, report: ComplianceReport) -> List[str]:
        fixes_applied: List[str] = []

        for res in report.results:
            if not res.passed:
                try:
                    rule = self.registry.get_rule(res.rule_id)
                    if rule.metadata.auto_fixable:
                        rule.fix(context)
                        fixes_applied.append(res.rule_id)
                except KeyError:
                    pass

        return fixes_applied
