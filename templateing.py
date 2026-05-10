from fastapi.responses import HTMLResponse
from pathlib import Path
import html

class MiniTemplates:
    """
    Lightweight replacement for Jinja2Templates.
    - No Jinja2
    - No caching
    - No parsing engine
    - Only simple {{ var }} replacement
    """

    def __init__(self, directory: str):
        self.base_dir = Path(directory)

    def get_template(self, name: str):
        path = self.base_dir / name

        if not path.exists():
            raise FileNotFoundError(f"Template not found: {name}")

        return path.read_text(encoding="utf-8")

    def TemplateResponse(self, name: str, context: dict = None, status_code: int = 200):
        context = context or {}

        raw_html = self.get_template(name)

        # Always inject request safety (FastAPI expects it in your old setup)
        context.setdefault("request", None)

        # Simple variable replacement: {{ key }}
        rendered = self._render(raw_html, context)

        return HTMLResponse(content=rendered, status_code=status_code)

    def _render(self, html_text: str, context: dict) -> str:
        result = html_text

        for key, value in context.items():
            placeholder = "{{ " + key + " }}"

            if value is None:
                value = ""

            # basic HTML escaping for safety
            value = html.escape(str(value))

            result = result.replace(placeholder, value)

        return result