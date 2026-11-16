# 📜 Generic Stickman Cinema Workflow & Timing Specification

> **Scope**: Universal production standards for producing high-retention 2D stickman animated videos with the Stickman Cinema toolchain.

---

## 🎯 1. Pacing & Cut Duration Standards
* **Rapid Cut Pacing**: Every shot cuts between **3.0 to 4.8 seconds** (average ~3.8s).
* **Hard Cut Ceiling**: **NO SHOT MAY EVER EXCEED 5.0 SECONDS.** Fast visual cadence is essential for audience engagement.
* **Standard Series Format**: 14 Grids × 9 Panels = 126 Shots (~8 to 10 minutes total runtime).
* **Standard Solo Movie Format**: 27 to 35 Grids (~15 to 20 minutes total runtime).

---

## 🎙️ 2. Audio-Visual Synchronization (Zero-Drift Architecture)
* **Never Divide Blindly**: Shot durations must NEVER be estimated by `total_audio / shot_count`.
* **1:1 Scene Narration Lock**:
  * Every visual shot corresponds directly to its specific narration line.
  * Shot duration is locked to the voiceover length: `max(3.0, min(audio_duration + 0.25, 4.8))`.
  * Narration audio is embedded directly into each individual clip (`-af "adelay=200|200,apad"`).
  * This guarantees **0% temporal drift** from the first frame to the last frame.

---

## 💬 3. Subtitle Formatting (Single-Line Rule)
* **Single Line Only**: Subtitles must NEVER form paragraph blocks.
* **Word Limit**: Strictly **5 to 8 words per subtitle event** (one short clause).
* **Position & Styling**: Centered at bottom above safety margins (`MarginV=75`), Arial Bold 28pt, bright white text with dark outline and drop shadow.

---

## 🎥 4. Camera Movement & Motion Standards
* **Default Standard (95%+ of Shots)**:
  * All standard shots must use smooth cinematic slides (horizontal dolly pans) and slow linear zooms (`min(zoom+0.0008, 1.08)` or `min(1.0+0.0015*on, 1.10)` or `max(1.08-0.0008*on, 1.0)`).
* **Shakiness Restriction**:
  * **Strictly Prohibited** on regular dialogue, walking, crafting, and tactical shots.
  * **Only Permitted** on high-impact seismic, explosive, or violent breach shots (e.g., impact shockwaves, dynamite detonations).

---

## 🕹️ 5. Dynamic HUD & Achievement Popups
* **Top-Left**: `[DAY XX | TIME XX:XX]` in semi-transparent black pill box (`boxcolor=black@0.65`). Frame-accurate to spoken text.
* **Top-Right**: Color-coded `[STATUS: RESOURCE | ALERT | THREAT LEVEL]` pill box.
* **Achievement Popups**: Displayed for 2 to 4 seconds via `enable='between(t, 0.6, 3.6)'`, cleanly hidden before the next cut.

---

## 🎯 6. Problem ➔ Solution Narrative Structure
* **Episode Goal**: Establish an urgent high-stakes objective and deadline within the first 30 seconds.
* **5-Step Micro-Arc Loop**:
  1. **Problem / Crisis**: Sudden physical catastrophe halts forward progress.
  2. **Stakes & Ticking Clock**: Clear penalty of failure.
  3. **Tactical Science & Formulation**: Scientific or engineering formula identified.
  4. **Execution & Lock-In**: Protagonist executes the physical action under pressure.
  5. **Payoff & Escalation**: Tangible victory earned, which immediately exposes the next challenge.
