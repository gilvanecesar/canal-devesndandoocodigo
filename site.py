# site.py
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
    page_title="Trilha de Estudos – Desvendando o Código - Prof. Marcos",
    page_icon="🎬",
    layout="wide"
)

CSV_FILE = "videos_enriquecidos.csv"
PROGRESS_FILE = "progresso.json"

# -------------------------
# UTIL: progresso (json)
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

# -------------------------
# UTIL: detectar módulo simples
# -------------------------
def detect_module(title: str):
    # Lista de palavras-chave comuns que identificam módulos
    keywords = ["Reduce", "Filter", "React", "TypeScript", "Type Script", "JavaScript", "Regex", "Array", "Node", "Map", "ForEach"]
    for k in keywords:
        if k.lower() in title.lower():
            return k.capitalize() if k.lower() != "type script" else "TypeScript"
    # Buscar padrões tipo "#01", "Modulo", "MÓDULO"
    m = re.search(r"\b(Reduce|Filter|React|TypeScript|JavaScript|Regex|Node)\b", title, re.I)
    if m:
        return m.group(1).capitalize()
    # fallback
    return "Outros"

# -------------------------
# CARREGAR DADOS
# -------------------------
if not os.path.exists(CSV_FILE):
    st.error(f"Arquivo {CSV_FILE} não encontrado. Rode os scripts de raspagem/enriquecimento primeiro.")
    st.stop()

df = pd.read_csv(CSV_FILE)
# garante colunas como strings
df["title"] = df["title"].astype(str)
df["id"] = df["id"].astype(str)
df["url"] = df["url"].astype(str)
df["thumbnail"] = df["thumbnail"].astype(str)

# detecta módulo para cada vídeo e adiciona coluna
df["module"] = df["title"].apply(detect_module)

# ordem natural do CSV preservada
video_ids = df["id"].tolist()
id_to_idx = {vid: i for i, vid in enumerate(video_ids)}

# -------------------------
# STATE: player e progresso
# -------------------------
if "current_video" not in st.session_state:
    st.session_state.current_video = None
if "player_visible" not in st.session_state:
    st.session_state.player_visible = False

progress = load_progress()

def abrir_player(vid_id, autoplay=False):
    st.session_state.current_video = vid_id
    st.session_state.player_visible = True
    # armazenar autoplay temporário
    st.session_state._autoplay = autoplay

def fechar_player():
    st.session_state.player_visible = False
    st.session_state.current_video = None
    st.session_state._autoplay = False

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
    # encontra primeiro vídeo NÃO marcado como assistido
    for vid in video_ids:
        if not progress.get(vid, False):
            abrir_player(vid, autoplay=True)
            return
    # se todos assistidos, abrir o primeiro
    if video_ids:
        abrir_player(video_ids[0], autoplay=True)

# -------------------------
# SIDEBAR (menu lateral)
# -------------------------
with st.sidebar:
    st.header("📚 Seu Progresso")
    total = len(video_ids)
    assistidos = sum(1 for v in video_ids if progress.get(v, False))
    perc = int((assistidos / total) * 100) if total > 0 else 0
    st.metric("Assistidos", f"{assistidos} / {total}", delta=f"{perc}%")
    st.progress(perc)

    st.write("---")
    if st.button("▶ Continuar de onde parei"):
        continuar_de_onde_parou()

    st.write("---")
    st.write("🔎 Filtros")
    modules = ["Todos"] + sorted(df["module"].unique().tolist())
    selected_module = st.selectbox("Filtrar por módulo", modules, index=0)

    st.write("---")
    # tema (aplicamos CSS alternativo)
    theme_choice = st.selectbox("Tema", ["Escuro", "Claro"])
    st.write("---")
    st.write("⚙️ Estatísticas rápidas")
    st.write(f"- Total de vídeos: **{total}**")
    st.write(f"- Assistidos: **{assistidos}**")
    st.write(f"- Restantes: **{total - assistidos}**")

# aplique CSS simples para tema claro/escuro
if theme_choice == "Claro":
    st.markdown("""
    <style>
    body { background-color: #f7f7f8; color: #111; }
    .video-card { background-color: #ffffff; color: #111; border:1px solid #ddd; }
    .player-area { background: #ffffff; color: #000; border:1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    body { background-color: #0e0f10; color: #fff; }
    .video-card { background-color: #1b1c1f; color: #fff; border:1px solid #2a2b2d; }
    .player-area { background: #0f1112; color:#fff; border:1px solid #232426; }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# CABEÇALHO E BUSCA
# -------------------------
st.title("🎬 Trilha de Estudos – Desvendando o Código")
st.write("Organize seus estudos marcando os vídeos já assistidos. Use o menu lateral para controlar sua jornada.")

query = st.text_input("🔎 Buscar vídeo", key="global_search")

# filtro por busca e módulo
df_filtrado = df.copy()
if query:
    df_filtrado = df_filtrado[df_filtrado["title"].str.contains(query, case=False, na=False)]
if selected_module and selected_module != "Todos":
    df_filtrado = df_filtrado[df_filtrado["module"] == selected_module]

# -------------------------
# PLAYER (se visível)
# -------------------------
if st.session_state.player_visible and st.session_state.current_video:
    vid = st.session_state.current_video
    st.markdown('<div class="player-area">', unsafe_allow_html=True)
    st.write("### ▶️ Player embutido")
    title = df.loc[df["id"] == vid, "title"].values[0] if not df.loc[df["id"] == vid, "title"].empty else vid
    st.markdown(f"**{title}**")
    autoplay_flag = getattr(st.session_state, "_autoplay", False)
    autoplay_qs = "1" if autoplay_flag else "0"
    embed_url = f"https://www.youtube.com/embed/{vid}?rel=0&autoplay={autoplay_qs}"
    components.html(f"""
        <iframe width="100%" height="480" src="{embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    """, height=520)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("◀ Anterior"):
            anterior()
    with col2:
        if st.button("Fechar player"):
            fechar_player()
    with col3:
        if st.button("Próximo ▶"):
            proximo()
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# GRID DE VÍDEOS
# -------------------------
cols = st.columns(3)
for i, row in df_filtrado.iterrows():
    with cols[i % 3]:
        st.markdown('<div class="video-card">', unsafe_allow_html=True)
        st.image(row["thumbnail"], use_container_width=True)
        st.markdown(f'<p style="font-size:16px;font-weight:600;color:inherit;margin:8px 0;">{row["title"]}</p>', unsafe_allow_html=True)

        # botões: abrir player embutido (autoplay=false) ou abrir no YouTube (nova aba)
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("▶️ Assistir aqui", key=f"play_{row['id']}"):
                abrir_player(row["id"], autoplay=False)
        with c2:
            st.markdown(f"[🔗 Abrir no YouTube]({row['url']})", unsafe_allow_html=True)

        # checkbox de progresso
        vid = row["id"]
        checked = progress.get(vid, False)
        novo_estado = st.checkbox("Já assisti", value=checked, key=f"chk_{vid}")
        if novo_estado != checked:
            progress[vid] = novo_estado
            save_progress(progress)

        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# RODAPÉ: resumo rápido
# -------------------------
st.write("---")
st.caption(f"Progresso: {assistidos} de {total} vídeos assistidos — filtro: {selected_module} — resultados mostrados: {len(df_filtrado)}")
