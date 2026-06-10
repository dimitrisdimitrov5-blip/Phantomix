from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent
from browser import BrowserController
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Phantomix API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

browser = BrowserController()
conversation_history = []

class TaskRequest(BaseModel):
    task: str

class BrowseRequest(BaseModel):
    url: str

class SearchRequest(BaseModel):
    query: str

class FillRequest(BaseModel):
    selector: str
    value: str

@app.on_event("startup")
async def startup():
    await browser.start()

@app.on_event("shutdown")
async def shutdown():
    await browser.stop()

@app.get("/")
async def root():
    return {"status": "Phantomix is running 🚀", "version": "1.0.0"}

@app.post("/task")
async def run_task(request: TaskRequest):
    global conversation_history
    try:
        reply, conversation_history = await run_agent(
            request.task, 
            conversation_history
        )
        return {"status": "success", "result": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browse")
async def browse(request: BrowseRequest):
    try:
        result = await browser.go_to(request.url)
        text = await browser.get_text()
        return {"status": "success", "result": result, "content": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(request: SearchRequest):
    try:
        results = await browser.search_google(request.query)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fill")
async def fill(request: FillRequest):
    try:
        result = await browser.fill_input(request.selector, request.value)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/screenshot")
async def screenshot():
    try:
        result = await browser.screenshot()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/memory")
async def clear_memory():
    global conversation_history
    conversation_history = []
    return {"status": "success", "message": "Memory cleared"}

@app.get("/health")
async def health():
    return {"status": "healthy", "browser": "running"}
