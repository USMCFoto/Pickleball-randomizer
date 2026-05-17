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
    st.session_state.used_pairs = set()
    st.session_state.bye_count = {}
    st.session_state.current_players = []

# ====================== INITIAL SETUP ======================
if not st.session_state.current_players:
    st.subheader("Start New Session")
    col1, col2, col3 = st.columns(3)
    with col1:
        num_players = st.number_input("Number of Players", min_value=4, value=15, step=1)
    with col2:
        num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
    with col3:
        total_rounds = st.number_input("Total Rounds", min_value=1, value=12, step=1)

    names_text = st.text_area("Player Names (one per line)", height=180)

    if st.button("🚀 Start New Session", type="primary", use_container_width=True):
        if names_text.strip():
            st.session_state.current_players = [line.strip() for line in names_text.splitlines() if line.strip()]
        else:
            st.session_state.current_players = [f"P{i+1}" for i in range(num_players)]
        st.session_state.num_courts = num_courts
        st.session_state.total_rounds = total_rounds
        st.rerun()

# ====================== MAIN APP ======================
else:
    st.success(f"Active Session — {len(st.session_state.current_players)} players | {len(st.session_state.roster)}/{st.session_state.total_rounds} rounds")

    # ====================== INTERRUPT SECTION ======================
    st.divider()
    st.subheader("🔄 Interrupt Game Session")

    interrupt_after = st.number_input(
        "Interrupt After Round #", 
        min_value=0, 
        max_value=len(st.session_state.roster), 
        value=len(st.session_state.roster),
        step=1
    )

    col1, col2 = st.columns(2)
    with col1:
        add_text = st.text_area("Add New Players (one per line)", height=100, placeholder="New Player 1\nNew Player 2")
    with col2:
        remove_text = st.text_area("Remove Players (one per line)", height=100, placeholder="Player to remove")

    if st.button("Apply Interrupt & Update Players"):
        current = st.session_state.current_players.copy()
        
        # Remove players
        for p in [x.strip() for x in remove_text.splitlines() if x.strip()]:
            if p in current:
                current.remove(p)
        
        # Add new players
        for p in [x.strip() for x in add_text.splitlines() if x.strip()]:
            if p not in current:
                current.append(p)
        
        st.session_state.current_players = current
        st.success(f"Player list updated! Now {len(current)} players.")
        st.rerun()

    # ====================== GENERATE REMAINING ROUNDS ======================
    remaining = st.session_state.total_rounds - len(st.session_state.roster)
    if remaining > 0:
        if st.button(f"Generate Next {remaining} Rounds", type="primary", use_container_width=True):
            player_names = st.session_state.current_players
            num_players = len(player_names)
            actual_courts = min(st.session_state.num_courts, num_players // 4)
            byes_per_round = num_players - (actual_courts * 4)

            for _ in range(remaining):
                round_num = len(st.session_state.roster) + 1
                
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

            st.success(f"Added {remaining} new rounds!")
            st.rerun()

    # ====================== DISPLAY ROSTER ======================
    if st.session_state.roster:
        st.divider()
        st.subheader("Full Roster")

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

# Reset
if st.button("Start Completely New Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
