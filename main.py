import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
import urllib3
import textwrap
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore

# Suppress SSL warnings if using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup a retry-enabled session
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount('http://', adapter)
session.mount('https://', adapter)

def scrape_quotes(url):
    all_quotes = []

    while url:
        print(f"\n Scraping: {url}")
        try:
            response = session.get(url, timeout=10, verify=False)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.find_all('div', class_='quote')

        for quote in quotes:
            text = quote.find('span', class_='text').text.strip('“”')
            author = quote.find('small', class_='author').text
            tags = [tag.text for tag in quote.find_all('a', class_='tag')]

            
            wrapped_text = textwrap.fill(text, width=80)

            all_quotes.append({
                'Quote': wrapped_text,
                'Author': author,
                'Tags': ", ".join(tags)
            })

        
        next_button = soup.find('li', class_='next')
        if next_button:
            next_page = next_button.a['href']
            url = f"https://quotes.toscrape.com{next_page}"
        else:
            break

    return all_quotes


data = scrape_quotes("https://quotes.toscrape.com/")
df = pd.DataFrame(data)


if not df.empty:
    print("\n📋 Clean and Structured Quote Data:\n")
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))


    df.to_csv("quotes_output.csv", index=False)
    print("\ Data saved to 'quotes_output.csv'")
else:
    print(" No data found.")
