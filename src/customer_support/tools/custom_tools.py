from crewai_tools import ScrapeWebsiteTool, SerperDevTool

# Scrapes the CrewAI docs page so the support agent can ground its
# answers in real documentation instead of hallucinating.
DOC_URLS = [
    "https://docs.crewai.com/how-to/Creating-a-Crew-and-kick-it-off/",
    "https://docs.crewai.com/concepts/memory",
]
 
# One ScrapeWebsiteTool instance per URL (each tool is bound to one page).
docs_scrape_tools = [ScrapeWebsiteTool(website_url=url) for url in DOC_URLS]
 
# Lets the agent run live Google searches (needs SERPER_API_KEY in .env).
search_tool = SerperDevTool()