import discord
import feedparser
import asyncio
import os

TOKEN = os.getenv('TOKEN')

CHANNEL_ID = 1432397659385233588

OBRA_ROLE_MAP = {
    "Koko Jidai ni Gomandatta Jou sama to no Dousei Seikatsu wa Igaito Igokochi ga Warukunai": 1431237763642167326,
    "Sensei, Bokutachi wa Koroshiteimasen.": 1434347955992920204,
    "Ki ni Naru Kurumi-san!": 1431237972178636831
}

RSS_FEED_URL = "https://mdrss.tijlvdb.me/feed?q=groups:https:%2F%2Fmangadex.org%2Fgroup%2Fb3b47a9b-2f9a-4ee5-8c06-82168253f527%2Faiko-scan%3Ftab%3Dfeed"

notificados_arquivo = "notificados.txt"

def carregar_notificados():
    if not os.path.exists(notificados_arquivo):
        return set()
    with open(notificados_arquivo, "r", encoding="utf8") as f:
        return set(linha.strip() for linha in f if linha.strip())

def salvar_notificado(chapter_id):
    with open(notificados_arquivo, "a", encoding="utf8") as f:
        f.write(f"{chapter_id}\n")

posted_chapters = carregar_notificados()

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def check_feed():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("Canal não encontrado. Verifique o ID.")
        return

    while not client.is_closed():
        feed = feedparser.parse(RSS_FEED_URL)
        for entry in reversed(feed.entries):
            chapter_id = entry.id if 'id' in entry else entry.link
            if chapter_id in posted_chapters:
                continue

            title = entry.title
            role_id = None
            for obra_name in OBRA_ROLE_MAP:
                if obra_name.lower() in title.lower():
                    role_id = OBRA_ROLE_MAP[obra_name]
                    break

            if role_id:
                msg = (
                    f"<@&{role_id}> **Novo capítulo disponível!**\n"
                    f"**{title}**\n"
                    f"[Ler no MangaDex]({entry.link})"
                )
            else:
                msg = (
                    f"**Novo capítulo disponível!**\n"
                    f"**{title}**\n"
                    f"[Ler no MangaDex]({entry.link})"
                )

            try:
                await channel.send(msg)
                posted_chapters.add(chapter_id)
                salvar_notificado(chapter_id)
                print(f"Postado: {title}")
            except Exception as e:
                print(f"Erro ao postar: {e}")

        await asyncio.sleep(300)

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

async def main():
    async with client:
        client.loop.create_task(check_feed())
        await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
