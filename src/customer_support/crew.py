import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, task, crew
from customer_support.tools.custom_tools import docs_scrape_tool

@CrewBase
class CustomerSupportCrew:
    """Customer Support Crew — resolves a customer inquiry, then a QA
    agent reviews the draft before it's considered final."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        # Gemini LLM (via LiteLLM). Requires GEMINI_API_KEY in the env.
        self.llm = LLM(
            model=os.getenv("MODEL", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.5,
        )

    @agent
    def customer_support_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["customer_support_agent"],
            llm=self.llm,
            tools=[docs_scrape_tool],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def quality_assurance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["quality_assurance_agent"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def inquiry_resolution(self) -> Task:
        return Task(
            config=self.tasks_config["inquiry_resolution"],
            agent=self.customer_support_agent(),
        )

    @task
    def quality_assurance_review(self) -> Task:
        return Task(
            config=self.tasks_config["quality_assurance_review"],
            agent=self.quality_assurance_agent(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=False,
            verbose=os.getenv("CREW_VERBOSE", "true").lower() == "true",
        )