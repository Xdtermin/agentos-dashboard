#!/usr/bin/env python3
"""
AgentOS Dashboard Server
Serves static files and provides SSE endpoint for live data
"""

import json
import time
import asyncio
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import random
import uvicorn

app = FastAPI()

# Mount static files
app.mount("/", StaticFiles(directory=".", html=True), name="static")


@dataclass
class Agent:
    id: str
    name: str
    accent: str
    active: bool
    responses: int
    status: str
    context_fill: float


@dataclass
class VPSHealth:
    cpu: float
    memory: float
    disk: float
    db_size: str


@dataclass
class Stats:
    integrity: float
    agent_calls: int
    messages: int
    tokens_in: int
    cache_hits: int
    queue: int
    sessions: int
    errors: int
    today: int
    uptime: str


@dataclass
class LogEntry:
    id: str
    agent: str
    task: str
    status: str
    timestamp: str


# Mock data - will be replaced with real AgentOS backend calls
AGENTS = [
    Agent("orchestrator", "ORCHESTRATOR", "var(--agent-orchestrator)", True, 1247, "active", 0.72),
    Agent("analyst", "ANALYST", "var(--agent-analyst)", True, 856, "active", 0.45),
    Agent("writer", "WRITER", "var(--agent-writer)", True, 642, "idle", 0.38),
    Agent("marketer", "MARKETER", "var(--agent-marketer)", True, 534, "active", 0.62),
    Agent("coder", "CODER", "var(--agent-coder)", True, 723, "active", 0.55),
]

LOG_ENTRIES = [
    {"id": "1", "agent": "ORCHESTRATOR", "task": "Pipeline execution started", "status": "active", "timestamp": "04:55:12"},
    {"id": "2", "agent": "ANALYST", "task": "Market research for SaaS pricing", "status": "active", "timestamp": "04:54:48"},
    {"id": "3", "agent": "CODER", "task": "Fixed auth token refresh bug", "status": "completed", "timestamp": "04:53:22"},
    {"id": "4", "agent": "WRITER", "task": "Drafted blog post outline", "status": "completed", "timestamp": "04:52:15"},
    {"id": "5", "agent": "MARKETER", "task": "Social media scheduling", "status": "active", "timestamp": "04:51:33"},
]


def generate_vps_health() -> VPSHealth:
    """Generate realistic VPS health metrics"""
    return VPSHealth(
        cpu=random.uniform(35, 65),
        memory=random.uniform(45, 75),
        disk=random.uniform(60, 85),
        db_size=f"{random.uniform(2.1, 3.4):.1f} GB"
    )


def generate_stats() -> Stats:
    """Generate realistic stats"""
    return Stats(
        integrity=random.uniform(98.5, 99.9),
        agent_calls=random.randint(4200, 4600),
        messages=random.randint(18500, 19200),
        tokens_in=random.randint(1240000, 1280000),
        cache_hits=random.randint(85000, 92000),
        queue=random.randint(5, 18),
        sessions=random.randint(42, 58),
        errors=0 if random.random() > 0.1 else random.randint(1, 3),
        today=random.randint(287, 324),
        uptime=f"{random.randint(14, 23)}d {random.randint(2, 8)}h {random.randint(15, 59)}m"
    )


def add_log_entry():
    """Add a new log entry"""
    global LOG_ENTRIES
    tasks = [
        "Processing user request",
        "Fetching data from API",
        "Generating content",
        "Executing pipeline step",
        "Analyzing results",
        "Sending notification",
        "Checking system health",
        "Updating cache"
    ]
    agents = ["ORCHESTRATOR", "ANALYST", "WRITER", "MARKETER", "CODER"]
    statuses = ["active", "completed", "idle", "error"]

    new_entry = {
        "id": str(len(LOG_ENTRIES) + 1),
        "agent": random.choice(agents),
        "task": random.choice(tasks),
        "status": random.choice(statuses),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    LOG_ENTRIES.insert(0, new_entry)
    if len(LOG_ENTRIES) > 20:
        LOG_ENTRIES.pop()


def event_stream():
    """SSE stream for live data"""
    while True:
        data = {
            "type": "update",
            "agents": [asdict(a) for a in AGENTS],
            "vps": asdict(generate_vps_health()),
            "stats": asdict(generate_stats()),
            "logs": LOG_ENTRIES[:8],
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(0.8)


@app.get("/api/stats")
async def get_stats():
    """Fallback polling endpoint for stats"""
    return {
        "agents": [asdict(a) for a in AGENTS],
        "vps": asdict(generate_vps_health()),
        "stats": asdict(generate_stats()),
        "logs": LOG_ENTRIES[:8],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/events")
async def sse_events():
    """SSE endpoint for live data"""
    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    print("AgentOS Dashboard Server running on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)