import os
import requests

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

# 3GPP TS 23.501 (5G System Architecture) PDF
PDF_URL = "https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/17.10.00_60/ts_123501v171000p.pdf"
SAVE_PATH = os.path.join(DATA_DIR, "3gpp_ts_23501.pdf")

def download_3gpp():
    if os.path.exists(SAVE_PATH):
        print("[+] 3GPP PDF already exists.")
        return

    print("[*] Downloading 3GPP TS 23.501 PDF...")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(PDF_URL, headers=headers, stream=True, timeout=30)
    response.raise_for_status()  # fail loudly on 4xx/5xx instead of saving an error page

    content_type = response.headers.get("Content-Type", "")
    if "pdf" not in content_type.lower():
        raise ValueError(
            f"[-] Expected a PDF but got Content-Type '{content_type}'. "
            "The URL may be returning an error page instead of the document."
        )

    with open(SAVE_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = os.path.getsize(SAVE_PATH) / (1024 * 1024)
    print(f"[+] Download complete! ({size_mb:.1f} MB)")

if __name__ == "__main__":
    download_3gpp()