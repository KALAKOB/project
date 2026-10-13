---
name: vn-game-ui-ux
description: "Comprehensive UI/UX design intelligence and implementation standards for Visual Novel and Interactive Storytelling desktop games in Python/Tkinter. Covers character sprite alpha transparency, progressive dialogue typewriter pacing, backlog history, HUD accessibility, micro-interactions, responsive canvas staging, and dark modern game aesthetics."
license: MIT
metadata:
  version: "1.0.0"
  author: "Antigravity UI/UX Design System"
---

# Visual Novel & Interactive Desktop Game UI/UX Design Intelligence

A battle-tested design framework and implementation standard for building premium, responsive, and accessible Visual Novel (VN) and narrative-driven educational games using Python and Tkinter.

---

## 1. Character Sprite Staging & Transparency Rules

### Alpha Channel & Matting
- **Format:** Always use 32-bit RGBA PNG (`.png`) for character sprites to guarantee crisp, anti-aliased edges without white matte fringe or halos.
- **De-fringing / Matte decontamination:** Character boundaries must blend cleanly onto dark backgrounds (`#0b111b` to `#152033`). Hair strands, fabric edges, and accessories must retain true color values without residual white background bleed.
- **Aspect Ratio Integrity:** Never stretch or distort character proportions. Always scale sprites proportionally using their intrinsic aspect ratio (e.g., width = `int(height * (848 / 1264))`).
- **Canvas Staging:** Position sprites on Tkinter `Canvas` anchored at bottom-right or center-right (`anchor="nw"`, `y = canvas_height - sprite_height`). This gives a natural standing perspective aligned with the dialogue box.

---

## 2. Dialogue Box UX & Typewriter Engine

### Progressive Text Reveal (Typewriter Effect)
- **Reading Rhythm:** Stream text at 15–20ms per character to create immersion and pacing.
- **Two-Phase Click UX:**
  1. **Phase 1 (Typing):** If user clicks, presses `Space`, or `Enter` while typing is active, instantly complete the sentence (`skip_typing`).
  2. **Phase 2 (Finished):** If sentence is complete, advancing input proceeds to the next dialogue entry.
- **Continuation Indicator:** Display a pulsing/blinking visual glyph (`▼` or `➔`) at the bottom-right corner when typing finishes to inform the user that input is expected.
- **Speaker Pill Badging:** Highlight the speaker name in a distinct pill container with contrasting accent color and avatar/icon:
  - NPC / Friend (Tee): Electric Blue (`#38bdf8`)
  - Player Protagonist: Emerald Green (`#34d399`) or Amber (`#fb923c`)
  - Narrator / Scene: Subtle Slate (`#94a3b8`)
  - System Alert / Minigame: Royal Purple (`#c084fc`)

### Quality-of-Life Controls (VN Standard)
- **Backlog / Dialogue Log (`LOG`):** Modal or drawer containing full scrollable history of conversations with timestamps/speakers.
- **Auto-Play Mode (`AUTO`):** Hands-free reading mode with adaptive delay (1.5s + text length calculation).
- **Fast-Forward (`SKIP`):** Fast-forward through previously read scenes.

---

## 3. HUD & Status Information Architecture

- **Visual Relationship Gauge:** Convert numeric stats (e.g. `50 / 100`) into visual progress bars or heart meters (`❤️❤️❤️🖤🖤` or `[██████░░░░] 60%`) for instant cognitive recognition.
- **Score & Achievement Feedback:** Use prominent icon badges (`🏆 150 PTS`) with high-contrast amber/yellow (`#f59e0b`).
- **Header Status Bar:** Keep persistent navigation controls (`💾 บันทึกเกม`, `🏠 เมนูหลัก`) neatly aligned on the top right, with clear visual separation from narrative content.
- **Scene Step Indicator:** Clearly convey the player's journey progress (e.g. `ฉากที่ 1 จาก 3: ตู้ยาสามัญ`).

---

## 4. Interactive Components & Micro-Interactions

### Styled Buttons
- **Hover Transitions:** 
  - Standard button: `#1f2e47` (Surface Light) $\to$ `#38bdf8` (Accent Cyan) with text contrasting in dark `#0b111b`.
  - Dangerous/Exit button: `#1f2e47` $\to$ `#ef4444` (Coral Red).
- **Active Press State:** Visually simulate depth/tactile response on click (`<Button-1>`) by adjusting border or inset color.
- **Cursor Affordance:** Explicitly enforce `cursor="hand2"` on all interactive elements.

### Keyboard Shortcuts
- `Space` / `Return` / `Right Arrow`: Advance dialogue / Confirm choice.
- `Escape`: Cancel modal / Return to menu / Pause game.
- `L`: Open Dialogue Log.
- `S`: Quick Save game progress.

---

## 5. Color Palette & Accessibility Tokens (Cyber-Clinic Theme)

| Token | Hex Value | Semantic Usage |
|---|---|---|
| `COLOR_BG` | `#0b111b` | Deep navy base viewport |
| `COLOR_SURFACE` | `#152033` | Panel and card containers |
| `COLOR_SURFACE_LIGHT` | `#1f2e47` | Interactive button default & elevated cards |
| `COLOR_TEXT_MAIN` | `#f1f5f9` | High-contrast primary text (WCAG AAA) |
| `COLOR_TEXT_MUTED` | `#94a3b8` | Subtitles, meta-information, narrative description |
| `COLOR_ACCENT` | `#38bdf8` | Healthcare sky cyan, active highlights |
| `COLOR_GREEN` | `#10b981` | Success states, correct medical choices |
| `COLOR_RED` | `#ef4444` | Hazard warnings, expired drugs, critical errors |
| `COLOR_YELLOW` | `#f59e0b` | Cautionary notes, score metrics, tip banners |
| `COLOR_PURPLE` | `#a855f7` | System events, special bond milestones |
| `COLOR_BORDER` | `#334155` | Crisp 1px border lines for card definition |
