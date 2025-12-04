import streamlit as st
import pandas as pd
import json
import os
import streamlit.components.v1 as components
import re

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Trilha de Estudos – Desvendando o Código",
    page_icon="🎬",
    layout="wide"
)

CSV_FILE = "todos_videos.csv"  # AGORA USANDO O CSV NOVO
PROGRESS_FILE = "progresso.json"

# -------------------------
# PROGRESSO (JSON)
# -------------------------
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=4)

progress = load_progress()

# -------------------------
# DETECTAR MÓDULO POR TÍTULO
# (para sidebar e filtros)
# -------------------------
def detect_module(title: str):
    keywords = ["Reduce", "Filter", "React", "TypeScript", "JavaScript", "Regex", "Node", "Array", "Map", "ForEach"]
    for k in keywords:
        if k.lower() in title.lower():
            return k.capitalize()
    return "Outros"

# -------------------------
# CARREGAR DADOS DO CSV NOVO
# -------------------------
if not os.path.exists(CSV_FILE):
    st.error(f"Arquivo {CSV_FILE} não encontrado.")
    st.stop()

df = pd.read_csv(CSV_FILE)

df["title"] = df["title"].astype(str)
df["id"] = df["id"].astype(str)
df["url"] = df["url"].astype(str)
df["thumbnail"] = df["thumbnail"].astype(str)

df["module"] = df["title"].apply(detect_module)

video_ids = df["id"].tolist()
id_to_idx = {vid: i for i, vid in enumerate(video_ids)}

# -------------------------
# SESSION STATE
# -------------------------
if "current_video" not in st.session_state:
    st.session_state.current_video = None
if "player_visible" not in st.session_state:
    st.session_state.player_visible = False

def abrir_player(vid, autoplay=False):
    st.session_state.current_video = vid
    st.session_state.player_visible = True
    st.session_state._autoplay = autoplay

def fechar_player():
    st.session_state.player_visible = False
    st.session_state.current_video = None

def proximo():
    cur = st.session_state.current_video
    if cur and cur in id_to_idx:
        idx = id_to_idx[cur]
        if idx + 1 < len(video_ids):
            st.session_state.current_video = video_ids[idx + 1]

def anterior():
    cur = st.session_state.current_video
    if cur and cur in id_to_idx:
        idx = id_to_idx[cur]
        if idx - 1 >= 0:
            st.session_state.current_video = video_ids[idx - 1]

def continuar_de_onde_parou():
    for vid in video_ids:
        if not progress.get(vid, False):
            abrir_player(vid, autoplay=True)
            return
    abrir_player(video_ids[0], autoplay=True)

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.header("📚 Seu Progresso")

    total = len(video_ids)
    assistidos = sum(1 for v in video_ids if progress.get(v, False))
    perc = int((assistidos / total) * 100) if total > 0 else 0

    st.metric("Assistidos", f"{assistidos}/{total}", delta=f"{perc}%")
    st.progress(perc)

    if st.button("▶ Continuar de onde parei"):
        continuar_de_onde_parou()

    st.write("---")

    modules = ["Todos"] + sorted(df["module"].unique().tolist())
    selected_module = st.selectbox("Filtrar por módulo", modules)

# -------------------------
# HEADER E BUSCA
# -------------------------
st.title("🎬 Trilha completa do canal – Desvendando o Código")
query = st.text_input("🔎 Buscar vídeo")

df_filtrado = df.copy()

if query:
    df_filtrado = df_filtrado[df_filtrado["title"].str.contains(query, case=False)]

if selected_module != "Todos":
    df_filtrado = df_filtrado[df_filtrado["module"] == selected_module]

# -------------------------
# PLAYER EMBUTIDO
# -------------------------
if st.session_state.player_visible and st.session_state.current_video:
    vid = st.session_state.current_video
    title = df[df["id"] == vid]["title"].values[0]

    st.subheader(f"▶️ {title}")

    autoplay_flag = "1" if st.session_state.get("_autoplay", False) else "0"
    embed_url = f"https://www.youtube.com/embed/{vid}?autoplay={autoplay_flag}"

    components.html(
        f"""
        <iframe width="100%" height="480" src="{embed_url}" frameborder="0" allowfullscreen></iframe>
        """,
        height=500
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    if c1.button("◀ Anterior"):
        anterior()
    if c2.button("Fechar player"):
        fechar_player()
    if c3.button("Próximo ▶"):
        proximo()

# -------------------------
# GRID
# -------------------------
cols = st.columns(3)

for i, row in df_filtrado.iterrows():
    with cols[i % 3]:
        st.image(row["thumbnail"], use_container_width=True)
        st.write(f"**{row['title']}**")

        c1, c2 = st.columns([1,1])
        if c1.button("▶️ Aqui", key=f"play_{row['id']}"):
            abrir_player(row["id"])
        c2.markdown(f"[🔗 YouTube]({row['url']})")

        vid = row["id"]
        checked = progress.get(vid, False)
        novo_estado = st.checkbox("Já assisti", value=checked, key=f"chk_{vid}")
        if novo_estado != checked:
            progress[vid] = novo_estado
            save_progress(progress)
