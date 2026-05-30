from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError,
)

from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from playwright.sync_api import sync_playwright

PLAYWRIGHT_TIMEOUT_MS = 30_000
PDF_RENDER_TIMEOUT_SECONDS = 60


def _render_pdf_sync(
    html_file: Path,
    output_path: str,
    allowed_asset_dirs: list[Path],
) -> None:
    browser = None

    html_file = html_file.resolve()
    allowed_asset_dirs = [allowed_dir.resolve() for allowed_dir in allowed_asset_dirs]

    def handle_route(route):
        request_url = route.request.url

        parsed = urlparse(request_url)

        if parsed.scheme == "file":
            file_path = Path(url2pathname(parsed.path)).resolve()

            for allowed_dir in allowed_asset_dirs:
                try:
                    file_path.relative_to(allowed_dir)

                    route.continue_()
                    return

                except ValueError:
                    pass

        route.abort()

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-dev-shm-usage",
                ],
            )

            page = browser.new_page(
                java_script_enabled=False,
            )

            page.set_default_timeout(PLAYWRIGHT_TIMEOUT_MS)

            page.set_default_navigation_timeout(PLAYWRIGHT_TIMEOUT_MS)

            page.route(
                "**/*",
                handle_route,
            )

            page.goto(
                html_file.as_uri(),
                wait_until="load",
                timeout=PLAYWRIGHT_TIMEOUT_MS,
            )

            page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
            )

        finally:
            if browser:
                browser.close()


def render_pdf(
    html_file: Path,
    output_path: str,
    allowed_asset_dirs: list[Path],
) -> None:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            _render_pdf_sync,
            html_file,
            output_path,
            allowed_asset_dirs,
        )

        try:
            future.result(timeout=PDF_RENDER_TIMEOUT_SECONDS)

        except TimeoutError:
            raise TimeoutError("Markdown PDF render exceeded timeout")
