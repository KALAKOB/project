"""
Scene 1: First Aid Household Medicines & Quality Check
ฉากที่ 1: ยาสามัญประจำบ้าน การตรวจสอบยาเสื่อมคุณภาพ และการซื้อของบริหารเงิน 1,000 บาท
"""

import tkinter as tk
from tkinter import ttk
from ui_theme import (
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_LIGHT, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_GREEN,
    COLOR_GREEN_HOVER, COLOR_RED, COLOR_RED_HOVER, COLOR_YELLOW, COLOR_PURPLE, COLOR_BORDER,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_BODY_BOLD,
    FONT_DIALOGUE, FONT_SPEAKER, FONT_CHOICE, FONT_SMALL, FONT_FAMILY,
    StyledButton, get_image
)
from vn_widgets import TopStatusBar, DialogueBox, show_knowledge_popup, show_save_slots_dialog, show_moph_poster_modal
from data import CABINET_MEDICINES, MISSING_CABINET_MEDICINES, SHOP_ITEMS
from save_manager import save_game

class Scene1MedicineFrame(tk.Frame):
    def __init__(self, parent, game_state, on_finish_scene, on_exit_to_menu):
        super().__init__(parent, bg=COLOR_BG)
        self.parent = parent
        self.game_state = game_state
        self.on_finish_scene = on_finish_scene
        self.on_exit_to_menu = on_exit_to_menu

        # สถานะในฉาก
        self.dialogue_index = 0
        self.checked_medicines = {}
        self.shopping_cart = set()
        self.current_med_inspect = None

        # แถบสถานะด้านบน
        self.top_bar = TopStatusBar(
            self,
            on_save_click=self.handle_manual_save,
            on_menu_click=self.on_exit_to_menu,
            on_log_click=lambda: self.dialogue_box.open_history_log()
        )
        self.update_top_bar()

        # Canvas/พื้นที่ภาพและเนื้อหาตรงกลาง
        self.stage_container = tk.Frame(self, bg=COLOR_BG)
        self.stage_container.pack(fill="both", expand=True)

        # พื้นหลังและตัวละคร
        self.current_bg = "dorm"
        self.current_char_pose = "none"
        self.bg_canvas = tk.Canvas(self.stage_container, bg=COLOR_BG, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.bind("<Configure>", self._on_bg_resize)

        # กล่องบทสนทนาด้านล่าง
        self.dialogue_box = DialogueBox(self, on_next=self.advance_story)
        self.dialogue_box.pack(fill="x", side="bottom", padx=20, pady=(0, 15), ipady=5)

        self.init_intro_dialogues()
        self.show_current_dialogue()

    def _on_bg_resize(self, event=None):
        if hasattr(self, "bg_canvas") and self.bg_canvas.winfo_exists():
            w = self.bg_canvas.winfo_width()
            h = self.bg_canvas.winfo_height()
            if w > 100 and h > 100:
                self.render_background_and_character(self.current_bg, self.current_char_pose)

    def update_top_bar(self):
        self.top_bar.update_status(
            self.game_state["player_name"],
            "ฉากที่ 1: ตู้ยาสามัญ & ห้างสรรพสินค้า",
            self.game_state["score"],
            self.game_state["relationship"]
        )

    def handle_manual_save(self):
        self.game_state["current_scene"] = "scene1"
        show_save_slots_dialog(self, self.game_state, on_saved=lambda sid: self.update_top_bar())

    # -------------------------------------------------------------
    # ระบบบทสนทนาเริ่มต้น
    # -------------------------------------------------------------
    def init_intro_dialogues(self):
        pname = self.game_state["player_name"]
        self.intro_choice_done = False
        self.story_scripts = [
            ("บรรยาย", "บ่ายวันเสาร์ในหอพัก... แสงแดดส่องผ่านหน้าต่างเข้ามาในห้องที่สภาพไม่ต่างจากสมรภูมิรบ กองกระดาษดราฟต์กับเศษโฟมตัดโมเดลเกลื่อนเต็มพื้น", COLOR_TEXT_MUTED, "dorm", "none"),
            ("ที", f"อือออ... วิญญาณฉันจะหลุดออกจากร่างแล้ว {pname}... กาแฟก็หมด ตู้เย็นเปิดไปก็เจอแค่น้ำเปล่าครึ่งขวดกับอากาศธาตุ...", "#38bdf8", "dorm", "sleepy"),
            (pname, "ก็เล่นโต้รุ่งตัดโมเดลสามวันติดไงล่ะที! วันนี้วันหยุด เลิกนอนอืดแล้วลุกขึ้นมา ได้เวลาออกไปซื้อของตุนเข้าหอแล้ว ลุก!", "#fb923c", "dorm", "angry"),
            ("ที", "ขอต่อเวลาอีกห้านาที... ไม่สิ สามนาทีก็ได้... แล้วจะซื้ออะไรมั่งอะ จดลิสต์ไว้ยัง...", "#38bdf8", "dorm", "sleepy"),
            (pname, "ของกินน่ะเรื่องรอง สิ่งแรกที่ต้องซื้อคือ 'ยาสามัญประจำบ้าน' ต่างหาก ขืนแกวูบตอนตีสามขึ้นมา ใครจะแบกแกไปส่งโรงบาลไหว! ฉันมีโปสเตอร์ทางการของกระทรวงสาธารณสุข 'ยาสามัญประจำบ้านที่จำหน่ายได้ในร้านชำ' อยู่ในมือพอดี เดี๋ยวเปิดเทียบให้ดูเลยว่าตู้เราขาดอะไรบ้าง!", "#fb923c", "dorm", "talk"),
            ("ที", "หืม... ตู้ยาบนชั้นนั่นก็มีตั้งเยอะนี่แก ไม่ต้องซื้อหรอก เปลืองตังค์ เอาเงินไปซื้อกระดาษชานอ้อยดีกว่า...", "#38bdf8", "dorm", "sleepy"),
            (pname, "เยอะกะผีสิ! ยาพวกนั้นหมดอายุไปตั้งแต่ชาติไหนแล้วก็ไม่รู้ กินเข้าไปไม่ได้หายป่วยหรอก ได้จองศาลาวัดแทนพอดี! ลุกมาช่วยกันเช็กเดี๋ยวนี้เลย!", "#fb923c", "dorm", "angry"),
            ("ระบบ", "เข้าสู่มินิเกม: ตรวจสอบยาสามัญประจำบ้านในตู้ยา คัดแยกยาที่ยังใช้ได้ และทิ้งยาที่เสื่อมสภาพเพื่อจดซื้อใหม่! (สามารถกดดูโปสเตอร์ทางการของ สธ. ได้ตลอดเวลา)", COLOR_PURPLE, "dorm", "none")
        ]

    def render_background_and_character(self, bg_name, char_pose="none"):
        self.current_bg = bg_name
        self.current_char_pose = char_pose
        self.bg_canvas.delete("all")
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        if w < 100:
            w = 1000
            h = 450

        # พื้นหลัง
        bg_file = "bg_dorm.jpg" if bg_name == "dorm" else "bg_pharmacy.jpg"
        bg_img = get_image(bg_file, (w, h))
        if bg_img:
            self.bg_canvas.create_image(0, 0, anchor="nw", image=bg_img)
            self.bg_canvas.image = bg_img

        # ตัวละคร
        if char_pose != "none":
            pose_map = {
                "sleepy": "tee_sleepy.png",
                "panicked": "tee_panicked.png",
                "worried": "tee_panicked.png",
                "happy": "tee_happy.png",
                "angry": "tee_happy.png",
                "talk": "tee_happy.png"
            }
            sprite_file = pose_map.get(char_pose, f"tee_{char_pose}.png")
            # ความสูงตัวละครประมาณ 88% ของความสูง canvas พร้อมรักษาสัดส่วนแท้จริง (848x1264)
            sprite_h = int(h * 0.88)
            sprite_w = int(sprite_h * (848 / 1264))
            char_img = get_image(sprite_file, (sprite_w, sprite_h))
            if char_img:
                # วาดตัวละครด้านขวา บนพื้นหลังอย่างกลมกลืนแบบไม่มีขอบขาว
                self.bg_canvas.create_image(w - sprite_w - 60, h - sprite_h, anchor="nw", image=char_img)
                self.bg_canvas.char_img = char_img

    def show_current_dialogue(self):
        if self.dialogue_index == 7 and not getattr(self, "intro_choice_done", False):
            self.show_intro_banter_choice()
            return

        if self.dialogue_index < len(self.story_scripts):
            speaker, text, color, bg_type, char_pose = self.story_scripts[self.dialogue_index]
            self.render_background_and_character(bg_type, char_pose)
            self.dialogue_box.set_dialogue(speaker, text, color, show_next_btn=True)
            self.dialogue_box.on_next = self.advance_story
        else:
            self.dialogue_box.pack_forget()
            self.start_cabinet_minigame()

    def show_intro_banter_choice(self):
        pname = self.game_state["player_name"]
        self.render_background_and_character("dorm", "sleepy")
        self.dialogue_box.set_dialogue(pname, "(เลือกวิธีตอบโต้เพื่อดึงสติทีและเพิ่มความสัมพันธ์):", "#fb923c", show_next_btn=False)
        choices = [
            ("1. ขู่ด้วยความเด็ดขาด: 'ถ้าไม่ลุก ฉันจะเอางานดราฟต์แกไปชั่งกิโลขายเศษกระดาษเดี๋ยวนี้!'", "threat"),
            ("2. หลอกล่อด้วยของโปรด: 'ลุกมาช่วยกันเช็กตู้ยาก่อน ถ้าเสร็จไวเดี๋ยวฉันเลี้ยงชานมไข่มุกแก้วโปรด'", "bribe"),
            ("3. แสดงความเป็นห่วงเป็นใย: 'ฉันเป็นห่วงแกนะเว้ย ขืนแกป่วยตายคาหอฉันจะอยู่กับใคร ลุก!'", "care")
        ]
        self.dialogue_box.show_choices(choices, self.handle_intro_banter_selected)

    def handle_intro_banter_selected(self, choice):
        self.intro_choice_done = True
        if choice == "threat":
            self.game_state["relationship"] += 5
            reply = ("ที", "อย่าน้าาาา! โมเดลส่งจารย์วันจันทร์ ลุกแล้วๆๆ! อย่ายุ่งกับงานฉัน!", "#38bdf8", "dorm", "panicked")
        elif choice == "bribe":
            self.game_state["relationship"] += 15
            reply = ("ที", "เพื่อนแท้ตัวจริง! หวานร้อยใส่ไข่มุกสองเท่าด้วยนะ! ลุกเดี๋ยวนี้เลย!", "#38bdf8", "dorm", "happy")
        else:
            self.game_state["relationship"] += 10
            reply = ("ที", "ซึ้งเลยว่ะ... เออๆ ลุกก็ได้ เป็นห่วงกันก็ไม่บอก!", "#38bdf8", "dorm", "happy")

        self.update_top_bar()
        self.story_scripts.insert(self.dialogue_index, reply)
        self.show_current_dialogue()

    def advance_story(self):
        self.dialogue_index += 1
        self.show_current_dialogue()

    # -------------------------------------------------------------
    # มินิเกม 1: ตรวจสอบตู้ยา
    # -------------------------------------------------------------
    def start_cabinet_minigame(self):
        for w in self.stage_container.winfo_children():
            w.destroy()

        container = tk.Frame(self.stage_container, bg=COLOR_BG)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_frame = tk.Frame(container, bg=COLOR_SURFACE, pady=10, padx=15, bd=1, relief="solid")
        header_frame.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            header_frame, text="🔍 ภารกิจที่ 1: ตรวจสอบสภาพยาสามัญประจำบ้านในตู้ยา",
            font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE
        ).pack(side="left")

        self.lbl_progress = tk.Label(
            header_frame, text=f"ตรวจแล้ว: {len(self.checked_medicines)} / {len(CABINET_MEDICINES)} รายการ",
            font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE
        )
        self.lbl_progress.pack(side="right")

        StyledButton(
            header_frame, text="📋 โปสเตอร์ยาสามัญ สธ. (long.pdf)",
            font=FONT_SMALL, bg="#0284c7", fg="white",
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=12, pady=4, command=lambda: show_moph_poster_modal(self)
        ).pack(side="right", padx=(0, 15))

        # Main Body (Split into Left list, Middle image, Right info/buttons)
        body_frame = tk.Frame(container, bg=COLOR_BG)
        body_frame.pack(fill="both", expand=True)

        # ซ้าย: รายการยา
        left_frame = tk.Frame(body_frame, bg=COLOR_SURFACE, width=320, bd=1, relief="solid")
        left_frame.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        tk.Label(
            left_frame, text="📋 ยาที่พบในตู้ยา",
            font=FONT_HEADING, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, pady=10
        ).pack(fill="x")

        self.med_buttons = {}
        for med in CABINET_MEDICINES:
            btn = StyledButton(
                left_frame,
                text=f"💊 {med['name']}",
                font=(FONT_BODY[0], 9),
                bg=COLOR_SURFACE_LIGHT,
                fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_ACCENT,
                hover_fg=COLOR_BG,
                justify="left",
                anchor="w",
                padx=8, pady=4,
                command=lambda m=med: self.select_medicine_to_inspect(m)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.med_buttons[med["id"]] = btn

        # กลาง-ขวา: รูปตู้ยา + รายละเอียดและการวินิจฉัย
        right_frame = tk.Frame(body_frame, bg=COLOR_SURFACE, bd=1, relief="solid")
        right_frame.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        right_frame.pack(side="right", fill="both", expand=True)

        # ส่วนรูปภาพตู้ยา
        img_box = tk.Frame(right_frame, bg=COLOR_SURFACE, height=180)
        img_box.pack(fill="x", padx=15, pady=10)
        img_box.pack_propagate(False)

        cab_img = get_image("med_cabinet.jpg", (280, 170))
        if cab_img:
            lbl_cab = tk.Label(img_box, image=cab_img, bg=COLOR_SURFACE, bd=1, relief="ridge")
            lbl_cab.image = cab_img
            lbl_cab.pack(side="left")

        guide_box = tk.Frame(img_box, bg=COLOR_SURFACE_LIGHT, padx=10, pady=10)
        guide_box.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(
            guide_box, text="💡 เคล็ดลับการตรวจสอบยา:", font=FONT_BODY_BOLD,
            fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT
        ).pack(anchor="w")
        tk.Label(
            guide_box,
            text="• ดูวันหมดอายุบนบรรจุภัณฑ์\n• ยาเม็ด: ต้องไม่แตกร่วน บวม มีจุดด่าง\n• ยาน้ำ: ต้องไม่ตกตะกอนแข็งหรือแยกชั้น\n• ยาแคปซูล: ต้องไม่นิ่มเหนียวติดกัน",
            font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, justify="left"
        ).pack(anchor="w", pady=(5, 0))

        # รายละเอียดการตรวจ
        self.inspect_details = tk.Frame(right_frame, bg=COLOR_SURFACE)
        self.inspect_details.pack(fill="both", expand=True, padx=20, pady=5)

        # ปุ่มสรุปเมื่อตรวจครบ
        self.bottom_bar = tk.Frame(right_frame, bg=COLOR_SURFACE)
        self.bottom_bar.pack(side="bottom", fill="x", padx=20, pady=10)

        self.btn_finish_cabinet = StyledButton(
            self.bottom_bar, text="📋 สรุปรายการยาที่ขาด และเตรียมไปซื้อของ ➔",
            font=FONT_BODY_BOLD, bg="#334155", fg=COLOR_TEXT_MUTED,
            hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            state="disabled", command=self.finish_cabinet_inspection
        )
        self.btn_finish_cabinet.pack(fill="x")

        self.select_medicine_to_inspect(CABINET_MEDICINES[0])

    def select_medicine_to_inspect(self, med):
        self.current_med_inspect = med
        for w in self.inspect_details.winfo_children():
            w.destroy()

        card = tk.Frame(self.inspect_details, bg=COLOR_SURFACE_LIGHT, padx=12, pady=10, bd=1, relief="solid")
        card.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="x", pady=5)

        card_split = tk.Frame(card, bg=COLOR_SURFACE_LIGHT)
        card_split.pack(fill="x")

        # รูปภาพตัวอย่างยา
        med_img_file = med.get("image", "")
        if med_img_file:
            im = get_image(med_img_file, (120, 120))
            if im:
                pic_box = tk.Frame(card_split, bg=COLOR_SURFACE, bd=1, relief="ridge", padx=6, pady=4)
                pic_box.pack(side="left", padx=(0, 12))
                lbl_pic = tk.Label(pic_box, image=im, bg=COLOR_SURFACE)
                lbl_pic.image = im
                lbl_pic.pack()
                tk.Label(pic_box, text="ภาพตัวอย่างยา", font=FONT_SMALL, fg=COLOR_YELLOW, bg=COLOR_SURFACE).pack(pady=(2, 0))

        text_info = tk.Frame(card_split, bg=COLOR_SURFACE_LIGHT)
        text_info.pack(side="left", fill="both", expand=True)

        tk.Label(text_info, text=f"🔍 กำลังตรวจสอบ: {med['name']}", font=FONT_HEADING, fg=COLOR_ACCENT, bg=COLOR_SURFACE_LIGHT).pack(anchor="w")
        tk.Label(text_info, text=f"• หมวดหมู่: {med['type']}", font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT).pack(anchor="w", pady=1)
        if med.get("classification"):
            tk.Label(text_info, text=f"• ประเภท: {med['classification']}", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE_LIGHT).pack(anchor="w")
        if med.get("short_effect"):
            tk.Label(text_info, text=f"• สรรพคุณ: {med['short_effect']}", font=FONT_BODY_BOLD, fg=COLOR_GREEN, bg=COLOR_SURFACE_LIGHT).pack(anchor="w", pady=1)
        if med.get("quantity"):
            tk.Label(text_info, text=f"• ปริมาณที่พบ: {med['quantity']}", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT).pack(anchor="w", pady=1)
        tk.Label(text_info, text=f"• วันหมดอายุ: {med['expiry']}", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT).pack(anchor="w", pady=1)
        if med.get("storage_condition"):
            tk.Label(text_info, text=f"• ตำแหน่งจัดเก็บ: {med['storage_condition']}", font=FONT_BODY, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT, wraplength=380, justify="left").pack(anchor="w", pady=1)
        if med.get("packaging_condition"):
            tk.Label(text_info, text=f"• สภาพบรรจุภัณฑ์: {med['packaging_condition']}", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, wraplength=380, justify="left").pack(anchor="w", pady=1)
        tk.Label(text_info, text=f"• สภาพจริงที่มองเห็น: {med['appearance']}", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, wraplength=380, justify="left").pack(anchor="w", pady=1)

        card_cat_file = med.get("card_image", "")
        StyledButton(
            text_info, text="📖 เปิดดูคู่มือโปสเตอร์หมวดนี้ ➔",
            font=FONT_SMALL, bg=COLOR_SURFACE, fg=COLOR_ACCENT, hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=10, pady=2,
            command=lambda cid=card_cat_file: show_moph_poster_modal(self, initial_category_id=cid)
        ).pack(anchor="w", pady=(5, 0))

        # แผงกดเลือกว่ายาดีหรือยาเสีย
        action_box = tk.Frame(self.inspect_details, bg=COLOR_SURFACE)
        action_box.pack(fill="x", pady=10)

        tk.Label(action_box, text="คำตัดสินของคุณ:", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE).pack(anchor="w", pady=(0, 5))

        btn_row = tk.Frame(action_box, bg=COLOR_SURFACE)
        btn_row.pack(fill="x")

        already_checked = med["id"] in self.checked_medicines

        btn_keep = StyledButton(
            btn_row, text="🟢 สภาพดี (เก็บไว้ใช้งานต่อ)",
            font=FONT_BODY_BOLD, bg="#065f46" if not already_checked else COLOR_SURFACE_LIGHT,
            fg=COLOR_TEXT_MAIN, hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            command=lambda: self.judge_medicine(med, decision=False)
        )
        btn_keep.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_throw = StyledButton(
            btn_row, text="🔴 เสื่อมคุณภาพ / หมดอายุ (ทิ้งและซื้อใหม่)",
            font=FONT_BODY_BOLD, bg="#991b1b" if not already_checked else COLOR_SURFACE_LIGHT,
            fg=COLOR_TEXT_MAIN, hover_bg=COLOR_RED_HOVER, hover_fg=COLOR_TEXT_MAIN,
            command=lambda: self.judge_medicine(med, decision=True)
        )
        btn_throw.pack(side="right", fill="x", expand=True, padx=(5, 0))

        if already_checked:
            dec = self.checked_medicines[med["id"]]
            res_txt = "✅ คุณตัดสินถูกต้อง!" if dec["is_correct"] else "❌ คุณตัดสินผิดพลาด!"
            res_color = COLOR_GREEN if dec["is_correct"] else COLOR_RED
            lbl_res = tk.Label(
                self.inspect_details,
                text=f"{res_txt}\nคำอธิบาย: {med['reason']}",
                font=FONT_BODY, fg=res_color, bg=COLOR_SURFACE, justify="left", wraplength=550
            )
            lbl_res.pack(anchor="w", pady=8)

    def judge_medicine(self, med, decision):
        is_correct = (decision == med["is_expired_or_spoiled"])
        first_time = med["id"] not in self.checked_medicines

        if first_time:
            if is_correct:
                self.game_state["score"] += 20
                self.game_state["relationship"] += 3
            else:
                self.game_state["score"] = max(0, self.game_state["score"] - 5)

        self.checked_medicines[med["id"]] = {
            "user_decision": decision,
            "is_correct": is_correct
        }

        btn = self.med_buttons[med["id"]]
        if is_correct:
            btn.config(bg="#064e3b", fg="#a7f3d0", text=f"✓ {med['name']}")
        else:
            btn.config(bg="#7f1d1d", fg="#fecaca", text=f"✗ {med['name']}")

        self.update_top_bar()
        self.lbl_progress.config(text=f"ตรวจแล้ว: {len(self.checked_medicines)} / {len(CABINET_MEDICINES)} รายการ")

        if len(self.checked_medicines) >= len(CABINET_MEDICINES):
            self.btn_finish_cabinet.config(
                state="normal", bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN
            )

        title = "ถูกต้องแม่นยำ!" if is_correct else "ประเมินผิดพลาด!"
        show_knowledge_popup(self, title, "การตรวจสอบยา", med["reason"], image_name="med_cabinet.jpg")
        self.select_medicine_to_inspect(med)

    # -------------------------------------------------------------
    # สรุปผลการตรวจตู้ยา & เช็คลิสต์ยาที่ขาด (Missing Medicine Check)
    # -------------------------------------------------------------
    def finish_cabinet_inspection(self):
        for w in self.stage_container.winfo_children():
            w.destroy()

        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=25, pady=12)

        # Header
        header = tk.Frame(card, bg=COLOR_SURFACE, pady=6)
        header.pack(fill="x")
        tk.Label(
            header, text="📋 สรุปผลการตรวจตู้ยา & ตรวจสอบยาที่ขาด (Missing Medicine Check)",
            font=FONT_TITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE
        ).pack()
        tk.Label(
            header, text="คัดแยกยาเสื่อมสภาพทิ้ง และเตรียมซื้อยาจำเป็น 7 กลุ่มให้ครบตามเกณฑ์ยาบังคับ",
            font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE
        ).pack()

        # Action Buttons Area (Pinned to bottom so it is NEVER clipped)
        action_bar = tk.Frame(card, bg=COLOR_SURFACE)
        action_bar.pack(side="bottom", fill="x", padx=20, pady=(6, 12))

        # ปุ่มไปร้านชำ ซื้อของตามเช็คลิสต์
        btn_shop = StyledButton(
            action_bar, text="🛒 เข้าสู่ร้านค้า: เติมสต็อกยาบังคับให้ครบ (งบ 1,000 ฿) ➔ [Enter]",
            font=FONT_BODY_BOLD, bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=16, pady=8, command=self.start_shopping_minigame
        )
        btn_shop.pack(fill="x")
        btn_shop.focus_set()

        # ปุ่มเปิดดูคู่มือโปสเตอร์ยาสามัญ
        StyledButton(
            card, text="📋 เปิดดูคู่มือโปสเตอร์ยาสามัญประจำบ้าน ➔",
            font=FONT_SMALL, bg=COLOR_SURFACE_LIGHT, fg=COLOR_ACCENT,
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=12, pady=3, command=lambda: show_moph_poster_modal(self)
        ).pack(side="bottom", fill="x", padx=20, pady=(2, 4))

        info_bar = tk.Frame(card, bg="#1e293b", padx=12, pady=4)
        info_bar.pack(side="bottom", fill="x", padx=20, pady=(2, 4))
        tk.Label(info_bar, text="💡 ยาสามัญประจำบ้านสังเกต 'กรอบสีเขียว' | ยาใช้ภายนอกมี 'กรอบสีแดง' ห้ามรับประทาน!", font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg="#1e293b").pack()

        # Split into 2 columns: Expired/Spoiled vs Missing to Buy
        cols_frame = tk.Frame(card, bg=COLOR_SURFACE)
        cols_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Col 1: ยาที่ต้องทิ้ง (ซ้าย)
        left_col = tk.Frame(cols_frame, bg=COLOR_SURFACE_LIGHT, bd=1, relief="solid", padx=12, pady=8)
        left_col.config(highlightbackground=COLOR_RED, highlightthickness=1)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left_col, text="🗑️ ยาเสื่อมคุณภาพ / หมดอายุ (ทิ้งทันที)", font=FONT_HEADING, fg=COLOR_RED, bg=COLOR_SURFACE_LIGHT).pack(anchor="w", pady=(0, 4))
        spoiled_items = [m for m in CABINET_MEDICINES if m["is_expired_or_spoiled"]]
        for s in spoiled_items:
            tk.Label(left_col, text=f"• {s['name']}\n  ({s['appearance'][:36]}...)", font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, justify="left").pack(anchor="w", pady=1)

        tk.Label(left_col, text="\n✅ ยาที่ยังสภาพดี เก็บต่อได้:\n• ยาธาตุน้ำแดง (สารละลายใส ไม่ตกตะกอน)\n• ยาหม่องขี้ผึ้ง (เนื้อเนียน ไม่แยกชั้น)", font=FONT_SMALL, fg=COLOR_GREEN, bg=COLOR_SURFACE_LIGHT, justify="left").pack(anchor="w", pady=(4, 0))

        # Col 2: เช็คลิสต์ยาที่ขาด (ขวา)
        right_col = tk.Frame(cols_frame, bg=COLOR_SURFACE_LIGHT, bd=1, relief="solid", padx=12, pady=8)
        right_col.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
        right_col.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(right_col, text="🛒 เช็คลิสต์ยาจำเป็นที่ 'ขาด' จากตู้ยา", font=FONT_HEADING, fg=COLOR_ACCENT, bg=COLOR_SURFACE_LIGHT).pack(anchor="w", pady=(0, 4))
        for item in MISSING_CABINET_MEDICINES:
            tk.Label(right_col, text=f"• {item['name']}\n  - {item['reason'][:38]}...", font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, justify="left").pack(anchor="w", pady=1)

        self.bind("<Return>", lambda e: self.start_shopping_minigame())
        self.bind("<space>", lambda e: self.start_shopping_minigame())

    # -------------------------------------------------------------
    # มินิเกม 2: ช้อปปิ้งร้านชำ & ตรวจสอบสต็อกยาบังคับ (งบ 1,000 บาท)
    # -------------------------------------------------------------
    def start_shopping_minigame(self):
        for w in self.stage_container.winfo_children():
            w.destroy()

        self.shopping_budget = 1000

        # Header
        header = tk.Frame(self.stage_container, bg=COLOR_SURFACE, pady=8, padx=15, bd=1, relief="solid")
        header.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        header.pack(fill="x", pady=(0, 8))

        tk.Label(
            header, text="🛒 ร้านชำจำลอง: ภารกิจเติมสต็อกยาบังคับ (งบ 1,000 บาท)",
            font=FONT_HEADING, fg=COLOR_YELLOW, bg=COLOR_SURFACE
        ).pack(side="left")

        # Live Checklist Tracker
        self.lbl_checklist_tracker = tk.Label(
            header, text="📋 ยาบังคับในตะกร้า: 0 / 7 กลุ่ม (ยังไม่ครบ ⚠️)",
            font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg=COLOR_SURFACE
        )
        self.lbl_checklist_tracker.pack(side="left", padx=15)

        self.lbl_money = tk.Label(
            header, text="💰 เงินคงเหลือ: 1,000 / 1,000 บาท",
            font=FONT_HEADING, fg=COLOR_GREEN, bg=COLOR_SURFACE
        )
        self.lbl_money.pack(side="right")

        StyledButton(
            header, text="📋 คู่มือโปสเตอร์ยาสามัญ",
            font=FONT_SMALL, bg="#0284c7", fg="white",
            hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
            padx=10, pady=3, command=lambda: show_moph_poster_modal(self)
        ).pack(side="right", padx=(0, 10))

        # Body
        body = tk.Frame(self.stage_container, bg=COLOR_BG)
        body.pack(fill="both", expand=True)

        # ฝั่งซ้าย: สินค้าบนชั้นวาง (Scrollable Canvas แบบ Responsive เต็มพื้นที่)
        left_shop = tk.Frame(body, bg=COLOR_SURFACE, bd=1, relief="solid")
        left_shop.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        left_shop.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(
            left_shop, text="🛒 ชั้นวางสินค้า (เลือกยาบังคับ 7 กลุ่มให้ครบก่อนงบหมด 1,000 บาท)",
            font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE, pady=6
        ).pack(fill="x")

        canvas_shop = tk.Canvas(left_shop, bg=COLOR_SURFACE, highlightthickness=0)
        scroll_shop = tk.Scrollbar(left_shop, orient="vertical", command=canvas_shop.yview)
        items_frame = tk.Frame(canvas_shop, bg=COLOR_SURFACE)

        items_frame.bind("<Configure>", lambda e: canvas_shop.configure(scrollregion=canvas_shop.bbox("all")))
        self.shop_win_id = canvas_shop.create_window((0, 0), window=items_frame, anchor="nw")

        def _on_shop_canvas_configure(event):
            if canvas_shop.winfo_exists():
                canvas_shop.itemconfig(self.shop_win_id, width=event.width)
        canvas_shop.bind("<Configure>", _on_shop_canvas_configure)

        def _on_shop_mousewheel(event):
            if canvas_shop.winfo_exists():
                canvas_shop.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas_shop.bind("<MouseWheel>", _on_shop_mousewheel)

        canvas_shop.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=4)
        scroll_shop.pack(side="right", fill="y", pady=4)

        self.item_check_buttons = {}
        for item in SHOP_ITEMS:
            row = tk.Frame(items_frame, bg=COLOR_SURFACE_LIGHT, pady=4, padx=8)
            row.pack(fill="x", pady=2)
            row.bind("<MouseWheel>", _on_shop_mousewheel)

            # 1. ปุ่มหยิบใส่ตะกร้า (Pack ขวาสุด)
            btn = StyledButton(
                row, text="➕ หยิบใส่",
                font=FONT_SMALL, bg=COLOR_ACCENT, fg=COLOR_BG,
                hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
                padx=10, pady=3,
                command=lambda i=item: self.toggle_shop_item(i)
            )
            btn.pack(side="right", padx=(6, 2))
            self.item_check_buttons[item["id"]] = btn

            # 2. ราคา
            lbl_price = tk.Label(row, text=f"{item['price']} ฿", font=FONT_BODY_BOLD, fg=COLOR_GREEN, bg=COLOR_SURFACE_LIGHT, width=6, anchor="e")
            lbl_price.pack(side="right", padx=(2, 6))

            # 3. ภาพ Thumbnail ไอคอนยา
            item_thumb = get_image(item.get("image", ""), (32, 32))
            if item_thumb:
                lbl_icon = tk.Label(row, image=item_thumb, bg=COLOR_SURFACE_LIGHT)
                lbl_icon.image = item_thumb
                lbl_icon.pack(side="left", padx=(2, 6))

            # 4. ป้ายหมวดหมู่
            cat_col = COLOR_YELLOW if item["is_needed"] else COLOR_PURPLE
            cat_tag = f"[{item['category'][:10]}]"
            lbl_cat = tk.Label(row, text=cat_tag, font=FONT_SMALL, fg=cat_col, bg=COLOR_SURFACE_LIGHT, width=12, anchor="w")
            lbl_cat.pack(side="left", padx=(0, 4))

            # 5. ชื่อสินค้า + สรรพคุณสั้นๆ 1 บรรทัด
            name_box = tk.Frame(row, bg=COLOR_SURFACE_LIGHT)
            name_box.pack(side="left", fill="x", expand=True, padx=4)
            name_lbl = tk.Label(name_box, text=item["name"], font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, anchor="w")
            name_lbl.pack(anchor="w")
            name_lbl.bind("<MouseWheel>", _on_shop_mousewheel)

            effect_text = item.get("short_effect", item.get("desc", ""))
            effect_lbl = tk.Label(name_box, text=f"• สรรพคุณ: {effect_text}", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE_LIGHT, anchor="w")
            effect_lbl.pack(anchor="w")
            effect_lbl.bind("<MouseWheel>", _on_shop_mousewheel)

        # ฝั่งขวา: ระบบตรวจสอบสต็อกยาบังคับ (Missing Stock Refill Tracker)
        right_cart = tk.Frame(body, bg=COLOR_SURFACE, width=320, bd=1, relief="solid")
        right_cart.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        right_cart.pack(side="right", fill="both")
        right_cart.pack_propagate(False)

        # ส่วนตรวจสอบยาบังคับที่ขาด
        tk.Label(
            right_cart, text="🎯 ตรวจสอบยาบังคับที่ขาด (7 กลุ่ม)",
            font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg=COLOR_SURFACE
        ).pack(pady=(6, 2))

        stock_box = tk.Frame(right_cart, bg=COLOR_SURFACE_LIGHT, padx=8, pady=4, bd=1, relief="solid")
        stock_box.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        stock_box.pack(fill="x", padx=8, pady=(2, 4))

        self.stock_status_labels = {}
        mandatory_categories = [
            ("pain", "💊 ยาแก้ปวด ลดไข้", "พาราเซตามอล"),
            ("ors", "💧 ผงเกลือแร่ ORS", "แก้ท้องเสีย"),
            ("stomach", "🍵 ยาลดกรด/ขับลม", "ธาตุน้ำขาว / แอนตาซิล"),
            ("allergy", "🌸 ยาแก้แพ้ ลดน้ำมูก", "เซทิริซีน / CPM"),
            ("nss", "🧪 น้ำเกลือ 0.9% NSS", "ล้างแผลสด"),
            ("betadine", "🩹 โพวิโดน-ไอโอดีน", "ยาใส่แผลสด"),
            ("gauze", "🩹 ชุดทำแผล", "ผ้าก๊อซปลอดเชื้อ")
        ]
        for cat_key, cat_title, _ in mandatory_categories:
            s_row = tk.Frame(stock_box, bg=COLOR_SURFACE_LIGHT)
            s_row.pack(fill="x", pady=1)
            tk.Label(s_row, text=f"• {cat_title}", font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT).pack(side="left")
            s_badge = tk.Label(s_row, text="[ ❌ ขาด ]", font=(FONT_FAMILY, 8, "bold"), fg=COLOR_RED, bg=COLOR_SURFACE_LIGHT)
            s_badge.pack(side="right")
            self.stock_status_labels[cat_key] = s_badge

        # ตะกร้าสินค้า
        tk.Label(right_cart, text="🧺 สินค้าในตะกร้าของคุณ", font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE).pack(pady=(4, 2))
        self.cart_listbox = tk.Listbox(
            right_cart, font=FONT_SMALL, bg=COLOR_BG, fg=COLOR_TEXT_MAIN,
            selectbackground=COLOR_ACCENT, bd=0, highlightthickness=1,
            highlightbackground=COLOR_BORDER, height=4
        )
        self.cart_listbox.pack(fill="both", expand=True, padx=8, pady=2)

        # สรุปยอดและปุ่มชำระเงิน
        summary_panel = tk.Frame(right_cart, bg=COLOR_SURFACE, pady=4)
        summary_panel.pack(fill="x", padx=8, side="bottom")

        self.lbl_cart_total = tk.Label(summary_panel, text="รวมเป็นเงิน: 0 บาท", font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE)
        self.lbl_cart_total.pack(anchor="w")

        self.lbl_budget_status = tk.Label(summary_panel, text="คงเหลือ: 1,000 บาท", font=FONT_BODY_BOLD, fg=COLOR_GREEN, bg=COLOR_SURFACE)
        self.lbl_budget_status.pack(anchor="w", pady=(0, 4))

        self.btn_checkout = StyledButton(
            summary_panel, text="💳 ตรวจรับสินค้าและชำระเงิน ➔",
            font=FONT_BODY_BOLD, bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            command=self.handle_checkout
        )
        self.btn_checkout.pack(fill="x", pady=(2, 4))

    def toggle_shop_item(self, item):
        item_id = item["id"]
        btn = self.item_check_buttons[item_id]

        if item_id in self.shopping_cart:
            self.shopping_cart.remove(item_id)
            btn.config(text="➕ หยิบใส่", bg=COLOR_ACCENT, fg=COLOR_BG)
        else:
            self.shopping_cart.add(item_id)
            btn.config(text="➖ เอาออก", bg=COLOR_RED, fg=COLOR_TEXT_MAIN)

        self.refresh_cart_display()

    def refresh_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        total_price = 0
        for item in SHOP_ITEMS:
            if item["id"] in self.shopping_cart:
                self.cart_listbox.insert(tk.END, f"{item['name']} ({item['price']} ฿)")
                total_price += item["price"]

        remaining = self.shopping_budget - total_price
        self.lbl_cart_total.config(text=f"รวมเป็นเงิน: {total_price} บาท")

        # ตรวจสอบจำนวนกลุ่มยาจำเป็นที่เลือกแล้ว (7 หมวด)
        required_cats = {"pain", "allergy", "ors", "stomach", "nss", "betadine", "gauze"}
        cart_items = [item for item in SHOP_ITEMS if item["id"] in self.shopping_cart]
        covered = {item.get("cat_key") for item in cart_items if item.get("cat_key")}.intersection(required_cats)
        count = len(covered)

        # อัปเดตป้ายสถานะสต็อกยาแต่ละตัว (Missing Medicine Tracker)
        if hasattr(self, "stock_status_labels"):
            for cat_key, s_badge in self.stock_status_labels.items():
                if cat_key in covered:
                    s_badge.config(text="[ ✓ เติมแล้ว ]", fg=COLOR_GREEN)
                else:
                    s_badge.config(text="[ ❌ ขาด ]", fg=COLOR_RED)

        if hasattr(self, "lbl_checklist_tracker"):
            if count == len(required_cats):
                self.lbl_checklist_tracker.config(
                    text=f"📋 ยาบังคับในตะกร้า: {count} / {len(required_cats)} กลุ่ม (ครบ 100% ✓)",
                    fg=COLOR_GREEN
                )
            else:
                self.lbl_checklist_tracker.config(
                    text=f"📋 ยาบังคับในตะกร้า: {count} / {len(required_cats)} กลุ่ม (ยังขาด ⚠️)",
                    fg=COLOR_YELLOW
                )

        if remaining >= 0:
            self.lbl_budget_status.config(text=f"คงเหลือ: {remaining} บาท", fg=COLOR_GREEN)
            self.lbl_money.config(text=f"💰 เงินคงเหลือ: {remaining} / 1,000 บาท", fg=COLOR_GREEN)
            self.btn_checkout.config(state="normal", bg=COLOR_GREEN)
        else:
            self.lbl_budget_status.config(text=f"เกินงบ {abs(remaining)} บาท! ❌", fg=COLOR_RED)
            self.lbl_money.config(text=f"⚠️ เกินงบ: {total_price} / 1,000 บาท", fg=COLOR_RED)
            self.btn_checkout.config(state="disabled", bg=COLOR_SURFACE_LIGHT)

    def handle_checkout(self):
        # 1. คำนวณยอดเงินรวมที่ใช้ซื้อสินค้าในตะกร้า
        total_spent = sum(item["price"] for item in SHOP_ITEMS if item["id"] in self.shopping_cart)
        if total_spent > self.shopping_budget:
            show_knowledge_popup(self, "เงินไม่พอ!", "การบริหารงบประมาณ", "คุณใช้เงินเกินงบ 1,000 บาท! กรุณานำของบางชิ้นออกจากตะกร้าก่อนชำระเงิน")
            return

        # 2. หมวดหมู่ยาจำเป็น 7 กลุ่มหลักที่ตู้ยาหอพักต้องมีเพื่อความปลอดภัย
        required_categories = {
            "pain": "ยาแก้ปวดลดไข้ (พาราเซตามอล)",
            "allergy": "ยาแก้แพ้ลดน้ำมูก (เซทิริซีน หรือ คลอร์เฟนิรามีน)",
            "ors": "ผงเกลือแร่ ORS แก้ท้องเสีย",
            "stomach": "ยาลดกรด / ขับลมแก้ท้องอืด (ธาตุน้ำขาว)",
            "nss": "น้ำเกลือล้างแผล 0.9% NSS",
            "betadine": "ยาใส่แผลสด (โพวิโดน-ไอโอดีน)",
            "gauze": "ชุดทำแผล/ผ้าก๊อซปลอดเชื้อ"
        }
        
        # 3. ตรวจสอบว่าในตะกร้ามีกลุ่มยาจำเป็นครบ 7 กลุ่มหรือไม่ (ใช้ Set Comprehension)
        cart_items = [item for item in SHOP_ITEMS if item["id"] in self.shopping_cart]
        covered_cats = {item.get("cat_key") for item in cart_items if item.get("cat_key")}
        missing_cat_keys = [k for k in required_categories if k not in covered_cats]
        missing_names = [required_categories[k] for k in missing_cat_keys]

        # 4. คำนวณเงินทอนคงเหลือ (สำหรับเงื่อนไขโบนัสกิน Sushiro)
        rem_budget = self.shopping_budget - total_spent

        # หากซื้อของไม่ครบตาม 7 กลุ่มจำเป็น -> เข้าสู่ BAD ENDING (วิกฤตกลางดึก)
        if len(missing_cat_keys) > 0:
            self.show_bad_ending_missing_meds(missing_names, total_spent, rem_budget)
            return

        # เมื่อซื้อของครบ 7 กลุ่มจำเป็น -> ได้รับคะแนนเต็มและโบนัสเติมสต็อกยาบังคับครบ 100%
        score_gain = 80  # 50 แต้มผ่านด่าน + 30 แต้มโบนัสสต็อกครบ
        rel_gain = 15
        has_burn_cream = "burn" in covered_cats
        bonus_msg = ""
        if has_burn_cream:
            score_gain += 10
            bonus_msg = " + ซื้อครีมแผลไฟไหม้เสริม (+10 แต้มโบนัส)"

        summary_msg = f"ยอดเยี่ยมมาก! เติมสต็อกยาบังคับครบ 7 รายการสมบูรณ์แบบ (+30 แต้มโบนัส){bonus_msg}! ใช้เงินไป {total_spent} ฿ เหลือเงินทอน {rem_budget} ฿"

        self.game_state["score"] += score_gain
        self.game_state["relationship"] += rel_gain
        self.game_state["remaining_budget"] = rem_budget
        self.game_state["inventory"] = list(self.shopping_cart)
        self.update_top_bar()

        self.start_storage_quiz(missing_names, total_spent, score_gain, rel_gain, summary_msg)

    def show_bad_ending_missing_meds(self, missing_names, total_spent, rem_budget):
        for w in self.stage_container.winfo_children():
            w.destroy()
        self.dialogue_box.pack_forget()

        # สร้างการ์ด Bad Ending
        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=3, relief="solid")
        card.config(highlightbackground=COLOR_RED, highlightthickness=3)
        card.pack(fill="both", expand=True, padx=30, pady=15)

        # ส่วนหัว Bad Ending
        tk.Label(
            card, text="💀 BAD ENDING: ยาสามัญไม่พร้อม วิกฤตกลางดึก!",
            font=FONT_TITLE, fg=COLOR_RED, bg=COLOR_SURFACE, pady=10
        ).pack(fill="x")

        # บรรยายเหตุการณ์
        pname = self.game_state.get("player_name", "คุณ")
        story_text = (
            f"ในคืนต่อมา... ขณะที่กำลังทำงานดึก ทีเกิดอุบัติเหตุฉุกเฉินและมีอาการบาดเจ็บกะทันหัน!\n"
            f"{pname} รีบวิ่งไปเปิดตู้ยาเพื่อหาอุปกรณ์ปฐมพยาบาลและยาจำเป็นมารักษาเพื่อน...\n"
            f"แต่กลับพบว่า 'ไม่มีของจำเป็นอยู่ในตู้ยาเลย!' เพราะตอนไปร้านชำไม่ได้ซื้อยาจำเป็นมาเติมสต็อกให้ครบ 7 กลุ่มบังคับ\n"
            f"อาการของทีทรุดหนักลงอย่างรวดเร็ว แผลเสี่ยงติดเชื้อรุนแรงจนสุดท้ายต้องโทร 1669 หามส่งโรงพยาบาลฉุกเฉินกลางดึก!"
        )
        tk.Label(
            card, text=story_text,
            font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, justify="center", wraplength=760
        ).pack(pady=(0, 10))

        # กล่องแสดงรายการยาที่ขาด
        missing_frame = tk.Frame(card, bg=COLOR_SURFACE_LIGHT, padx=15, pady=10, bd=1, relief="solid")
        missing_frame.config(highlightbackground=COLOR_RED, highlightthickness=1)
        missing_frame.pack(fill="both", expand=True, padx=25, pady=5)

        tk.Label(
            missing_frame, text=f"⚠️ รายการกลุ่มยาจำเป็นที่ขาดไป ({len(missing_names)} กลุ่ม):",
            font=FONT_HEADING, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT
        ).pack(anchor="w", pady=(0, 5))

        for item_name in missing_names:
            tk.Label(
                missing_frame, text=f"  ❌ {item_name}",
                font=FONT_BODY, fg="#fca5a5", bg=COLOR_SURFACE_LIGHT
            ).pack(anchor="w", pady=1)

        # ข้อคิดความรู้ทางการแพทย์
        tk.Label(
            missing_frame,
            text="\n💡 คำแนะนำทางการแพทย์: ยาสามัญประจำบ้าน 7 กลุ่มหลัก (แก้ปวดลดไข้, ยาแก้แพ้, ผงเกลือแร่ ORS, ยาลดกรด/ขับลม, น้ำเกลือ NSS, เบตาดีน, ผ้าก๊อซทำแผล) ควรมีติดบ้านไว้เสมอเพื่อพร้อมรับมือยามฉุกเฉินกลางดึก! (สำหรับครีมรักษาแผลไฟไหม้ Silverderm เป็นยาเฉพาะทางทางเลือก ขั้นปฐมพยาบาลแรกที่สำคัญที่สุดคือน้ำสะอาดไหลผ่าน 15-20 นาทีและปิดด้วยผ้าสะอาด)",
            font=FONT_SMALL, fg=COLOR_ACCENT, bg=COLOR_SURFACE_LIGHT, justify="left", wraplength=720
        ).pack(anchor="w", pady=(5, 0))

        # ปุ่มกดย้อนกลับไปซื้อใหม่
        btn_box = tk.Frame(card, bg=COLOR_SURFACE)
        btn_box.pack(side="bottom", fill="x", padx=25, pady=12)

        StyledButton(
            btn_box, text="🔄 กลับไปเลือกซื้อยาให้ครบตามเช็คลิสต์ (ร้านขายยา) [Enter]",
            font=FONT_HEADING, bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=20, pady=10,
            command=self.restart_shopping_after_bad_ending
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        StyledButton(
            btn_box, text="🏠 กลับสู่หน้าจอหลัก",
            font=FONT_BODY, bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_BORDER, hover_fg=COLOR_TEXT_MAIN,
            padx=16, pady=10,
            command=self.on_exit_to_menu
        ).pack(side="right", padx=(10, 0))

    def restart_shopping_after_bad_ending(self):
        self.start_shopping_minigame()


    # -------------------------------------------------------------
    # จัดตู้ยา & คำถามการเก็บรักษายา
    # -------------------------------------------------------------
    def start_storage_quiz(self, missing_needed, total_spent, score_gain=0, rel_gain=0, summary_msg=""):
        for w in self.stage_container.winfo_children():
            w.destroy()

        self.bg_canvas = tk.Canvas(self.stage_container, bg=COLOR_BG, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.bind("<Configure>", self._on_bg_resize)

        self.dialogue_box.pack(fill="x", side="bottom", padx=20, pady=(0, 15), ipady=5)
        pname = self.game_state["player_name"]
        rem = 1000 - total_spent

        self.storage_scripts = []
        if summary_msg:
            self.storage_scripts.append(("ระบบ", f"💳 {summary_msg} (คะแนน +{score_gain}, ความสัมพันธ์ +{rel_gain})", COLOR_PURPLE, "dorm", "none"))

        self.storage_scripts.append(
            (pname, f"กลับมาถึงหอแล้ว! ใช้เงินไปทั้งหมด {total_spent} บาท มีเงินทอนเหลือ {rem} บาท", "#fb923c", "dorm", "none")
        )

        # บทแซวพาราน้ำเชื่อม
        if "item_para_syrup" in self.shopping_cart:
            self.storage_scripts.append(("ที", f"55555 โตจนหมาเลียตูดไม่ถึงแล้ว ยังจะกินพาราน้ำเชื่อมเด็กอยู่อีกเหรอแก {pname}! กลืนยาเม็ดไม่เป็นใช่มั้ยเนี่ย!", "#38bdf8", "dorm", "happy"))
            self.storage_scripts.append((pname, "หุบปากไปเลยที! ยาน้ำเชื่อมสตรอว์เบอร์รีมันอร่อยดีออก ใครจะไปอยากกลืนยาเม็ดขมติดคอแบบแกล่ะ!", "#fb923c", "dorm", "angry"))

        # บทตรวจงบ Sushiro (<200 vs >=200)
        if rem < 200:
            self.storage_scripts.append((pname, f"แต่ดูเงินทอนสิ... เหลือแค่ {rem} บาทเอง เดือนนี้อดกินแล้วสินะ Sushiro ของโปรดเรา... T_T ซื้อของเพลินไปหน่อย เงินไม่พอกินซูชิสายพานแล้ว...", "#fb923c", "dorm", "sleepy"))
            self.storage_scripts.append(("ที", "ฮือออ ไม่เป็นไรน่าเพื่อน... ไว้งวดหน้าค่อยไปกินใหม่ อย่างน้อยตอนนี้เราก็มียาตุนไว้รอดตายแล้วนะ!", "#38bdf8", "dorm", "happy"))
        else:
            self.storage_scripts.append((pname, f"แถมดูเงินทอนสิ! มีเงินเหลือตั้ง {rem} บาท (เกิน 200 บาท) บริหารเงินขั้นเทพ!", "#fb923c", "dorm", "happy"))
            self.storage_scripts.append(("ที", f"เย้! เย็นนี้เราสองคนแวะไปฉลอง Sushiro ของโปรดกันได้แล้วเพื่อนรัก! รอดตายแถมได้กินซูชิฟินๆ!", "#38bdf8", "dorm", "happy"))

        self.storage_scripts.extend([
            (pname, "เอาล่ะ เลิกดีใจแล้วเอาของไปจัดเก็บในตู้ยาให้เรียบร้อยเลยที", "#fb923c", "dorm", "talk"),
            ("ที", "โอเคคค... ตู้ยานี่เอาไว้ในห้องน้ำมั้ย? ตอนอาบน้ำแปรงฟันจะได้หยิบง่ายดี หรือไม่ก็ยัดใส่ตู้เย็นให้ยาเย็นสดชื่นดีมั้ย?", "#38bdf8", "dorm", "sleepy"),
            (pname, "หยุดความคิดนั้นเดี๋ยวนี้เลยนะที! แกจะเอายาไปเก็บในที่แบบนั้นไม่ได้!", "#fb923c", "dorm", "angry")
        ])
        self.storage_dialogue_idx = 0
        self.show_storage_dialogue()

    def show_storage_dialogue(self):
        if self.storage_dialogue_idx < len(self.storage_scripts):
            spk, txt, col, bg_type, char_pose = self.storage_scripts[self.storage_dialogue_idx]
            self.render_background_and_character(bg_type, char_pose)
            self.dialogue_box.set_dialogue(spk, txt, col, show_next_btn=True)
            self.dialogue_box.on_next = self.advance_storage_dialogue
        else:
            self.prompt_storage_choice()

    def advance_storage_dialogue(self):
        self.storage_dialogue_idx += 1
        self.show_storage_dialogue()

    def prompt_storage_choice(self):
        self.dialogue_box.pack_forget()

        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(
            card, text="❓ คุณจะอธิบายวิธีเก็บรักษายาที่ถูกต้องให้ทีฟังว่าอย่างไร?",
            font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE, pady=12
        ).pack(fill="x")

        choices = [
            ("1. เก็บยาในตู้เย็นทุกชนิดเพื่อความเย็น และเก็บในห้องน้ำเพราะหยิบสะดวกเวลาล้างหน้า", False,
             "ห้องน้ำมีความชื้นสูงมากทำให้ยาเม็ดบวมและเสื่อมเร็ว ส่วนตู้เย็นห้ามเก็บเด็ดขาดเว้นแต่ฉลากระบุ เพราะความชื้นจะทำลายยา"),
            ("2. เก็บในที่แห้ง อุณหภูมิห้องปกติ (ไม่เกิน 25-30°C) พ้นจากแสงแดด ห้ามเก็บในห้องน้ำและตู้เย็น (เว้นแต่ฉลากสั่ง)", True,
             "ถูกต้องตามหลักการแพทย์! ยาส่วนใหญ่ต้องเก็บในที่แห้ง พ้นแสงแดดและความร้อน ห้ามเก็บในที่ชื้นอย่างห้องน้ำ และแยกยาใช้ภายนอกออกจากยากินเสมอ"),
            ("3. เทรวมกันในกระปุกเดียวเพื่อประหยัดพื้นที่ แล้ววางไว้ข้างหน้าต่างรับแดดฆ่าเชื้อ", False,
             "การนำยามารวมกันทำให้สารเคมีทำปฏิกิริยากันและอาจหยิบยากินผิด ส่วนแสงแดดและความร้อนจะเร่งให้ยาเสื่อมสภาพในเวลาอันรวดเร็ว")
        ]

        for txt, is_corr, expl in choices:
            btn = StyledButton(
                card, text=txt, font=FONT_BODY,
                bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
                justify="left", wraplength=740,
                command=lambda ic=is_corr, ex=expl: self.finish_storage_quiz(ic, ex)
            )
            btn.pack(fill="x", padx=20, pady=6)

    def finish_storage_quiz(self, is_correct, explanation):
        if is_correct:
            self.game_state["score"] += 30
            self.game_state["relationship"] += 10

        self.update_top_bar()
        self.show_scene1_summary(is_correct, explanation)

    def show_scene1_summary(self, is_correct=True, explanation=""):
        for w in self.stage_container.winfo_children():
            w.destroy()
        self.dialogue_box.pack_forget()

        if "scene1" not in self.game_state["completed_scenes"]:
            self.game_state["completed_scenes"].append("scene1")
        self.game_state["current_scene"] = "scene2"
        save_game(self.game_state, "auto")

        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_GREEN, highlightthickness=2)
        card.pack(fill="both", expand=True, padx=30, pady=15)

        # Header Title
        tk.Label(
            card, text="🎉 จบฉากที่ 1: ตู้ยาสามัญ & ห้างสรรพสินค้า",
            font=FONT_TITLE, fg=COLOR_GREEN, bg=COLOR_SURFACE, pady=8
        ).pack(fill="x")

        # Auto-Save Pill
        save_pill = tk.Frame(card, bg="#064e3b", padx=12, pady=3, highlightbackground=COLOR_GREEN, highlightthickness=1)
        save_pill.pack(pady=(0, 4))
        tk.Label(
            save_pill, text="💾 ระบบได้ทำการบันทึกข้อมูล (Auto-Save) เข้าสู่ฉากที่ 2 เรียบร้อยแล้ว",
            font=FONT_SMALL, fg="#a7f3d0", bg="#064e3b"
        ).pack()

        # Action Buttons Pinned to Bottom (Guaranteed Visible)
        btn_box = tk.Frame(card, bg=COLOR_SURFACE)
        btn_box.pack(side="bottom", fill="x", padx=25, pady=(10, 15))

        btn_next = StyledButton(
            btn_box, text="เข้าสู่ฉากที่ 2: เช้าวันใหม่ & วิกฤตน้ำร้อนลวกในห้องครัว ➡️ [Enter]",
            font=FONT_HEADING, bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=20, pady=10,
            command=self.advance_to_next_scene
        )
        btn_next.pack(side="left", fill="x", expand=True, padx=(0, 10))
        btn_next.focus_set()

        StyledButton(
            btn_box, text="🏠 กลับสู่หน้าจอหลัก",
            font=FONT_BODY, bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_BORDER, hover_fg=COLOR_TEXT_MAIN,
            padx=16, pady=10,
            command=self.on_exit_to_menu
        ).pack(side="right", padx=(10, 0))

        # Content Container in Middle
        content_box = tk.Frame(card, bg=COLOR_SURFACE)
        content_box.pack(fill="both", expand=True, padx=25, pady=4)

        # Storage Quiz Feedback Box
        fb_frame = tk.Frame(content_box, bg=COLOR_SURFACE_LIGHT, padx=14, pady=6, bd=1, relief="solid")
        fb_frame.config(highlightbackground=COLOR_GREEN if is_correct else COLOR_YELLOW, highlightthickness=1)
        fb_frame.pack(fill="x", pady=4)

        if is_correct:
            tk.Label(
                fb_frame, text="✅ ตอบคำถามการเก็บรักษายาถูกต้อง! (+30 คะแนนความรู้ | +10 ความสัมพันธ์)",
                font=FONT_BODY_BOLD, fg=COLOR_GREEN, bg=COLOR_SURFACE_LIGHT
            ).pack(anchor="w")
        else:
            tk.Label(
                fb_frame, text="⚠️ คำตอบการเก็บรักษายายังไม่ถูกต้อง (+0 คะแนน)",
                font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT
            ).pack(anchor="w")

        if explanation:
            tk.Label(
                fb_frame, text=f"หลักวิชาการ: {explanation}",
                font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, justify="left", wraplength=740
            ).pack(anchor="w", pady=(2, 0))

        # Stats summary
        pname = self.game_state["player_name"]
        score = self.game_state["score"]
        rel = self.game_state["relationship"]
        rem = self.game_state.get("remaining_budget", 0)

        stats_box = tk.Frame(content_box, bg=COLOR_SURFACE, padx=10, pady=4)
        stats_box.pack(fill="x", pady=4)

        stats_text = (
            f"👤 ผู้เล่น: {pname}    |    🏆 คะแนนสะสม: {score} แต้ม    |    ❤️ ความสัมพันธ์: {rel}/100    |    💵 เงินคงเหลือ: {rem} ฿\n\n"
            "✨ ที: 'ขอบคุณมากนะแก! ถ้าไม่ได้แก ตู้ยาหอเราคงมีแต่ยาบูดแน่นอน\n"
            "ตอนนี้ตู้ยาเป็นระเบียบสุดๆ ซื้อยาจำเป็นครบ แถมเก็บรักษาถูกวิธี ปลอดภัยชัวร์!'"
        )
        tk.Label(
            stats_box, text=stats_text, font=FONT_BODY,
            fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, justify="center"
        ).pack()

        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self.advance_to_next_scene())
        self.bind("<space>", lambda e: self.advance_to_next_scene())

    def advance_to_next_scene(self):
        try:
            self.grab_release()
        except Exception:
            pass
        if "scene1" not in self.game_state["completed_scenes"]:
            self.game_state["completed_scenes"].append("scene1")
        self.game_state["current_scene"] = "scene2"
        save_game(self.game_state, "auto")
        if self.on_finish_scene:
            self.on_finish_scene()
