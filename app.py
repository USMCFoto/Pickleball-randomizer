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

if 'roster' not in st.session_state:
    st.session_state.roster = []

st.subheader("Generate Roster")

col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=15, step=1)
with col2:
    num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area("Player Names (one per line - optional)", height=160)

if st.button("Generate Full Roster", type="primary", use_container_width=True):
    # Get player names
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
    else:
        player_names = [f"P{i+1}" for i in range(num_players)]

    actual_courts = min(num_courts, len(player_names) // 4)
    byes_per_round = len(player_names) - (actual_courts * 4)

    roster = []

    for round_num in range(1, num_rounds + 1):
        # Create list of players and shuffle
        players_list = player_names.copy()
        random.shuffle(players_list)

        # Take byes from the end
        bye_list = players_list[-byes_per_round:] if byes_per_round > 0 else []
        playing_list = players_list[:-byes_per_round] if byes_per_round > 0 else players_list

        courts = []
        for c in range(actual_courts):
            if len(playing_list) < 4:
                break
            p1, p2, p3, p4 = playing_list[:4]
            playing_list = playing_list[4:]

            team1 = sorted([p1, p2])
            team2 = sorted([p3, p4])

            courts.append(f"**Court {c+1}:** {team1[0]} & {team1[1]} serving to {team2[0]} & {team2[1]}")

        roster.append({
            "round": round_num,
            "byes": sorted(bye_list),
            "courts": courts
        })

    st.session_state.roster = roster
    st.success("✅ Roster Generated Successfully!")

# ====================== DISPLAY ROSTER ======================
if st.session_state.roster:
    st.divider()
    st.subheader("Current Roster")

    for r in st.session_state.roster:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

    full_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r['byes'] else 'None'}\n" + "\n".join(r['courts'])
        for r in st.session_state.roster
    ])
    st.download_button("📥 Download Roster", full_text, "Pickleball_Roster.txt", use_container_width=True)

# Reset
if st.button("Start New Session"):
    st.session_state.roster = []
    st.rerun()
