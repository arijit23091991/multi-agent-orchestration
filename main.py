from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from pipeline import run_research_pipeline


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="AI-powered research using search, reader, writer, and critic agents.",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class ResearchRequest(BaseModel):
    topic: str = Field(
        min_length=3,
        max_length=500,
        description="Topic to research",
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/research")
def research(request: ResearchRequest):
    topic = request.topic.strip()

    if len(topic) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please enter a topic with at least 3 characters.",
        )

    try:
        result = run_research_pipeline(topic, verbose=False)

        return {
            "topic": topic,
            "search_results": result.get("search_results", ""),
            "scraped_content": result.get("scrapped_content", ""),
            "report": result.get("report", ""),
            "feedback": result.get("feedback", ""),
        }

    except Exception as exc:
        # Log the full error on the server, not in the API response.
        import logging
        logging.exception("Research pipeline failed")

        raise HTTPException(
            status_code=500,
            detail="Research failed. Check the server logs and API configuration.",
        ) from exc