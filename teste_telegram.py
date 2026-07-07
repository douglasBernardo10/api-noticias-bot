import requests

TELEGRAM_BOT_TOKEN = "8861716448:AAFq7myUJaABquBzKMAe3yFurrKSTFOE4hs"
TELEGRAM_CHAT_ID = "5160797079"

mensagem = "✅ Bot funcionando! Agora posso mandar notícias no Telegram."

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

dados = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": mensagem
}

resposta = requests.post(url, data=dados)

print(resposta.text)