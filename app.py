import streamlit as st
import random

st.set_page_config(page_title="Pickleball Randomizer", page_icon="🥒", layout="centered")

# Hide Streamlit branding
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
if 'roster' not in st.session_state:
    st.session_state.roster = []
    st.session_state.used_pairs = set()
    st.session_state.bye_count = {}
    st.session_state.current_players = []

# ====================== INITIAL SETUP ======================
if len(st.session_state.roster) == 0:
    st.subheader("Initial Setup")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num_players = st.number_input("Number of Players", min_value=4, value=12, step=1)
    with col2:
        num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
    with col3:
        total_rounds = st.number_input("Total Rounds", min_value=1, value=12, step=1)

    names_text = st.text_area(
        "Player Names (one per line)",
        height=160,
        placeholder="Enter player names here..."
    )

    if st.button("Start New Session", type="primary", use_container_width=True):
        if names_text.strip():
            st.session_state.current_players = [line.strip() for line in names_text.splitlines() if line.strip()]
        else:
            st.session_state.current_players = [f"P{i+1}" for i in range(num_players)]
        
        st.success(f"Session started with {len(st.session_state.current_players)} players!")
        st.rerun()

# ====================== INTERRUPT / MODIFY PLAYERS ======================
else:
    st.subheader("🔄 Interrupt Game Session (Add or Remove Players)")
    
    st.info(f"Current Progress: **{len(st.session_state.roster)}** rounds completed")
    
    add_text = st.text_area("Add New Players (one per line)", height=70, placeholder="John\nSarah")
    remove_text = st.text_area("Remove Players (one per line)", height=70, placeholder="Bob\nLisa")

    if st.button("Apply Changes to Player List", type="primary"):
        current = st.session_state.current_players.copy()
        
        # Remove players
        to_remove = [line.strip() for line in remove_text.splitlines() if line.strip()]
        for p in to_remove:
            if p in current:
                current.remove(p)
        
        # Add new players
        to_add = [line.strip() for line in add_text.splitlines() if line.strip()]
        for p in to_add:
            if p not in current:
                current.append(p)
        
        st.session_state.current_players = current
        st.success(f"Player list updated! Now {len(current)} players.")
        st.rerun()

    # Generate more rounds
    remaining = total_rounds - len(st.session_state.roster) if 'total_rounds' in locals() else 8
    if st.button(f"Generate Next {remaining} Rounds", type="primary", use_container_width=True):
        # (Generation logic - same as before)
        player_names = st.session_state.current_players
        num_players = len(player_names)
        actual_courts = min(num_courts, num_players // 4)
        byes_per_round = num_players - (actual_courts * 4)

        for p in player_names:
            if p not in st.session_state.bye_count:
                st.session_state.bye_count[p] = 0

        new_rounds = []
        for _ in range(remaining):
            round_num = len(st.session_state.roster) + len(new_rounds) + 1
            
            if byes_per_round > 0:
                candidates = sorted(player_names, key=lambda p: (st.session_state.bye_count.get(p, 0), random.random()))
                bye_list = candidates[:byes_per_round]
                for p in bye_list:
                    st.session_state.bye_count[p] += 1
            else:
                bye_list = []

            playing = [p for p in player_names if p not in bye_list]
            random.shuffle(playing)

            courts = []
            for c in range(actual_courts):
                if len(playing) < 4: break
                t1a, t1b, t2a, t2b = playing[:4]
                playing = playing[4:]

                team1 = sorted([t1a, t1b])
                team2 = sorted([t2a, t2b])

                if tuple(team1) in st.session_state.used_pairs and len(st.session_state.used_pairs) < 200:
                    random.shuffle(team1)
                if tuple(team2) in st.session_state.used_pairs and len(st.session_state.used_pairs) < 200:
                    random.shuffle(team2)

                courts.append(f"**Court {c+1}:** {team1[0]} & {team1[1]} serving to {team2[0]} & {team2[1]}")
                st.session_state.used_pairs.add(tuple(team1))
                st.session_state.used_pairs.add(tuple(team2))

            new_rounds.append({
                "round": round_num,
                "byes": sorted(bye_list),
                "courts": courts
            })

        st.session_state.roster.extend(new_rounds)
        st.success(f"Added {remaining} new rounds!")
        st.rerun()

# ====================== DISPLAY ROSTER ======================
if st.session_state.roster:
    st.divider()
    st.subheader("Full Session Roster")

    full_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r['byes'] else 'None'}\n" + "\n".join(r['courts'])
        for r in st.session_state.roster
    ])
    
    st.download_button("📥 Download Full Roster", full_text, "Pickleball_Full_Roster.txt", use_container_width=True)

    for r in st.session_state.roster:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

# Reset Button
if st.button("🗑️ Clear Everything & Start New Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
