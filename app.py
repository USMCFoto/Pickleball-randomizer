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

# Session State
if 'roster' not in st.session_state:
    st.session_state.roster = []
    st.session_state.current_players = []

# ====================== GENERATE ROSTER ======================
st.subheader("Generate Roster")

col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=15, step=1)
with col2:
    num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area("Player Names (one per line - optional)", height=140)

if st.button("Generate Full Roster", type="primary", use_container_width=True):
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
    else:
        player_names = [f"P{i+1}" for i in range(num_players)]

    st.session_state.current_players = player_names
    actual_courts = min(num_courts, len(player_names) // 4)
    byes_per_round = len(player_names) - (actual_courts * 4)

    st.session_state.roster = []

    for round_num in range(1, num_rounds + 1):
        players_list = player_names.copy()
        random.shuffle(players_list)

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

        st.session_state.roster.append({
            "round": round_num,
            "byes": sorted(bye_list),
            "courts": courts
        })

    st.success("✅ Roster Generated!")

# ====================== INTERRUPT SECTION ======================
if st.session_state.roster:
    st.divider()
    st.subheader("🔄 Interrupt Game Session")

    col1, col2 = st.columns(2)
    with col1:
        add_text = st.text_area("Add New Players (one per line)", height=80)
    with col2:
        remove_text = st.text_area("Remove Players (one per line)", height=80)

    if st.button("Apply Player Changes"):
        current = st.session_state.current_players.copy()
        for p in [x.strip() for x in remove_text.splitlines() if x.strip()]:
            if p in current:
                current.remove(p)
        for p in [x.strip() for x in add_text.splitlines() if x.strip()]:
            if p not in current:
                current.append(p)
        st.session_state.current_players = current
        st.success(f"Player list updated! Now {len(current)} players.")
        st.rerun()

    # Display Roster
    st.divider()
    st.subheader("Current Roster")

    full_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r['byes'] else 'None'}\n" + "\n".join(r['courts'])
        for r in st.session_state.roster
    ])
    st.download_button("📥 Download Full Roster", full_text, "Pickleball_Roster.txt", use_container_width=True)

    for r in st.session_state.roster:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

# Reset
if st.button("Start Completely New Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
