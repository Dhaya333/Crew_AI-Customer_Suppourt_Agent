"""
Custom / configured tools for the Customer Support Crew.
"""

from crewai_tools import ScrapeWebsiteTool

# Scrapes the CrewAI docs page so the support agent can ground its
# answers in real documentation instead of hallucinating.
docs_scrape_tool = ScrapeWebsiteTool(
    website_url="https://docs.crewai.com/how-to/Creating-a-Crew-and-kick-it-off/"
)

# Add more tools here as needed, e.g.:
#
# from crewai_tools import SerperDevTool, WebsiteSearchTool
#
# search_tool = SerperDevTool()
# website_search_tool = WebsiteSearchTool()
