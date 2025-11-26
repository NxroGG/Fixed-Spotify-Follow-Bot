import time, threading, random, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ============================
# SETTINGS
# ============================
SPOTIFY_PROFILE = input("Spotify Link or Username: ").strip()
THREADS = int(input("Threads: "))

# Turn raw username into full URL
if "spotify.com" not in SPOTIFY_PROFILE:
    SPOTIFY_PROFILE = f"https://open.spotify.com/user/{SPOTIFY_PROFILE}"

FOLLOW_SELECTOR = "button[data-testid='follow-button']"

success = 0
success_lock = threading.Lock()


# ============================
# LOAD PROXY WEBSITES
# ============================
def load_proxy_sites():
    if not os.path.exists("proxies.txt"):
        print("\n[ERROR] proxies.txt not found")
        raise SystemExit

    with open("proxies.txt", "r", encoding="utf-8") as f:
        proxies = [line.strip() for line in f if line.strip()]

    if not proxies:
        print("\n[ERROR] proxies.txt is empty!")
        raise SystemExit

    print(f"\nLoaded {len(proxies)} proxy websites.\n")
    return proxies


PROXY_SITES = load_proxy_sites()


# ============================
# SELENIUM SETUP
# ============================
def create_driver():
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=900,900")

    # OPTIONAL: Headless mode
    # opts.add_argument("--headless=new")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    return driver


# ============================
# AUTO-DETECT PROXY INPUT BOX
# ============================
POSSIBLE_INPUTS = [
    "input[name='d']",          # proxysite.com
    "input#input",              # hidester
    "input[name='u']",          # generic
    "input[type='text']",
    "input.form-control",
]


def find_proxy_input(driver):
    for selector in POSSIBLE_INPUTS:
        try:
            el = driver.find_element(By.CSS_SELECTOR, selector)
            return el
        except:
            pass
    return None


# ============================
# WORKER THREAD
# ============================
def worker():
    global success

    try:
        proxy_url = random.choice(PROXY_SITES)
        print(f"[THREAD] Using proxy → {proxy_url}")

        driver = create_driver()
        driver.get(proxy_url)
        time.sleep(2)

        input_box = find_proxy_input(driver)
        if not input_box:
            print("[ERROR] Input box not found (new layout / Cloudflare)")
            driver.quit()
            return

        # Type Spotify URL
        input_box.clear()
        input_box.send_keys(SPOTIFY_PROFILE)
        time.sleep(0.5)

        # Try to submit
        try:
            input_box.submit()
        except:
            # Try clicking the first submit button
            try:
                btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                btn.click()
            except:
                print("[ERROR] Unable to submit URL")
                driver.quit()
                return

        time.sleep(5)

        # Try clicking follow
        try:
            follow_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, FOLLOW_SELECTOR))
            )
            follow_btn.click()

            with success_lock:
                success += 1
                print(f"[SUCCESS] Follow #{success}")

        except:
            print("[ERROR] Follow button not found.")

        driver.quit()

    except Exception as e:
        print(f"[THREAD ERROR] {e}")


# ============================
# THREAD MANAGER
# ============================
def start_threads():
    while True:
        if threading.active_count() - 1 < THREADS:
            threading.Thread(target=worker, daemon=True).start()
        time.sleep(0.1)


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("\nStarting Web Proxy Spotify Bot...\n")
    try:
        start_threads()
    except KeyboardInterrupt:
        print("\nStopped by user.")



