

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys


OUTPUT_FILE = "reels_links.txt"
START_URL = "https://www.instagram.com/reels/"

def find_chrome_binary():
    """Znajdź prawdziwe Google Chrome (nie Chromium)."""
    env_path = os.getenv("CHROME_BINARY_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    candidates = []
    if sys.platform.startswith("win"):  # Windows
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    elif sys.platform.startswith("darwin"):  # macOS
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
    else:  # Linux
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
        ]

    for path in candidates:
        if os.path.exists(path):
            return path

    print("Nie znaleziono Google Chrome. Sprawdź instalację lub ustaw CHROME_BINARY_PATH.")
    sys.exit(1)

def find_user_data_dir():
    """Znajdź folder User Data, żeby załadować istniejący profil z zalogowaną sesją."""
    env_dir = os.getenv("CHROME_USER_DATA_DIR")
    if env_dir and os.path.exists(env_dir):
        return env_dir

    if sys.platform.startswith("win"):
        local_app = os.getenv("LOCALAPPDATA")
        default = os.path.join(local_app, r"Google\Chrome\User Data")
    elif sys.platform.startswith("darwin"):
        default = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    else:
        default = os.path.expanduser("~/.config/google-chrome")

    if os.path.exists(default):
        return default

    print("Nie znaleziono folderu User Data Chrome. Ustaw CHROME_USER_DATA_DIR.")
    sys.exit(1)

PROFILE_NAME = os.getenv("CHROME_PROFILE", "Default")

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)

    chrome_binary = find_chrome_binary()
    user_data_dir = find_user_data_dir()

    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={PROFILE_NAME}")
    options.add_argument("--log-level=3")

    try:
        service = Service(ChromeDriverManager().install())
    except Exception as e:
        print(f"Błąd podczas instalacji ChromeDrivera: {e}")
        sys.exit(1)

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        print(f"Nie udało się uruchomić ChromeDriver: {e}")
        sys.exit(1)

    driver.get(START_URL)

    visited = set()

    try:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            print(f"Monitoruję linki w Chrome (profile: {PROFILE_NAME}, data dir: {user_data_dir})...")
            while True:
                try:
                    for handle in driver.window_handles:
                        driver.switch_to.window(handle)
                        url = driver.current_url
                        if url and url not in visited:
                            visited.add(url)
                            f.write(url + "\n")
                            f.flush()
                            print(f"Nowy link zapisany: {url}")
                except WebDriverException as e:
                    print(f"Błąd podczas pobierania URL: {e}")
                time.sleep(1)
    except KeyboardInterrupt:
        print("Monitorowanie linków zakończone przez użytkownika.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
