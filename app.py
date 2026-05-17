import streamlit as st
import random

st.set_page_config(page_title="Pickleball Randomizer", page_icon="🥒", layout="centered")

# Hide branding
st.markdown("""
    <style>
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
    </style>
""", unsafe_allow_html=True)

st.title("🥒 Pickleball Randomizer")
st.markdown("**Brought to you by [Ecoglitter.com](https://ecoglitter.com)**")

# ====================== SESSION STATE ======================
if 'roster_history' not in st.session_state:
    st.session_state.roster_history = []      # Completed rounds
    st.session_state.used_pairs = set()
    st.session_state.bye_count = {}
    st.session_state.all_players = []         # Current list of player names

# ====================== MAIN INPUTS ======================
st.subheader("Current Players")
current_players = st.text_area(
    "Current Player List (one per line)",
    value="\n".join(st.session_state.all_players) if st.session_state.all_players else "",
    height=160,
    placeholder="Enter player names here..."
)

col1, col2, col3 = st.columns(3)
with col1:
    num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col2:
    remaining_rounds = st.number_input("Remaining Rounds to Generate", min_value=1, value=8, step=1)

if st.button("Update Player List & Continue", type="primary"):
    new_players = [line.strip() for line in current_players.splitlines() if line.strip()]
    st.session_state.all_players = new_players
    st.success(f"Player list updated to {len(new_players)} players")
    st.rerun()

# ====================== GENERATE NEXT ROUNDS ======================
if st.button("Generate Next Rounds", type="primary", use_container_width=True) and st.session_state.all_players:
    player_names = st.session_state.all_players
    num_players = len(player_names)
    
    actual_courts = min(num_courts, num_players // 4)
    byes_per_round = num_players - (actual_courts * 4)

    # Initialize bye count for new players
    for p in player_names:
        if p not in st.session_state.bye_count:
            st.session_state.bye_count[p] = 0

    new_rounds = []

    for r in range(1, remaining_rounds + 1):
        # Select byes fairly
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
            if len(playing) < 4:
                break
            t1a, t1b, t2a, t2b = playing[:4]
            playing = playing[4:]

            team1 = sorted([t1a, t1b])
            team2 = sorted([t2a, t2b])

            pair1 = tuple(team1)
            pair2 = tuple(team2)

            # Strong avoidance of repeat pairs
            if pair1 in st.session_state.used_pairs and len(st.session_state.used_pairs) < (num_players*(num_players-1)//2 - 30):
                random.shuffle(team1)
            if pair2 in st.session_state.used_pairs and len(st.session_state.used_pairs) < (num_players*(num_players-1)//2 - 30):
                random.shuffle(team2)

            courts.append(f"**Court {c+1}:** {team1[0]} & {team1[1]} serving to {team2[0]} & {team2[1]}")
            st.session_state.used_pairs.add(tuple(sorted(team1)))
            st.session_state.used_pairs.add(tuple(sorted(team2)))

        new_rounds.append({
            "round": len(st.session_state.roster_history) + r,
            "byes": sorted(bye_list),
            "courts": courts
        })

    # Add new rounds to history
    st.session_state.roster_history.extend(new_rounds)

    st.success(f"✅ Generated {remaining_rounds} new rounds!")

# ====================== DISPLAY FULL ROSTER ======================
if st.session_state.roster_history:
    st.divider()
    st.subheader("Full Roster So Far")

    # Download full roster
    full_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r['byes'] else 'None'}\n" + "\n".join(r['courts'])
        for r in st.session_state.roster_history
    ])
    
    st.download_button(
        label="📥 Download Full Roster",
        data=full_text,
        file_name="Pickleball_Full_Roster.txt",
        mime="text/plain",
        use_container_width=True
    )

    for r in st.session_state.roster_history:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

# Reset option
if st.button("Clear All History & Start Fresh"):
    st.session_state.roster_history = []
    st.session_state.used_pairs = set()
    st.session_state.bye_count = {}
    st.success("History cleared. Ready for a new session.")
    st.rerun()
