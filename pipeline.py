from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain,
)
from langchain_core.messages import HumanMessage


def run_research_pipeline(topic: str, verbose: bool = True) -> dict:
    state = {}

    def log(*args):
        if verbose:
            print(*args)

    log("\n" + "=" * 50)
    log("STEP 1 - SEARCH AGENT")
    log("=" * 50)

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [
            HumanMessage(
                content=(
                    f"Find recent, reliable, detailed information about {topic}. "
                    "Return relevant titles, URLs, and evidence."
                )
            )
        ]
    })

    state["search_results"] = search_result["messages"][-1].content

    log("\nSTEP 2 - READER AGENT")

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            HumanMessage(
                content=(
                    f"Research the topic: {topic}\n\n"
                    "Select the most relevant URL from these results. "
                    "Use the scrape_url tool to retrieve its content. "
                    "Return the source URL and extracted content.\n\n"
                    f"Search Results:\n{state['search_results'][:4000]}"
                )
            )
        ]
    })

    state["scrapped_content"] = reader_result["messages"][-1].content

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"SCRAPED CONTENT:\n{state['scrapped_content']}"
    )

    log("STEP 3 - WRITER AGENT")

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    })

    log("STEP 4 - CRITIC AGENT")

    state["feedback"] = critic_chain.invoke({
        "report": state["report"],
    })

    return state