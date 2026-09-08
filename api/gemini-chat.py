import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.get('/api/health')
async def health():
    return {'ok': True, 'gemini_configured': bool(os.getenv('GEMINI_API_KEY'))}

@app.post('/api/gemini')
async def gemini(req: ChatRequest):
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        raise HTTPException(503, 'Gemini API is not configured on the server.')
    contents = []
    for item in req.history[-12:]:
        role = 'model' if item.get('role') == 'assistant' else 'user'
        text = str(item.get('text', '')).strip()
        if text:
            contents.append({'role': role, 'parts': [{'text': text}]})
    contents.append({'role': 'user', 'parts': [{'text': req.message}]})
    payload = {
        'system_instruction': {'parts': [{'text': 'You are Aither Gaming AI, a helpful gaming assistant. Help with Minecraft Java and Bedrock, commands, redstone, survival, PvP, multiplayer, troubleshooting, game development, and general gaming. Be concise but useful.'}]},
        'contents': contents,
        'generationConfig': {'temperature': 0.7, 'maxOutputTokens': 1024}
    }
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, params={'key': key}, json=payload)
    if response.status_code >= 400:
        raise HTTPException(response.status_code, 'Gemini request failed.')
    data = response.json()
    try:
        text = data['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError, TypeError):
        raise HTTPException(502, 'Gemini returned an unexpected response.')
    return {'text': text}
