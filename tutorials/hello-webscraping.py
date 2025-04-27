from scrapegraphai.graphs import SmartScraperGraph

# Define the configuration for the scraping pipeline
graph_config = {
    "llm": {
        "model": "ollama/llama3.2",
        "model_tokens": 8192
    },
    "verbose": True,
    "headless": False,
}


# from dotenv import load_dotenv
# import os
# # Load environment variables from a .env file
# load_dotenv()

# # Get the OpenAI API key from the .env file
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise ValueError("OPENAI_API_KEY is not set in the .env file")

# graph_config = {
#    "llm": {
#        "api_key": api_key,
#        "model": "openai/gpt-4o-mini",
#    },
#    "verbose": True,
#    "headless": False,
# }

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(
    prompt="Extract useful information from the webpage, including a description of what the company does, founders and social media links",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# Run the pipeline
result = smart_scraper_graph.run()

# Run the pipeline
import json
print(json.dumps(result, indent=4))