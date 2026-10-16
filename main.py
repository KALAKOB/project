"""
Pharmacy Afterlife - Educational Visual Novel Game
Main Entry Point with Full UI and Visual Enhancements
"""

import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ui_theme import (
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_LIGHT, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_GREEN,
    COLOR_GREEN_HOVER, COLOR_RED, COLOR_RED_HOVER, COLOR_YELLOW, COLOR_BORDER,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_BODY_BOLD,
    FONT_SMALL, StyledButton, get_image, BASE_DIR, PHOTO_DIR
)
import save_manager
from vn_widgets import (
    show_load_slots_dialog, center_modal,
    set_global_volume, get_global_volume, toggle_global_sound, is_sound_enabled, play_sfx,
    set_global_text_speed, get_global_text_speed, ADVANCE_SOUND, show_moph_poster_modal
)
from data import DRUG_STORAGE_KNOWLEDGE
from scene1_medicine import Scene1MedicineFrame
from scene2_burn_firstaid import Scene2BurnFirstAidFrame
from scene3_mohpromt import Scene3MohpromtFrame

# ข้อมูลสมาชิกคณะผู้จัดทำโครงการ (In-Ma-Nee-Ma Team)
MEMBERS_DATA = [
    {
        "id": "690813048",
        "name": "นางสาวปรินทร คุณกิตติ",
        "nickname": "Miu",
        "position": "Game Logic & Scenario Developer",
        "duty": (
            "• เขียนและดูแลตรรกะการทำงานของเกม (Game Logic) ทั้งหมด\n"
            "• ออกแบบและพัฒนาเงื่อนไขการเล่น สถานการณ์จำลอง และบทสนทนาภายในเกม\n"
            "• ออกแบบมินิเกมฉากที่ 1: การตรวจสอบตู้ยาสามัญประจำบ้าน คัดแยกยาเสื่อมคุณภาพ และช้อปปิ้งงบ 1,000 บาท\n"
            "• ออกแบบมินิเกมฉากที่ 2: แบบทดสอบสถานการณ์การปฐมพยาบาลแผลน้ำร้อนลวกตามมาตรฐาน รพ.ศิริราช\n"
            "• ออกแบบมินิเกมฉากที่ 3: ระบบจำลองการนัดหมายแพทย์ล่วงหน้าผ่านแอปพลิเคชันหมอพร้อม"
        ),
        "photo_file": "690813048.png"
    },
    {
        "id": "690813058",
        "name": "นางสาวสรชา ทุกข์จาก",
        "nickname": "In",
        "position": "UI & Visual Novel Components",
        "duty": (
            "• ออกแบบและพัฒนาส่วนติดต่อผู้ใช้ (UI / UX Pro Max) สไตล์ Dark Modern Cyber-Clinic\n"
            "• พัฒนาคอมโพเนนต์ Visual Novel: กล่องบทสนทนาพิมพ์ดีด (DialogueBox) พร้อมเสียง Typewriter\n"
            "• พัฒนาแถบสถานะผู้เล่นด้านบน (TopStatusBar) แสดงคะแนนและเกจความสัมพันธ์แบบเรียลไทม์\n"
            "• ออกแบบปุ่มกดและแอนิเมชันปุ่ม (StyledButton) พร้อมระบบคีย์บอร์ดลัด (Hotkeys & Escape)\n"
            "• พัฒนาระบบหน้าต่างป๊อปอัปให้ความรู้ (Knowledge Popup) และคู่มือการใช้งานเกม (guide.txt)"
        ),
        "photo_file": "690813058.png"
    },
    {
        "id": "690813067",
        "name": "นางสาวยสุตมา ค่ำชู",
        "nickname": "Khim",
        "position": "Game Engine",
        "duty": (
            "• พัฒนาและดูแลโครงสร้างสถาปัตยกรรมหลักของเกม (Core Game Engine & Architecture)\n"
            "• พัฒนาระบบบันทึกและโหลดสถานะเกมแบบหลายช่องเซฟ (Multi-slot Save/Load System)\n"
            "• พัฒนาระบบจัดการเสียงประกอบเกม (Sound & Audio Engine) แบบ Asynchronous ผ่าน winsound\n"
            "• ดูแลระบบแคชรูปภาพประสิทธิภาพสูง (Image Cache Engine) และการแสดงผลตัวละครโปร่งใส (Alpha Sprites)\n"
            "• ควบคุมการเปลี่ยนผ่านฉาก (Scene Transitions) และความเสถียรของแอปพลิเคชัน"
        ),
        "photo_file": "690813067.png"
    }
]

class PharmacyAfterlifeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stay Alive, Tee!: เมทข้าต้องรอด!")
        self.root.geometry("1024x720")
        self.root.minsize(1000, 680)
        self.root.configure(bg=COLOR_BG)

        # จัดการปุ่ม Esc แบบมีลำดับชั้นและตรวจสอบบริบท (Context-Aware Escape)
        self.root.bind("<Escape>", self.handle_escape_key)

        # ตัวแปรสถานะเกมปัจจุบัน
        self.game_state = save_manager.DEFAULT_STATE.copy()

        # สร้างเฟรมหลักสำหรับสลับหน้า
        self.container = tk.Frame(self.root, bg=COLOR_BG)
        self.container.pack(fill="both", expand=True)

        # หน้าเมนูต่างๆ
        self.menu_frame = tk.Frame(self.container, bg=COLOR_BG)
        self.options_frame = tk.Frame(self.container, bg=COLOR_BG)
        self.credits_frame = tk.Frame(self.container, bg=COLOR_BG)
        self.member_menu_frame = tk.Frame(self.container, bg=COLOR_BG)
        self.member_detail_frame = tk.Frame(self.container, bg=COLOR_BG)
        self.guide_frame = tk.Frame(self.container, bg=COLOR_BG)
        self.current_scene_frame = None
        self.current_page_frame = self.menu_frame

        self.setup_menu_page()
        self.setup_options_page()
        self.setup_credits_page()
        self.setup_member_menu_page()
        self.setup_guide_page()

        self.show_page(self.menu_frame)

    def show_page(self, frame):
        """สลับหน้าจอหลัก"""
        if self.current_scene_frame and frame == self.menu_frame:
            self.current_scene_frame.destroy()
            self.current_scene_frame = None

        self.current_page_frame = frame
        frame.place(x=0, y=0, relwidth=1, relheight=1)
        frame.tkraise()

    def handle_escape_key(self, event=None):
        """
        จัดการปุ่ม Esc อย่างชาญฉลาดตามบริบทของผู้เล่น:
        1. หากมีหน้าต่าง Popup / Toplevel เปิดอยู่ -> ปิดหน้าต่างบนสุด
        2. หากอยู่ในหน้า User Guide -> ย้อนกลับสู่หน้า Options
        3. หากอยู่ในหน้ารายละเอียดสมาชิก -> ย้อนกลับสู่หน้าเมนูสมาชิก
        4. หากอยู่ในหน้า Options, Credits หรือ Member Menu -> ย้อนกลับสู่เมนูหลัก
        5. หากกำลังเล่นอยู่ในฉากเกม -> ถามยืนยันเพื่อหยุดพักกลับสู่เมนูหลัก (พร้อม Auto-Save)
        6. หากอยู่ที่หน้าเมนูหลักอยู่แล้ว -> ถามยืนยันออกจากโปรแกรม
        """
        # 1. ปิดหน้าต่าง Toplevel หรือ Popup ที่เปิดอยู่ด้านบนสุดก่อน
        toplevels = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel) and w.winfo_exists()]
        if toplevels:
            top = toplevels[-1]
            try:
                top.grab_release()
            except Exception:
                pass
            top.destroy()
            return "break"

        cur_frame = getattr(self, "current_page_frame", None)

        # 2. ถ้าอยู่ในหน้า User Guide ให้ย้อนกลับสู่หน้า Options
        if cur_frame == self.guide_frame:
            self.show_page(self.options_frame)
            return "break"

        # 3. ถ้าอยู่ในหน้ารายละเอียดสมาชิก ให้ย้อนกลับสู่หน้าเลือกสมาชิก
        if cur_frame == self.member_detail_frame:
            self.show_page(self.member_menu_frame)
            return "break"

        # 4. ถ้าอยู่ในหน้า Options, Credits หรือ Member Menu ให้ย้อนกลับสู่เมนูหลัก
        if cur_frame in [self.options_frame, self.credits_frame, self.member_menu_frame]:
            self.show_page(self.menu_frame)
            return "break"

        # 5. ถ้ากำลังเล่นฉากในเกม (Scene 1, 2, 3) ให้ถามยืนยันหยุดพักและกลับสู่เมนูหลัก (พร้อม Auto-Save)
        if self.current_scene_frame and cur_frame == self.current_scene_frame:
            if messagebox.askyesno("กลับสู่เมนูหลัก", "คุณต้องการหยุดพักและกลับสู่หน้าเมนูหลักหรือไม่?\n(ระบบจะทำการบันทึกเกมอัตโนมัติ)"):
                save_manager.save_game(self.game_state, "auto")
                self.return_to_menu()
            return "break"

        # 6. หากอยู่ที่หน้าเมนูหลักอยู่แล้ว ให้ถามยืนยันออกจากเกม
        self.confirm_exit()
        return "break"

    def confirm_exit(self):
        if messagebox.askyesno("ออกจากเกม", "คุณต้องการออกจากเกมใช่หรือไม่?"):
            self.root.destroy()

    # -------------------------------------------------------------
    # 1. หน้าจอเมนูหลัก (MAIN MENU)
    # -------------------------------------------------------------
    def setup_menu_page(self):
        for w in self.menu_frame.winfo_children():
            w.destroy()

        # Canvas พื้นหลังรูปภาพ พร้อมตัวปรับขนาดอัตโนมัติ (Responsive BG)
        bg_canvas = tk.Canvas(self.menu_frame, bg=COLOR_BG, highlightthickness=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        def _on_menu_bg_resize(event):
            if event.width > 100 and event.height > 100:
                new_bg = get_image("bg_title.jpg", (event.width, event.height))
                if new_bg:
                    bg_canvas.delete("all")
                    bg_canvas.create_image(0, 0, anchor="nw", image=new_bg)
                    bg_canvas.image = new_bg
        bg_canvas.bind("<Configure>", _on_menu_bg_resize)

        # แผงเมนูด้านซ้าย (จัดกึ่งกลางแนวตั้ง พอดีหน้าจอ ไม่ล้น)
        panel = tk.Frame(self.menu_frame, bg=COLOR_BG, bd=2, relief="solid")
        panel.config(highlightbackground=COLOR_BORDER, highlightthickness=2)
        panel.place(relx=0.05, rely=0.5, anchor="w", width=440, height=590)

        # ชื่อเกม
        title_box = tk.Frame(panel, bg=COLOR_BG)
        title_box.pack(pady=(14, 6), padx=15)

        tk.Label(
            title_box,
            text="STAY ALIVE, TEE!",
            font=("Segoe UI", 26, "bold"),
            fg=COLOR_ACCENT,
            bg=COLOR_BG,
            justify="center"
        ).pack()

        tk.Label(
            title_box,
            text="~ เมทข้าต้องรอด! ~",
            font=FONT_HEADING,
            fg=COLOR_YELLOW,
            bg=COLOR_BG
        ).pack(pady=(2, 3))

        tk.Label(
            title_box,
            text="เกมจำลองสถานการณ์เพื่อการเรียนรู้เรื่องยา\nการปฐมพยาบาล และระบบบริการสาธารณสุข",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_BG,
            justify="center"
        ).pack(pady=(0, 4))

        # แผงปุ่มเมนู
        btn_box = tk.Frame(panel, bg=COLOR_BG)
        btn_box.pack(fill="x", padx=30, pady=(4, 10))

        has_saved_data = save_manager.has_save()

        self.btn_continue = StyledButton(
            btn_box,
            text="▶ เล่นต่อ (CONTINUE)",
            font=FONT_BODY_BOLD,
            bg="#0369a1" if has_saved_data else COLOR_SURFACE,
            fg=COLOR_TEXT_MAIN if has_saved_data else COLOR_TEXT_MUTED,
            hover_bg=COLOR_ACCENT if has_saved_data else COLOR_SURFACE,
            hover_fg=COLOR_BG if has_saved_data else COLOR_TEXT_MUTED,
            state="normal" if has_saved_data else "disabled",
            padx=12, pady=5,
            command=self.action_continue
        )
        self.btn_continue.pack(fill="x", pady=4)

        self.btn_new = StyledButton(
            btn_box,
            text="✨ เริ่มเกมใหม่ (NEW GAME)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT,
            fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT,
            hover_fg=COLOR_BG,
            padx=12, pady=5,
            command=self.action_new_game_prompt
        )
        self.btn_new.pack(fill="x", pady=4)

        self.btn_load = StyledButton(
            btn_box,
            text="📁 โหลดเซฟ (LOAD GAME)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT,
            fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT,
            hover_fg=COLOR_BG,
            padx=12, pady=5,
            command=self.action_load_game
        )
        self.btn_load.pack(fill="x", pady=4)

        self.btn_options = StyledButton(
            btn_box,
            text="⚙️ ตั้งค่า (OPTIONS)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT,
            fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT,
            hover_fg=COLOR_BG,
            padx=12, pady=5,
            command=self.open_options_page
        )
        self.btn_options.pack(fill="x", pady=4)

        self.btn_member = StyledButton(
            btn_box,
            text="👥 สมาชิก (MEMBER)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT,
            fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT,
            hover_fg=COLOR_BG,
            padx=12, pady=5,
            command=self.open_member_menu
        )
        self.btn_member.pack(fill="x", pady=4)

        self.btn_credits = StyledButton(
            btn_box,
            text="ℹ️ เกี่ยวกับเกม (CREDITS)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT,
            fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT,
            hover_fg=COLOR_BG,
            padx=12, pady=5,
            command=lambda: self.show_page(self.credits_frame)
        )
        self.btn_credits.pack(fill="x", pady=4)

        self.btn_quit = StyledButton(
            btn_box,
            text="🚪 ออกจากเกม (QUIT)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT,
            fg=COLOR_RED,
            hover_bg=COLOR_RED_HOVER,
            hover_fg=COLOR_TEXT_MAIN,
            padx=12, pady=5,
            command=self.confirm_exit
        )
        self.btn_quit.pack(fill="x", pady=4)

        # กรอบแนะนำตัวละครด้านขวา (Tee preview - จัดกึ่งกลางแนวตั้ง พอดีจอ)
        right_panel = tk.Frame(self.menu_frame, bg=COLOR_SURFACE, bd=2, relief="solid")
        right_panel.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        right_panel.place(relx=0.52, rely=0.5, anchor="w", width=440, height=590)

        # Pill header
        header_pill = tk.Frame(right_panel, bg=COLOR_SURFACE_LIGHT, padx=12, pady=3, highlightbackground=COLOR_BORDER, highlightthickness=1)
        header_pill.pack(pady=(12, 4))

        tk.Label(
            header_pill, text="👤 ตัวละครหลัก / รูมเมทของคุณ",
            font=FONT_HEADING, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT
        ).pack()

        # กล่องคำพูดของตัวละคร (Speech bubble)
        speech_box = tk.Frame(right_panel, bg=COLOR_SURFACE_LIGHT, padx=12, pady=4, highlightbackground=COLOR_ACCENT, highlightthickness=1)
        speech_box.pack(fill="x", padx=20, pady=(2, 4))

        self.lbl_tee_quote = tk.Label(
            speech_box,
            text='💬 "มีชีวิตรอดถึงปีสองก็บุญแล้ว..."',
            font=FONT_BODY, fg=COLOR_ACCENT, bg=COLOR_SURFACE_LIGHT, wraplength=360, justify="center"
        )
        self.lbl_tee_quote.pack()

        # รูปตัวละครโปร่งใสชุดใหม่ (คลิกเปลี่ยนอารมณ์ได้ 4 แบบ)
        self.tee_poses = [
            ("tee_sleepy.png", '💬 "โมเดลยังไม่เสร็จเลยอ่ะแก..."', "โหมด: ซึม/ง่วง"),
            ("tee_surprise.png", '💬 "เจ๋งแจ๋วคับเพื่อน! รอดตายแล้ว!"', "โหมด: ตื่นเต้น/ดีใจ"),
            ("tee_burn.png", '💬 "โอ๊ยยย! ร้อนๆๆ น้ำร้อนลวกมือ!"', "โหมด: โดนน้ำร้อนลวก"),
            ("tee_bandage.png", '💬 "พันแผลเรียบร้อย ปลอดภัยหายห่วง"', "โหมด: ปฐมพยาบาลแล้ว")
        ]
        self.current_pose_idx = 0

        tee_img = get_image(self.tee_poses[0][0], (214, 328))
        self.lbl_tee = tk.Label(right_panel, image=tee_img, bg=COLOR_SURFACE, cursor="hand2")
        self.lbl_tee.image = tee_img
        self.lbl_tee.pack(pady=2)

        def cycle_tee_pose(event=None):
            self.current_pose_idx = (self.current_pose_idx + 1) % len(self.tee_poses)
            pose_data = self.tee_poses[self.current_pose_idx]
            pose_file = pose_data[0]
            quote = pose_data[1]
            mode_name = pose_data[2] if len(pose_data) > 2 else ""

            new_img = get_image(pose_file, (214, 328))
            if new_img:
                self.lbl_tee.configure(image=new_img)
                self.lbl_tee.image = new_img
            self.lbl_tee_quote.config(text=quote)
            if mode_name:
                self.lbl_tee_hint.config(text=f"👆 คลิกเพื่อเปลี่ยนอารมณ์ ({mode_name})")
            else:
                self.lbl_tee_hint.config(text="👆 คลิกเพื่อเปลี่ยนอารมณ์")

        self.lbl_tee.bind("<Button-1>", cycle_tee_pose)
        self.lbl_tee_quote.bind("<Button-1>", cycle_tee_pose)

        self.lbl_tee_hint = tk.Label(
            right_panel, text="👆 คลิกตัวละครเพื่อทักทาย / เปลี่ยนอารมณ์",
            font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE
        )
        self.lbl_tee_hint.pack(pady=(1, 2))

        bio_box = tk.Frame(right_panel, bg=COLOR_SURFACE_LIGHT, padx=12, pady=6, highlightbackground=COLOR_BORDER, highlightthickness=1)
        bio_box.pack(fill="x", padx=18, pady=(2, 8))
        tk.Label(
            bio_box, text="ที (Tee) | คณะสถาปัตยกรรมศาสตร์ ปี 2\nนิสัย: นอนวันละ 3 ชั่วโมง วันๆอยู่แต่กับโม",
            font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, justify="center"
        ).pack()

    # -------------------------------------------------------------
    # จัดการการเริ่มเกมใหม่ / โหลดเกม
    # -------------------------------------------------------------
    def action_new_game_prompt(self):
        top = tk.Toplevel(self.root)
        top.title("สร้างโปรไฟล์ผู้เล่นใหม่")
        top.configure(bg=COLOR_BG)
        top.transient(self.root)
        top.grab_set()
        center_modal(top, self.root, 520, 420)

        card = tk.Frame(top, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(card, text="🎮 ยินดีต้อนรับสู่อพาร์ตเมนต์นักศึกษา", font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE).pack(pady=(15, 5))

        desc = (
            "• ตัวคุณ: นิสัยหัวร้อน ปากร้ายใจดี ตัวตบมุก คอยแก้ปัญหาให้เมท\n"
            "• เมทของคุณ (ที): เด็กสถาปัตย์นอนน้อย ซุ่มซ่ามแต่จริงใจ"
        )
        tk.Label(card, text=desc, font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE, justify="left").pack(pady=10, padx=20)

        tk.Label(card, text="โปรดระบุชื่อของคุณ:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE).pack(pady=(5, 5))

        entry_name = tk.Entry(card, font=FONT_HEADING, justify="center", bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, insertbackground="white")
        entry_name.insert(0, "กราฟ")
        entry_name.pack(fill="x", padx=40, pady=5)
        entry_name.focus_set()

        def _close_new_prompt(e=None):
            try:
                top.grab_release()
            except Exception:
                pass
            top.destroy()
            return "break"

        def start_btn_click():
            name = entry_name.get().strip()
            if not name:
                name = "นักศึกษาหัวร้อน"
            self.game_state = save_manager.DEFAULT_STATE.copy()
            self.game_state["player_name"] = name
            save_manager.save_game(self.game_state, "slot1")
            save_manager.save_game(self.game_state, "auto")
            _close_new_prompt()
            self.load_scene("scene1")

        StyledButton(
            card, text="🚀 เริ่มต้นการผจญภัย [Enter]", font=FONT_BODY_BOLD,
            bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            command=start_btn_click
        ).pack(pady=20)

        entry_name.bind("<Return>", lambda e: start_btn_click())
        top.bind("<Escape>", _close_new_prompt)

    def action_continue(self):
        slots_info = save_manager.get_all_slots_info()
        active_slots = [s for s in slots_info if not s["is_empty"]]
        if active_slots:
            # โหลดเซฟแรกที่มีอยู่
            self.game_state = active_slots[0]["data"]
            target_scene = self.game_state.get("current_scene", "scene1")
            if target_scene == "finished":
                target_scene = "scene3"
            self.load_scene(target_scene)
        else:
            messagebox.showinfo("แจ้งเตือน", "ไม่พบข้อมูลเซฟเกมเดิม กรุณากด 'เริ่มเกมใหม่'")

    def action_load_game(self):
        def on_slot_loaded(loaded_data):
            if loaded_data:
                self.game_state = loaded_data
                target_scene = self.game_state.get("current_scene", "scene1")
                if target_scene == "finished":
                    target_scene = "scene3"
                self.load_scene(target_scene)

        show_load_slots_dialog(self.root, on_loaded=on_slot_loaded)

    # -------------------------------------------------------------
    # การโหลดและเปลี่ยนฉาก (Scene Controller)
    # -------------------------------------------------------------
    def load_scene(self, scene_name):
        # ปิดหน้าต่าง Popup หรือ Toplevel ตกค้าง และปล่อย Grab ทั้งหมด
        for child in list(self.root.winfo_children()):
            if isinstance(child, tk.Toplevel) and child.winfo_exists():
                try:
                    child.grab_release()
                except Exception:
                    pass
                child.destroy()

        if self.current_scene_frame:
            try:
                self.current_scene_frame.grab_release()
            except Exception:
                pass
            self.current_scene_frame.destroy()
            self.current_scene_frame = None

        if scene_name == "scene1":
            self.current_scene_frame = Scene1MedicineFrame(
                self.container, self.game_state,
                on_finish_scene=lambda: self.load_scene("scene2"),
                on_exit_to_menu=self.return_to_menu
            )
        elif scene_name == "scene2":
            self.current_scene_frame = Scene2BurnFirstAidFrame(
                self.container, self.game_state,
                on_finish_scene=lambda: self.load_scene("scene3"),
                on_exit_to_menu=self.return_to_menu
            )
        elif scene_name in ["scene3", "finished"]:
            self.current_scene_frame = Scene3MohpromtFrame(
                self.container, self.game_state,
                on_finish_game=self.return_to_menu,
                on_exit_to_menu=self.return_to_menu
            )

        self.current_page_frame = self.current_scene_frame
        self.current_scene_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.current_scene_frame.tkraise()
        self.root.focus_set()

    def return_to_menu(self):
        has_saved_data = save_manager.has_save()
        self.btn_continue.config(
            state="normal" if has_saved_data else "disabled",
            fg=COLOR_TEXT_MAIN if has_saved_data else COLOR_TEXT_MUTED,
            bg="#0369a1" if has_saved_data else COLOR_SURFACE,
            cursor="hand2" if has_saved_data else "arrow"
        )
        self.show_page(self.menu_frame)

    # -------------------------------------------------------------
    # หน้า OPTIONS: ตัวปรับระดับเสียง, ความเร็วพิมพ์, เปลี่ยนชื่อผู้เล่น, คู่มือ
    # -------------------------------------------------------------
    def open_options_page(self):
        self.setup_options_page()
        self.show_page(self.options_frame)

    def setup_options_page(self):
        for w in self.options_frame.winfo_children():
            w.destroy()

        header = tk.Frame(self.options_frame, bg=COLOR_BG)
        header.pack(fill="x", padx=30, pady=(15, 8))

        tk.Label(header, text="⚙️ ตั้งค่าระบบ (OPTIONS & SETTINGS)", font=FONT_TITLE, fg=COLOR_YELLOW, bg=COLOR_BG).pack(anchor="w")
        tk.Label(header, text="ปรับแต่งระดับเสียง ความเร็วตัวอักษร และแก้ไขชื่อตัวละครของคุณ", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG).pack(anchor="w")

        # Scrollable area
        canvas = tk.Canvas(self.options_frame, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.options_frame, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg=COLOR_BG)

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=940)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(fill="both", expand=True, padx=30, pady=5)
        scrollbar.pack(side="right", fill="y")

        # -----------------------------
        # เมนูลัดการตั้งค่า (Options Sub-Menu): 1. User Guide, 2. Back to Main Menu
        # -----------------------------
        nav_card = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=2, relief="solid", padx=16, pady=12)
        nav_card.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
        nav_card.pack(fill="x", pady=(2, 8))

        tk.Label(
            nav_card,
            text="📌 เมนูลัด (Options Navigation)",
            font=FONT_HEADING,
            fg=COLOR_YELLOW,
            bg=COLOR_SURFACE
        ).pack(anchor="w", pady=(0, 6))

        nav_row = tk.Frame(nav_card, bg=COLOR_SURFACE)
        nav_row.pack(fill="x")

        StyledButton(
            nav_row,
            text="📖 คู่มือการใช้งานเกม (User Guide) ➔",
            font=FONT_BODY_BOLD,
            bg="#0284c7", fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=16, pady=6,
            command=self.open_user_guide_page
        ).pack(side="left")

        # -----------------------------
        # หมวด 1: ระบบเสียง (Volume & Sound Controls)
        # -----------------------------
        sec_vol = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=1, relief="solid", padx=16, pady=12)
        sec_vol.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        sec_vol.pack(fill="x", pady=6)

        tk.Label(sec_vol, text="🔊 1. ควบคุมระดับเสียง (Audio Controls)", font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 6))

        vol_row = tk.Frame(sec_vol, bg=COLOR_SURFACE)
        vol_row.pack(fill="x", pady=4)

        cur_vol = get_global_volume()
        lbl_vol_status = tk.Label(vol_row, text=f"ระดับเสียงปัจจุบัน: {cur_vol}%", font=FONT_BODY_BOLD, fg=COLOR_GREEN, bg=COLOR_SURFACE, width=22, anchor="w")
        lbl_vol_status.pack(side="left")

        def on_slider_change(val):
            v = int(float(val))
            set_global_volume(v)
            lbl_vol_status.config(text=f"ระดับเสียงปัจจุบัน: {v}%", fg=COLOR_GREEN if v > 0 else COLOR_RED)
            btn_mute.config(text="🔇 ปิดเสียง (Mute)" if is_sound_enabled() else "🔊 เปิดเสียง (Unmute)")

        vol_slider = tk.Scale(
            vol_row, from_=0, to=100, orient="horizontal", length=320,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, highlightthickness=0,
            troughcolor=COLOR_BG, activebackground=COLOR_ACCENT,
            command=on_slider_change
        )
        vol_slider.set(cur_vol)
        vol_slider.pack(side="left", padx=15)

        def step_volume(delta):
            new_v = max(0, min(100, get_global_volume() + delta))
            vol_slider.set(new_v)
            on_slider_change(new_v)

        def toggle_mute_action():
            is_on = toggle_global_sound()
            v = get_global_volume()
            vol_slider.set(v)
            lbl_vol_status.config(text=f"ระดับเสียงปัจจุบัน: {v}%", fg=COLOR_GREEN if is_on else COLOR_RED)
            btn_mute.config(text="🔇 ปิดเสียง (Mute)" if is_on else "🔊 เปิดเสียง (Unmute)")
            if is_on:
                play_sfx(ADVANCE_SOUND)

        btn_vol_down = StyledButton(
            vol_row, text="➖ ลดเสียง (-10%)", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=8, pady=3, command=lambda: step_volume(-10)
        )
        btn_vol_down.pack(side="left", padx=3)

        btn_vol_up = StyledButton(
            vol_row, text="➕ เพิ่มเสียง (+10%)", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=8, pady=3, command=lambda: step_volume(10)
        )
        btn_vol_up.pack(side="left", padx=3)

        btn_mute = StyledButton(
            vol_row, text="🔇 ปิดเสียง (Mute)" if is_sound_enabled() else "🔊 เปิดเสียง (Unmute)",
            font=FONT_SMALL, bg=COLOR_SURFACE_LIGHT, fg=COLOR_YELLOW,
            hover_bg=COLOR_YELLOW, hover_fg=COLOR_BG,
            padx=8, pady=3, command=toggle_mute_action
        )
        btn_mute.pack(side="left", padx=3)

        btn_test_sfx = StyledButton(
            vol_row, text="🔔 ทดสอบเสียง (Test SFX)", font=FONT_SMALL,
            bg="#0369a1", fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=10, pady=3, command=lambda: play_sfx(ADVANCE_SOUND)
        )
        btn_test_sfx.pack(side="left", padx=5)

        # -----------------------------
        # หมวด 2: ความเร็วการแสดงข้อความ (Typewriter Speed)
        # -----------------------------
        sec_speed = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=1, relief="solid", padx=16, pady=12)
        sec_speed.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        sec_speed.pack(fill="x", pady=6)

        tk.Label(sec_speed, text="✍️ 2. ความเร็วการพิมพ์ตัวอักษร (Text Speed)", font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 6))

        speed_row = tk.Frame(sec_speed, bg=COLOR_SURFACE)
        speed_row.pack(fill="x", pady=4)

        cur_speed = get_global_text_speed()
        lbl_speed_status = tk.Label(speed_row, text=f"ความเร็วปัจจุบัน: {cur_speed} ms/ตัวอักษร", font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg=COLOR_SURFACE, width=28, anchor="w")
        lbl_speed_status.pack(side="left")

        def set_speed_option(spd, name):
            set_global_text_speed(spd)
            lbl_speed_status.config(text=f"ความเร็ว: {name} ({spd} ms/ตัว)")
            play_sfx(ADVANCE_SOUND)

        StyledButton(
            speed_row, text="🚀 เร็วมาก (10 ms)", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=12, pady=4, command=lambda: set_speed_option(10, "เร็วมาก")
        ).pack(side="left", padx=5)

        StyledButton(
            speed_row, text="⚡ ปกติ (18 ms)", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=12, pady=4, command=lambda: set_speed_option(18, "ปกติ")
        ).pack(side="left", padx=5)

        StyledButton(
            speed_row, text="📖 ช้า (30 ms)", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=12, pady=4, command=lambda: set_speed_option(30, "ช้า")
        ).pack(side="left", padx=5)

        # -----------------------------
        # หมวด 3: โปรไฟล์และชื่อผู้เล่น (Player Profile)
        # -----------------------------
        sec_player = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=1, relief="solid", padx=16, pady=12)
        sec_player.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        sec_player.pack(fill="x", pady=6)

        tk.Label(sec_player, text="👤 3. โปรไฟล์และชื่อตัวละคร (Player Name)", font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 4))
        tk.Label(sec_player, text="คุณสามารถแก้ไขชื่อตัวละครของคุณได้ตลอดเวลา ชื่อนี้จะปรากฏในบทสนทนาและบันทึกเซฟเกม", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 6))

        pname_row = tk.Frame(sec_player, bg=COLOR_SURFACE)
        pname_row.pack(fill="x", pady=4)

        tk.Label(pname_row, text="ชื่อตัวละครของคุณ:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE).pack(side="left", padx=(0, 10))

        entry_name = tk.Entry(pname_row, font=FONT_HEADING, bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, insertbackground="white", width=20)
        entry_name.insert(0, self.game_state.get("player_name", "กราฟ"))
        entry_name.pack(side="left", padx=(0, 15))

        def save_player_name():
            new_name = entry_name.get().strip()
            if new_name:
                self.game_state["player_name"] = new_name
                save_manager.save_game(self.game_state, "auto")
                play_sfx(ADVANCE_SOUND)
                messagebox.showinfo("สำเร็จ", f"เปลี่ยนชื่อตัวละครเป็น '{new_name}' เรียบร้อยแล้ว!")
            else:
                messagebox.showwarning("คำเตือน", "กรุณาระบุชื่อตัวละคร")

        StyledButton(
            pname_row, text="💾 บันทึกชื่อตัวละคร", font=FONT_BODY_BOLD,
            bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=14, pady=3, command=save_player_name
        ).pack(side="left")

        # -----------------------------
        # หมวด 4: คลังคู่มือความรู้สุขภาพ (Medical Handbook)
        # -----------------------------
        sec_handbook = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=1, relief="solid", padx=16, pady=12)
        sec_handbook.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        sec_handbook.pack(fill="x", pady=6)

        tk.Label(sec_handbook, text="📖 4. คลังคู่มือความรู้การแพทย์ & ยาสามัญประจำบ้าน (Handbook)", font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 4))
        tk.Label(sec_handbook, text="เข้าถึงคู่มือทางการฉบับเต็มจากกระทรวงสาธารณสุข และสาระสำคัญด้านการตรวจยา, แผลไหม้, และระบบหมอพร้อม", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 8))

        sec_handbook_btns = tk.Frame(sec_handbook, bg=COLOR_SURFACE)
        sec_handbook_btns.pack(fill="x", pady=4)

        StyledButton(
            sec_handbook_btns, text="📋 เปิดดูคู่มือโปสเตอร์ยาสามัญประจำบ้าน ➔", font=FONT_BODY_BOLD,
            bg="#0284c7", fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=16, pady=6, command=lambda: show_moph_poster_modal(self.root)
        ).pack(side="left", padx=(0, 10))

        StyledButton(
            sec_handbook_btns, text="📚 เปิดอ่านคู่มือความรู้สุขภาพ & ปฐมพยาบาล (ตรวจยา, แผลไหม้, หมอพร้อม) ➔", font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=16, pady=6, command=self.open_handbook_modal
        ).pack(side="left")

        # ปุ่มกลับ
        StyledButton(
            self.options_frame, text="⬅️ ย้อนกลับเมนูหลัก", font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            command=lambda: self.show_page(self.menu_frame)
        ).pack(pady=10)

    def open_handbook_modal(self):
        """เปิดหน้าต่างอ่านคู่มือความรู้สุขภาพฉบับเต็ม"""
        top = tk.Toplevel(self.root)
        top.title("📖 คู่มือความรู้สุขภาพและยาสามัญประจำบ้าน")
        top.configure(bg=COLOR_BG)
        top.transient(self.root)
        top.grab_set()
        center_modal(top, self.root, 960, 650)

        def _close_handbook(e=None):
            try:
                top.grab_release()
            except Exception:
                pass
            top.destroy()
            return "break"

        header = tk.Frame(top, bg=COLOR_SURFACE, pady=10, padx=16, bd=1, relief="solid")
        header.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        header.pack(fill="x")

        tk.Label(header, text="📖 คู่มือความรู้สุขภาพและการปฐมพยาบาล", font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE).pack(side="left")

        StyledButton(
            header, text="✕ ปิด (Esc)", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_RED, hover_fg=COLOR_TEXT_MAIN,
            padx=12, pady=3, command=_close_handbook
        ).pack(side="right")

        canvas = tk.Canvas(top, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg=COLOR_BG)

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=910)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # หมวด 1: ยาสามัญประจำบ้าน (11 หมวดหมู่สำคัญ)
        sec1 = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=1, relief="solid", padx=15, pady=12)
        sec1.pack(fill="x", pady=6)
        tk.Label(sec1, text="1. คู่มือยาสามัญประจำบ้าน (11 หมวดหมู่สำคัญ)", font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 4))
        tk.Label(sec1, text="โปสเตอร์แสดงตัวอย่างยาจริง สรรพคุณ และวิธีสังเกตสัญลักษณ์ยา สำหรับร้านชำและตู้ยาประจำบ้าน", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 8))

        sec1_action_box = tk.Frame(sec1, bg=COLOR_SURFACE_LIGHT, padx=14, pady=12, bd=1, relief="solid")
        sec1_action_box.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
        sec1_action_box.pack(fill="x", pady=(0, 6))

        tk.Label(
            sec1_action_box,
            text="✨ เข้าดูโปสเตอร์แบบเต็ม (Full Scroll) แสดงภาพยาจริง พร้อมแถบลัดไปยังกลุ่มยาต่างๆ:",
            font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT
        ).pack(anchor="w", pady=(0, 6))

        StyledButton(
            sec1_action_box, text="📋 เปิดดูคู่มือโปสเตอร์ยาสามัญประจำบ้าน ➔",
            font=FONT_BODY_BOLD, bg="#0284c7", fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=18, pady=6, command=lambda: show_moph_poster_modal(top)
        ).pack(anchor="w")

        # หมวด 2: การตรวจยาเสื่อมสภาพ
        sec2 = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=1, relief="solid", padx=15, pady=12)
        sec2.pack(fill="x", pady=6)
        tk.Label(sec2, text="2. การตรวจสอบยาเสื่อมคุณภาพ และการเก็บรักษาที่ถูกต้อง", font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 6))
        sec2_box = tk.Frame(sec2, bg=COLOR_SURFACE)
        sec2_box.pack(fill="x")
        cab_pic = get_image("med_cabinet.jpg", (240, 160))
        if cab_pic:
            lbl_c = tk.Label(sec2_box, image=cab_pic, bg=COLOR_SURFACE, bd=1, relief="ridge")
            lbl_c.image = cab_pic
            lbl_c.pack(side="left", padx=(0, 15))

        sec2_text_frame = tk.Frame(sec2_box, bg=COLOR_SURFACE)
        sec2_text_frame.pack(side="left", fill="both", expand=True)
        tk.Label(sec2_text_frame, text="[ วิธีสังเกตยาเสื่อมคุณภาพ ]", font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg=COLOR_SURFACE).pack(anchor="w")
        for key, desc in DRUG_STORAGE_KNOWLEDGE["degradation_signs"].items():
            tk.Label(sec2_text_frame, text=f"• {desc}", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, justify="left").pack(anchor="w")

        # หมวด 3: ปฐมพยาบาลแผลน้ำร้อนลวก
        sec3 = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=1, relief="solid", padx=15, pady=12)
        sec3.pack(fill="x", pady=6)
        tk.Label(sec3, text="3. การปฐมพยาบาลแผลน้ำร้อนลวก และความเชื่อที่ผิด (รพ.ศิริราช)", font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 6))
        sec3_box = tk.Frame(sec3, bg=COLOR_SURFACE)
        sec3_box.pack(fill="x")
        burn_pic = get_image("burn_wound.jpg", (260, 150))
        if burn_pic:
            lbl_b = tk.Label(sec3_box, image=burn_pic, bg=COLOR_SURFACE, bd=1, relief="ridge")
            lbl_b.image = burn_pic
            lbl_b.pack(side="left", padx=(0, 15))

        burn_guide = (
            "• แผลไฟไหม้/น้ำร้อนลวกระดับ 2 ชนิดตื้น: มีตุ่มน้ำพองใส ปวดแสบร้อน\n"
            "• การปฐมพยาบาลที่ถูกต้อง:\n"
            "   1. แช่หรือล้างด้วยน้ำสะอาดอุณหภูมิห้อง 10-15 นาที (ห้ามใช้น้ำแข็ง/น้ำเย็นจัด)\n"
            "   2. ห้ามเจาะตุ่มน้ำพองใสโดยเด็ดขาด เพราะตุ่มน้ำช่วยป้องกันการติดเชื้อ\n"
            "   3. ปิดแผลหลวมๆ ด้วยผ้าก๊อซสะอาด ไม่รัดแน่น ไม่ใช้สำลีติดเนื้อเยื่อ\n"
            "• ความเชื่อที่ผิดและอันตราย:\n"
            "   - การทายาสีฟัน, น้ำปลา, น้ำมัน, ซอสปรุงรส (เสี่ยงติดเชื้อรุนแรง ล้างออกยากมาก)\n"
            "   - การใช้น้ำแข็งประคบโดยตรง (ทำให้หลอดเลือดหดตัว เนื้อเยื่อตายเพิ่มขึ้น)"
        )
        tk.Label(sec3_box, text=burn_guide, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, justify="left").pack(side="left", anchor="nw")

        # หมวด 4: แอปหมอพร้อม
        sec4 = tk.Frame(scroll_content, bg=COLOR_SURFACE, bd=1, relief="solid", padx=15, pady=12)
        sec4.pack(fill="x", pady=6)
        tk.Label(sec4, text="4. ขั้นตอนการจองคิวตรวจผ่านแอปพลิเคชัน 'หมอพร้อม' (MOPH Appointment Center)", font=FONT_SUBTITLE, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 6))
        moh_guide = (
            "1. เปิดหน้าแรกของแอปพลิเคชันหมอพร้อม -> เลือกเมนู 'นัดหมายออนไลน์'\n"
            "2. ในหน้าบริการ -> เลือก 'จองคิวหมอ'\n"
            "3. ระบุข้อมูลการนัดหมาย:\n"
            "   - เลือก จังหวัด และ เขต/อำเภอ\n"
            "   - เลือก โรงพยาบาล และ แผนกที่ต้องการรับการตรวจ\n"
            "   - เลือก วันที่ และ แพทย์ (สามารถเลือก 'ไม่ระบุแพทย์' ได้)\n"
            "   - เลือก เวลานัดหมาย และกรอก อาการเบื้องต้น\n"
            "   - เลือก รูปแบบการรับบริการ (ที่โรงพยาบาล หรือ พบแพทย์ออนไลน์)\n"
            "4. กดยืนยันการจองคิว -> ตรวจสอบและบันทึก 'ใบนัดหมาย' เพื่อนำไปยื่นตามวันเวลา"
        )
        tk.Label(sec4, text=moh_guide, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, justify="left").pack(anchor="w")

        top.bind("<Escape>", _close_handbook)

    # -------------------------------------------------------------
    # หน้า CREDITS (อ่านข้อมูลจาก credits.txt แบบ Scrollable)
    # -------------------------------------------------------------
    def setup_credits_page(self):
        for w in self.credits_frame.winfo_children():
            w.destroy()

        header = tk.Frame(self.credits_frame, bg=COLOR_BG)
        header.pack(fill="x", padx=30, pady=(15, 8))

        top_row = tk.Frame(header, bg=COLOR_BG)
        top_row.pack(fill="x")

        tk.Label(
            top_row,
            text="ℹ️ เกี่ยวกับเกมและคณะผู้จัดทำ (CREDITS)",
            font=FONT_TITLE,
            fg=COLOR_ACCENT,
            bg=COLOR_BG
        ).pack(side="left")

        StyledButton(
            top_row,
            text="⬅️ กลับสู่เมนูหลัก (Back to Main Menu)",
            font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=10, pady=3,
            command=lambda: self.show_page(self.menu_frame)
        ).pack(side="right")

        tk.Label(
            header,
            text="ข้อมูลโครงการ วัตถุประสงค์ ประโยชน์ที่ได้รับ และรายชื่อทีมพัฒนา",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_BG
        ).pack(anchor="w")

        card = tk.Frame(self.credits_frame, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=30, pady=(5, 12))

        txt_scrollbar = tk.Scrollbar(card, orient="vertical")
        txt = tk.Text(
            card,
            bg=COLOR_SURFACE,
            fg=COLOR_TEXT_MAIN,
            font=FONT_BODY,
            wrap="word",
            padx=20,
            pady=15,
            bd=0,
            highlightthickness=0,
            yscrollcommand=txt_scrollbar.set
        )
        txt_scrollbar.config(command=txt.yview)
        txt_scrollbar.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)

        credits_path = os.path.join(BASE_DIR, "credits.txt")
        credits_content = ""
        if os.path.exists(credits_path):
            try:
                with open(credits_path, "r", encoding="utf-8") as f:
                    credits_content = f.read()
            except Exception as e:
                credits_content = f"เกิดข้อผิดพลาดในการอ่านไฟล์ credits.txt: {e}"
        else:
            credits_content = (
                "================================================================================\n"
                "STAY ALIVE, TEE!: เมทข้าต้องรอด! (CREDITS)\n"
                "================================================================================\n\n"
                "[ ข้อมูลโครงการ / Project Overview ]\n"
                "• ชื่อโปรแกรม: Stay Alive, Tee!: เมทข้าต้องรอด!\n"
                "• ชื่อทีมพัฒนา: อินมานี่มา (In-Ma-Nee-Ma Team)\n"
                "• หลักสูตร: วิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีสารสนเทศ\n\n"
                "[ รายชื่อสมาชิกทีมพัฒนา ]\n"
                "1. นางสาวปรินทร คุณกิตติ (รหัสนักศึกษา: 690813048) - Game Logic & Scenario Developer\n"
                "2. นางสาวสรชา ทุกข์จาก (รหัสนักศึกษา: 690813058) - UI & Visual Novel Components\n"
                "3. นางสาวยสุตมา ค่ำชู (รหัสนักศึกษา: 690813067) - Game Engine\n"
            )

        txt.insert("1.0", credits_content)
        txt.config(state="disabled")

        b_bar = tk.Frame(self.credits_frame, bg=COLOR_BG)
        b_bar.pack(fill="x", padx=30, pady=(0, 10))

        StyledButton(
            b_bar,
            text="⬅️ กลับสู่เมนูหลัก (Back to Main Menu)",
            font=FONT_BODY_BOLD,
            bg=COLOR_ACCENT, fg=COLOR_BG,
            hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=18, pady=5,
            command=lambda: self.show_page(self.menu_frame)
        ).pack(side="left")

    # -------------------------------------------------------------
    # หน้า USER GUIDE (อ่านข้อมูลจาก guide.txt แบบ Scrollable)
    # -------------------------------------------------------------
    def open_user_guide_page(self):
        self.setup_guide_page()
        self.show_page(self.guide_frame)

    def setup_guide_page(self):
        for w in self.guide_frame.winfo_children():
            w.destroy()

        header = tk.Frame(self.guide_frame, bg=COLOR_BG)
        header.pack(fill="x", padx=30, pady=(15, 8))

        top_row = tk.Frame(header, bg=COLOR_BG)
        top_row.pack(fill="x")

        tk.Label(
            top_row,
            text="📖 คู่มือการใช้งานเกม (USER GUIDE)",
            font=FONT_TITLE,
            fg=COLOR_YELLOW,
            bg=COLOR_BG
        ).pack(side="left")

        btn_row = tk.Frame(top_row, bg=COLOR_BG)
        btn_row.pack(side="right")

        StyledButton(
            btn_row,
            text="⬅️ กลับสู่หน้าการตั้งค่า (Back to Options)",
            font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=10, pady=3,
            command=lambda: self.show_page(self.options_frame)
        ).pack(side="left", padx=4)

        StyledButton(
            btn_row,
            text="🏠 เมนูหลัก (Main Menu)",
            font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=10, pady=3,
            command=lambda: self.show_page(self.menu_frame)
        ).pack(side="left", padx=4)

        tk.Label(
            header,
            text="คำแนะนำขั้นตอนการเล่น การควบคุมระบบบันทึก และสาระสำคัญในแต่ละฉาก",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_BG
        ).pack(anchor="w")

        card = tk.Frame(self.guide_frame, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=30, pady=(5, 12))

        txt_scrollbar = tk.Scrollbar(card, orient="vertical")
        txt = tk.Text(
            card,
            bg=COLOR_SURFACE,
            fg=COLOR_TEXT_MAIN,
            font=FONT_BODY,
            wrap="word",
            padx=20,
            pady=15,
            bd=0,
            highlightthickness=0,
            yscrollcommand=txt_scrollbar.set
        )
        txt_scrollbar.config(command=txt.yview)
        txt_scrollbar.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)

        guide_path = os.path.join(BASE_DIR, "guide.txt")
        guide_content = ""
        if os.path.exists(guide_path):
            try:
                with open(guide_path, "r", encoding="utf-8") as f:
                    guide_content = f.read()
            except Exception as e:
                guide_content = f"เกิดข้อผิดพลาดในการอ่านไฟล์ guide.txt: {e}"
        else:
            guide_content = "ไม่พบไฟล์ guide.txt ในโฟลเดอร์โครงการ"

        txt.insert("1.0", guide_content)
        txt.config(state="disabled")

        b_bar = tk.Frame(self.guide_frame, bg=COLOR_BG)
        b_bar.pack(fill="x", padx=30, pady=(0, 10))

        StyledButton(
            b_bar,
            text="⬅️ กลับสู่หน้าการตั้งค่า (Back to Options)",
            font=FONT_BODY_BOLD,
            bg=COLOR_ACCENT, fg=COLOR_BG,
            hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=16, pady=5,
            command=lambda: self.show_page(self.options_frame)
        ).pack(side="left")

        StyledButton(
            b_bar,
            text="🏠 กลับสู่เมนูหลัก (Back to Main Menu)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=16, pady=5,
            command=lambda: self.show_page(self.menu_frame)
        ).pack(side="right")

    # -------------------------------------------------------------
    # หน้า MEMBER MENU & MEMBER DETAIL (รายชื่อและข้อมูลสมาชิก)
    # -------------------------------------------------------------
    def open_member_menu(self):
        self.setup_member_menu_page()
        self.show_page(self.member_menu_frame)

    def setup_member_menu_page(self):
        for w in self.member_menu_frame.winfo_children():
            w.destroy()

        card = tk.Frame(self.member_menu_frame, bg=COLOR_SURFACE, bd=2, relief="solid", padx=25, pady=20)
        card.config(highlightbackground=COLOR_ACCENT, highlightthickness=2)
        card.place(relx=0.5, rely=0.5, anchor="center", width=580, height=450)

        tk.Label(
            card,
            text="👥 รายชื่อสมาชิกทีมพัฒนา (MEMBERS)",
            font=FONT_SUBTITLE,
            fg=COLOR_YELLOW,
            bg=COLOR_SURFACE
        ).pack(pady=(4, 2))

        tk.Label(
            card,
            text="ทีม: อินมานี่มา (In-Ma-Nee-Ma) | สาขาวิชาเทคโนโลยีสารสนเทศ",
            font=FONT_SMALL,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_SURFACE,
            justify="center"
        ).pack(pady=(0, 14))

        btn_box = tk.Frame(card, bg=COLOR_SURFACE)
        btn_box.pack(fill="x", padx=15)

        # 1. 690813048 นางสาวปรินทร คุณกิตติ
        StyledButton(
            btn_box,
            text="1. 690813048 นางสาวปรินทร คุณกิตติ  ➔",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=14, pady=7, anchor="w",
            command=lambda: self.show_member_detail("690813048")
        ).pack(fill="x", pady=4)

        # 2. 690813058 นางสาวสรชา ทุกข์จาก
        StyledButton(
            btn_box,
            text="2. 690813058 นางสาวสรชา ทุกข์จาก  ➔",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=14, pady=7, anchor="w",
            command=lambda: self.show_member_detail("690813058")
        ).pack(fill="x", pady=4)

        # 3. 690813067 นางสาวยสุตมา ค่ำชู
        StyledButton(
            btn_box,
            text="3. 690813067 นางสาวยสุตมา ค่ำชู  ➔",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=14, pady=7, anchor="w",
            command=lambda: self.show_member_detail("690813067")
        ).pack(fill="x", pady=4)

        # 4. Back to Main Menu
        StyledButton(
            btn_box,
            text="⬅️ 4. กลับสู่เมนูหลัก (Back to Main Menu)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE, fg=COLOR_RED,
            hover_bg=COLOR_RED_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=14, pady=7, anchor="center",
            command=lambda: self.show_page(self.menu_frame)
        ).pack(fill="x", pady=(12, 4))

    def show_member_detail(self, member_id):
        for w in self.member_detail_frame.winfo_children():
            w.destroy()

        member = next((m for m in MEMBERS_DATA if m["id"] == member_id), None)
        if not member:
            self.show_page(self.member_menu_frame)
            return

        card = tk.Frame(self.member_detail_frame, bg=COLOR_SURFACE, bd=2, relief="solid", padx=22, pady=16)
        card.config(highlightbackground=COLOR_ACCENT, highlightthickness=2)
        card.place(relx=0.5, rely=0.5, anchor="center", width=840, height=530)

        # Top Title Bar
        title_bar = tk.Frame(card, bg=COLOR_SURFACE)
        title_bar.pack(fill="x", pady=(0, 10))

        tk.Label(
            title_bar,
            text=f"👤 ข้อมูลผู้จัดทำ: {member['name']}",
            font=FONT_SUBTITLE,
            fg=COLOR_YELLOW,
            bg=COLOR_SURFACE
        ).pack(side="left")

        # Main Body: 2 Columns (Left: Photo, Right: Info)
        body = tk.Frame(card, bg=COLOR_SURFACE)
        body.pack(fill="both", expand=True)

        # Left Column: Photo Frame with aspect ratio preservation
        left_col = tk.Frame(body, bg=COLOR_SURFACE_LIGHT, bd=1, relief="solid", padx=8, pady=8, width=240)
        left_col.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        left_col.pack(side="left", fill="y", padx=(0, 18))
        left_col.pack_propagate(False)

        photo_canvas = tk.Canvas(left_col, bg=COLOR_BG, highlightthickness=0, width=220, height=290)
        photo_canvas.pack(pady=6)

        # Aspect-ratio preserved image loading with error handling
        photo_img = None
        photo_file = member.get("photo_file", "")
        photo_path = os.path.join(PHOTO_DIR, "member", photo_file)
        if not os.path.exists(photo_path):
            photo_path = os.path.join(PHOTO_DIR, photo_file)

        if os.path.exists(photo_path):
            try:
                pil_im = Image.open(photo_path)
                orig_w, orig_h = pil_im.size
                max_w, max_h = 210, 280
                scale = min(max_w / orig_w, max_h / orig_h)
                new_w = max(1, int(orig_w * scale))
                new_h = max(1, int(orig_h * scale))
                pil_resized = pil_im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(pil_resized)
            except Exception as e:
                print(f"Error loading member photo {photo_file}: {e}")

        if photo_img:
            photo_canvas.create_image(110, 145, image=photo_img, anchor="center")
            photo_canvas.image = photo_img
        else:
            photo_canvas.create_text(
                110, 145,
                text="[ ไม่พบรูปภาพ ]\n(Missing Photo)",
                fill=COLOR_TEXT_MUTED,
                font=FONT_BODY_BOLD,
                justify="center"
            )

        # Right Column: Member Details
        right_col = tk.Frame(body, bg=COLOR_SURFACE)
        right_col.pack(side="left", fill="both", expand=True)

        def make_field(parent, label_text, val_text, val_color=COLOR_TEXT_MAIN, is_multiline=False):
            f = tk.Frame(parent, bg=COLOR_SURFACE)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label_text, font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE, width=14, anchor="w").pack(side="left", anchor="nw")
            if is_multiline:
                tk.Label(f, text=val_text, font=FONT_BODY, fg=val_color, bg=COLOR_SURFACE, justify="left", wraplength=450).pack(side="left", fill="x", expand=True, anchor="w")
            else:
                tk.Label(f, text=val_text, font=FONT_BODY, fg=val_color, bg=COLOR_SURFACE, anchor="w").pack(side="left", fill="x", expand=True)

        make_field(right_col, "รหัสนักศึกษา:", member["id"], COLOR_YELLOW)
        make_field(right_col, "ชื่อ-นามสกุล:", member["name"], COLOR_TEXT_MAIN)
        make_field(right_col, "ชื่อเล่น:", member["nickname"], COLOR_TEXT_MUTED)
        make_field(right_col, "ตำแหน่ง:", member["position"], COLOR_GREEN)

        tk.Frame(right_col, height=1, bg=COLOR_BORDER).pack(fill="x", pady=6)

        tk.Label(right_col, text="หน้าที่ความรับผิดชอบ:", font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 4))
        
        duty_box = tk.Frame(right_col, bg=COLOR_SURFACE_LIGHT, padx=12, pady=8, bd=1, relief="solid")
        duty_box.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        duty_box.pack(fill="both", expand=True)

        tk.Label(
            duty_box,
            text=member["duty"],
            font=FONT_BODY,
            fg=COLOR_TEXT_MAIN,
            bg=COLOR_SURFACE_LIGHT,
            justify="left",
            wraplength=460
        ).pack(anchor="nw", fill="both")

        # Bottom Button Bar: Direct link to Main Menu & Back to Member List
        btn_bar = tk.Frame(card, bg=COLOR_SURFACE)
        btn_bar.pack(fill="x", pady=(12, 0))

        StyledButton(
            btn_bar,
            text="⬅️ กลับสู่หน้ารายชื่อสมาชิก (Back to Members)",
            font=FONT_BODY_BOLD,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=14, pady=5,
            command=lambda: self.show_page(self.member_menu_frame)
        ).pack(side="left")

        StyledButton(
            btn_bar,
            text="🏠 กลับสู่เมนูหลัก (Back to Main Menu)",
            font=FONT_BODY_BOLD,
            bg=COLOR_ACCENT, fg=COLOR_BG,
            hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=16, pady=5,
            command=lambda: self.show_page(self.menu_frame)
        ).pack(side="right")

        self.show_page(self.member_detail_frame)


def main():
    root = tk.Tk()
    app = PharmacyAfterlifeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()