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
    st.session_state.used_pairs = set()
    st.session_state.bye_count = {}
    st.session_state.current_players = []
    st.session_state.num_courts = 3
    st.session_state.total_rounds = 12

# ====================== GENERATE ROSTER ======================
st.subheader("Generate Roster")

col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=15, step=1)
with col2:
    st.session_state.num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    st.session_state.total_rounds = st.number_input("Total Rounds", min_value=1, value=12, step=1)

names_text = st.text_area("Player Names (one per line - optional)", height=140)

if st.button("Generate Full Roster", type="primary", use_container_width=True):
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
    else:
        player_names = [f"P{i+1}" for i in range(num_players)]

    st.session_state.current_players = player_names
    actual_courts = min(st.session_state.num_courts, len(player_names) // 4)
    byes_per_round = len(player_names) - (actual_courts * 4)

    st.session_state.roster = []   # Clear previous roster

    for round_num in range(1, st.session_state.total_rounds + 1):
        if byes_per_round > 0:
            candidates = sorted(player_names, key=lambda p: (st.session_state.bye_count.get(p, 0), random.random()))
            bye_list = candidates[:byes_per_round]
            for p in bye_list:
                st.session_state.bye_count[p] = st.session_state.bye_count.get(p, 0) + 1
        else:
            bye_list = []

        playing = [p for p in player_names if p not in bye_list]
        random.shuffle(playing)

        courts = []
        for c in range(actual_courts):
            if len(playing) < 4: break
            a, b, c_idx, d = playing[:4]
            playing = playing[4:]

            team1 = sorted([player_names[a], player_names[b]])
            team2 = sorted([player_names[c_idx], player_names[d]])

            courts.append(f"**Court {c+1}:** {team1[0]} & {team1[1]} serving to {team2[0]} & {team2[1]}")

        st.session_state.roster.append({
            "round": round_num,
            "byes": sorted(bye_list),
            "courts": courts
        })

    st.success("✅ Full Roster Generated!")

# ====================== INTERRUPT SECTION ======================
if st.session_state.roster:
    st.divider()
    st.subheader("🔄 Interrupt Game Session")

    interrupt_after = st.number_input("Interrupt After Round #", min_value=0, max_value=len(st.session_state.roster), value=len(st.session_state.roster))

    col1, col2 = st.columns(2)
    with col1:
        add_text = st.text_area("Add New Players", height=80)
    with col2:
        remove_text = st.text_area("Remove Players", height=80)

    if st.button("Apply Player Changes"):
        current = st.session_state.current_players.copy()
        for p in [x.strip() for x in remove_text.splitlines() if x.strip()]:
            if p in current:
                current.remove(p)
        for p in [x.strip() for x in add_text.splitlines() if x.strip()]:
            if p not in current:
                current.append(p)
        st.session_state.current_players = current
        st.success(f"Updated to {len(current)} players")
        st.rerun()

    # Display Roster
    st.divider()
    st.subheader("Current Roster")

    full_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r.get('byes') else 'None'}\n" + "\n".join(r['courts'])
        for r in st.session_state.roster
    ])
    st.download_button("📥 Download Full Roster", full_text, "Pickleball_Roster.txt", use_container_width=True)

    for r in st.session_state.roster:
        st.subheader(f"Round {r['round']}")
        if r.get('byes'):
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

# Reset Button
if st.button("Start New Session From Scratch"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
    
