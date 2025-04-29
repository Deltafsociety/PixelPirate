import os
import time
import hashlib
import urllib.parse
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from PIL import Image
from fpdf import FPDF
import tkinter as tk
from tkinter import simpledialog, messagebox

visited = set()
screenshots = []

def sanitize_filename(url):
    return hashlib.md5(url.encode()).hexdigest() + ".png"

def create_driver():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,10800")  # Large height for full-page screenshots
    return webdriver.Chrome(options=options)

def crawl_and_screenshot(start_url, output_dir="screenshots", limit=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    domain = urllib.parse.urlparse(start_url).netloc
    queue = [start_url]

    driver = create_driver()
    count = 0

    while queue and count < limit:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            print(f"Visiting: {url}")
            driver.get(url)
            time.sleep(2)

            # Save screenshot
            filename = sanitize_filename(url)
            filepath = os.path.join(output_dir, filename)
            driver.save_screenshot(filepath)
            screenshots.append(filepath)
            count += 1
            print(f"Saved screenshot: {filepath}")

            # Extract links
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = urllib.parse.urljoin(url, link["href"])
                parsed = urllib.parse.urlparse(href)

                # Only crawl internal links (same domain)
                if parsed.netloc == domain and href not in visited:
                    queue.append(href)
        except Exception as e:
            print(f"Error visiting {url}: {e}")

    driver.quit()
    create_pdf_from_images(screenshots)

def create_pdf_from_images(image_files, output_pdf="website_screenshots.pdf"):
    pdf = FPDF()
    for image in image_files:
        img = Image.open(image)
        img_path = os.path.abspath(image)
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=180)  # Adjust for image size
    pdf.output(output_pdf)
    print(f"Saved PDF: {output_pdf}")

def get_inputs_from_user():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Get website URL from the user
    url = simpledialog.askstring("Website URL", "Enter the website URL:")
    if not url:
        messagebox.showerror("Input Error", "Website URL is required!")
        return

    # Get page limit from the user
    limit = simpledialog.askinteger("Crawl Limit", "Enter the number of pages to crawl:", minvalue=1, maxvalue=100)
    if not limit:
        messagebox.showerror("Input Error", "Valid page limit is required!")
        return

    # Start crawling and screenshotting
    crawl_and_screenshot(url, limit=limit)
    messagebox.showinfo("Crawl Complete", f"Finished crawling and screenshotting {limit} pages.")

if __name__ == "__main__":
    get_inputs_from_user()
