import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import os

# Download DejaVuSans if not present
def ensure_dejavu():
    import requests
    font_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(font_dir, 'DejaVuSans.ttf')
    # Use a CDN for reliability
    url = 'https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans.ttf'
    def is_valid_ttf(path):
        try:
            with open(path, 'rb') as f:
                return f.read(4) in [b'\x00\x01\x00\x00', b'OTTO']
        except Exception:
            return False
    try:
        if not os.path.exists(font_path) or not is_valid_ttf(font_path):
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            with open(font_path, 'wb') as f:
                f.write(r.content)
        if is_valid_ttf(font_path):
            return font_path
    except Exception:
        pass
    return None  # Fallback if download fails

import re

def fetch_guidelines(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the main content area
    main = soup.find('main')
    if not main:
        main = soup.body

    # Extract headings and list items (guidelines)
    content = []
    for tag in main.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li']):
        text = tag.get_text(strip=True)
        if text:
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            content.append(text)
    return content

import unicodedata

def save_to_pdf(lines, pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    font_path = ensure_dejavu()
    if font_path:
        try:
            pdf.add_font('DejaVu', '', font_path)
            pdf.set_font('DejaVu', '', 12)
            for line in lines:
                pdf.multi_cell(0, 10, line)
                pdf.ln(1)
            pdf.output(pdf_path)
            print("PDF generated with DejaVuSans Unicode font.")
            return
        except Exception as e:
            print(f"Unicode font failed: {e}. Falling back to Helvetica (ASCII only).")
    # Fallback: use Helvetica and sanitize text
    pdf.set_font('Helvetica', '', 12)
    for line in lines:
        safe_line = unicodedata.normalize('NFKD', line).encode('ascii', 'ignore').decode('ascii')
        pdf.multi_cell(0, 10, safe_line)
        pdf.ln(1)
    pdf.output(pdf_path)
    print("PDF generated with Helvetica (ASCII fallback). Some characters may be missing.")

def main():
    url = 'https://legal.trustpilot.com/for-reviewers/guidelines-for-reviewers'
    pdf_file = 'trustpilot_guidelines.pdf'
    print(f"Fetching guidelines from {url} ...")
    guidelines = fetch_guidelines(url)
    print(f"Saving to {pdf_file} ...")
    save_to_pdf(guidelines, pdf_file)
    print(f"Done! PDF saved as {pdf_file}")

if __name__ == '__main__':
    main()
