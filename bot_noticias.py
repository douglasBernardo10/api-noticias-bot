import requests
import os
from datetime import datetime, timedelta, timezone

WORLD_NEWS_API_KEY = os.getenv("WORLD_NEWS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TEMA = "futebol"
ARQUIVO_ENVIADAS = "noticias_enviadas.txt"

BRASILIA = timezone(timedelta(hours=-3))


def carregar_noticias_enviadas():
    if not os.path.exists(ARQUIVO_ENVIADAS):
        return set()

    with open(ARQUIVO_ENVIADAS, "r", encoding="utf-8") as arquivo:
        return set(linha.strip() for linha in arquivo.readlines())


def salvar_noticia_enviada(noticia_id):
    with open(ARQUIVO_ENVIADAS, "a", encoding="utf-8") as arquivo:
        arquivo.write(str(noticia_id) + "\n")


def buscar_noticias():
    url = "https://api.worldnewsapi.com/search-news"

    agora = datetime.now(BRASILIA)
    inicio_do_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_do_dia = inicio_do_dia + timedelta(days=1)
    hoje = agora.strftime("%Y-%m-%d")

    params = {
        "api-key": WORLD_NEWS_API_KEY,
        "text": TEMA,
        "language": "pt",
        "number": 20,
        "sort": "publish-time",
        "sort-direction": "DESC",
        "earliest-publish-date": inicio_do_dia.strftime("%Y-%m-%d %H:%M:%S"),
        "latest-publish-date": fim_do_dia.strftime("%Y-%m-%d %H:%M:%S")
    }

    resposta = requests.get(url, params=params)

    if resposta.status_code != 200:
        print("Erro na API de notícias:")
        print(resposta.status_code)
        print(resposta.text)
        return []

    dados = resposta.json()
    todas_noticias = dados.get("news", [])

    noticias_de_hoje = []

    for noticia in todas_noticias:
        data_publicacao = noticia.get("publish_date", "")

        if data_publicacao.startswith(hoje):
            noticias_de_hoje.append(noticia)
        else:
            print("Ignorada por ser antiga:", data_publicacao)

    print("Data de hoje:", hoje)
    print("Quantidade encontrada pela API:", len(todas_noticias))
    print("Notícias realmente de hoje:", len(noticias_de_hoje))

    return noticias_de_hoje


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    dados = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "disable_web_page_preview": False
    }

    resposta = requests.post(url, data=dados)

    if resposta.status_code == 200:
        print("Notícia enviada!")
    else:
        print("Erro ao enviar para Telegram:")
        print(resposta.status_code)
        print(resposta.text)


def montar_mensagem(noticia):
    titulo = noticia.get("title", "Sem título")
    resumo = noticia.get("summary", "Sem resumo")
    link = noticia.get("url", "")
    data = noticia.get("publish_date", "")

    mensagem = f"""🚨 NOVA NOTÍCIA DE FUTEBOL

📰 {titulo}

📌 {resumo}

🕒 {data}

🔗 {link}
"""
    return mensagem


def iniciar_bot():
    if not WORLD_NEWS_API_KEY or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: alguma chave não foi configurada nos Secrets do GitHub.")
        return

    print("Bot de notícias iniciado...")

    enviadas = carregar_noticias_enviadas()
    noticias = buscar_noticias()

    novas = 0
    repetidas = 0

    for noticia in noticias:
        noticia_id = noticia.get("url") or noticia.get("title")

        if noticia_id in enviadas:
            repetidas += 1
            continue

        mensagem = montar_mensagem(noticia)
        enviar_telegram(mensagem)

        salvar_noticia_enviada(noticia_id)
        enviadas.add(noticia_id)

        novas += 1

    print(f"Novas enviadas: {novas}")
    print(f"Repetidas ignoradas: {repetidas}")
    print("Execução finalizada.")


iniciar_bot()