from flask import Flask
import feedparser
import requests
import json
import os
import threading
import time

app = Flask(__name__)

TOKEN = "633827893:AAFuHVeSYX6BayMSh13DJgkXpMhfv3dehoo"
CHAT_ID = "-1001057411639"
FEED_URL = "https://febnet.org.br/feed/"
ARQUIVO_ENVIADOS = "enviados.json"

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
    feed = feedparser.parse(FEED_URL)
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
        time.sleep(900)  # checa a cada 15 minutos

@app.route("/")
def home():
    return "Bot rodando!"

threading.Thread(target=loop_checagem, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
