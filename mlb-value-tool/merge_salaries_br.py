import requests
from bs4 import BeautifulSoup
from docx import Document
import time

def extract_links_from_docx(path):
    doc = Document(path)
    pairs = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if "http" in text:
            name, url = text.split("http", 1)
            name = name.strip()
            url = "http" + url.strip()
            pairs.append((name, url))

    return pairs

def get_payroll_salary(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        salary_box = soup.find("div", string=lambda s: s and "2025 PAYROLL SALARY" in s)
        if not salary_box:
            return None

        # Look for salary number in next sibling
        parent = salary_box.find_parent()
        if not parent:
            return None

        salary_div = parent.find_next("div")
        if not salary_div:
            return None

        salary_text = salary_div.get_text().strip().replace("$", "").replace(",", "")
        return int(salary_text)
    except Exception as e:
        print(f"❌ Failed to extract from {url}: {e}")
        return None

def main():
    input_docx = "Batters Links.docx"  # Change if needed
    output_txt = "salaries_2025.txt"

    players = extract_links_from_docx(input_docx)
    with open(output_txt, "w") as f:
        for name, url in players:
            print(f"🔍 Fetching salary for {name}...")
            salary = get_payroll_salary(url)
            if salary is not None:
                f.write(f"{name}: {salary}\n")
                print(f"✅ {name}: {salary}")
            else:
                f.write(f"{name}: None\n")
                print(f"❌ {name}: None")
            time.sleep(1.5)  # Be polite to Spotrac

if __name__ == "__main__":
    main()































