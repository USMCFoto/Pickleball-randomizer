import streamlit as st
import random

st.set_page_config(
    page_title="Pickleball Randomizer v1.5",
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
if "used_partner_pairs" not in st.session_state:
    st.session_state.used_partner_pairs = set()
if "used_matchups" not in st.session_state:
    st.session_state.used_matchups = set()

# ---------- Inputs ----------
col1, col2, col3 = st.columns(3)
with col1:
    num_players_input = st.number_input("Number of Players", min_value=4, value=12, step=1)
with col2:
    num_courts_input = st.number_input("Number of Courts", min_value=1, value=3, step=1)
with col3:
    num_rounds_input = st.number_input("Number of Rounds (max 25)", min_value=1, max_value=25, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)",
    height=140,
    placeholder="Enter one name per line\nOr leave blank for P1, P2, etc."
)

# ---------- Helper: generate rounds with no repeat partners and no repeat team-vs-team ----------
def generate_rounds(start_round, end_round, player_names, used_partner_pairs, used_matchups, bye_count, num_courts):
    rounds = []
    num_players = len(player_names)

    for round_num in range(start_round, end_round + 1):
        num_players = len(player_names)
        if num_players < 4:
            break

        actual_courts = min(num_courts, num_players // 4)
        if actual_courts == 0:
            break

        byes_per_round = num_players - (actual_courts * 4)

        # choose byes, favoring those with fewer byes so far
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
        playing_players = [player_names[i] for i in playing_indices]

        # ---- Step 1: build partner pairs (no repeat partners) ----
        # candidate pairs: all unused partner pairs among playing players
        candidate_pairs = []
        for i in range(len(playing_players)):
            for j in range(i + 1, len(playing_players)):
                p1 = playing_players[i]
                p2 = playing_players[j]
                pair_key = frozenset({p1, p2})
                if pair_key not in used_partner_pairs:
                    candidate_pairs.append((p1, p2))

        random.shuffle(candidate_pairs)

        # greedy maximum matching on candidate_pairs
        chosen_pairs = []
        used_this_round = set()
        needed_pairs = actual_courts * 2

        for p1, p2 in candidate_pairs:
            if len(chosen_pairs) >= needed_pairs:
                break
            if p1 in used_this_round or p2 in used_this_round:
                continue
            chosen_pairs.append((p1, p2))
            used_this_round.add(p1)
            used_this_round.add(p2)

        # if we still don't have enough pairs, allow repeats as fallback
        if len(chosen_pairs) < needed_pairs:
            # build all possible pairs (including previously used)
            all_pairs = []
            for i in range(len(playing_players)):
                for j in range(i + 1, len(playing_players)):
                    p1 = playing_players[i]
                    p2 = playing_players[j]
                    all_pairs.append((p1, p2))
            random.shuffle(all_pairs)

            for p1, p2 in all_pairs:
                if len(chosen_pairs) >= needed_pairs:
                    break
                if p1 in used_this_round or p2 in used_this_round:
                    continue
                chosen_pairs.append((p1, p2))
                used_this_round.add(p1)
                used_this_round.add(p2)

        # if still not enough, reduce number of courts for this round
        if len(chosen_pairs) < 2:
            # can't form even one court
            break

        # trim to even number of pairs and to max needed
        max_pairs_for_round = (len(chosen_pairs) // 2) * 2
        chosen_pairs = chosen_pairs[:max_pairs_for_round]
        courts_this_round = min(actual_courts, len(chosen_pairs) // 2)
        chosen_pairs = chosen_pairs[:courts_this_round * 2]

        # ---- Step 2: assign matches (no repeat team-vs-team) ----
        def teams_key(team):
            return tuple(sorted(team))

        def matchup_key(team1, team2):
            return frozenset({teams_key(team1), teams_key(team2)})

        best_matches = None
        for _ in range(50):
            random.shuffle(chosen_pairs)
            ok = True
            matches = []
            for i in range(0, courts_this_round * 2, 2):
                t1 = chosen_pairs[i]
                t2 = chosen_pairs[i + 1]
                mk = matchup_key(t1, t2)
                if mk in used_matchups:
                    ok = False
                    break
                matches.append((t1, t2, mk))
            if ok:
                best_matches = matches
                break

        # if we couldn't avoid repeat matchups, accept last arrangement
        if best_matches is None:
            matches = []
            for i in range(0, courts_this_round * 2, 2):
                t1 = chosen_pairs[i]
                t2 = chosen_pairs[i + 1]
                mk = matchup_key(t1, t2)
                matches.append((t1, t2, mk))
            best_matches = matches

        courts = []
        for court_index, (team1, team2, mk) in enumerate(best_matches, start=1):
            # update global tracking
            used_partner_pairs.add(frozenset(team1))
            used_partner_pairs.add(frozenset(team2))
            used_matchups.add(mk)

            t1_sorted = sorted(team1)
            t2_sorted = sorted(team2)
            text = f"**Court {court_index}:** {t1_sorted[0]} & {t1_sorted[1]} serving to {t2_sorted[0]} & {t2_sorted[1]}"
            courts.append({
                "team1": t1_sorted,
                "team2": t2_sorted,
                "text": text
            })

        round_obj = {
            "round": round_num,
            "byes": [player_names[i] for i in sorted(bye_indices)] if byes_per_round > 0 else [],
            "courts": courts
        }
        rounds.append(round_obj)

    return rounds, used_partner_pairs, used_matchups, bye_count

# ---------- Generate Roster Button ----------
st.markdown("### Generate Full Session Roster")

generate_clicked = st.button("Generate Roster", type="primary", use_container_width=True)

if generate_clicked:
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
        if len(player_names) != num_players_input:
            st.error(f"You entered {len(player_names)} names but selected {num_players_input} players.")
            st.stop()
    else:
        player_names = [f"P{i+1}" for i in range(num_players_input)]

    used_partner_pairs = set()
    used_matchups = set()
    bye_count = {name: 0 for name in player_names}

    roster, used_partner_pairs, used_matchups, bye_count = generate_rounds(
        start_round=1,
        end_round=num_rounds_input,
        player_names=player_names,
        used_partner_pairs=used_partner_pairs,
        used_matchups=used_matchups,
        bye_count=bye_count,
        num_courts=num_courts_input
    )

    st.session_state.roster_history = roster
    st.session_state.player_names = player_names
    st.session_state.num_rounds = num_rounds_input
    st.session_state.num_courts = num_courts_input
    st.session_state.num_players_original = num_players_input
    st.session_state.used_partner_pairs = used_partner_pairs
    st.session_state.used_matchups = used_matchups

    if roster:
        first_round = roster[0]
        st.success(
            f"Generated using {len(first_round['courts'])} courts "
            f"({len(first_round['byes'])} byes in Round 1)"
        )
    else:
        st.warning("Could not generate any rounds with the given constraints.")

# ---------- MODIFY MID‑SESSION ----------
if st.session_state.roster_history:
    st.subheader("Modify Roster Mid‑Session")

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

    original_count = st.session_state.num_players_original
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
        # preserve rounds before change_round
        preserved_rounds = [r for r in st.session_state.roster_history if r["round"] < change_round]

        # rebuild player list
        player_names = current_players

        # apply leaving players
        for p in players_leaving:
            if p in player_names:
                player_names.remove(p)

        # apply numbered additions
        for p in numbered_additions:
            if p not in player_names:
                player_names.append(p)

        # apply named additions
        if new_players_text.strip():
            for raw in new_players_text.split(","):
                name = raw.strip()
                if name and name not in player_names:
                    player_names.append(name)

        if len(player_names) < 4:
            st.error("Not enough players to continue (need at least 4).")
        else:
            # rebuild tracking from preserved rounds
            used_partner_pairs = set()
            used_matchups = set()
            bye_count = {name: 0 for name in player_names}

            def teams_key(team):
                return tuple(sorted(team))

            def matchup_key(team1, team2):
                return frozenset({teams_key(team1), teams_key(team2)})

            for r in preserved_rounds:
                # byes history
                for b in r["byes"]:
                    if b in bye_count:
                        bye_count[b] += 1
                # partner pairs and matchups
                for court in r["courts"]:
                    t1 = court["team1"]
                    t2 = court["team2"]
                    used_partner_pairs.add(frozenset(t1))
                    used_partner_pairs.add(frozenset(t2))
                    used_matchups.add(matchup_key(t1, t2))

            new_rounds, used_partner_pairs, used_matchups, bye_count = generate_rounds(
                start_round=change_round,
                end_round=st.session_state.num_rounds,
                player_names=player_names,
                used_partner_pairs=used_partner_pairs,
                used_matchups=used_matchups,
                bye_count=bye_count,
                num_courts=st.session_state.num_courts
            )

            st.session_state.roster_history = preserved_rounds + new_rounds
            st.session_state.player_names = player_names
            st.session_state.used_partner_pairs = used_partner_pairs
            st.session_state.used_matchups = used_matchups

            st.success("Roster updated starting at Round "
                       f"{change_round}.")
            st.rerun()

    st.divider()

    # ---------- DOWNLOAD BUTTON ----------
    roster = st.session_state.roster_history
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
            st.write(f"**Byes:** {', '.join(r["byes"])}")
        for court in r["courts"]:
            st.write(court["text"])
        st.divider()

st.caption("")
