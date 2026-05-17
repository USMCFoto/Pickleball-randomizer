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

col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=12, step=1)
with col2:
    num_courts = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)",
    height=140,
    placeholder="Enter one name per line\nOr leave blank for P1, P2, etc."
)

if st.button("Generate Roster", type="primary", use_container_width=True):
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
        if len(player_names) != num_players:
            st.error(f"You entered {len(player_names)} names but selected {num_players} players.")
            st.stop()
    else:
        player_names = [f"P{i+1}" for i in range(num_players)]

    actual_courts = min(num_courts, num_players // 4)
    byes_per_round = num_players - (actual_courts * 4)

    roster = []
    used_pairs = set()
    bye_count = [0] * num_players

    for round_num in range(1, num_rounds + 1):
        if byes_per_round > 0:
            candidates = sorted(range(num_players), key=lambda i: (bye_count[i], random.random()))
            bye_indices = candidates[:byes_per_round]
            for i in bye_indices:
                bye_count[i] += 1
        else:
            bye_indices = []

        playing = [i for i in range(num_players) if i not in bye_indices]
        random.shuffle(playing)

        courts = []
        for c in range(actual_courts):
            if len(playing) < 4:
                break
            a, b, c_idx, d = playing[:4]
            playing = playing[4:]

            team1 = sorted([player_names[a], player_names[b]])
            team2 = sorted([player_names[c_idx], player_names[d]])

            pair1 = tuple(team1)
            pair2 = tuple(team2)

            if pair1 in used_pairs and len(used_pairs) < (num_players * (num_players-1) // 2 - 20):
                random.shuffle(team1)
            if pair2 in used_pairs and len(used_pairs) < (num_players * (num_players-1) // 2 - 20):
                random.shuffle(team2)

            # New format with "serving to"
            court_str = f"**Court {c+1}:** {team1[0]} & {team1[1]} serving to {team2[0]} & {team2[1]}"
            courts.append(court_str)
            used_pairs.add(tuple(sorted(team1)))
            used_pairs.add(tuple(sorted(team2)))

        roster.append({
            "round": round_num,
            "byes": [player_names[i] for i in sorted(bye_indices)] if bye_indices else None,
            "courts": courts
        })

    st.success(f"✅ Generated using {actual_courts} courts ({byes_per_round} byes per round)")

    # Download button (above roster)
    output_text = "\n\n".join([
        f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r.get('byes') else 'None'}\n" + "\n".join(r['courts'])
        for r in roster
    ])
    st.download_button(
        label="📥 Download Roster as Text File",
        data=output_text,
        file_name=f"Pickleball_Roster_{random.randint(1000,9999)}.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.divider()

    # Display roster
    for r in roster:
        st.subheader(f"Round {r['round']}")
        if r.get('byes'):
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

st.caption("")
