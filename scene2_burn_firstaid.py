"""
Scene 2: Scalds First Aid & Burn Assessment
ฉากที่ 2: การปฐมพยาบาลแผลน้ำร้อนลวก การประเมินระดับแผล และการรับมืออุบัติเหตุ
"""

import tkinter as tk
from ui_theme import (
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_LIGHT, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_GREEN,
    COLOR_GREEN_HOVER, COLOR_RED, COLOR_RED_HOVER, COLOR_YELLOW,
    COLOR_PURPLE, COLOR_BORDER,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_BODY_BOLD,
    FONT_DIALOGUE, FONT_SPEAKER, FONT_CHOICE, FONT_SMALL,
    StyledButton, get_image
)
from vn_widgets import TopStatusBar, DialogueBox, show_knowledge_popup, show_save_slots_dialog
from data import BURN_LEVELS, FIRST_AID_QUIZ_STEPS
from save_manager import save_game

class Scene2BurnFirstAidFrame(tk.Frame):
    def __init__(self, parent, game_state, on_finish_scene, on_exit_to_menu):
        super().__init__(parent, bg=COLOR_BG)
        self.parent = parent
        self.game_state = game_state
        self.on_finish_scene = on_finish_scene
        self.on_exit_to_menu = on_exit_to_menu

        # ตัวแปรควบคุมสถานะ
        self.dialogue_index = 0
        self.mistakes_count = 0
        self.current_aid_step_idx = 0
        self.failed_explanations = []

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

        self.current_bg = "bg_kitchen.jpg"
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
            "ฉากที่ 2: วิกฤตน้ำร้อนลวกในห้องครัว",
            self.game_state["score"],
            self.game_state["relationship"]
        )

    def handle_manual_save(self):
        self.game_state["current_scene"] = "scene2"
        show_save_slots_dialog(self, self.game_state, on_saved=lambda sid: self.update_top_bar())

    def render_background_and_character(self, bg_file="bg_kitchen.jpg", char_pose="none"):
        self.current_bg = bg_file
        self.current_char_pose = char_pose
        self.bg_canvas.delete("all")
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        if w < 100:
            w = 1000
            h = 450

        # พื้นหลัง
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
                "angry": "tee_happy.png"
            }
            sprite_file = pose_map.get(char_pose, f"tee_{char_pose}.png")
            sprite_h = int(h * 0.88)
            sprite_w = int(sprite_h * (848 / 1264))
            char_img = get_image(sprite_file, (sprite_w, sprite_h))
            if char_img:
                self.bg_canvas.create_image(w - sprite_w - 60, h - sprite_h, anchor="nw", image=char_img)
                self.bg_canvas.char_img = char_img

    # -------------------------------------------------------------
    # เนื้อเรื่องเริ่มต้นของฉาก 2
    # -------------------------------------------------------------
    def init_intro_dialogues(self):
        pname = self.game_state["player_name"]
        self.story_scripts = [
            ("บรรยาย", "ในวันปกติ คุณมักจะเป็นคนตื่นมาทำอาหารเช้าง่ายๆ ไว้กินกับเมท เพื่อความปลอดภัยต่อเพื่อนร่วมห้องและตัวคุณเอง...", COLOR_TEXT_MUTED, "none"),
            ("บรรยาย", "การให้คนที่นอนไม่ครบ 5 ชั่วโมงอย่าง 'ที' มาจับเตาแก๊สหรือเข้าครัว ก็ไม่ต่างจากการเอาภัยพิบัติระดับ 10 เข้าบ้าน...", COLOR_TEXT_MUTED, "none"),
            (pname, "แต่งวดนี้ ดูเหมือนฉันจะนอนเพลินไปหน่อย... เมื่อคืนปั่นโปรเจกต์ตีสาม ตอนนี้สิบโมงเช้าแล้วยังไม่อยากลุกเลย...", "#fb923c", "none"),
            ("บรรยาย", "ในระหว่างที่คุณกำลังนอนกลิ้งไปมา ตัดสินใจว่าจะหลับต่อหรือลุกไปหาอะไรกิน ในครัวก็มีเสียงดังลั่น!", COLOR_TEXT_MUTED, "none"),
            ("เสียงในครัว", "💥 เพล้งงงงงงงงงงงงงงงงงงง!", COLOR_RED, "none"),
            ("ที", "อ๊ากกกกกก! ร้อนนนนนน! ร้อนๆๆๆๆๆๆ! ฮือออออ!", "#38bdf8", "panicked"),
            (pname, "เกิดอะไรขึ้นวะเนี่ย!? เสียงทีนี่หว่า!", "#fb923c", "panicked"),
            ("บรรยาย", "คุณสะดุ้งสุดตัว วิ่งถลันออกจากห้องนอนตรงไปยังห้องครัวทันที...", COLOR_TEXT_MUTED, "panicked"),
            ("บรรยาย", "ภาพที่เห็นคือ: ที กำลังยืนสะบัดมือขวาอย่างรุนแรง หน้าตาเหยเกด้วยความเจ็บปวด บนพื้นมีเศษแก้วมัคแตกกระจายเกลื่อน ใกล้กาน้ำร้อนบนโต๊ะที่เพิ่งเดือดจัด", COLOR_TEXT_MUTED, "panicked"),
            (pname, "(ประเมินสถานการณ์) เจ้าหมอนี่... ท่าทางจะเบลอจัดจนกดน้ำร้อนใส่หลังมือตัวเองแทนที่จะลงแก้วกาแฟแน่ๆ!", "#fb923c", "panicked")
        ]

    def show_current_dialogue(self):
        if self.dialogue_index < len(self.story_scripts):
            speaker, text, color, char_pose = self.story_scripts[self.dialogue_index]
            self.render_background_and_character("bg_kitchen.jpg", char_pose)
            self.dialogue_box.set_dialogue(speaker, text, color, show_next_btn=True)
            self.dialogue_box.on_next = self.advance_story
        else:
            self.dialogue_box.pack_forget()
            self.show_first_reaction_choice()

    def advance_story(self):
        self.dialogue_index += 1
        self.show_current_dialogue()

    # -------------------------------------------------------------
    # ช้อยส์ที่ 1: สิ่งแรกที่จะทำเมื่อเจอเหตุการณ์
    # -------------------------------------------------------------
    def show_first_reaction_choice(self):
        for w in self.stage_container.winfo_children():
            w.destroy()

        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=800, height=450)

        tk.Label(
            card, text="🚨 สถานการณ์ฉุกเฉิน: พื้นเต็มไปด้วยเศษแก้ว และทียืนกุมมือร้องโวยวาย",
            font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE, pady=15
        ).pack(fill="x")

        tk.Label(
            card, text="สิ่งแรกที่คุณควรทำคืออะไร?",
            font=FONT_HEADING, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE
        ).pack(pady=(0, 15))

        options = [
            ("1. รีบวิ่งเข้าไปกระชากมือทีมาดูอาการทันที ไม่ต้องสนใจอะไรทั้งนั้น", "rush"),
            ("2. คว้าไม้กวาดใกล้ตัว กวาดเศษแก้วที่แตกกระจายไปรวมกองไว้ด้านข้างก่อน เพื่อเคลียร์ทางปลอดภัย แล้วจึงเข้าไปหาที", "sweep"),
            ("3. ยืนพิงประตูแล้วด่าทีก่อน 5 นาทีเรื่องความซุ่มซ่ามไม่ดูตาม้าตาเรือ", "scold")
        ]

        for text, val in options:
            btn = StyledButton(
                card, text=text, font=FONT_BODY,
                bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
                justify="left", wraplength=740,
                command=lambda v=val: self.handle_first_reaction(v)
            )
            btn.pack(fill="x", padx=25, pady=8)

    def handle_first_reaction(self, choice):
        if choice == "rush":
            show_knowledge_popup(
                self, "ระวัง! อันตรายซ้ำซ้อน", "ความปลอดภัยในที่เกิดเหตุ (Scene Safety)",
                "คุณรีบวิ่งเข้าไปโดยไม่เคลียร์พื้นที่ เกือบเหยียบเศษแก้วมัคที่แตกกระจายบาดเท้า!\n"
                "ตามหลักการปฐมพยาบาล สิ่งสำคัญอันดับแรกคือ 'ความปลอดภัยของพื้นที่และผู้ช่วยเหลือ' "
                "ต้องกำจัดอันตรายรอบตัวก่อนเสมอ เพื่อไม่ให้เกิดผู้บาดเจ็บเพิ่ม"
            )
        elif choice == "scold":
            self.game_state["relationship"] -= 5
            self.update_top_bar()
            show_knowledge_popup(
                self, "ใจเย็นก่อน!", "การจัดการอารมณ์",
                "ทียืนน้ำตาคลอเบ้าด้วยความเจ็บปวดสุดขีด: 'ฮืออออ อย่าเพิ่งบ่น มือฉันจะสุกแล้ววว!'\n"
                "รีบเข้าไปช่วยเพื่อนก่อนเทศนาเถอะ! (ความสัมพันธ์ -5)"
            )
        elif choice == "sweep":
            self.game_state["score"] += 15
            self.game_state["relationship"] += 5
            self.update_top_bar()
            show_knowledge_popup(
                self, "ยอดเยี่ยม!", "ความปลอดภัยเป็นอันดับแรก",
                "คุณรีบคว้าไม้กวาดกวาดเศษแก้วเปิดทางอย่างรวดเร็ว ทำให้ทั้งคุณและทีปลอดภัยจากแก้วบาด!\n"
                "หลักการปฐมพยาบาลที่ถูกต้อง: ประเมินความปลอดภัยของสถานที่เกิดเหตุ (Scene Safety) ก่อนเสมอ!\n\n"
                "🏆 คะแนน +15 | ❤️ ความสัมพันธ์ +5"
            )
            self.start_siriraj_quiz()

    # -------------------------------------------------------------
    # แบบทดสอบการประเมินและการปฐมพยาบาลครบถ้วนตามมาตรฐาน รพ.ศิริราช
    # -------------------------------------------------------------
    def start_siriraj_quiz(self):
        self.mistakes_count = 0
        self.current_aid_step_idx = 0
        self.failed_explanations.clear()
        self.show_next_first_aid_step()

    def show_next_first_aid_step(self):
        if self.current_aid_step_idx >= len(FIRST_AID_QUIZ_STEPS):
            self.finish_first_aid_success()
            return

        for w in self.stage_container.winfo_children():
            w.destroy()

        step_data = FIRST_AID_QUIZ_STEPS[self.current_aid_step_idx]

        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_ACCENT, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=8)

        # Top bar with lives & step indicator
        top_bar = tk.Frame(card, bg=COLOR_SURFACE)
        top_bar.pack(fill="x", padx=20, pady=(10, 0))

        step_indicator = f"ข้อที่ {self.current_aid_step_idx + 1} จาก {len(FIRST_AID_QUIZ_STEPS)} (มาตรฐาน รพ.ศิริราช)"
        tk.Label(top_bar, text=step_indicator, font=FONT_SMALL, fg=COLOR_YELLOW, bg=COLOR_SURFACE).pack(side="left")

        rem_lives = max(0, 3 - self.mistakes_count)
        lives_icons = "❤️ " * rem_lives + "💔 " * (3 - rem_lives)
        lives_color = COLOR_GREEN if rem_lives >= 2 else (COLOR_YELLOW if rem_lives == 1 else COLOR_RED)
        tk.Label(top_bar, text=f"โอกาสคงเหลือ: {lives_icons}", font=FONT_BODY_BOLD, fg=lives_color, bg=COLOR_SURFACE).pack(side="right")

        tk.Label(
            card, text=f"🩺 {step_data['title']}",
            font=FONT_HEADING, fg=COLOR_ACCENT, bg=COLOR_SURFACE, pady=6
        ).pack(fill="x")

        # Situation area
        sit_frame = tk.Frame(card, bg=COLOR_SURFACE_LIGHT, padx=12, pady=8, bd=1, relief="solid", highlightbackground=COLOR_BORDER, highlightthickness=1)
        sit_frame.pack(fill="x", padx=20, pady=(0, 8))

        # Show burn wound image for Step 1
        if step_data.get("step_num") == 1:
            wound_img = get_image("burn_wound.jpg", (180, 100))
            if wound_img:
                lbl_img = tk.Label(sit_frame, image=wound_img, bg=COLOR_SURFACE_LIGHT)
                lbl_img.image = wound_img
                lbl_img.pack(side="left", padx=(0, 10))

        tk.Label(
            sit_frame, text=step_data["situation"],
            font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT,
            justify="left", wraplength=640 if step_data.get("step_num") == 1 else 820
        ).pack(side="left", fill="both", expand=True)

        # Options
        for opt in step_data["options"]:
            btn = StyledButton(
                card, text=opt["text"], font=FONT_BODY,
                bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG,
                justify="left", wraplength=820,
                padx=12, pady=5,
                command=lambda o=opt, sd=step_data: self.handle_step_choice(o, sd)
            )
            btn.pack(fill="x", padx=20, pady=3)

    def handle_step_choice(self, opt, step_data):
        if opt["is_correct"]:
            self.game_state["score"] += 20
            self.game_state["relationship"] += 3
            self.update_top_bar()
            show_knowledge_popup(
                self, "ถูกต้องตามหลักการแพทย์ศิริราช!", "การปฐมพยาบาลแผลไฟไหม้",
                f"{opt['explanation']}\n\n🏆 คะแนน +20 | ❤️ ความสัมพันธ์ +3",
                image_name="burn_wound.jpg" if step_data.get("step_num") == 1 else None
            )
            self.current_aid_step_idx += 1
            self.show_next_first_aid_step()
        else:
            self.mistakes_count += 1
            self.failed_explanations.append(opt["explanation"])
            self.game_state["score"] = max(0, self.game_state["score"] - 5)
            self.update_top_bar()

            if self.mistakes_count >= 3:
                self.trigger_game_over()
            else:
                rem = 3 - self.mistakes_count
                show_knowledge_popup(
                    self, f"คำเตือน: วิธีนี้ผิดและอันตราย! (โอกาสเหลือ {rem} ครั้ง)", "ความเชื่อผิดๆ",
                    f"{opt['explanation']}\n\n⚠️ คุณทำผิดแล้ว {self.mistakes_count}/3 ครั้ง ระวัง! หากผิดครบ 3 ครั้งจะ GAME OVER"
                )
                self.show_next_first_aid_step()

    # -------------------------------------------------------------
    # หน้าจอ GAME OVER
    # -------------------------------------------------------------
    def trigger_game_over(self):
        for w in self.stage_container.winfo_children():
            w.destroy()

        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=3, relief="solid")
        card.config(highlightbackground=COLOR_RED, highlightthickness=3)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        tk.Label(
            card, text="💀 GAME OVER - การปฐมพยาบาลผิดวิธี",
            font=FONT_TITLE, fg=COLOR_RED, bg=COLOR_SURFACE, pady=10
        ).pack(fill="x")

        tk.Label(
            card, text="คุณเลือกวิธีปฐมพยาบาลที่เป็นความเชื่อผิดๆ สะสมครบ 3 ครั้ง ทำให้แผลของทีเสี่ยงติดเชื้อรุนแรง!",
            font=FONT_BODY_BOLD, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, wraplength=720
        ).pack(pady=(0, 10))

        reasons_frame = tk.Frame(card, bg=COLOR_SURFACE_LIGHT, padx=15, pady=10)
        reasons_frame.pack(fill="both", expand=True, padx=25, pady=5)

        tk.Label(
            reasons_frame, text="[ บทวิเคราะห์ข้อผิดพลาดที่เป็นอันตราย ]",
            font=FONT_HEADING, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT
        ).pack(anchor="w", pady=(0, 5))

        reasons_text = "\n\n".join([f"⚠️ {r}" for r in self.failed_explanations])
        tk.Label(
            reasons_frame, text=reasons_text, font=FONT_BODY,
            fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, justify="left", wraplength=700
        ).pack(anchor="w")

        StyledButton(
            card, text="🔄 เริ่มต้นขั้นตอนปฐมพยาบาลใหม่อีกครั้ง",
            font=FONT_BODY_BOLD, bg=COLOR_RED, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_RED_HOVER, hover_fg=COLOR_TEXT_MAIN,
            command=self.restart_scene
        ).pack(pady=15)

    def restart_scene(self):
        self.start_siriraj_quiz()

    # -------------------------------------------------------------
    # ปฐมพยาบาลสำเร็จ & บทสนทนากับที
    # -------------------------------------------------------------
    def finish_first_aid_success(self):
        for w in self.stage_container.winfo_children():
            w.destroy()

        self.bg_canvas = tk.Canvas(self.stage_container, bg=COLOR_BG, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.bind("<Configure>", self._on_bg_resize)

        self.dialogue_box.pack(fill="x", side="bottom", padx=20, pady=(0, 15), ipady=5)
        pname = self.game_state["player_name"]

        self.post_aid_scripts = [
            ("บรรยาย", "หลังจากผ่านการล้างน้ำสะอาดอุณหภูมิห้อง ไม่เจาะตุ่มพอง และปิดแผลหลวมๆ ด้วยผ้าก๊อซ แผลของทีได้รับการดูแลอย่างถูกต้อง...", COLOR_TEXT_MUTED, "happy"),
            (pname, "เฮ้อออ... รอดตัวไป โชคดีนะที่แกถนัดซ้าย แต่มือที่โดนลวกเป็นมือขวา ไม่งั้นคงเขียนแบบไม่ได้แน่ๆ", "#fb923c", "happy"),
            ("บรรยาย", "ทีนั่งถอนหายใจอยู่บนเก้าอี้ ดวงตาเลื่อนลอยเหมือนวิญญาณหลุดออกจากร่าง...", COLOR_TEXT_MUTED, "sleepy"),
            (pname, "หน้าตาแบบนี้... ให้ทายนะ งานยังไม่เสร็จใช่ป่ะ?", "#fb923c", "sleepy"),
            ("ที", "ฮืออออ... ถูกเผงเลย ขึ้นโมไปแค่ครึ่งเดียวเอง แวะมาเติมกาแฟกะว่าจะโต้รุ่งแท้ๆ...", "#38bdf8", "sleepy")
        ]
        self.post_aid_idx = 0
        self.show_post_aid_dialogue()

    def show_post_aid_dialogue(self):
        if self.post_aid_idx < len(self.post_aid_scripts):
            spk, txt, col, char_pose = self.post_aid_scripts[self.post_aid_idx]
            self.render_background_and_character("bg_kitchen.jpg", char_pose)
            self.dialogue_box.set_dialogue(spk, txt, col, show_next_btn=True)
            self.dialogue_box.on_next = self.advance_post_aid_dialogue
        else:
            self.show_friendship_choice()

    def advance_post_aid_dialogue(self):
        self.post_aid_idx += 1
        self.show_post_aid_dialogue()

    def show_friendship_choice(self):
        self.dialogue_box.pack_forget()

        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_PURPLE, highlightthickness=2)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        tk.Label(
            card, text="💬 เลือกคำพูดที่คุณจะบอกกับที:",
            font=FONT_SUBTITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE, pady=15
        ).pack(fill="x")

        options = [
            ("1. 'สู้ๆ นะเพื่อน... คนเราเกิดมาเพื่อไฟต์ แกทำทันอยู่แล้วแหละ!'", 10,
             "ที: 'ขอบใจนะแก... ถึงจะพูดแบบนั้นแต่ขาข้างนึงฉันก้าวเข้าห้องสอบด้วยร่างวิญญาณแล้วล่ะ...'"),
            ("2. [ตบไหล่ทีเบาๆ โดยไม่พูดอะไร สื่อถึงความเข้าใจของเพื่อนแท้]", 15,
             "ทีน้ำตาคลอเบ้า สบตาคุณด้วยความซึ้งใจ: '...เข้าใจกันโดยไม่ต้องพูดสินะเพื่อนแท้... ขอบใจนะ'"),
            ("3. 'เอ่อ... เดี๋ยวฉันช่วยแกตัดโมเดลละกัน ทนดูสภาพอนาถไม่ไหวว่ะ'", 25,
             "ทีกระโดดกอดคุณทั้งน้ำตา: 'ฮือออออ! เทพบุตรมาโปรด! บุญคุณครั้งนี้จะไม่ลืมเลยเพื่อนรัก!'")
        ]

        for text, rel_boost, reaction in options:
            btn = StyledButton(
                card, text=text, font=FONT_BODY_BOLD,
                bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
                hover_bg=COLOR_PURPLE, hover_fg=COLOR_TEXT_MAIN,
                justify="left", wraplength=720,
                command=lambda rb=rel_boost, r=reaction: self.finish_scene2(rb, r)
            )
            btn.pack(fill="x", padx=20, pady=8)

    def finish_scene2(self, rel_boost, reaction):
        self.game_state["relationship"] += rel_boost
        self.game_state["score"] += 20
        self.update_top_bar()

        for w in self.stage_container.winfo_children():
            w.destroy()
        self.dialogue_box.pack_forget()

        if "scene2" not in self.game_state["completed_scenes"]:
            self.game_state["completed_scenes"].append("scene2")
        self.game_state["current_scene"] = "scene3"
        save_game(self.game_state, "auto")

        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_GREEN, highlightthickness=2)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        tk.Label(
            card, text="🎉 จบฉากที่ 2: วิกฤตน้ำร้อนลวกและการปฐมพยาบาล",
            font=FONT_TITLE, fg=COLOR_GREEN, bg=COLOR_SURFACE, pady=10
        ).pack(fill="x")

        # Auto-Save Pill
        save_pill = tk.Frame(card, bg="#064e3b", padx=12, pady=3, highlightbackground=COLOR_GREEN, highlightthickness=1)
        save_pill.pack(pady=(0, 6))
        tk.Label(
            save_pill, text="💾 ระบบได้ทำการบันทึกข้อมูล (Auto-Save) เข้าสู่ฉากที่ 3 เรียบร้อยแล้ว",
            font=FONT_SMALL, fg="#a7f3d0", bg="#064e3b"
        ).pack()

        # Reaction / Relationship Pill
        rel_pill = tk.Frame(card, bg=COLOR_SURFACE_LIGHT, padx=14, pady=8, bd=1, relief="solid")
        rel_pill.config(highlightbackground=COLOR_PURPLE, highlightthickness=1)
        rel_pill.pack(fill="x", padx=25, pady=4)

        tk.Label(
            rel_pill, text=f"❤️ ระดับความสัมพันธ์เพิ่มขึ้น (+{rel_boost} ความสัมพันธ์ | +20 คะแนน)",
            font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE_LIGHT
        ).pack(anchor="w")

        tk.Label(
            rel_pill, text=reaction,
            font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, justify="left", wraplength=710
        ).pack(anchor="w", pady=(2, 0))

        btn_box = tk.Frame(card, bg=COLOR_SURFACE)
        btn_box.pack(side="bottom", fill="x", padx=20, pady=(6, 12))

        btn_next = StyledButton(
            btn_box, text="เข้าสู่ฉากที่ 3: จบไฟนอล & นัดหมอผ่านแอปหมอพร้อม ➡️ [Enter]",
            font=FONT_BODY_BOLD, bg=COLOR_ACCENT, fg=COLOR_BG,
            hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=20, pady=8,
            command=self.advance_to_next_scene
        )
        btn_next.pack(side="left", fill="x", expand=True, padx=(0, 10))
        btn_next.focus_set()

        StyledButton(
            btn_box, text="🏠 กลับสู่หน้าจอหลัก",
            font=FONT_BODY, bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_BORDER, hover_fg=COLOR_TEXT_MAIN,
            padx=14, pady=8,
            command=self.on_exit_to_menu
        ).pack(side="right")

        info_text = (
            f"👤 ผู้เล่น: {self.game_state['player_name']}    |    🏆 คะแนนรวม: {self.game_state['score']} แต้ม    |    ❤️ ความสัมพันธ์: {self.game_state['relationship']}/100\n\n"
            "✨ สรุปความรู้ทางการแพทย์ที่ได้ (รพ.ศิริราช):\n"
            "• แผลระดับที่ 2 ชนิดตื้น: มีตุ่มน้ำพองใส ปวดแสบร้อน\n"
            "• ใช้น้ำสะอาดอุณหภูมิห้องไหลผ่าน 10-15 นาที (ห้ามใช้น้ำแข็งโดยตรง)\n"
            "• ห้ามเจาะตุ่มน้ำเด็ดขาด และห้ามทาสารแปลกปลอม (ยาสีฟัน, น้ำปลา)\n"
            "• ปิดแผลหลวมๆ ด้วยผ้าก๊อซสะอาดเพื่อป้องกันการติดเชื้อ"
        )

        tk.Label(
            card, text=info_text, font=FONT_BODY,
            fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE, justify="center"
        ).pack(fill="both", expand=True, pady=8)

        self.bind("<Return>", lambda e: self.advance_to_next_scene())
        self.bind("<space>", lambda e: self.advance_to_next_scene())

    def advance_to_next_scene(self):
        try:
            self.grab_release()
        except Exception:
            pass
        if self.on_finish_scene:
            self.on_finish_scene()
