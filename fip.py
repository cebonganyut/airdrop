from colorama import init, Fore, Style
from datetime import datetime, timedelta
from fake_useragent import FakeUserAgent
from faker import Faker
import aiohttp
import asyncio
import json
import os
import re
import sys
from urllib.parse import parse_qs

# Initialize colorama
init(autoreset=True)

class Fintopio:
    def __init__(self) -> None:
        self.faker = Faker()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Host': 'fintopio-tg.fintopio.com',
            'Pragma': 'no-cache',
            'Priority': 'u=3, i',
            'Referer': 'https://fintopio-tg.fintopio.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': FakeUserAgent().random
        }
        self.input_file = None
        self.queries = []

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_timestamp(self, message):
        print(
            f"{Fore.BLUE + Style.BRIGHT}[ {datetime.now().astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{message}",
            flush=True
        )

    def load_queries(self):
        self.input_file = input("Enter the name of your query file (including .txt extension): ")
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"File '{self.input_file}' not found. Please ensure it exists.")
        
        with open(self.input_file, 'r') as file:
            self.queries = [line.strip() for line in file if line.strip()]
        
        if not self.queries:
            raise ValueError(f"File '{self.input_file}' is empty.")
        
        self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Loaded {len(self.queries)} queries from '{self.input_file}' ]{Style.RESET_ALL}")

    async def generate_token(self, session: aiohttp.ClientSession, query: str):
        url = f'https://fintopio-tg.fintopio.com/api/auth/telegram?{query}'
        try:
            async with session.get(url=url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                token = data['token']
                parsed_query = parse_qs(query)
                user_data_json = parsed_query['user'][0]
                user_data = json.loads(user_data_json)
                username = user_data['username'] if user_data else self.faker.user_name()
                return (token, username)
        except Exception as e:
            self.print_timestamp(
                f"{Fore.YELLOW + Style.BRIGHT}[ Failed To Process {query} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}"
            )
            return None

    async def generate_tokens(self, session: aiohttp.ClientSession, queries):
        tasks = [self.generate_token(session, query) for query in queries]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

    async def init_fast(self, session: aiohttp.ClientSession, token: str):
        url = 'https://fintopio-tg.fintopio.com/api/fast/init'
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}'
        }
        try:
            async with session.get(url=url, headers=headers) as response:
                response.raise_for_status()
                return True
        except Exception:
            return False

    async def activate_referrals(self, session: aiohttp.ClientSession, token: str):
        url = 'https://fintopio-tg.fintopio.com/api/referrals/activate'
        data = json.dumps({'code': 'l5bYPIC8FtjMColV'})
        headers = {
            **self.headers,
            'Authorization': f'Bearer {token}',
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json',
            'Origin': 'https://fintopio-tg.fintopio.com'
        }
        try:
            async with session.post(url=url, headers=headers, data=data) as response:
                response.raise_for_status()
                return True
        except Exception:
            return False

    async def main(self):
        self.load_queries()
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    accounts = await self.generate_tokens(session=session, queries=self.queries)
                    restart_times = []
                    total_balance = 0

                    for (token, username) in accounts:
                        self.print_timestamp(
                            f"{Fore.WHITE + Style.BRIGHT}[ Home/Gem ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                        )
                        await self.init_fast(session=session, token=token)
                        await self.activate_referrals(session=session, token=token)

                        # Rest of your flow, including handling diamond state and daily check-ins
                        # Modify similar methods to use `session` and `await` as needed

                except Exception as e:
                    self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
                    continue

if __name__ == "__main__":
    fintopio = Fintopio()
    asyncio.run(fintopio.main())
