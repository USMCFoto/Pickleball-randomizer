import streamlit as st
import random

st.set_page_config(page_title="Pickleball Randomizer", page_icon="🥒", layout="centered")

st.markdown("""
    <style>
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🥒 Pickleball Randomizer")
st.markdown("**Brought to you by [Ecoglitter.com](https://ecoglitter.com)**")

# Simple session state
if 'roster' not in st.session_state:
    st.session_state.roster = []

# ====================== INPUTS ======================
st.subheader("Create Roster")

col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=15, step=1)
with col2:
    num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)", 
    height=180,
    placeholder="Leave blank to use P1, P2, etc."
)

if st.button("Generate Roster", type="primary", use_container_width=True):
    # Get player names
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
    else:
        player_names = [f"P{i+1}" for i in range(num_players)]

    actual_courts = min(num_courts, len(player_names) // 4)
    byes_per_round = len(player_names) - (actual_courts * 4)

    roster = []
    used_pairs = set()

    for round_num in range(1, num_rounds + 1):
        # Byes
        if byes_per_round > 0:
            candidates = sorted(range(len(player_names)), key=lambda i: (0, random.random()))  # Simplified for now
            bye_indices = candidates[:byes_per_round]
        else:
            bye_indices = []

        playing = [i for i in range(len(player_names)) if i not in bye_indices]
        random.shuffle(playing)

        courts = []
        for c in range(actual_courts):
            if len(playing) < 4:
                break
            a, b, c_idx, d = playing[:4]
            playing = playing[4:]

            team1 = sorted([player_names[a], player_names[b]])
            team2 = sorted([player_names[c_idx], player_names[d]])

            courts.append(f"**Court {c+1}:** {team1[0]} & {team1[1]} serving to {team2[0]} & {team2[1]}")

        roster.append({
            "round": round_num,
            "byes": [player_names[i] for i in bye_indices],
            "courts": courts
        })

    st.session_state.roster = roster
    st.success("✅ Roster Generated!")

# ====================== DISPLAY ======================
if st.session_state.roster:
    st.divider()
    st.subheader("Generated Roster")

    for r in st.session_state.roster:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

    full_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes'])}\n" + "\n".join(r['courts'])
        for r in st.session_state.roster
    ])
    st.download_button("📥 Download Roster", full_text, "Pickleball_Roster.txt")

else:
    st.info("Click 'Generate Roster' above to create the schedule.")
