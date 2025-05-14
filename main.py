from datetime import datetime
import time
from colorama import Fore
import requests
import random
from fake_useragent import UserAgent
import asyncio
import json
import gzip
import brotli
import zlib
import chardet
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class divo:
    BASE_URL = "https://front-divo.banana.codes/api/"
    HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "br",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "Connection": "keep-alive",
        "Host": "front-divo.banana.codes",
        "Referer": "https://front-divo.banana.codes/tasks",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "sec-ch-ua": '"Microsoft Edge";v="136", "Microsoft Edge WebView2";v="136", "Not.A/Brand";v="99", "Chromium";v="136"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"' 
    }

    def __init__(self):
        self.config = self.load_config()
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.session = self.sessions()
        self._original_requests = {
            "get": requests.get,
            "post": requests.post,
            "put": requests.put,
            "delete": requests.delete,
        }
        self.proxy_session = None

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Divo Bot", Fore.CYAN)
        self.log("🚀 Created by MRPTech", Fore.CYAN)
        self.log("📢 Channel: t.me/mrptechofficial\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
        safe_message = message.encode("utf-8", "backslashreplace").decode("utf-8")
        print(
            Fore.LIGHTBLACK_EX
            + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |")
            + " "
            + color
            + safe_message
            + Fore.RESET
        )

    def sessions(self):
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 520]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def decode_response(self, response):
        """
        Mendekode response dari server secara umum.

        Parameter:
            response: objek requests.Response

        Mengembalikan:
            - Jika Content-Type mengandung 'application/json', maka mengembalikan objek Python (dict atau list) hasil parsing JSON.
            - Jika bukan JSON, maka mengembalikan string hasil decode.
        """
        # Ambil header
        content_encoding = response.headers.get("Content-Encoding", "").lower()
        content_type = response.headers.get("Content-Type", "").lower()

        # Tentukan charset dari Content-Type, default ke utf-8
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=")[-1].split(";")[0].strip()

        # Ambil data mentah
        data = response.content

        # Dekompresi jika perlu
        try:
            if content_encoding == "gzip":
                data = gzip.decompress(data)
            elif content_encoding in ["br", "brotli"]:
                data = brotli.decompress(data)
            elif content_encoding in ["deflate", "zlib"]:
                data = zlib.decompress(data)
        except Exception:
            # Jika dekompresi gagal, lanjutkan dengan data asli
            pass

        # Coba decode menggunakan charset yang didapat
        try:
            text = data.decode(charset)
        except Exception:
            # Fallback: deteksi encoding dengan chardet
            detection = chardet.detect(data)
            detected_encoding = detection.get("encoding", "utf-8")
            text = data.decode(detected_encoding, errors="replace")

        # Jika konten berupa JSON, kembalikan hasil parsing JSON
        if "application/json" in content_type:
            try:
                return json.loads(text)
            except Exception:
                # Jika parsing JSON gagal, kembalikan string hasil decode
                return text
        else:
            return text

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log(
                "❌ Failed to parse config.json. Please check the file format.",
                Fore.RED,
            )
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        """
        Single-step login: fetch user info using getUser API and display key fields.
        """
        self.log("🔐 Attempting to log in...", Fore.GREEN)
        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        token = self.query_list[index]
        self.log(f"📋 Using token: {token[:10]}... (truncated for security)", Fore.CYAN)

        # Store token for future use
        self.token = token

        # API: getUser
        login_url = f"{self.BASE_URL}getUser?user_id={token}"
        headers = {**self.HEADERS}

        try:
            self.log("📡 Sending request to getUser...", Fore.CYAN)
            response = requests.get(login_url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            self.log(f"❌ API request failed: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {response.text}", Fore.RED)
            except Exception:
                pass
            return
        except ValueError:
            self.log("❌ Failed to parse JSON response", Fore.RED)
            return

        # Check status
        if data.get("status") != "success":
            self.log(f"❌ API returned error: {data.get('status')}", Fore.RED)
            return

        # Extract result
        result = data.get("result", {})
        user_id = result.get("user_id", "N/A")
        user_status = result.get("user_status", "N/A")
        coins = result.get("coins", "N/A")
        remaining_votes = result.get("remaining_votes", "N/A")
        potential_reward = result.get("potential_reward", "N/A")
        register_date = result.get("register_date", "N/A")

        # Display key information
        self.log("👤 User Information:", Fore.GREEN)
        self.log(f"    - ID: {user_id}", Fore.CYAN)
        self.log(f"    - Status: {user_status}", Fore.CYAN)
        self.log(f"    - Coins: {coins}", Fore.CYAN)
        self.log(f"    - Remaining Votes: {remaining_votes}", Fore.CYAN)
        self.log(f"    - Potential Reward: {potential_reward}", Fore.CYAN)
        self.log(f"    - Registered At: {register_date}", Fore.CYAN)

    def model(self) -> None:
        """
        Pick up models based on remaining_votes: fetch available models and vote.
        """
        self.log("🤖 Starting model pickup...", Fore.GREEN)

        if not hasattr(self, "token"):
            self.log("❌ No token found. Please login first.", Fore.RED)
            return

        # Refresh user info to get latest remaining votes
        self.log("🔄 Checking remaining votes...", Fore.CYAN)
        user_url = f"{self.BASE_URL}getUser?user_id={self.token}"
        try:
            resp = requests.get(user_url, headers=self.HEADERS)
            resp.raise_for_status()
            user_data = resp.json().get("result", {})
            remaining = user_data.get("remaining_votes", 0)
        except Exception as e:
            self.log(f"❌ Failed to get remaining votes: {e}", Fore.RED)
            return

        if remaining <= 0:
            self.log("ℹ️ No remaining votes available", Fore.YELLOW)
            return
        self.log(f"📊 You have {remaining} vote(s) available", Fore.CYAN)

        # Get list of models
        models_url = f"{self.BASE_URL}getModels?user_id={self.token}"
        try:
            self.log("📡 Fetching models list...", Fore.CYAN)
            models_resp = requests.get(models_url, headers=self.HEADERS)
            models_resp.raise_for_status()
            models = models_resp.json().get("result", {}).get("models", [])
        except Exception as e:
            self.log(f"❌ Failed to fetch models: {e}", Fore.RED)
            return

        # Filter models not yet voted
        available = [m for m in models if not m.get("user_voted")]
        if not available:
            self.log("ℹ️ No new models available to vote", Fore.YELLOW)
            return

        picks = min(remaining, len(available))
        self.log(f"🔢 Preparing to vote for {picks} model(s)...", Fore.CYAN)

        for m in available[:picks]:
            vote_url = f"{self.BASE_URL}voteForModel?user_id={self.token}&model_id={m['id']}"
            try:
                vote_resp = requests.post(vote_url, headers=self.HEADERS)
                vote_resp.raise_for_status()
                result = vote_resp.json().get("result", {})
                self.log(
                    f"✅ Voted model {m['id']}, coins_awarded: {result.get('coins_awarded', 0)}",
                    Fore.GREEN
                )
            except Exception as e:
                self.log(f"❌ Failed to vote model {m['id']}: {e}", Fore.RED)

        # Refresh remaining votes after voting
        self.log("🔄 Refreshing vote count...", Fore.CYAN)
        try:
            final = requests.get(user_url, headers=self.HEADERS).json().get("result", {})
            new_remaining = final.get("remaining_votes", 0)
            self.log(f"📊 Remaining votes: {new_remaining}", Fore.CYAN)
            self.remaining_votes = new_remaining
        except Exception:
            pass
        
    def load_proxies(self, filename="proxy.txt"):
        """
        Reads proxies from a file and returns them as a list.

        Args:
            filename (str): The path to the proxy file.

        Returns:
            list: A list of proxy addresses.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty.")
            return proxies
        except Exception as e:
            self.log(f"❌ Failed to load proxies: {e}", Fore.RED)
            return []

    def set_proxy_session(self, proxies: list) -> requests.Session:
        """
        Creates a requests session with a working proxy from the given list.

        If a chosen proxy fails the connectivity test, it will try another proxy
        until a working one is found. If no proxies work or the list is empty, it
        will return a session with a direct connection.

        Args:
            proxies (list): A list of proxy addresses (e.g., "http://proxy_address:port").

        Returns:
            requests.Session: A session object configured with a working proxy,
                            or a direct connection if none are available.
        """
        # If no proxies are provided, use a direct connection.
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            self.proxy_session = requests.Session()
            return self.proxy_session

        # Copy the list so that we can modify it without affecting the original.
        available_proxies = proxies.copy()

        while available_proxies:
            proxy_url = random.choice(available_proxies)
            self.proxy_session = requests.Session()
            self.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}

            try:
                test_url = "https://httpbin.org/ip"
                response = self.proxy_session.get(test_url, timeout=5)
                response.raise_for_status()
                origin_ip = response.json().get("origin", "Unknown IP")
                self.log(
                    f"✅ Using Proxy: {proxy_url} | Your IP: {origin_ip}", Fore.GREEN
                )
                return self.proxy_session
            except requests.RequestException as e:
                self.log(f"❌ Proxy failed: {proxy_url} | Error: {e}", Fore.RED)
                # Remove the failed proxy and try again.
                available_proxies.remove(proxy_url)

        # If none of the proxies worked, use a direct connection.
        self.log("⚠️ All proxies failed. Using direct connection.", Fore.YELLOW)
        self.proxy_session = requests.Session()
        return self.proxy_session

    def override_requests(self):
        import random

        """Override requests functions globally when proxy is enabled."""
        if self.config.get("proxy", False):
            self.log("[CONFIG] 🛡️ Proxy: ✅ Enabled", Fore.YELLOW)
            proxies = self.load_proxies()
            self.set_proxy_session(proxies)

            # Override request methods
            requests.get = self.proxy_session.get
            requests.post = self.proxy_session.post
            requests.put = self.proxy_session.put
            requests.delete = self.proxy_session.delete
        else:
            self.log("[CONFIG] proxy: ❌ Disabled", Fore.RED)
            # Restore original functions if proxy is disabled
            requests.get = self._original_requests["get"]
            requests.post = self._original_requests["post"]
            requests.put = self._original_requests["put"]
            requests.delete = self._original_requests["delete"]


async def process_account(account, original_index, account_label, div, config):

    ua = UserAgent()
    div.HEADERS["user-agent"] = ua.random

    # Menampilkan informasi akun
    display_account = account[:10] + "..." if len(account) > 10 else account
    div.log(f"👤 Processing {account_label}: {display_account}", Fore.YELLOW)

    # Override proxy jika diaktifkan
    if config.get("proxy", False):
        div.override_requests()
    else:
        div.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)

    # Login (fungsi blocking, dijalankan di thread terpisah) dengan menggunakan index asli (integer)
    await asyncio.to_thread(div.login, original_index)

    div.log("🛠️ Starting task execution...", Fore.CYAN)
    tasks_config = {
        "model": "pickup model",
    }

    for task_key, task_name in tasks_config.items():
        task_status = config.get(task_key, False)
        color = Fore.YELLOW if task_status else Fore.RED
        div.log(
            f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}",
            color,
        )
        if task_status:
            div.log(f"🔄 Executing {task_name}...", Fore.CYAN)
            await asyncio.to_thread(getattr(div, task_key))

    delay_switch = config.get("delay_account_switch", 10)
    div.log(
        f"➡️ Finished processing {account_label}. Waiting {Fore.WHITE}{delay_switch}{Fore.CYAN} seconds before next account.",
        Fore.CYAN,
    )
    await asyncio.sleep(delay_switch)


async def worker(worker_id, div, config, queue):
    """
    Setiap worker akan mengambil satu akun dari antrian dan memprosesnya secara berurutan.
    Worker tidak akan mengambil akun baru sebelum akun sebelumnya selesai diproses.
    """
    while True:
        try:
            original_index, account = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        account_label = f"Worker-{worker_id} Account-{original_index+1}"
        await process_account(account, original_index, account_label, div, config)
        queue.task_done()
    div.log(f"Worker-{worker_id} finished processing all assigned accounts.", Fore.CYAN)


async def main():
    div = divo()  
    config = div.load_config()
    all_accounts = div.query_list
    num_threads = config.get("thread", 1)  # Jumlah worker sesuai konfigurasi

    if config.get("proxy", False):
        proxies = div.load_proxies()

    div.log(
        "🎉 [LIVEXORDS] === Welcome to Divo Automation === [LIVEXORDS]", Fore.YELLOW
    )
    div.log(f"📂 Loaded {len(all_accounts)} accounts from query list.", Fore.YELLOW)

    while True:
        # Buat queue baru dan masukkan semua akun (dengan index asli)
        queue = asyncio.Queue()
        for idx, account in enumerate(all_accounts):
            queue.put_nowait((idx, account))

        # Buat task worker sesuai dengan jumlah thread yang diinginkan
        workers = [
            asyncio.create_task(worker(i + 1, div, config, queue))
            for i in range(num_threads)
        ]

        # Tunggu hingga semua akun di queue telah diproses
        await queue.join()

        # Opsional: batalkan task worker (agar tidak terjadi tumpang tindih)
        for w in workers:
            w.cancel()

        div.log("🔁 All accounts processed. Restarting loop.", Fore.CYAN)
        delay_loop = config.get("delay_loop", 30)
        div.log(
            f"⏳ Sleeping for {Fore.WHITE}{delay_loop}{Fore.CYAN} seconds before restarting.",
            Fore.CYAN,
        )
        await asyncio.sleep(delay_loop)


if __name__ == "__main__":
    asyncio.run(main())
