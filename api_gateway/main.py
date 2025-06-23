from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI()


@app.get("/")
async def msg():
    html_content = '<a href="/docs"> go to docs </a>'
    return HTMLResponse(html_content)
