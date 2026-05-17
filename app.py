import streamlit as st
import random

st.set_page_config(
    page_title="Pickleball Randomizer",
    page_icon="🥒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit branding
st.markdown("""
    <style>
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🥒 Pickleball Randomizer")
st.markdown("**Brought to you by [Ecoglitter.com](https://ecoglitter.com)**")

# ---------- Session state init ----------
if "roster_history" not in st.session_state:
    st.session_state.roster_history = []
if "player_names" not in st.session_state:
    st.session_state.player_names = []
if "num_rounds" not in st.session_state:
    st.session_state.num_rounds = 0
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 0
if "num_players_original" not in st.session_state:
    st.session_state.num_players_original = 0

# ---------- Inputs ----------
col1, col2, col3 = st.columns(3)
with col1:
    num_players_input = st.number_input("Number of Players", min_value=4, value=12, step=1)
with col2:
    num_courts_input = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    num_rounds_input = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)",
    height=140,
    placeholder="Enter one name per line\nOr leave blank for P1, P2, etc."
)

# ---------- Helper: generate rounds ----------
def generate_rounds(start_round, end_round, player_names, used_pairs, bye_count, num_courts):
    rounds = []
    num_players = len(player_names)

    for round_num in range(start_round, end_round + 1):
        actual_courts = min(num_courts, num_players // 4)
        byes_per_round = num_players - (actual_courts * 4)

        if byes_per_round > 0:
            indices = list(range(num_players))
            indices_sorted = sorted(
                indices,
                key=lambda i: (bye_count[player_names[i]], random.random())
            )
            bye_indices = indices_sorted[:byes_per_round]
            for i in bye_indices:
                bye_count[player_names[i]] += 1
        else:
            bye_indices = []

        playing_indices = [i for i in range(num_players) if i not in bye_indices]
        random.shuffle(playing_indices)

        courts = []
        for c in range(actual_courts):
            if len(playing_indices) < 4:
                break
            a_idx, b_idx, c_idx, d_idx = playing_indices[:4]
            playing_indices = playing_indices[4:]

            a = player_names[a_idx]
            b = player_names[b_idx]
            c_name = player_names[c_idx]
            d = player_names[d_idx]

            team1 = sorted([a, b])
