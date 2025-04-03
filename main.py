import os
import time
import subprocess
from datetime import datetime

# تنظیمات
REPO_PATH = r"/root/up"  # مسیر لوکال ریپازیتوری
GIT_REMOTE = "https://github.com/MohammadHosseinkargar/proxylist.git"

FILES = {
    "http.txt": "https://vakhov.github.io/fresh-proxy-list/http.txt",
    "https.txt": "https://vakhov.github.io/fresh-proxy-list/https.txt",
    "socks4.txt": "https://vakhov.github.io/fresh-proxy-list/socks4.txt",
    "socks5.txt": "https://vakhov.github.io/fresh-proxy-list/socks5.txt",
}

# تابع برای دانلود فایل‌ها
def download_files():
    for filename, url in FILES.items():
        filepath = os.path.join(REPO_PATH, filename)
        command = f"curl -sL {url} -o {filepath}"
        subprocess.run(command, shell=True)
        print(f"Downloaded: {filename}")

# تابع برای بررسی و تنظیم `git remote`
def setup_git():
    os.chdir(REPO_PATH)
    
    # مقداردهی اولیه گیت اگر لازم بود
    if not os.path.exists(os.path.join(REPO_PATH, ".git")):
        subprocess.run(["git", "init"], check=True)
    
    # بررسی اینکه `origin` قبلاً مقداردهی شده یا نه
    result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
    if "origin" not in result.stdout:
        subprocess.run(["git", "remote", "add", "origin", GIT_REMOTE], check=True)

# تابع برای کامیت و پوش به گیت
def commit_and_push():
    os.chdir(REPO_PATH)
    subprocess.run(["git", "add", "."], check=True)
    commit_message = f"Auto-update proxy list: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    print("Changes pushed to repository.")

# اجرای برنامه در یک حلقه بی‌نهایت
setup_git()
while True:
    print("Starting update...")
    download_files()
    commit_and_push()
    print("Waiting for 30 minutes...")
    time.sleep(1800)
