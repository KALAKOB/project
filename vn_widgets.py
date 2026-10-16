"""
Visual Novel UI Widgets for Tkinter
คอมโพเนนต์กล่องบทสนทนาแบบ Typewriter พร้อมระบบเสียง, แถบสถานะด้านบน, ป๊อปอัปความรู้
และระบบบันทึก/โหลดแบบหลายช่องเซฟ (Multi-slot Save Dialog)
อ้างอิงมาตรฐาน UI/UX Pro Max และ Visual Novel Design System
"""

import os
import tkinter as tk
from tkinter import messagebox
import winsound
import save_manager
from ui_theme import (
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_LIGHT, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_GREEN,
    COLOR_GREEN_HOVER, COLOR_RED, COLOR_RED_HOVER, COLOR_YELLOW, COLOR_PURPLE, COLOR_BORDER,
    FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_BODY_BOLD,
    FONT_DIALOGUE, FONT_SPEAKER, FONT_SMALL,
    StyledButton, get_image
)

# -------------------------------------------------------------
# ตัวจัดการเสียงเอฟเฟกต์ (Sound Manager)
# -------------------------------------------------------------
# โฟลเดอร์เก็บไฟล์เสียงประกอบเกม (เสียงพิมพ์ดีด และเสียงกดปุ่ม)
_base_dir = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(_base_dir, "sounds")
TYPEWRITER_SOUND = os.path.join(SOUND_DIR, "typewriter.wav")
ADVANCE_SOUND = os.path.join(SOUND_DIR, "advance.wav")

_sound_enabled = True
_global_text_speed_ms = 18

def set_global_text_speed(speed_ms):
    global _global_text_speed_ms
    _global_text_speed_ms = max(5, min(100, int(speed_ms)))
    return _global_text_speed_ms

def get_global_text_speed():
    return _global_text_speed_ms

def set_global_volume(vol_pct):
    """ตั้งค่าระดับเสียงหลัก (0-100) พร้อมปรับระดับเสียงระบบ Windows"""
    global _global_volume, _sound_enabled
    _global_volume = max(0, min(100, int(vol_pct)))
    _sound_enabled = (_global_volume > 0)
    try:
        import ctypes
        vol_val = int((_global_volume / 100.0) * 0xFFFF)
        ctypes.windll.winmm.waveOutSetVolume(0, (vol_val << 16) | vol_val)
    except Exception:
        pass
    return _global_volume

def get_global_volume():
    """ดึงระดับเสียงปัจจุบัน (0-100)"""
    return _global_volume

# เริ่มต้นด้วยระดับเสียง 80%
try:
    set_global_volume(80)
except Exception:
    pass

def toggle_global_sound():
    global _sound_enabled, _global_volume
    _sound_enabled = not _sound_enabled
    if _sound_enabled and _global_volume == 0:
        set_global_volume(80)
    elif not _sound_enabled:
        set_global_volume(0)
    return _sound_enabled

def is_sound_enabled():
    return _sound_enabled

def play_sfx(sound_path):
    """เล่นเสียงเอฟเฟกต์แบบ Asynchronous (ไม่บล็อก UI)"""
    if not _sound_enabled:
        return
    try:
        if os.path.exists(sound_path):
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass


def center_modal(top, parent, width, height):
    """จัดตำแหน่งหน้าต่าง Modal ให้อยู่กึ่งกลางหน้าต่างหลัก"""
    top.geometry(f"{width}x{height}")
    top.update_idletasks()
    pw = parent.winfo_toplevel()
    rx = pw.winfo_rootx() + (pw.winfo_width() // 2) - (width // 2)
    ry = pw.winfo_rooty() + (pw.winfo_height() // 2) - (height // 2)
    top.geometry(f"+{rx}+{ry}")


class TopStatusBar(tk.Frame):
    """
    แถบสถานะด้านบน สไตล์ Modern Cyber-Clinic HUD
    แสดงข้อมูลผู้เล่น, ฉาก, คะแนน, และเกจวัดความสัมพันธ์แบบภาพ พร้อมปุ่มลัด
    """
    def __init__(self, parent, on_save_click=None, on_menu_click=None, on_log_click=None):
        super().__init__(parent, bg=COLOR_SURFACE, height=52)
        self.pack(fill="x", side="top")
        self.pack_propagate(False)

        # ขอบล่างเรืองแสงบางๆ
        border = tk.Frame(self, bg=COLOR_BORDER, height=1)
        border.pack(side="bottom", fill="x")

        # ข้อมูลฝั่งซ้าย: ผู้เล่น & ฉาก
        self.left_frame = tk.Frame(self, bg=COLOR_SURFACE)
        self.left_frame.pack(side="left", padx=14, pady=5)

        # Pill badge สำหรับชื่อผู้เล่น
        player_pill = tk.Frame(self.left_frame, bg=COLOR_SURFACE_LIGHT, padx=8, pady=2, highlightbackground=COLOR_BORDER, highlightthickness=1)
        player_pill.pack(side="left", padx=(0, 10))

        self.lbl_player = tk.Label(player_pill, text="👤 ผู้เล่น: -", font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE_LIGHT)
        self.lbl_player.pack()

        self.lbl_scene = tk.Label(self.left_frame, text="📍 ฉาก: -", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE)
        self.lbl_scene.pack(side="left")

        # ข้อมูลตรงกลาง: คะแนน และ เกจวัดความสัมพันธ์
        self.mid_frame = tk.Frame(self, bg=COLOR_SURFACE)
        self.mid_frame.pack(side="left", expand=True)

        # Pill badge สำหรับคะแนน
        score_pill = tk.Frame(self.mid_frame, bg=COLOR_SURFACE_LIGHT, padx=8, pady=2, highlightbackground=COLOR_BORDER, highlightthickness=1)
        score_pill.pack(side="left", padx=8)

        self.lbl_score = tk.Label(score_pill, text="🏆 0 คะแนน", font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT)
        self.lbl_score.pack()

        # แถบแสดงความสัมพันธ์แบบ Visual Bar
        rel_pill = tk.Frame(self.mid_frame, bg=COLOR_SURFACE_LIGHT, padx=8, pady=2, highlightbackground=COLOR_BORDER, highlightthickness=1)
        rel_pill.pack(side="left", padx=8)

        self.lbl_rel = tk.Label(rel_pill, text="❤️ สัมพันธ์: 50/100 [█████░░░░░]", font=FONT_BODY_BOLD, fg="#f472b6", bg=COLOR_SURFACE_LIGHT)
        self.lbl_rel.pack()

        # ข้อมูลฝั่งขวา: ปุ่มบันทึก, ประวัติบทสนทนา & เมนู
        self.right_frame = tk.Frame(self, bg=COLOR_SURFACE)
        self.right_frame.pack(side="right", padx=14, pady=5)

        if on_log_click:
            self.btn_log = StyledButton(
                self.right_frame, text="📜 ประวัติ (L)",
                bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
                font=FONT_SMALL, padx=8, pady=2, command=on_log_click
            )
            self.btn_log.pack(side="left", padx=3)

        if on_save_click:
            self.btn_save = StyledButton(
                self.right_frame, text="💾 บันทึกเกม (S)",
                bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_GREEN, hover_fg=COLOR_TEXT_MAIN,
                font=FONT_SMALL, padx=8, pady=2, command=on_save_click
            )
            self.btn_save.pack(side="left", padx=3)

        if on_menu_click:
            self.btn_menu = StyledButton(
                self.right_frame, text="🏠 หน้าหลัก",
                bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_RED, hover_fg=COLOR_TEXT_MAIN,
                font=FONT_SMALL, padx=8, pady=2, command=on_menu_click
            )
            self.btn_menu.pack(side="left", padx=3)

    def update_status(self, player_name, scene_title, score, relationship):
        self.lbl_player.config(text=f"👤 {player_name}")
        self.lbl_scene.config(text=f"📍 {scene_title}")
        self.lbl_score.config(text=f"🏆 {score} คะแนน")
        
        # คำนวณเกจความสัมพันธ์แบบ 10 ส่วน
        rel_clamped = max(0, min(100, relationship))
        filled_bars = int(round(rel_clamped / 10))
        empty_bars = 10 - filled_bars
        bar_visual = "█" * filled_bars + "░" * empty_bars
        self.lbl_rel.config(text=f"❤️ สัมพันธ์: {rel_clamped}/100 [{bar_visual}]")


class DialogueBox(tk.Frame):
    """
    กล่องบทสนทนาสไตล์ Visual Novel ระดับมืออาชีพ
    - รองรับ Typewriter Effect + เสียงพิมพ์ดีด (Typewriter SFX)
    - คลิกหรือกด Space/Enter เพื่อเร่งข้อความให้เต็ม หรือเลื่อนไปบทต่อไป
    - มีลูกศรกระพริบแจ้งเตือนเมื่อพิมพ์เสร็จ
    - มีระบบจัดเก็บและเปิดดูประวัติบทสนทนาย้อนหลัง (Backlog / Dialogue Log)
    - มีโหมดเล่นอัตโนมัติ (Auto-Play) และเปิด/ปิดเสียงเอฟเฟกต์ (Mute Toggle)
    """
    global_dialogue_log = []

    def __init__(self, parent, on_next=None):
        super().__init__(parent, bg=COLOR_SURFACE, bd=2, relief="solid")
        self.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.on_next = on_next

        # ตัวแปรสถานะ Typewriter
        self._full_text = ""
        self._char_index = 0
        self._is_typing = False
        self._type_after_id = None
        self._type_speed_ms = _global_text_speed_ms

        # ส่วนหัวชื่อตัวละคร (Speaker Badge Pill)
        self.top_bar = tk.Frame(self, bg=COLOR_SURFACE)
        self.top_bar.pack(fill="x", padx=14, pady=(6, 0))

        self.speaker_pill = tk.Frame(
            self.top_bar, bg=COLOR_SURFACE_LIGHT, padx=10, pady=2,
            highlightbackground=COLOR_ACCENT, highlightthickness=1
        )
        self.speaker_pill.pack(side="left")

        self.lbl_speaker = tk.Label(
            self.speaker_pill, text="ตัวละคร", font=FONT_SPEAKER,
            fg=COLOR_ACCENT, bg=COLOR_SURFACE_LIGHT
        )
        self.lbl_speaker.pack(side="left")

        # ปุ่มฟังก์ชันด่วน (Sound, History Log) ฝั่งขวาบนของกล่องบทสนทนา
        self.quick_tools = tk.Frame(self.top_bar, bg=COLOR_SURFACE)
        self.quick_tools.pack(side="right")

        sound_icon = "🔊 เสียง: เปิด" if is_sound_enabled() else "🔇 เสียง: ปิด"
        self.btn_sound = StyledButton(
            self.quick_tools, text=sound_icon, font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MUTED,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=7, pady=1, command=self.toggle_sound
        )
        self.btn_sound.pack(side="left", padx=3)

        self.btn_history = StyledButton(
            self.quick_tools, text="📜 ประวัติ", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MUTED,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=7, pady=1, command=self.open_history_log
        )
        self.btn_history.pack(side="left", padx=3)

        # กล่องเนื้อหาบทสนทนา
        self.content_frame = tk.Frame(self, bg=COLOR_SURFACE)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(6, 4))

        self.lbl_text = tk.Label(
            self.content_frame, text="", font=FONT_DIALOGUE,
            fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE,
            justify="left", anchor="nw", wraplength=920
        )
        self.lbl_text.pack(fill="both", expand=True)

        # แถบปุ่มควบคุมด้านล่างขวา พร้อมลูกศรแจ้งสถานะ
        self.action_bar = tk.Frame(self, bg=COLOR_SURFACE)
        self.action_bar.pack(fill="x", padx=14, pady=(0, 6))

        # สัญลักษณ์ลูกศรแจ้งเตือนพร้อมไปต่อ (Blinking Arrow)
        self.lbl_indicator = tk.Label(
            self.action_bar, text="▼", font=("Segoe UI", 11, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_SURFACE
        )
        self.lbl_indicator.pack(side="right", padx=(6, 0))
        self._indicator_visible = True
        self._blink_after_id = None

        self.btn_next = StyledButton(
            self.action_bar, text="ถัดไป ➔  [Space]", font=FONT_BODY_BOLD,
            bg=COLOR_ACCENT, fg=COLOR_BG, hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=16, pady=3, command=self._handle_user_advance
        )
        self.btn_next.pack(side="right")

        # ผูกคลิกเมาส์ที่กล่องข้อความเพื่อเลื่อนไปข้างหน้าได้
        self.bind("<Button-1>", lambda e: self._handle_user_advance())
        self.lbl_text.bind("<Button-1>", lambda e: self._handle_user_advance())
        self.content_frame.bind("<Button-1>", lambda e: self._handle_user_advance())

        # ผูกปุ่มคีย์บอร์ด Space / Return บนหน้าต่างหลัก
        parent_toplevel = self.winfo_toplevel()
        parent_toplevel.bind("<space>", lambda e: self._handle_user_advance())
        parent_toplevel.bind("<Return>", lambda e: self._handle_user_advance())
        parent_toplevel.bind("<Right>", lambda e: self._handle_user_advance())
        parent_toplevel.bind("<Key-l>", lambda e: self.open_history_log())
        parent_toplevel.bind("<Key-L>", lambda e: self.open_history_log())

        self._start_blinking()

    def _start_blinking(self):
        """ทำให้สัญลักษณ์ลูกศรกระพริบเมื่อพร้อมไปต่อ"""
        if self._is_typing:
            self.lbl_indicator.config(fg=COLOR_SURFACE)
        else:
            current_fg = self.lbl_indicator.cget("fg")
            next_fg = COLOR_ACCENT if current_fg == COLOR_SURFACE else COLOR_SURFACE
            self.lbl_indicator.config(fg=next_fg)
        
        self._blink_after_id = self.after(550, self._start_blinking)

    def toggle_sound(self):
        """สลับเปิด/ปิดเสียงเอฟเฟกต์"""
        is_on = toggle_global_sound()
        self.btn_sound.config(text="🔊 เสียง: เปิด" if is_on else "🔇 เสียง: ปิด")
        if is_on:
            play_sfx(ADVANCE_SOUND)

    def _handle_user_advance(self):
        """
        พฤติกรรมสองจังหวะ (Two-Phase Advance UX):
        1. หากกำลังพิมพ์อยู่ -> แสดงข้อความให้ครบเต็มประโยคทันที
        2. หากข้อความเต็มแล้ว -> เล่นเสียงคลิกแล้วเลื่อนไปยังประโยคถัดไป
        """
        if self._is_typing:
            self._skip_to_full_text()
        else:
            play_sfx(ADVANCE_SOUND)
            if self.on_next:
                self.on_next()

    def _skip_to_full_text(self):
        """เร่งข้อความให้ปรากฏครบทั้งประโยคทันที"""
        if self._type_after_id:
            self.after_cancel(self._type_after_id)
            self._type_after_id = None
        self._is_typing = False
        self.lbl_text.config(text=self._full_text)
        self.lbl_indicator.config(fg=COLOR_ACCENT)

    def _type_step(self):
        """ขั้นตอน Typewriter สตรีมตัวอักษรทีละตัวพร้อมเสียงพิมพ์ดีด"""
        self._type_speed_ms = _global_text_speed_ms
        if self._char_index < len(self._full_text):
            self._char_index += 1
            self.lbl_text.config(text=self._full_text[:self._char_index])
            
            # เล่นเสียงพิมพ์ดีดทุกๆ 2 ตัวอักษร (ยกเว้นเว้นวรรค)
            cur_char = self._full_text[self._char_index - 1]
            if self._char_index % 2 == 0 and cur_char not in (" ", "\n", "\t"):
                play_sfx(TYPEWRITER_SOUND)
                
            self._type_after_id = self.after(self._type_speed_ms, self._type_step)
        else:
            self._is_typing = False
            self.lbl_indicator.config(fg=COLOR_ACCENT)

    def show_choices(self, choices, on_select):
        """
        แสดงตัวเลือกตอบโต้ในกล่องบทสนทนา (Interactive Dialogue Choices)
        choices: รายการ tuple (ข้อความ, ค่าที่จะส่งกลับ) หรือ (ข้อความ, callback)
        """
        self.clear_choices()
        self.btn_next.pack_forget()
        self.lbl_indicator.config(fg=COLOR_SURFACE)

        self._choices_frame = tk.Frame(self.content_frame, bg=COLOR_SURFACE)
        self._choices_frame.pack(fill="x", pady=(6, 2))

        for item in choices:
            if len(item) == 2:
                txt, val = item
            else:
                txt, val = item[0], item[1]

            btn = StyledButton(
                self._choices_frame, text=f"💬 {txt}", font=FONT_BODY_BOLD,
                bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
                justify="left", anchor="w", padx=12, pady=5,
                command=lambda v=val: self._select_choice(v, on_select)
            )
            btn.pack(fill="x", pady=2)

    def _select_choice(self, val, on_select):
        play_sfx(ADVANCE_SOUND)
        self.clear_choices()
        if on_select:
            on_select(val)

    def clear_choices(self):
        if hasattr(self, "_choices_frame") and self._choices_frame:
            try:
                self._choices_frame.destroy()
            except Exception:
                pass
            self._choices_frame = None

    def set_dialogue(self, speaker, text, speaker_color=COLOR_ACCENT, show_next_btn=True):
        """ตั้งค่าข้อความและเริ่มเอฟเฟกต์ Typewriter พร้อมบันทึกประวัติบทสนทนา"""
        self.clear_choices()
        if self._type_after_id:
            self.after_cancel(self._type_after_id)
            self._type_after_id = None

        self.global_dialogue_log.append({
            "speaker": speaker,
            "text": text,
            "color": speaker_color
        })

        self.speaker_pill.config(highlightbackground=speaker_color)
        self.lbl_speaker.config(text=f" 💬 {speaker} ", fg=speaker_color)

        self._full_text = text
        self._char_index = 0
        self._is_typing = True
        self.lbl_indicator.config(fg=COLOR_SURFACE)
        self.lbl_text.config(text="")

        if show_next_btn:
            self.btn_next.pack(side="right")
        else:
            self.btn_next.pack_forget()

        self._type_step()

    def open_history_log(self):
        """เปิดหน้าต่างแสดงประวัติบทสนทนาย้อนหลัง (Backlog Modal)"""
        top = tk.Toplevel(self)
        top.title("📜 ประวัติบทสนทนาย้อนหลัง (Dialogue History)")
        top.configure(bg=COLOR_BG)
        top.transient(self.winfo_toplevel())
        top.grab_set()
        center_modal(top, self, 740, 540)

        header = tk.Frame(top, bg=COLOR_SURFACE, pady=10, padx=16, bd=1, relief="solid")
        header.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        header.pack(fill="x")

        tk.Label(
            header, text="📜 ประวัติบทสนทนาทั้งหมดในฉากนี้",
            font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE
        ).pack(side="left")

        def _close_log(event=None):
            try:
                top.grab_release()
            except Exception:
                pass
            top.destroy()
            return "break"

        StyledButton(
            header, text="✕ ปิด (Esc)", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_RED, hover_fg=COLOR_TEXT_MAIN,
            padx=12, pady=3, command=_close_log
        ).pack(side="right")

        container = tk.Frame(top, bg=COLOR_BG, padx=15, pady=10)
        container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        txt = tk.Text(
            container, bg=COLOR_SURFACE, fg=COLOR_TEXT_MAIN, font=FONT_BODY,
            wrap="word", yscrollcommand=scrollbar.set, bd=0, padx=15, pady=15,
            highlightthickness=1, highlightbackground=COLOR_BORDER
        )
        txt.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=txt.yview)

        txt.tag_config("narrator", foreground=COLOR_TEXT_MUTED, font=FONT_BODY)
        txt.tag_config("tee", foreground=COLOR_ACCENT, font=FONT_BODY_BOLD)
        txt.tag_config("player", foreground="#34d399", font=FONT_BODY_BOLD)
        txt.tag_config("system", foreground=COLOR_PURPLE, font=FONT_BODY_BOLD)
        txt.tag_config("body", foreground=COLOR_TEXT_MAIN, font=FONT_BODY)

        for entry in self.global_dialogue_log:
            spk = entry["speaker"]
            msg = entry["text"]
            tag = "narrator"
            if "ที" in spk or "Tee" in spk:
                tag = "tee"
            elif "ระบบ" in spk:
                tag = "system"
            elif spk not in ["บรรยาย", ""]:
                tag = "player"

            txt.insert("end", f"[{spk}]: ", tag)
            txt.insert("end", f"{msg}\n\n", "body")

        txt.config(state="disabled")
        txt.see("end")

        top.bind("<Escape>", _close_log)


# -------------------------------------------------------------
# หน้าต่างเลือกช่องบันทึก / โหลดเกมแบบหลายช่อง (Multi-slot Save/Load Modal)
# -------------------------------------------------------------
def show_save_slots_dialog(parent, current_game_state, on_saved=None):
    """เปิดหน้าต่างเลือกช่องเพื่อบันทึกเกม (Save Slots Modal)"""
    top = tk.Toplevel(parent)
    top.title("💾 บันทึกเกม - เลือกช่องเซฟ")
    top.configure(bg=COLOR_BG)
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    center_modal(top, parent, 640, 520)

    header = tk.Frame(top, bg=COLOR_SURFACE, pady=10, padx=16, bd=1, relief="solid")
    header.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
    header.pack(fill="x")

    tk.Label(
        header, text="💾 เลือกช่องที่ต้องการบันทึกความคืบหน้า",
        font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE
    ).pack(side="left")

    def _close_save(event=None):
        try:
            top.grab_release()
        except Exception:
            pass
        top.destroy()
        return "break"

    StyledButton(
        header, text="✕ ยกเลิก (Esc)", font=FONT_SMALL,
        bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
        hover_bg=COLOR_RED, hover_fg=COLOR_TEXT_MAIN,
        padx=10, pady=3, command=_close_save
    ).pack(side="right")

    container = tk.Frame(top, bg=COLOR_BG, padx=16, pady=12)
    container.pack(fill="both", expand=True)

    slots_info = save_manager.get_all_slots_info()
    # ไม่รวม auto-save ในหน้าบันทึกด้วยตัวเอง ให้บันทึกใน slot1, slot2, slot3
    user_slots = [s for s in slots_info if s["slot_id"] != "auto"]

    def do_save(slot_id):
        save_manager.save_game(current_game_state, slot_id)
        play_sfx(ADVANCE_SOUND)
        messagebox.showinfo("บันทึกสำเร็จ", f"บันทึกความคืบหน้าลงใน '{slot_id.upper()}' เรียบร้อยแล้ว!")
        _close_save()
        if on_saved:
            on_saved(slot_id)

    for s in user_slots:
        card = tk.Frame(container, bg=COLOR_SURFACE, bd=1, relief="solid", highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="x", pady=6, ipady=4)

        top_row = tk.Frame(card, bg=COLOR_SURFACE)
        top_row.pack(fill="x", padx=12, pady=(6, 2))

        tk.Label(top_row, text=f"📁 {s['slot_name']}", font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(side="left")
        time_text = s['saved_at'] if not s['is_empty'] else "ว่าง"
        tk.Label(top_row, text=f"🕒 {time_text}", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE).pack(side="right")

        mid_row = tk.Frame(card, bg=COLOR_SURFACE)
        mid_row.pack(fill="x", padx=12, pady=2)

        if s["is_empty"]:
            tk.Label(mid_row, text="• ช่องว่าง ยังไม่มีข้อมูลบันทึก", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE).pack(side="left")
            btn_text = "💾 บันทึกในช่องนี้"
        else:
            txt_info = f"👤 {s['player_name']} | 📍 {s['scene_title']}\n🏆 คะแนน: {s['score']} | ❤️ สัมพันธ์: {s['relationship']}/100"
            tk.Label(mid_row, text=txt_info, font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, justify="left").pack(side="left")
            btn_text = "💾 บันทึกทับช่องนี้"

        StyledButton(
            card, text=btn_text, font=FONT_BODY_BOLD,
            bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=16, pady=4, command=lambda sid=s["slot_id"]: do_save(sid)
        ).pack(side="right", padx=12, pady=(0, 6))

    top.bind("<Escape>", _close_save)


def show_load_slots_dialog(parent, on_loaded=None):
    """เปิดหน้าต่างเลือกช่องเพื่อโหลดเกม (Load Slots Modal)"""
    top = tk.Toplevel(parent)
    top.title("📁 โหลดเซฟ - เลือกช่องที่ต้องการเล่นต่อ")
    top.configure(bg=COLOR_BG)
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    center_modal(top, parent, 660, 560)

    header = tk.Frame(top, bg=COLOR_SURFACE, pady=10, padx=16, bd=1, relief="solid")
    header.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
    header.pack(fill="x")

    tk.Label(
        header, text="📁 เลือกไฟล์เซฟเพื่อโหลดเล่นต่อ",
        font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE
    ).pack(side="left")

    def _close_load(event=None):
        try:
            top.grab_release()
        except Exception:
            pass
        top.destroy()
        return "break"

    StyledButton(
        header, text="✕ ยกเลิก (Esc)", font=FONT_SMALL,
        bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
        hover_bg=COLOR_RED, hover_fg=COLOR_TEXT_MAIN,
        padx=10, pady=3, command=_close_load
    ).pack(side="right")

    container = tk.Frame(top, bg=COLOR_BG, padx=16, pady=10)
    container.pack(fill="both", expand=True)

    def refresh_list():
        for w in container.winfo_children():
            w.destroy()

        slots_info = save_manager.get_all_slots_info()
        for s in slots_info:
            card = tk.Frame(container, bg=COLOR_SURFACE, bd=1, relief="solid", highlightbackground=COLOR_BORDER, highlightthickness=1)
            card.pack(fill="x", pady=5, ipady=3)

            top_row = tk.Frame(card, bg=COLOR_SURFACE)
            top_row.pack(fill="x", padx=12, pady=(5, 2))

            tk.Label(top_row, text=f"📁 {s['slot_name']}", font=FONT_BODY_BOLD, fg=COLOR_YELLOW if s["slot_id"]=="auto" else COLOR_ACCENT, bg=COLOR_SURFACE).pack(side="left")
            time_text = s['saved_at'] if not s['is_empty'] else "ว่าง"
            tk.Label(top_row, text=f"🕒 {time_text}", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE).pack(side="right")

            mid_row = tk.Frame(card, bg=COLOR_SURFACE)
            mid_row.pack(fill="x", padx=12, pady=2)

            if s["is_empty"]:
                tk.Label(mid_row, text="• ช่องว่าง ไม่มีข้อมูลเซฟ", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE).pack(side="left")
            else:
                txt_info = f"👤 ผู้เล่น: {s['player_name']} | 📍 {s['scene_title']}\n🏆 คะแนน: {s['score']} | ❤️ สัมพันธ์: {s['relationship']}/100"
                tk.Label(mid_row, text=txt_info, font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, justify="left").pack(side="left")

                btn_box = tk.Frame(card, bg=COLOR_SURFACE)
                btn_box.pack(side="right", padx=12, pady=(0, 6))

                StyledButton(
                    btn_box, text="🗑️ ลบ", font=FONT_SMALL,
                    bg=COLOR_SURFACE_LIGHT, fg=COLOR_RED, hover_bg=COLOR_RED_HOVER, hover_fg=COLOR_TEXT_MAIN,
                    padx=8, pady=3,
                    command=lambda sid=s["slot_id"]: do_delete(sid)
                ).pack(side="right", padx=(5, 0))

                StyledButton(
                    btn_box, text="▶ เล่นต่อ", font=FONT_BODY_BOLD,
                    bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
                    padx=14, pady=3,
                    command=lambda data=s["data"]: do_load(data)
                ).pack(side="right")

    def do_load(data):
        play_sfx(ADVANCE_SOUND)
        _close_load()
        if on_loaded:
            on_loaded(data)

    def do_delete(slot_id):
        if messagebox.askyesno("ยืนยัน", f"คุณต้องการลบข้อมูลเซฟใน {slot_id.upper()} ใช่หรือไม่?"):
            save_manager.delete_save(slot_id)
            refresh_list()

    refresh_list()
    top.bind("<Escape>", _close_load)


def show_knowledge_popup(parent, title, category, message, button_text="เข้าใจแล้ว", image_name=None, img_size=(260, 200)):
    """
    แสดงหน้าต่างป๊อปอัปให้ความรู้ทางการแพทย์และสุขภาพ พร้อมรูปภาพประกอบ (ถ้ามี)
    จัดแต่งตาม Design System สวยงาม โมเดิร์น พร้อมคีย์ลัด Esc / Enter เพื่อปิด
    """
    top = tk.Toplevel(parent)
    top.title(title)
    width = 720 if image_name else 620
    height = 540 if image_name else 460
    top.configure(bg=COLOR_BG)
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    center_modal(top, parent, width, height)

    card = tk.Frame(top, bg=COLOR_SURFACE, bd=2, relief="solid")
    card.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
    card.pack(fill="both", expand=True, padx=20, pady=20)

    pill = tk.Frame(card, bg=COLOR_SURFACE_LIGHT, padx=12, pady=4, highlightbackground=COLOR_YELLOW, highlightthickness=1)
    pill.pack(pady=(16, 6))

    tk.Label(
        pill, text=f"💡 เกร็ดความรู้: {category}",
        font=FONT_HEADING, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT
    ).pack()

    tk.Label(
        card, text=title,
        font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE
    ).pack(pady=(4, 12))

    body_container = tk.Frame(card, bg=COLOR_SURFACE)
    body_container.pack(fill="both", expand=True, padx=22, pady=6)

    if image_name:
        img = get_image(image_name, size=img_size)
        if img:
            lbl_img = tk.Label(body_container, image=img, bg=COLOR_SURFACE, bd=1, relief="ridge", highlightbackground=COLOR_BORDER, highlightthickness=1)
            lbl_img.image = img
            lbl_img.pack(side="left", padx=(0, 16))

    txt_frame = tk.Frame(body_container, bg=COLOR_SURFACE)
    txt_frame.pack(side="left", fill="both", expand=True)

    lbl_msg = tk.Label(
        txt_frame, text=message, font=FONT_BODY,
        fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE,
        justify="left", anchor="nw", wraplength=410 if image_name else 550
    )
    lbl_msg.pack(fill="both", expand=True)

    def _close_popup(event=None):
        try:
            top.grab_release()
        except Exception:
            pass
        top.destroy()
        return "break"

    btn_ok = StyledButton(
        card, text=f"{button_text} ➔ [Enter]", font=FONT_BODY_BOLD,
        bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
        padx=32, pady=8, command=_close_popup
    )
    btn_ok.pack(pady=16)

    top.bind("<Escape>", _close_popup)
    top.bind("<Return>", _close_popup)
    top.bind("<space>", _close_popup)


def show_moph_poster_modal(parent, initial_category_id=None):
    """
    หน้าต่างแสดงคู่มือยาสามัญประจำบ้านทางการฉบับเต็ม (Full Official Poster Viewer)
    อ้างอิงจากไฟล์เอกสารต้นฉบับ assets/long.pdf (กระทรวงสาธารณสุข)
    เป็นตัวเต็มตัวเดียวสำหรับดูโปสเตอร์พร้อมแถบลัด 11 กลุ่มยา
    """
    top = tk.Toplevel(parent)
    top.title("📋 คู่มือโปสเตอร์ยาสามัญประจำบ้าน (11 หมวดหมู่)")
    top.configure(bg=COLOR_BG)
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    center_modal(top, parent, 1060, 700)

    def _close_poster(event=None):
        try:
            top.grab_release()
        except Exception:
            pass
        top.destroy()
        return "break"

    # Top Header
    header = tk.Frame(top, bg=COLOR_SURFACE, pady=8, padx=16, bd=1, relief="solid")
    header.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
    header.pack(fill="x")

    title_box = tk.Frame(header, bg=COLOR_SURFACE)
    title_box.pack(side="left")

    tk.Label(
        title_box,
        text="📋 คู่มือโปสเตอร์: ตัวอย่างยาสามัญประจำบ้านและวิธีสังเกตสัญลักษณ์",
        font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE
    ).pack(anchor="w")

    tk.Label(
        title_box,
        text="ตัวอย่างรายการยา สรรพคุณ และสัญลักษณ์ที่ถูกต้องสำหรับร้านชำและตู้ยาหอพัก",
        font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE
    ).pack(anchor="w")

    StyledButton(
        header, text="✕ ปิด (Esc)", font=FONT_SMALL,
        bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
        hover_bg=COLOR_RED, hover_fg=COLOR_TEXT_MAIN,
        padx=14, pady=4, command=_close_poster
    ).pack(side="right")

    # Main Content Area (Single Unified Viewer)
    content_area = tk.Frame(top, bg=COLOR_BG)
    content_area.pack(fill="both", expand=True, padx=16, pady=8)

    split_frame = tk.Frame(content_area, bg=COLOR_BG)
    split_frame.pack(fill="both", expand=True)

    # Left: Quick Category Jump Navigation (11 groups + symbol)
    jump_panel = tk.Frame(split_frame, bg=COLOR_SURFACE, width=290, bd=1, relief="solid", padx=10, pady=10)
    jump_panel.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
    jump_panel.pack(side="left", fill="y", padx=(0, 10))
    jump_panel.pack_propagate(False)

    tk.Label(
        jump_panel, text="🎯 ลัดไปดูหมวดหมู่ยา (11 กลุ่ม)",
        font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE
    ).pack(anchor="w", pady=(0, 4))

    tk.Label(
        jump_panel, text="คลิกเพื่อเลื่อนไปยังกลุ่มยาในโปสเตอร์ทันที:",
        font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE, justify="left"
    ).pack(anchor="w", pady=(0, 8))

    jump_canvas = tk.Canvas(jump_panel, bg=COLOR_SURFACE, highlightthickness=0)
    jump_scroll = tk.Scrollbar(jump_panel, orient="vertical", command=jump_canvas.yview)
    jump_box = tk.Frame(jump_canvas, bg=COLOR_SURFACE)
    jump_box.bind("<Configure>", lambda e: jump_canvas.configure(scrollregion=jump_canvas.bbox("all")))
    jump_canvas.create_window((0, 0), window=jump_box, anchor="nw", width=250)
    jump_canvas.configure(yscrollcommand=jump_scroll.set)
    jump_canvas.pack(side="left", fill="both", expand=True)
    jump_scroll.pack(side="right", fill="y")

    # Right: Scrollable Full Poster Canvas
    poster_frame = tk.Frame(split_frame, bg=COLOR_SURFACE, bd=1, relief="solid")
    poster_frame.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
    poster_frame.pack(side="right", fill="both", expand=True)

    canvas_p = tk.Canvas(poster_frame, bg="#0d1b2a", highlightthickness=0)
    scroll_p = tk.Scrollbar(poster_frame, orient="vertical", command=canvas_p.yview)

    # Load high-resolution poster image (width ~660, height ~1640)
    poster_img = get_image("poster_display.png", (660, 1640))

    if poster_img:
        canvas_p.create_image(370, 10, anchor="n", image=poster_img)
        canvas_p.image_ref = poster_img
        canvas_p.configure(scrollregion=(0, 0, 740, 1660))
    else:
        canvas_p.create_text(370, 200, text="กำลังเตรียมไฟล์ภาพโปสเตอร์...", fill="white", font=FONT_HEADING)

    canvas_p.configure(yscrollcommand=scroll_p.set)
    canvas_p.pack(side="left", fill="both", expand=True)
    scroll_p.pack(side="right", fill="y")

    # Jump fractional positions in full poster
    jump_targets = [
        ("1. ปวดท้อง ท้องอืด เฟ้อ", 0.07, "stomach"),
        ("2. แก้ท้องเสีย (ORS)", 0.23, "ors"),
        ("3. บรรเทาปวด ลดไข้ (พารา)", 0.28, "fever"),
        ("4. ยาระบาย (มะขามแขก)", 0.36, "laxative"),
        ("5. แก้ไอ ขับเสมหะ", 0.47, "cough"),
        ("6. ยาดม/วิงเวียน/เมารถ", 0.57, "inhaler"),
        ("7. ยาโรคปากและลำคอ", 0.68, "mouth"),
        ("8. ยาโรคตา", 0.71, "eye"),
        ("9. ปวดกล้ามเนื้อ แมลงต่อย", 0.74, "muscle"),
        ("10. ใส่แผล ล้างแผลสด", 0.80, "wound"),
        ("11. ยาโรคผิวหนัง", 0.83, "skin"),
        ("⭐ ข้อสังเกตสัญลักษณ์ยา สธ.", 0.90, "notice")
    ]

    def jump_to_pos(fraction):
        canvas_p.yview_moveto(fraction)

    for label_text, frac, cat_key in jump_targets:
        b = StyledButton(
            jump_box, text=f"• {label_text}",
            font=(FONT_BODY[0], 9),
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            justify="left", anchor="w", padx=8, pady=4,
            command=lambda f=frac: jump_to_pos(f)
        )
        b.pack(fill="x", pady=2)

    # Mousewheel scroll binding
    def _on_mousewheel(event):
        if canvas_p.winfo_exists():
            canvas_p.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas_p.bind("<MouseWheel>", _on_mousewheel)

    # Bottom Notice Bar
    notice_bar = tk.Frame(top, bg=COLOR_SURFACE, pady=6, padx=16, bd=1, relief="solid")
    notice_bar.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
    notice_bar.pack(fill="x", side="bottom")

    badge = tk.Frame(notice_bar, bg="#065f46", padx=8, pady=2, highlightbackground=COLOR_GREEN, highlightthickness=1)
    badge.pack(side="left", padx=(0, 10))
    tk.Label(badge, text="ยาสามัญประจำบ้าน", font=FONT_BODY_BOLD, fg="white", bg="#065f46").pack()

    tk.Label(
        notice_bar,
        text="สังเกตสัญลักษณ์ [ยาสามัญประจำบ้าน] สีเขียว ที่ฉลากยา | ยาใช้ภายนอกมี [กรอบสีแดง] ห้ามรับประทาน",
        font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE
    ).pack(side="left")
    top.bind("<Escape>", _close_poster)

    # Initial scroll jump if category specified
    if initial_category_id:
        for _, frac, cat_key in jump_targets:
            if cat_key == initial_category_id or initial_category_id in cat_key:
                top.after(50, lambda f=frac: jump_to_pos(f))
                break

    return top

