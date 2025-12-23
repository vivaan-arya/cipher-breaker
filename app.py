from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


from cipher_breaker import break_caesar, break_vigenere

app = FastAPI(title="Probabilistic Cipher Breaker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class CipherInput(BaseModel):
    ciphertext: str

@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html") as f:
        return f.read()

@app.post("/decrypt/caesar")
def caesar_api(data: CipherInput):
    if len(data.ciphertext) > 1000:
        raise HTTPException(400, "Ciphertext too long")
    return break_caesar(data.ciphertext)

@app.post("/decrypt/vigenere")
def vigenere_api(data: CipherInput):
    if len(data.ciphertext) > 1000:
        raise HTTPException(400, "Ciphertext too long")
    return break_vigenere(data.ciphertext)
