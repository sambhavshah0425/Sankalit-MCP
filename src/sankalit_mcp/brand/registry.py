from typing import Dict, List
from sankalit_mcp.brand.rules.base_rule import BaseRule


class RuleRegistry:

    def __init__(self):
        self._rules: Dict[str, BaseRule] = {}

    def register(self, rule_instance: BaseRule) -> None:
        rule_id = rule_instance.metadata.id
        if rule_id in self._rules:
            raise ValueError(f"Duplicate rule registration: {rule_id}")
        self._rules[rule_id] = rule_instance

    def get_rule(self, rule_id: str) -> BaseRule:
        rule = self._rules.get(rule_id)
        if not rule:
            raise KeyError(f"Rule {rule_id} is not registered.")
        return rule

    def get_all_rules(self) -> List[BaseRule]:
        return list(self._rules.values())

    def clear(self) -> None:
        self._rules.clear()
