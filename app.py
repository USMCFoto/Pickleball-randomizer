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

# ---------- Session state init ----------
if "roster_history" not in st.session_state:
    st.session_state.roster_history = []
if "player_names" not in st.session_state:
    st.session_state.player_names = []
if "num_rounds" not in st.session_state:
    st.session_state.num_rounds = 0
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 0
if "num_players_original" not in st.session_state:
    st.session_state.num_players_original = 0

# ---------- Inputs ----------
col1, col2, col3 = st.columns(3)
with col1:
    num_players_input = st.number_input("Number of Players", min_value=4, value=12, step=1)
with col2:
    num_courts_input = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    num_rounds_input = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)",
    height=140,
    placeholder="Enter one name per line\nOr leave blank for P1, P2, etc."
)

# ---------- Helper: generate rounds ----------
def generate_rounds(start_round, end_round, player_names, used_pairs, bye_count, num_courts):
    rounds = []
    num_players = len(player_names)

    for round_num in range(start_round, end_round + 1):
        actual_courts = min(num_courts, num_players // 4)
        byes_per_round = num_players - (actual_courts * 4)

        if byes_per_round > 0:
            indices = list(range(num_players))
            indices_sorted = sorted(
                indices,
                key=lambda i: (bye_count[player_names[i]], random.random())
            )
            bye_indices = indices_sorted[:byes_per_round]
            for i in bye_indices:
                bye_count[player_names[i]] += 1
        else:
            bye_indices = []

        playing_indices = [i for i in range(num_players) if i not in bye_indices]
        random.shuffle(playing_indices)

        courts = []
        for c in range(actual_courts):
            if len(playing_indices) < 4:
                break
            a_idx, b_idx, c_idx, d_idx = playing_indices[:4]
            playing_indices = playing_indices[4:]

            a = player_names[a_idx]
            b = player_names[b_idx]
            c_name = player_names[c_idx]
            d = player_names[d_idx]

            team1 = sorted([a, b])
            team2 = sorted([c_name, d])

            pair1 = tuple(team1)
            pair2 = tuple(team2)

            max_pairs = len(player_names) * (len(player_names) - 1) // 2
            if pair1 in used_pairs and len(used_pairs) < (max_pairs - 20):
                random.shuffle(team1)
                pair1 = tuple(sorted(team1))
            if pair2 in used_pairs and len(used_pairs) < (max_pairs - 20):
                random.shuffle(team2)
                pair2 = tuple(sorted(team2))

            used_pairs.add(pair1)
            used_pairs.add(pair2)

            text = f"**Court {c+1}:** {team1[0]} & {team1[1]} serving to {team2[0]} & {team2[1]}"
            courts.append({
                "team1": team1,
                "team2": team2,
                "text": text
            })

        round_obj = {
            "round": round_num,
            "byes": [player_names[i] for i in sorted(bye_indices)] if bye_indices else [],
            "courts": courts
        }
        rounds.append(round_obj)

    return rounds, used_pairs, bye_count

# ---------- Generate full roster ----------
if st.button("Generate Roster", type="primary", use_container_width=True):
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
        if len(player_names) != num_players_input:
            st.error(f"You entered {len(player_names)} names but selected {num_players_input} players.")
            st.stop()
    else:
        player_names = [f"P{i+1}" for i in range(num_players_input)]

    used_pairs = set()
    bye_count = {name: 0 for name in player_names}

    roster, used_pairs, bye_count = generate_rounds(
        start_round=1,
        end_round=num_rounds_input,
        player_names=player_names,
        used_pairs=used_pairs,
        bye_count=bye_count,
        num_courts=num_courts_input
    )

    st.session_state.roster_history = roster
    st.session_state.player_names = player_names
    st.session_state.num_rounds = num_rounds_input
    st.session_state.num_courts = num_courts_input
    st.session_state.num_players_original = num_players_input

    first_round = roster[0]
    actual_courts = len(first_round["courts"])
    byes_per_round = len(first_round["byes"])
    st.success(f"✅ Generated using {actual_courts} courts ({byes_per_round} byes in Round 1)")

# ---------- If we have a roster, show it ----------
if st.session_state.roster_history:
    roster = st.session_state.roster_history

    # ---------- MODIFY MID‑SESSION (RETROACTIVE) ----------
    st.subheader("Modify Roster Mid‑Session (Retroactive)")

    max_round = st.session_state.num_rounds
    change_round = st.number_input(
        "Round where roster change occurs",
        min_value=1,
        max_value=max_round,
        value=1,
        step=1
    )

    current_players = st.session_state.player_names.copy()

    players_leaving = st.multiselect(
        "Players leaving at this round:",
        current_players
    )

    st.markdown("### Add New Numbered Players")

    original_count = st.session_state.num_players_original or len(current_players)
    next_numbers = [f"P{i}" for i in range(original_count + 1, original_count + 11)]

    numbered_additions = st.multiselect(
        "Select new numbered players to add:",
        next_numbers
    )

    new_players_text = st.text_input(
        "Or add new players by name (comma separated):",
        placeholder="e.g. Alex, Jamie, Taylor"
    )

    if st.button("Apply Roster Changes and Regenerate"):
        preserved_rounds = [r for r in st.session_state.roster_history if r["round"] < change_round]

        player_names = current_players

        used_pairs = set()
        bye_count = {name: 0 for name in player_names}

        for r in preserved_rounds:
            for b in r["byes"]:
                if b in bye_count:
                    bye_count[b] += 1
            for court in r["courts"]:
                t1 = tuple(sorted(court["team1"]))
                t2 = tuple(sorted(court["team2"]))
                used_pairs.add(t1)
                used_pairs.add(t2)

        for p in players_leaving:
            if p in player_names:
                player_names.remove(p)
            bye_count.pop(p, None)

        for p in numbered_additions:
            if p not in player_names:
                player_names.append(p)
                bye_count[p] = 0

        if new_players_text.strip():
            for raw in new_players_text.split(","):
                name = raw.strip()
                if name and name not in player_names:
                    player_names.append(name)
                    bye_count[name] = 0

        if len(player_names) < 4:
            st.error("Not enough players to continue after these changes (need at least 4).")
        else:
            new_rounds, used_pairs, bye_count = generate_rounds(
                start_round=change_round,
                end_round=st.session_state.num_rounds,
                player_names=player_names,
                used_pairs=used_pairs,
                bye_count=bye_count,
                num_courts=st.session_state.num_courts
            )

            st.session_state.roster_history = preserved_rounds + new_rounds
            st.session_state.player_names = player_names

            st.success(
                f"Roster updated starting at Round {change_round}. "
                f"Players leaving: {', '.join(players_leaving) if players_leaving else 'None'}. "
                f"Players added: {', '.join(numbered_additions) if numbered_additions else 'None'}."
            )
            st.experimental_rerun()

    st.divider()

    # ---------- DOWNLOAD BUTTON ----------
    output_text_parts = []
    for r in roster:
        byes_str = ", ".join(r["byes"]) if r["byes"] else "None"
        courts_lines = [c["text"].replace("**", "") for c in r["courts"]]
        block = f"ROUND {r['round']}\nByes: {byes_str}\n" + "\n".join(courts_lines)
        output_text_parts.append(block)
    output_text = "\n\n".join(output_text_parts)

    st.download_button(
        label="📥 Download Roster as Text File",
        data=output_text,
        file_name=f"Pickleball_Roster_{random.randint(1000,9999)}.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.divider()

    # ---------- DISPLAY ROSTER ----------
    for r in roster:
        st.subheader(f"Round {r['round']}")
        if r["byes"]:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r["courts"]:
            st.write(court["text"])
        st.divider()

st.caption("")

