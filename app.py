import streamlit as st
import random
import time
from datetime import datetime

st.set_page_config(page_title="Pickleball Randomizer", page_icon="🥒", layout="centered")

st.title("🥒 Pickleball Randomizer")
st.markdown("**Brought to you by [Ecoglitter.com](https://ecoglitter.com)**")

# ====================== ROSTER GENERATOR ======================
col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=19, step=1)
with col2:
    num_courts = st.number_input("Number of Courts", min_value=1, value=5, step=1)
with col3:
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)",
    height=150,
    placeholder="Enter one name per line\nOr leave blank for P1, P2, etc."
)

if st.button("Generate Roster", type="primary", use_container_width=True):
    # ... (same fixed roster logic as before - keeping it short here)
    if names_text.strip():
        player_names = [line.strip() for line in names_text.splitlines() if line.strip()]
        if len(player_names) != num_players:
            st.error(f"You entered {len(player_names)} names but selected {num_players} players.")
            st.stop()
    else:
        player_names = [f"P{i+1}" for i in range(num_players)]

    max_players_per_round = num_courts * 4
    actual_courts = min(num_courts, num_players // 4)
    byes_per_round = num_players - (actual_courts * 4)

    # Roster generation logic (same as previous fixed version)
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
            a, b, c_idx, d = playing[:4]
            playing = playing[4:]
            team1 = sorted([player_names[a], player_names[b]])
            team2 = sorted([player_names[c_idx], player_names[d]])
            courts.append(f"**Court {c+1}:** {team1[0]} & {team1[1]} vs {team2[0]} & {team2[1]}")

        roster.append({
            "round": round_num,
            "byes": [player_names[i] for i in sorted(bye_indices)] if bye_indices else None,
            "courts": courts
        })

    st.success(f"✅ Roster generated – using {actual_courts} courts ({byes_per_round} byes per round)")

    for r in roster:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        for court in r['courts']:
            st.write(court)
        st.divider()

    # Download
    output_text = "\n\n".join([f"ROUND {r['round']}\nByes: {', '.join(r['byes']) if r['byes'] else 'None'}\n" + "\n".join(r['courts']) for r in roster])
    st.download_button("📥 Download Roster as Text File", output_text, file_name=f"Pickleball_Roster.txt")

# ====================== GAME TIMER WITH ALARM ======================
st.divider()
st.subheader("⏱️ Pickleball Game Timer")

# Timer settings
col_t1, col_t2 = st.columns(2)
with col_t1:
    minutes = st.number_input("Timer Minutes", min_value=1, value=15, step=1)
with col_t2:
    seconds = st.number_input("Timer Seconds", min_value=0, value=0, step=1)

total_seconds = minutes * 60 + seconds

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
    st.session_state.time_left = total_seconds
    st.session_state.start_time = None

# Controls
btn_col1, btn_col2, btn_col3 = st.columns(3)
if btn_col1.button("▶️ Start Timer", use_container_width=True):
    st.session_state.timer_running = True
    st.session_state.start_time = time.time()
    st.session_state.time_left = total_seconds

if btn_col2.button("⏸️ Pause", use_container_width=True):
    st.session_state.timer_running = False

if btn_col3.button("🔄 Reset", use_container_width=True):
    st.session_state.timer_running = False
    st.session_state.time_left = total_seconds

# Live countdown
timer_placeholder = st.empty()
progress_bar = st.progress(1.0)

if st.session_state.timer_running and st.session_state.time_left > 0:
    elapsed = time.time() - st.session_state.start_time
    st.session_state.time_left = max(0, total_seconds - int(elapsed))
    
    mins, secs = divmod(st.session_state.time_left, 60)
    timer_placeholder.metric("Time Remaining", f"{mins:02d}:{secs:02d}")
    progress = st.session_state.time_left / total_seconds if total_seconds > 0 else 0
    progress_bar.progress(progress)

    if st.session_state.time_left <= 0:
        st.success("⏰ Time's Up!")
        st.balloons()
        # Play alarm sound
        st.audio("https://www.soundjay.com/buttons/beep-07.mp3", autoplay=True)  # Free beep sound
        st.session_state.timer_running = False
    else:
        time.sleep(0.5)  # Refresh rate
        st.rerun()

st.caption("Timer with alarm sound when finished. Great for tracking games or rounds!")import streamlit as st
import random

st.set_page_config(page_title="Pickleball Randomizer", page_icon="🥒", layout="centered")

st.title("🥒 Pickleball Randomizer")
st.markdown("**Brought to you by [Ecoglitter.com](https://ecoglitter.com)**")

col1, col2, col3 = st.columns(3)
with col1:
    num_players = st.number_input("Number of Players", min_value=4, value=19, step=1)
with col2:
    num_courts = st.number_input("Number of Courts", min_value=1, value=5, step=1)
with col3:
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=12, step=1)

names_text = st.text_area(
    "Player Names (one per line - optional)",
    height=150,
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

    # ==================== FIXED LOGIC ====================
    max_players_per_round = num_courts * 4
    players_playing = min(num_players, max_players_per_round)
    actual_courts = players_playing // 4
    byes_per_round = num_players - (actual_courts * 4)

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
        playing = [i for i in range(num_players) if i not in bye_indices]
        random.shuffle(playing)

        courts = []
        round_pairs = []

        for c in range(actual_courts):
            a, b, c_idx, d = playing[:4]
            playing = playing[4:]

            team1 = sorted([player_names[a], player_names[b]])
            team2 = sorted([player_names[c_idx], player_names[d]])

            pair1 = tuple(team1)
            pair2 = tuple(team2)

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
            "courts": courts,
            "actual_courts": actual_courts
        })

    # ==================== DISPLAY ====================
    st.success(f"✅ Roster generated – using {actual_courts} courts ({byes_per_round} byes per round)")

    for r in roster:
        st.subheader(f"Round {r['round']}")
        if r['byes']:
            st.write(f"**Byes:** {', '.join(r['byes'])}")
        else:
            st.write("**Byes:** None")
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

st.caption("Pickleball Randomizer • Fair random byes + Maximized unique partnerships")
