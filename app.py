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

# ====================== GENERATE ROSTER ======================
st.subheader("Create / Generate Roster")

col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=15, step=1)
with col2:
    num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)", 
    height=140,
    placeholder="Leave blank for P1, P2, etc."
)

if st.button("Generate New Roster", type="primary", use_container_width=True):
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
    else:
        player_names = [f"P{i+1}" for i in range(num_players)]

    st.session_state.current_players = player_names
    actual_courts = min(num_courts, len(player_names) // 4)
    byes_per_round = len(player_names) - (actual_courts * 4)

    st.session_state.roster = []
    used_pairs = set()

    for round_num in range(1, num_rounds + 1):
        if byes_per_round > 0:
            candidates = sorted(range(len(player_names)), key=lambda i: (0, random.random()))
            bye_indices = candidates[:byes_per_round]
        else:
            bye_indices = []

        playing = [i for i in range(len(player_names)) if i not in bye_indices]
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
            "byes": [player_names[i] for i in bye_indices],
            "courts": courts
        })

    st.success("✅ Roster Generated!")

# ====================== INTERRUPT / MODIFY ======================
if st.session_state.roster:
    st.divider()
    st.subheader("🔄 Interrupt Game Session (Add or Remove Players)")

    col_a, col_b = st.columns(2)
    with col_a:
        add_text = st.text_area("Add New Players", height=80, placeholder="New players here...")
    with col_b:
        remove_text = st.text_area("Remove Players", height=80, placeholder="Players to remove...")

    if st.button("Apply Changes to Player List"):
        current = st.session_state.current_players.copy()
        
        # Remove
        for p in [x.strip() for x in remove_text.splitlines() if x.strip()]:
            if p in current:
                current.remove(p)
        # Add
        for p in [x.strip() for x in add_text.splitlines() if x.strip()]:
            if p not in current:
                current.append(p)
        
        st.session_state.current_players = current
        st.success(f"Player list updated! Now {len(current)} players.")
        st.rerun()

    # Show Current Roster
    st.divider()
    st.subheader("Current Roster")

    full_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r['byes'] else 'None'}\n" + "\n".join(r['courts'])
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

# Reset
if st.button("Start Completely New Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
    
