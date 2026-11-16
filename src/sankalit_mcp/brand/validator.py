import time
from typing import List
from sankalit_mcp.brand.models import ComplianceReport, ValidationResult, Severity
from sankalit_mcp.brand.context import ValidationContext
from sankalit_mcp.brand.registry import RuleRegistry
from sankalit_mcp.brand.grade_policy import GradePolicy


class BrandValidator:

    def __init__(self, registry: RuleRegistry):
        self.registry = registry

    def validate(self, context: ValidationContext) -> ComplianceReport:
        start_time = time.perf_counter()

        results: List[ValidationResult] = []
        passed_count = 0
        warning_count = 0
        error_count = 0

        rules = self.registry.get_all_rules()

        # Track passed rule IDs to check dependencies
        passed_rule_ids = set()
        failed_rule_ids = set()

        for rule in rules:
            rule_id = rule.metadata.id

            # Check dependencies
            deps_failed = False
            for dep in rule.metadata.dependencies:
                if dep in failed_rule_ids:
                    deps_failed = True
                    break

            if deps_failed:
                results.append(
                    ValidationResult(
                        rule_id=rule_id,
                        passed=False,
                        expected="Dependencies passed",
                        actual="Dependency failed",
                        message=f"Skipped rule validation because dependency rule failed.",
                    )
                )
                failed_rule_ids.add(rule_id)
                error_count += 1
                continue

            try:
                res = rule.validate(context)
                results.append(res)
                if res.passed:
                    passed_rule_ids.add(rule_id)
                    passed_count += 1
                else:
                    failed_rule_ids.add(rule_id)
                    if rule.metadata.severity == Severity.WARNING:
                        warning_count += 1
                    else:
                        error_count += 1
            except Exception as e:
                results.append(
                    ValidationResult(
                        rule_id=rule_id,
                        passed=False,
                        expected="Successful execution",
                        actual=f"Exception: {str(e)}",
                        message=f"Rule validator crashed with error: {str(e)}",
                    )
                )
                failed_rule_ids.add(rule_id)
                error_count += 1

        total_executed = len(rules)
        score = 100.0
        if total_executed > 0:
            score = (passed_count / total_executed) * 100.0

        grade = GradePolicy.resolve_grade(score)
        end_time = time.perf_counter()

        return ComplianceReport(
            score=score,
            grade=grade,
            execution_time_seconds=end_time - start_time,
            total_executed=total_executed,
            passed_count=passed_count,
            warning_count=warning_count,
            error_count=error_count,
            results=results,
            fixes_applied=[],
        )
