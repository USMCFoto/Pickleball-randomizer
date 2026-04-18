import streamlit as st
import random
from collections import defaultdict

st.set_page_config(page_title="Pickleball Randomizer", page_icon="🥒", layout="centered")

st.title("🥒 Pickleball Randomizer")
st.markdown("**Brought to you by [Ecoglitter.com](https://ecoglitter.com)**")

# Input fields
col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=9, step=1)
with col2:
    num_courts = st.number_input("Number of Courts", min_value=1, value=2, step=1)
with col3:
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)",
    height=150,
    placeholder="Enter one name per line\nOr leave blank to use P1, P2, etc."
)

if st.button("Generate Roster", type="primary", use_container_width=True):
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
        if len(player_names) != num_players:
            st.error(f"You entered {len(player_names)} names but selected {num_players} players.")
            st.stop()
    else:
        player_names = [f"P{i+1}" for i in range(num_players)]

    # Generate roster
    players = list(range(num_players))
    players_per_round = num_courts * 4
    byes_per_round = max(0, num_players - players_per_round)
    
    roster = []
    used_pairs = set()
    bye_count = [0] * num_players

    for round_num in range(1, num_rounds + 1):
        # Fair + random byes
        if byes_per_round > 0:
            candidates = sorted(range(num_players), key=lambda i: (bye_count[i], random.random()))
            bye_indices = candidates[:byes_per_round]
            for i in bye_indices:
                bye_count[i] += 1
        else:
            bye_indices = []

        # Playing players
        playing = [i for i in players if i not in bye_indices]
        random.shuffle(playing)

        courts = []
        round_pairs = []

        for c in range(num_courts):
            if len(playing) < 4:
                break
            a, b, c_idx, d = playing[:4]
            playing = playing[4:]

            team1 = sorted([player_names[a], player_names[b]])
            team2 = sorted([player_names[c_idx], player_names[d]])

            pair1 = tuple(team1)
            pair2 = tuple(team2)

            # Avoid repeating partnerships when possible
            if pair1 in used_pairs and len(used_pairs) < 200:
                team1.reverse()
            if pair2 in used_pairs and len(used_pairs) < 200:
                team2.reverse()

            courts.append(f"**Court {c+1}:** {team1[0]} & {team1[1]} vs {team2[0]} & {team2[1]}")
            round_pairs.extend([pair1, pair2])

        used_pairs.update(round_pairs)

        roster.append({
            "round": round_num,
            "byes": [player_names[i] for i in sorted(bye_indices)] if bye_indices else None,
            "courts": courts
        })

    # Display the roster
    st.success(f"✅ Roster generated for {num_players} players, {num_courts} courts, {num_rounds} rounds!")

    for r in roster:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

    # Download button
    output_text = "\n\n".join([
        f"ROUND {r['round']}\n" +
        (f"Byes: {', '.join(r['byes'])}\n" if r['byes'] else "Byes: None\n") +
        "\n".join(r['courts'])
        for r in roster
    ])
    
    st.download_button(
        label="📥 Download Roster as Text File",
        data=output_text,
        file_name=f"Pickleball_Roster_{random.randint(1000,9999)}.txt",
        mime="text/plain"
    )

st.caption("Pickleball Randomizer • Fair byes + Maximized unique partnerships")
