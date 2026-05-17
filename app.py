import streamlit as st
import random

st.set_page_config(page_title="Pickleball Randomizer", page_icon="🥒", layout="centered")

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
    st.session_state.roster = []           # All generated rounds
    st.session_state.used_pairs = set()
    st.session_state.bye_count = {}
    st.session_state.current_players = []

# ====================== CURRENT STATUS ======================
st.subheader("Session Status")
total_rounds = st.number_input("Total Rounds in Session", min_value=1, value=12, step=1)

if st.session_state.roster:
    current_round = len(st.session_state.roster)
    st.info(f"**Progress:** {current_round} / {total_rounds} rounds completed")

# ====================== INTERRUPT GAME SESSION ======================
st.divider()
st.subheader("🔄 Interrupt Game Session")

interrupt_col1, interrupt_col2 = st.columns(2)
with interrupt_col1:
    interrupt_after = st.number_input("Interrupt After Round #", 
                                      min_value=0, 
                                      max_value=max(0, len(st.session_state.roster)), 
                                      value=len(st.session_state.roster),
                                      step=1)

st.write("**Update Players** (add or remove)")
add_players = st.text_area("Add New Players (one per line)", height=80, placeholder="John\nSarah\nMike")
remove_players = st.text_area("Remove Players (one per line)", height=80, placeholder="Bob\nLisa")

if st.button("Apply Interrupt & Update Player List", type="primary"):
    current = st.session_state.current_players.copy()
    
    # Remove players
    to_remove = [line.strip() for line in remove_players.splitlines() if line.strip()]
    for p in to_remove:
        if p in current:
            current.remove(p)
    
    # Add new players
    to_add = [line.strip() for line in add_players.splitlines() if line.strip()]
    for p in to_add:
        if p not in current:
            current.append(p)
    
    st.session_state.current_players = current
    st.success(f"Player list updated! Now {len(current)} players.")
    st.rerun()

# ====================== GENERATE / CONTINUE ROSTER ======================
remaining = total_rounds - len(st.session_state.roster)

if st.button(f"Generate Next {remaining} Rounds", type="primary", use_container_width=True) and st.session_state.current_players:
    player_names = st.session_state.current_players
    num_players = len(player_names)
    num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1, key="courts_input")
    
    actual_courts = min(num_courts, num_players // 4)
    byes_per_round = num_players - (actual_courts * 4)

    # Initialize bye counts
    for p in player_names:
        if p not in st.session_state.bye_count:
            st.session_state.bye_count[p] = 0

    new_rounds = []

    for _ in range(remaining):
        round_num = len(st.session_state.roster) + len(new_rounds) + 1
        
        # Select byes
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
            t1a, t1b, t2a, t2b = playing[:4]
            playing = playing[4:]

            team1 = sorted([t1a, t1b])
            team2 = sorted([t2a, t2b])

            if tuple(team1) in st.session_state.used_pairs and len(st.session_state.used_pairs) < 150:
                random.shuffle(team1)
            if tuple(team2) in st.session_state.used_pairs and len(st.session_state.used_pairs) < 150:
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

# ====================== DISPLAY FULL ROSTER ======================
if st.session_state.roster:
    st.divider()
    st.subheader("Full Session Roster")

    full_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r['byes'] else 'None'}\n" + "\n".join(r['courts'])
        for r in st.session_state.roster
    ])
    
    st.download_button("📥 Download Full Roster", full_text, "Full_Pickleball_Roster.txt", use_container_width=True)

    for r in st.session_state.roster:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

# Reset
if st.button("Clear Everything & Start New Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Session cleared!")
    st.rerun()
