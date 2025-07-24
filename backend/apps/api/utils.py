import tempfile
import base64

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def html_to_pdf(html_content, page_width=8.27, page_height=11.69):
    """
    Converts HTML content to PDF using Selenium and ChromeDriver.

    :param html_content: HTML content to convert.
    :param page_width: Width of the PDF page in inches.
    :param page_height: Height of the PDF page in inches.
    :return: PDF content as bytes.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    ChromeDriverManager().install()
    driver = webdriver.Chrome(options=options)

    with tempfile.NamedTemporaryFile(delete=True, suffix=".html") as temp_html_file:
        temp_html_file.write(html_content.encode("utf-8"))
        temp_html_file.flush()

        driver.get(f"file://{temp_html_file.name}")
        driver.execute_script("return document.fonts.ready")
        pdf_content = driver.execute_cdp_cmd(
            "Page.printToPDF",
            {
                "printBackground": True,
                "paperWidth": page_width,
                "paperHeight": page_height,
                "marginTop": 0,
                "marginBottom": 0,
                "marginLeft": 0,
                "marginRight": 0,
            },
        )

        return base64.b64decode(pdf_content["data"])
