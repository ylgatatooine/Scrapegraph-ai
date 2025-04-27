import requests
from bs4 import BeautifulSoup
import re
import os
import json
import openai

class AMCHyperlinkScraper:
    def __init__(self, url, output_file):
        self.url = url
        self.output_file = output_file

    def scrape_and_save_links(self):
        try:
            # Send a GET request to the URL
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an error for bad status codes

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all hyperlinks
            links = soup.find_all('a', href=True)

            # Filter links based on the text pattern
            valid_links = []
            for link in links:
                text = link.text.strip()
                if re.match(r'^(199[7-9]|20[0-2][0-9]|202[0-5])([ABCD]?)$', text):
                    valid_links.append((text, link['href']))

            # Write the links to the output file
            with open(self.output_file, 'w') as file:
                for text, href in valid_links:
                    file.write(f"{text}: https://live.poshenloh.com{href}\n")

            print(f"Successfully saved {len(valid_links)} links to {self.output_file}")

        except requests.RequestException as e:
            print(f"Error during request: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

class AMCResourceDownloader:
    def __init__(self, input_file, download_dir):
        self.input_file = input_file
        self.download_dir = download_dir

    def download_resources(self):
        try:
            # Read the input file for links
            with open(self.input_file, 'r') as file:
                lines = file.readlines()

            # Create download directory if it doesn't exist
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)

            for line in lines:
                # Extract the URL from the line
                _, url = line.strip().split(": ", 1)

                # Send a GET request to the URL
                response = requests.get(url)
                response.raise_for_status()

                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find "printable PDF" and "answer key" links
                pdf_links = soup.find_all('a', href=True, text=re.compile(r'printable PDF', re.IGNORECASE))
                answer_key_links = soup.find_all('a', href=True, text=re.compile(r'answer key', re.IGNORECASE))

                # Download the resources
                for link in pdf_links + answer_key_links:
                    resource_url = link['href']
                    if not resource_url.startswith('http'):
                        resource_url = requests.compat.urljoin(url, resource_url)

                    # Extract the two closest sections in the URL for renaming
                    url_parts = resource_url.split('/')
                    if len(url_parts) >= 3:
                        section1 = url_parts[-3]
                        section2 = url_parts[-2]
                        resource_name = f"{section1}-{section2}-{os.path.basename(resource_url)}"
                    else:
                        resource_name = os.path.basename(resource_url)

                    resource_path = os.path.join(self.download_dir, resource_name)
                    resource_response = requests.get(resource_url)
                    resource_response.raise_for_status()

                    with open(resource_path, 'wb') as resource_file:
                        resource_file.write(resource_response.content)

                    print(f"Downloaded: {resource_path}")

        except requests.RequestException as e:
            print(f"Error during request: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

class AMCAnswerFileRenamer:
    def __init__(self, folder):
        self.folder = folder

    def rename_answer_files(self):
        try:
            # Iterate through all files in the folder
            for root, _, files in os.walk(self.folder):
                for file in files:
                    # Check if the file name ends with "answers"
                    if file.endswith("answers"):
                        # Add the .html extension
                        old_path = os.path.join(root, file)
                        new_path = f"{old_path}.html"
                        os.rename(old_path, new_path)
                        print(f"Renamed: {old_path} -> {new_path}")

        except Exception as e:
            print(f"An error occurred while renaming files: {e}")
            
class HTMLToOllamaParser:
    def __init__(self, html_file, ollama_model):
        self.html_file = html_file
        self.ollama_model = ollama_model

    def parse_and_query_ollama(self):
        try:
            # Read the HTML file
            with open(self.html_file, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Prepare the prompt for Ollama
            prompt = f"Extract the list of answers from the following HTML content:\n\n{html_content}"

            # Query Ollama
            response = openai.Completion.create(
                model=self.ollama_model,
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )

            # Parse and print the response
            answers = response.choices[0].text.strip()
            print("Extracted Answers:")
            print(answers)

        except FileNotFoundError:
            print(f"File not found: {self.html_file}")
        except openai.error.OpenAIError as e:
            print(f"Error querying Ollama: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
# Usage
if __name__ == "__main__":
    # url = "https://live.poshenloh.com/past-contests"
    # output_file = "amc_links.txt"
    # scraper = AMCHyperlinkScraper(url, output_file)
    # scraper.scrape_and_save_links()
    download_dir = "amc_resources"
    # downloader = AMCResourceDownloader(output_file, download_dir)
    # downloader.download_resources()
    renamer = AMCAnswerFileRenamer(download_dir)
    renamer.rename_answer_files()