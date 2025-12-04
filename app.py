from flask import Flask, jsonify
import subprocess
import json
import traceback

app = Flask(__name__)

CHANNEL_URL = "https://www.youtube.com/@descomplicandoocodigo"


@app.route("/videos")
def get_videos():
    try:
        cmd = [
            "yt-dlp",
            "-J",
            "--extractor-args",
            "youtube:player_client=android",
            CHANNEL_URL,
        ]

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90
        )

        raw = result.stdout.strip()
        if not raw:
            raise Exception("yt-dlp retornou vazio")

        data = json.loads(raw)

        entries = data.get("entries", [])

        final = []

        for item in entries:
            # IGNORA QUALQUER COISA QUE NÃO SEJA DICIONÁRIO
            if not isinstance(item, dict):
                continue

            title = item.get("title")
            vid = item.get("id")

            # Só aceita vídeo válido
            if not title or not vid:
                continue

            thumb = item.get("thumbnail") or ""

            final.append(
                {
                    "title": str(title),
                    "id": str(vid),
                    "url": f"https://youtube.com/watch?v={vid}",
                    "thumbnail": str(thumb),
                }
            )

        return jsonify(final)

    except Exception as e:
        print("\n=== ERRO NO BACKEND ===")
        print(traceback.format_exc())
        print("========================\n")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001, debug=True)
