import requests
import json
import csv
import re

# -----------------------------
# CONFIGURAÇÃO
# -----------------------------
CHANNEL_HANDLE = "@DesvendandooCodigo"  # você pode mudar depois
BASE_URL = f"https://www.youtube.com/{CHANNEL_HANDLE}/videos"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

# -----------------------------
# 1. Pegar HTML inicial
# -----------------------------
print("📥 Baixando HTML inicial do canal...")

html = requests.get(BASE_URL, headers=HEADERS).text

# Extrair o JSON embedado no HTML
match = re.search(r"var ytInitialData = ({.*?});</script>", html)
if not match:
    print("Erro: não encontrei ytInitialData.")
    exit()

yt_initial_data = json.loads(match.group(1))

# -----------------------------
# Função para extrair vídeos de um bloco
# -----------------------------
def extract_videos(data):
    videos = []
    try:
        # caminho onde ficam os vídeos na página inicial
        tabs = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        for tab in tabs:
            if "tabRenderer" in tab and tab["tabRenderer"]["title"] == "Videos":
                section = tab["tabRenderer"]["content"]["richGridRenderer"]["contents"]
                for item in section:
                    if "richItemRenderer" in item:
                        video = item["richItemRenderer"]["content"]["videoRenderer"]
                        videos.append({
                            "id": video["videoId"],
                            "title": video.get("title", {}).get("runs", [{}])[0].get("text", ""),
                            "thumbnail": video.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url", ""),
                        })
    except:
        pass
    return videos

# -----------------------------
# Pegar continuation token inicial
# -----------------------------
def get_continuation(data):
    try:
        continuation = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][1] \
            ["tabRenderer"]["content"]["richGridRenderer"]["contents"][-1] \
            ["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
        return continuation
    except:
        return None


# -----------------------------
# Extração inicial
# -----------------------------
print("📦 Extraindo primeiros vídeos...")

videos_final = []
videos_final.extend(extract_videos(yt_initial_data))

continuation = get_continuation(yt_initial_data)

# -----------------------------
# 2. Loop usando continuationToken
# -----------------------------
API_URL = "https://www.youtube.com/youtubei/v1/browse?key=AIzaSyA-1V5W4n_tYb9t7ZHFhpQyZ8ZRvJ2VFrA"

YOUTUBE_CLIENT = {
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20240202.01.00"
        }
    }
}

print("🔄 Buscando páginas adicionais...")

while continuation:
    print(f"➡ Continuation: {continuation[:12]}...")

    YOUTUBE_CLIENT["continuation"] = continuation

    r = requests.post(API_URL, json=YOUTUBE_CLIENT, headers=HEADERS)
    data = r.json()

    # Extrair vídeos adicionais
    try:
        items = data["onResponseReceivedActions"][0]["appendContinuationItemsAction"]["continuationItems"]
        for item in items:
            if "richItemRenderer" in item:
                video = item["richItemRenderer"]["content"]["videoRenderer"]
                videos_final.append({
                    "id": video["videoId"],
                    "title": video.get("title", {}).get("runs", [{}])[0].get("text", ""),
                    "thumbnail": video.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url", ""),
                })
    except:
        pass

    # Pegar novo continuation
    continuation = None
    try:
        continuation = data["onResponseReceivedActions"][0]["appendContinuationItemsAction"] \
            ["continuationItems"][-1] \
            ["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
    except:
        continuation = None


# -----------------------------
# 3. Salvar em CSV
# -----------------------------
print(f"\n📊 Total de vídeos encontrados: {len(videos_final)}")

with open("todos_videos.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "title", "thumbnail", "url"])
    for v in videos_final:
        writer.writerow([
            v["id"],
            v["title"],
            v["thumbnail"],
            f"https://www.youtube.com/watch?v={v['id']}"
        ])

print("💾 Arquivo salvo: todos_videos.csv")
print("✔ Raspar canal completo finalizado!")
