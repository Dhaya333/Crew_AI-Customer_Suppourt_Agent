from crewai_tools import ScrapeWebsiteTool, SerperDevTool

# Scrapes the CrewAI docs page so the support agent can ground its
# answers in real documentation instead of hallucinating.
docs_scrape_tool = ScrapeWebsiteTool(
    website_url="https://docs.crewai.com/how-to/Creating-a-Crew-and-kick-it-off/"
)


search_tool = SerperDevTool()