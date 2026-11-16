from sankalit_mcp.brand.models import ComplianceReport


class ComplianceReportFormatter:

    @staticmethod
    def format_text(report: ComplianceReport) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("SANKALIT BRAND COMPLIANCE REPORT")
        lines.append("=" * 60)
        lines.append(f"Score:  {report.score:.1f}%")
        lines.append(f"Grade:  {report.grade}")
        lines.append(f"Execution Time: {report.execution_time_seconds:.4f} seconds")
        lines.append("-" * 60)
        lines.append(f"Rules Executed: {report.total_executed}")
        lines.append(f"Passed:         {report.passed_count}")
        lines.append(f"Warnings:       {report.warning_count}")
        lines.append(f"Errors:         {report.error_count}")

        if report.fixes_applied:
            lines.append(f"Auto-Fixes:     {', '.join(report.fixes_applied)}")

        lines.append("=" * 60)
        lines.append("DIAGNOSTICS:")
        for res in report.results:
            status = "PASSED" if res.passed else "FAILED"
            lines.append(f"[{status}] Rule: {res.rule_id}")
            lines.append(f"  Message:  {res.message}")
            if not res.passed:
                lines.append(f"  Expected: {res.expected}")
                lines.append(f"  Actual:   {res.actual}")

        lines.append("=" * 60)
        return "\n".join(lines)
