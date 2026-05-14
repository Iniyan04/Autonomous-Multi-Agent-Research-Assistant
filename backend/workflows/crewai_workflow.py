from textwrap import dedent

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool

from config.settings import (
    CREWAI_VERBOSE,
    GROQ_API_KEY,
    GROQ_MODEL,
    MAX_CONTEXT_CHARS,
    MAX_TOKENS,
)
from tools.scrape_tool import fetch_webpage_content
from tools.search_tool import search_web


MAX_CREWAI_SEARCH_RESULTS = 5
MAX_SEARCH_RESULT_WORDS = 120
MAX_FETCHED_PAGE_WORDS = 450


def _normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def _trim_words(text: str, max_words: int) -> str:
    """
    Keep snippets readable and compact before CrewAI stores them in context.
    """
    words = _normalize_text(text).split()
    if len(words) <= max_words:
        return " ".join(words)
    return f"{' '.join(words[:max_words])}..."


def _cap_context(text: str) -> str:
    """
    Final safety cap for data passed between CrewAI stages.
    """
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(normalized) <= MAX_CONTEXT_CHARS:
        return normalized
    return f"{normalized[:MAX_CONTEXT_CHARS].rstrip()}..."


def _run_single_task(agent: Agent, task: Task) -> str:
    """
    Run one agent step and cap its output before it feeds the next stage.
    """
    task.description = _cap_context(task.description)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=CREWAI_VERBOSE,
    )
    return _cap_context(str(crew.kickoff()))


@tool("search_web")
def crewai_search_web(query: str) -> str:
    """
    Search the web for relevant research sources.
    """
    results = search_web.invoke({"query": query})
    if not results:
        return "No search results found."

    trimmed_results = results[:MAX_CREWAI_SEARCH_RESULTS]

    return "\n\n".join(
        f"Title: {result.get('title', 'Untitled')}\n"
        f"URL: {result.get('url', '')}\n"
        f"Summary: {_trim_words(result.get('content', ''), MAX_SEARCH_RESULT_WORDS)}"
        for result in trimmed_results
    )


@tool("fetch_webpage_content")
def crewai_fetch_webpage_content(url: str) -> str:
    """
    Fetch readable text content from a webpage URL.
    """
    content = fetch_webpage_content.invoke({"url": url})
    return _trim_words(content, MAX_FETCHED_PAGE_WORDS)


def run_crewai_pipeline(query: str) -> str:
    """
    Runs the multi-agent collaboration pipeline via CrewAI.
    """
    print(f"\n[CrewAI] Starting autonomous collaboration for: '{query}'\n")

    llm = LLM(
        model=GROQ_MODEL,
        provider="openai",
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        temperature=0.3,
        max_tokens=MAX_TOKENS,
    )

    researcher = Agent(
        role="Senior Research Analyst",
        goal="Find concise, reliable evidence from at most 5 sources for the query",
        backstory=dedent(
            """
            You are an expert researcher who extracts only the most relevant
            findings and source URLs. Keep notes compact and avoid copying long
            passages from webpages.
            """
        ),
        verbose=CREWAI_VERBOSE,
        allow_delegation=False,
        tools=[crewai_search_web],
        llm=llm,
    )

    fact_checker = Agent(
        role="Chief Fact-Checker",
        goal="Verify key claims using concise evidence from the provided sources",
        backstory=dedent(
            """
            You are a meticulous fact-checker. Review only the most important
            claims, use short excerpts or summaries, and flag anything speculative,
            biased, or unverified.
            """
        ),
        verbose=CREWAI_VERBOSE,
        allow_delegation=False,
        tools=[crewai_fetch_webpage_content],
        llm=llm,
    )

    report_writer = Agent(
        role="Senior Technical Writer",
        goal="Create a concise Markdown report from verified findings",
        backstory=dedent(
            """
            You synthesize research into clear, structured reports with concise
            sections and source links.
            """
        ),
        verbose=CREWAI_VERBOSE,
        allow_delegation=False,
        llm=llm,
    )

    research_task = Task(
        description=dedent(
            f"""
            Conduct a comprehensive web search to answer this query: "{query}".
            Use at most 5 sources. Extract concise key findings, relevant facts,
            and source URLs only. Do not copy full webpage content.
            """
        ),
        expected_output="A concise research summary with no more than 5 source URLs.",
        agent=researcher,
    )

    research_summary = _run_single_task(researcher, research_task)

    verify_task = Task(
        description=dedent(
            f"""
            Review this capped research summary:
            {research_summary}

            Cross-reference only the most important claims and provide a clear
            reliability verdict. Avoid fetching or copying full webpage content.
            Include verified claims, flagged claims, and any corrections.
            """
        ),
        expected_output="A concise verified summary with a fact-check verdict.",
        agent=fact_checker,
    )
    fact_check_summary = _run_single_task(fact_checker, verify_task)

    report_task = Task(
        description=dedent(
            f"""
            Create a final professional Markdown report for this query: "{query}".

            Capped research summary:
            {research_summary}

            Capped fact-check summary:
            {fact_check_summary}

            Include:
            # Report Title

            ## Executive Summary
            Write 2-3 concise sentences.

            ## Key Findings
            Use 4-6 bullet points. Start each bullet on its own line.

            ## Timeline / Background
            Use short paragraphs or bullets when useful.

            ## Fact-Check Verdict
            Explain what is verified, uncertain, or disputed.

            ## References
            List source titles and URLs as bullets.

            Keep the report focused. Use only the sources provided by the
            researcher and fact-checker. Return valid Markdown with blank lines
            between every heading, paragraph, and list. Do not put multiple
            headings or bullets on the same line.
            """
        ),
        expected_output="A fully formatted Markdown report.",
        agent=report_writer,
    )
    result = _run_single_task(report_writer, report_task)

    print("\n[CrewAI] Collaboration complete.\n")
    return _cap_context(result)
