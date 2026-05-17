"""Render the premium enterprise report HTML template with backend context."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class EnterpriseReportTemplateService:
    def __init__(self) -> None:
        template_dir = Path(__file__).resolve().parents[1] / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,  # We control all input — no user HTML
        )
        self.template_name = "premium_enterprise_report.html"

    def render(self, context: dict[str, Any]) -> str:
        template = self.env.get_template(self.template_name)
        return template.render(**context)
