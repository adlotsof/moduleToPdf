from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pdfkit
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from bs4 import BeautifulSoup
import re


COURSE_WEBSITE = 'https://learn2.open......view.php?name=MU123-123'

def attach_to_existing_session(debugging_port='9222'):
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "debuggerAddress", f"localhost:{debugging_port}")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_weekly_links(driver, overview_url):
    driver.get(overview_url)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Try to find and click the "All weeks" button
    try:
        all_weeks_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-visiblelabel='All weeks']"))
        )
        all_weeks_button.click()
        print("Clicked 'All weeks' button.")

        # Wait for the content to update
        time.sleep(2)
    except (TimeoutException, NoSuchElementException):
        print("Could not find or click the 'All weeks' button. Proceeding with current page content.")

    # Get the updated page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Try to find links matching the pattern
    links = soup.find_all('a', href=re.compile(
        r'mod/oucontent/view\.php\?id=\d+'))

    if not links:
        print("Could not find any links matching the expected pattern.")
        print("Page title:", driver.title)
        print("Current URL:", driver.current_url)
        print("Available classes:", [
              cls for cls in soup.find_all() if cls.get('class')])
        raise Exception(
            "No matching links found. Please check the page structure.")

    # Extract and modify the links
    weekly_links = []
    for link in links:
        href = link.get('href')
        if not href.startswith('http'):
            # If it's a relative URL, make it absolute
            href = f"{driver.current_url.split('//', 1)[0]}//{driver.current_url.split('//', 1)[1].split('/', 1)[0]}{href}"
        # Append the printable parameter
        printable_link = f"{href}&printable=1"
        weekly_links.append(printable_link)

    print(f"Found {len(weekly_links)} links.")
    weekly_links = list(dict.fromkeys(weekly_links))  # Remove duplicates
    print(f"Found {len(weekly_links)} unique links.")
    return weekly_links


def get_printable_content(driver, url):
    driver.get(url)
    # Wait for content to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "region-main"))
    )
    return driver.page_source


def extract_headings(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = soup.find_all(['h1', 'h2'])
    return [(heading.name, heading.text.strip()) for heading in headings]


def create_toc(all_headings):
    toc_html = "<h1>Table of Contents</h1>"
    for week, headings in enumerate(all_headings, 1):
        toc_html += f"<h2>Week {week}</h2>"
        for heading_type, heading_text in headings:
            indent = "&nbsp;" * 4 if heading_type == 'h2' else ""
            toc_html += f"<p>{indent}{heading_text}</p>"
    return toc_html


def html_to_pdf(html_content, output_filename):
    pdfkit.from_string(html_content, output_filename)


def merge_pdfs(pdf_files, output_filename):
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_filename)
    merger.close()


def add_page_numbers(input_pdf, output_pdf):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num, page in enumerate(reader.pages, 1):
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 10)
        can.drawString(540, 25, str(page_num))  # Adjust position as needed
        can.save()

        packet.seek(0)
        new_page = PdfReader(packet).pages[0]
        page.merge_page(new_page)
        writer.add_page(page)

    with open(output_pdf, "wb") as fp:
        writer.write(fp)

def main():
    # Attach to the existing Chrome session
    driver = attach_to_existing_session()

    # Get list of weekly content URLs
    overview_url = COURSE_WEBSITE
    weekly_urls = get_weekly_links(driver, overview_url)

    pdf_files = []
    all_headings = []
    for i, url in enumerate(weekly_urls):
        content = get_printable_content(driver, url)
        headings = extract_headings(content)
        all_headings.append(headings)
        pdf_filename = f"week_{i+1}.pdf"
        html_to_pdf(content, pdf_filename)
        pdf_files.append(pdf_filename)

    # Create and add TOC
    toc_html = create_toc(all_headings)
    toc_filename = "table_of_contents.pdf"
    html_to_pdf(toc_html, toc_filename)
    pdf_files.insert(0, toc_filename)

    # Merge all PDFs into one
    merged_filename = "coursework_ebook_with_toc.pdf"
    merge_pdfs(pdf_files, merged_filename)

    # Add page numbers
    final_filename = "coursework_ebook_final.pdf"
    add_page_numbers(merged_filename, final_filename)

    print(f"Created final PDF: {final_filename}")

    # Note: We don't call driver.quit() here to keep the existing session open

if __name__ == "__main__":
    main()
