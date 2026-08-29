from flask import Flask
import feedparser
import requests
import json
import os
import threading
import time

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
FEED_URL = os.environ.get("FEED_URL")
ARQUIVO_ENVIADOS = "enviados.json"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def carregar_enviados():
    if os.path.exists(ARQUIVO_ENVIADOS):
        with open(ARQUIVO_ENVIADOS, "r") as f:
            return json.load(f)
    return []

def salvar_enviados(lista):
    with open(ARQUIVO_ENVIADOS, "w") as f:
        json.dump(lista, f)

def enviar_mensagem(titulo, link):
    texto = f"📰 *{titulo}*\n{link}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    resposta = requests.post(url, data=payload)
    print(resposta.json())

def checar_feed():
    enviados = carregar_enviados()
    feed = feedparser.parse(FEED_URL, request_headers=HEADERS)
    novos_enviados = enviados.copy()
    for entrada in reversed(feed.entries):
        if entrada.link not in enviados:
            enviar_mensagem(entrada.title, entrada.link)
            novos_enviados.append(entrada.link)
    salvar_enviados(novos_enviados[-100:])

def loop_checagem():
    while True:
        try:
            checar_feed()
        except Exception as e:
            print("Erro:", e)
        time.sleep(900)

@app.route("/")
def home():
    return "Bot rodando!"

@app.route("/debug")
def debug():
    feed = feedparser.parse(FEED_URL, request_headers=HEADERS)
    enviados = carregar_enviados()
    return {
        "token_configurado": bool(TOKEN),
        "chat_id_configurado": bool(CHAT_ID),
        "feed_url": FEED_URL,
        "entradas_encontradas": len(feed.entries),
        "ja_enviados": len(enviados),
        "erro_feed": feed.bozo
    }

threading.Thread(target=loop_checagem, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
