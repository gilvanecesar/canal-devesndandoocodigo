import requests
import re
import csv

CHANNEL_URL = "https://www.youtube.com/@DesvendandooCodigo/videos"

print("Baixando HTML do canal...")
html = requests.get(CHANNEL_URL).text

print("Extraindo IDs de vídeo...")
ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)

# Remover duplicados
ids_unicos = list(dict.fromkeys(ids))

print(f"Total encontrado: {len(ids_unicos)} IDs")

print("Salvando no CSV...")
with open("videos.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["video_id", "youtube_url"])
    for vid in ids_unicos:
        writer.writerow([vid, f"https://www.youtube.com/watch?v={vid}"])

print("CSV gerado com sucesso: videos.csv")
