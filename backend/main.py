"""FastAPI application entry point."""
from fastapi import FastAPI

app = FastAPI(
    title="Carbon- and Latency-Aware Agent Workflow Scheduler",
    description="Backend API for scheduling AI agent workflows based on carbon intensity and latency constraints.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Carbon- and Latency-Aware Agent Workflow Scheduler API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
