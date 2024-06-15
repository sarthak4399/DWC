import scrapy
import requests
from pathlib import Path

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["onion"]
    start_urls = [
        "http://ysra3n2sraa5p5t4mtdx4xzyafdz5z2iypmjbvwlygjljhj4csztmbid.onion/"
    ]
    suspicious_keywords = [
        "drugs", "heroin", "cocaine", "methamphetamine", "meth", "cannabis",
        "marijuana", "ecstasy", "LSD", "narcotics", "opium", "fentanyl", "ketamine",
        "PCP", "crack", "speed", "hashish", "hallucinogen", "psilocybin", "MDMA",
        "amphetamine", "benzos", "oxycodone", "hydrocodone", "morphine", "weapons",
        "guns", "firearms", "explosives", "grenades", "ammunition", "bullets", "rifles",
        "pistols", "shotguns", "bombs", "silencers", "tasers", "knives", "switchblades",
        "swords", "crossbows", "molotov", "IED", "mines", "RPG", "AK-47", "AR-15",
        "hacking", "hacker", "malware", "ransomware", "spyware", "trojan", "virus",
        "phishing", "DDoS", "brute force", "keylogger", "backdoor", "botnet", "exploit",
        "zero-day", "SQL injection", "XSS", "cross-site scripting", "rootkit", "dark web",
        "darknet", "Tor", "bitcoin", "cryptocurrency", "wallet", "encryption", "decryption",
        "cryptojacking", "fraud", "scam", "counterfeit", "money laundering", "embezzlement",
        "forgery", "identity theft", "credit card fraud", "skimming", "phishing", "Ponzi scheme",
        "pyramid scheme", "tax evasion", "insider trading", "bribery", "kickbacks", "extortion",
        "blackmail", "racketeering", "smuggling", "fence", "fake IDs", "false documents",
        "human trafficking", "sex trafficking", "exploitation", "forced labor", "child pornography",
        "illegal adoption", "organ trafficking", "slavery", "coerced", "abducted", "kidnapped",
        "prostitution", "brothel", "escort", "pimp", "illegal", "banned", "prohibited", "black market",
        "underground market", "smuggling", "bootleg", "contraband", "poaching", "wildlife trafficking",
        "counterfeit goods", "stolen", "fence", "chop shop", "hitman", "contract killing", "assassination",extremist", "radical", "jihad", "bomb", "bomb-making", "arson"
    ]

    def start_requests(self):
        if not self.is_tor_connection():
            self.log("No Tor connection detected. Aborting spider.")
            return
        

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
        

    def parse(self, response):
        self.log(f"Parsing URL: {response.url}")
        try:
            quotes = response.css("div.h1")
            if not quotes:
                self.log(f"No quotes found on {response.url}")

            for quote in quotes:
                text = quote.css("span.text::text").get(default="").strip()
                author = quote.css("small.author::text").get(default="").strip()
                tags = quote.css("div.tags a.tag::text").extract()
                contains_suspicious_terms = any(tag.lower() in self.suspicious_keywords for tag in tags)
                yield {
                    "text": text,
                    "author": author,
                    "tags": tags,
                    "contains_suspicious_terms": contains_suspicious_terms,
                    "url": response.url
                }
            if self.should_save_file(response):
                self.save_file(response.body, response.url)

        except Exception as e:
            self.log(f"Error parsing {response.url}: {e}")

    def should_save_file(self, response):
        if not response.headers.get("Content-Type", "").startswith("text/html"):
            return False
        
        return True

    def save_file(self, content, url):
        try:
            page = url.split("/")[-2] if url.split("/")[-2] else "index"
            filename = Path("saved_pages") / f"quotes-{page}.html"
            filename.parent.mkdir(parents=True, exist_ok=True)
            filename.write_bytes(content)
            self.log(f"Saved file {filename}")
        except Exception as e:
            self.log(f"Error saving file: {e}")

    def is_tor_connection(self):
        try:
            response = requests.get("https://check.torproject.org", proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"})
            if "Congratulations. This browser is configured to use Tor." in response.text:
                self.log("Tor connection detected.")
                return True
            else:
                self.log("Tor connection not detected.")
                return False
        except Exception as e:
            self.log(f"Error checking Tor connection: {e}")
            return False


# Run the spider
# scrapy crawl quotes


# Output:
# 2021-07-27 01:43:03 [quotes] INFO: Tor connection detected.
# 2021-07-27 01:43:03 [quotes] INFO: Parsing URL: http://ysra3n2sraa5p5t4mtdx4xzyafdz5z2iypmjbvwlygjljhj4csztmbid.onion/
# 2021-07-27 01:43:03 [quotes] INFO: Saved file saved_pages/quotes-index.html

