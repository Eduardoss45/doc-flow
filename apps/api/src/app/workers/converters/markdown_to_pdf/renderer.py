from playwright.sync_api import sync_playwright


def render_pdf(
    html_document: str,
    output_path: str,
) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
            ],
        )

        page = browser.new_page(
            java_script_enabled=False,
        )

        page.route(
            "**/*",
            lambda route: route.abort(),
        )

        page.set_content(
            html_document,
            wait_until="load",
        )

        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
        )

        browser.close()
