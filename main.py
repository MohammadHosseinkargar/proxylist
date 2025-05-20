import os
import time
import subprocess
from datetime import datetime

# تنظیمات
REPO_PATH = r"/root/fresh-proxylist"  # مسیر لوکال ریپازیتوری
GITHUB_USER = "MohammadHosseinkargar"
GITHUB_REPO = "proxylist"

# URL ریموت با SSH
GIT_REMOTE = f"git@github.com:{GITHUB_USER}/{GITHUB_REPO}.git"

FILES = {
    "http.txt": "https://vakhov.github.io/fresh-proxy-list/http.txt",
    "https.txt": "https://vakhov.github.io/fresh-proxy-list/https.txt",
    "socks4.txt": "https://vakhov.github.io/fresh-proxy-list/socks4.txt",
    "socks5.txt": "https://vakhov.github.io/fresh-proxy-list/socks5.txt",
}

def run_cmd(command, check=True):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0 and check:
        print(f"Command failed: {command}")
        print(f"Error: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, command)
    return result

def download_files():
    for filename, url in FILES.items():
        filepath = os.path.join(REPO_PATH, filename)
        command = f"curl -sL {url} -o {filepath}"
        run_cmd(command)
        print(f"Downloaded: {filename}")

def setup_git():
    os.chdir(REPO_PATH)

    if not os.path.exists(os.path.join(REPO_PATH, ".git")):
        run_cmd("git init")

    # اگر ریموت origin وجود ندارد اضافه‌اش کن
    remote_check = run_cmd("git remote", check=False).stdout
    if "origin" not in remote_check:
        run_cmd(f"git remote add origin {GIT_REMOTE}")
    else:
        run_cmd("git remote remove origin", check=False)
        run_cmd(f"git remote add origin {GIT_REMOTE}")

    # اگر داخل حالت detached HEAD هستیم، یک شاخه بساز
    head_status = run_cmd("git symbolic-ref --short -q HEAD", check=False).stdout.strip()
    if not head_status:
        run_cmd("git checkout -b main", check=False)

def commit_and_push():
    os.chdir(REPO_PATH)
    run_cmd("git add .")
    commit_message = f"Auto-update proxy list: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    result = run_cmd(f"git diff --cached --quiet", check=False)
    if result.returncode == 0:
        print("No changes to commit.")
        return

    run_cmd(f"git commit -m \"{commit_message}\"")

    # اطمینان از اینکه روی شاخه main هستیم
    run_cmd("git branch -M main", check=False)

    # هندل کردن pull قبل از push (در صورت conflict)
    result = run_cmd("git pull origin main --rebase", check=False)
    if result.returncode != 0:
        print("Pull conflict – skipping push.")
        return

    run_cmd("git push -u origin main")
    print("Changes pushed to repository.")

# اجرای برنامه
setup_git()
while True:
    print("Starting update...")
    download_files()
    try:
        commit_and_push()
    except Exception as e:
        print(f"Error during commit/push: {e}")
    print("Waiting for 30 minutes...")
    time.sleep(10)  # 30 دقیقه

