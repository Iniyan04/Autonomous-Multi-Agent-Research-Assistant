# ─────────────────────────────────────────────
# workflows/crewai_workflow.py
# Agent Collaboration Workflow using CrewAI
# ─────────────────────────────────────────────

from crewai import Agent, Task, Crew, Process
from langchain.tools import tool
from textwrap import dedent

from tools.search_tool import search_web
from tools.scrape_tool import fetch_webpage_content
from llm.groq_client import get_llm

# ── 2. Define CrewAI Workflow ─────────────────
def run_crewai_pipeline(query: str) -> str:
    """
    Main entry point — runs the multi-agent collaboration pipeline via CrewAI.
    """
    print(f"\n[CrewAI] Starting autonomous collaboration for: '{query}'\n")

    # Initialize the LLM
    llm = get_llm()

    # ── Agents ──
    researcher = Agent(
        role='Senior Research Analyst',
        goal='Uncover deep insights, raw data, and factual information about the query',
        backstory=dedent("""
            You are an expert researcher. Your expertise lies in finding the most 
            accurate, up-to-date, and relevant information across the internet. 
            You leave no stone unturned and always provide sources.
        """),
        verbose=True,
        allow_delegation=False,
        tools=[search_web],
        llm=llm
    )

    fact_checker = Agent(
        role='Chief Fact-Checker',
        goal='Scrutinize research findings for accuracy and reliability',
        backstory=dedent("""
            You are a meticulous fact-checker. You review data provided by the researcher 
            and ensure that all claims are backed by solid evidence. You flag anything 
            that seems speculative, biased, or unverified. You can ask the researcher 
            to find more data if needed.
        """),
        verbose=True,
        allow_delegation=True, # Allows delegating back to researcher if needed
        tools=[fetch_webpage_content],
        llm=llm
    )

    report_writer = Agent(
        role='Senior Technical Writer',
        goal='Compile research and fact-check data into a polished, professional Markdown report',
        backstory=dedent("""
            You are a master at synthesizing complex information into clear, 
            engaging, and highly structured reports. Your formatting is impeccable.
        """),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # ── Tasks ──
    research_task = Task(
        description=dedent(f"""
            Conduct a comprehensive web search to answer the following query: "{query}"
            Gather all key facts, statistics, and context.
            You MUST compile these findings into a detailed summary. Include your source URLs.
        """),
        expected_output="A detailed summary of research findings with source URLs.",
        agent=researcher
    )

    verify_task = Task(
        description=dedent("""
            Review the research summary provided by the researcher.
            Cross-reference the claims. Provide a clear verdict on the reliability of the data.
            If information is missing, delegate to the researcher to find it.
            Produce a verified summary that includes a 'Fact-Check Verdict'.
        """),
        expected_output="A verified research summary including a specific Fact-Check Verdict and list of flagged/verified claims.",
        agent=fact_checker
    )

    report_task = Task(
        description=dedent(f"""
            Take the verified summary from the Fact-Checker and create a final, 
            professional Markdown report for the query: "{query}".
            
            The report MUST include:
            - A clear, engaging Title
            - An Executive Summary
            - Detailed Sections based on findings
            - A Fact-Check Verdict section
            - A References list
        """),
        expected_output="A fully formatted Markdown report.",
        agent=report_writer
    )

    # ── Crew Orchestration ──
    research_crew = Crew(
        agents=[researcher, fact_checker, report_writer],
        tasks=[research_task, verify_task, report_task],
        process=Process.sequential, # Tasks execute sequentially, but fact-checker can delegate to researcher
        verbose=True
    )

    # Execute the crew
    result = research_crew.kickoff()
    
    print("\n[CrewAI] Collaboration complete.\n")
    return str(result)
