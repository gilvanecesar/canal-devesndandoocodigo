import csv
import requests
from bs4 import BeautifulSoup

input_csv = "videos.csv"
output_csv = "videos_enriquecidos.csv"

def get_info(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    html = requests.get(url).text

    soup = BeautifulSoup(html, "html.parser")

    # Extrair título
    title_tag = soup.find("meta", {"name": "title"})
    title = title_tag["content"] if title_tag else "(sem título)"

    # Extrair thumbnail padrão
    thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    return {
        "id": video_id,
        "url": url,
        "title": title,
        "thumbnail": thumb
    }


# Ler os IDs do CSV anterior
videos = []
with open(input_csv, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        videos.append(row["video_id"])


dados = []
print(f"Processando {len(videos)} vídeos...")

for vid in videos:
    try:
        info = get_info(vid)
        dados.append(info)
        print("OK:", vid, info["title"])
    except Exception as e:
        print("ERRO EM", vid, e)


# Salvar o CSV final
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "url", "title", "thumbnail"])
    for item in dados:
        writer.writerow([item["id"], item["url"], item["title"], item["thumbnail"]])

print("\nCSV FINAL GERADO COM SUCESSO!")
print("Arquivo:", output_csv)
