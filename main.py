from follow_bot import spotify
import threading, os, time

# ======================
# GLOBALS
# ======================
lock = threading.Lock()
counter = 0
proxies = []
proxy_index = 0


# ======================
# LOAD SETTINGS
# ======================
spotify_profile = input("Spotify Link or Username: ").strip()
threads = int(input("\nThreads: "))

print("\n[1] Proxies\n[2] Proxyless")
option = int(input("\n> ").strip())


# ======================
# FUNCTIONS
# ======================

def load_proxies():
    """Load proxies from proxies.txt."""
    if not os.path.exists("proxies.txt"):
        print("\nFile proxies.txt not found")
        time.sleep(3)
        raise SystemExit

    with open("proxies.txt", "r", encoding="utf-8") as f:
        for line in f:
            proxy = line.strip()
            if proxy:
                proxies.append(proxy)

    if not proxies:
        print("\nNo proxies found in proxies.txt")
        time.sleep(3)
        raise SystemExit


if option == 1:
    load_proxies()


def safe_print(msg: str):
    """Thread-safe print."""
    with lock:
        print(msg)


def get_proxy():
    """Rotate proxies safely."""
    global proxy_index

    if not proxies:
        return None

    with lock:
        proxy = proxies[proxy_index]
        proxy_index = (proxy_index + 1) % len(proxies)
        return proxy


def worker():
    """Thread worker that attempts to follow with up to 3 retries."""
    global counter

    for _ in range(3):  # retry up to 3 times
        try:
            if option == 1:
                proxy = get_proxy()
                obj = spotify(spotify_profile, proxy)
            else:
                obj = spotify(spotify_profile)

            result, error = obj.follow()

            if result is True:
                with lock:
                    counter += 1
                safe_print(f"[SUCCESS] Followed {counter}")
                return

            else:
                safe_print(f"[ERROR] {error}")
                time.sleep(0.4)

        except Exception as e:
            safe_print(f"[THREAD ERROR] {e}")
            time.sleep(0.4)


def start_threads():
    """Main loop that spawns threads up to thread limit."""
    while True:
        current_threads = threading.active_count() - 1  # subtract main thread

        if current_threads < threads:
            t = threading.Thread(target=worker, daemon=True)
            t.start()

        time.sleep(0.01)


# ======================
# MAIN START
# ======================
if __name__ == "__main__":
    safe_print("Starting follower system…\n")

    try:
        start_threads()
    except KeyboardInterrupt:
        safe_print("\nStopped by user.")