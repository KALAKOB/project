"""
Scene 3: Mohpromt Application Booking & Grand Finale
ฉากที่ 3: ขั้นตอนการจองคิวผ่านแอปพลิเคชันหมอพร้อม และบทสรุปของเรื่องราว
"""

import tkinter as tk
from tkinter import ttk
import datetime
from ui_theme import (
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_LIGHT, COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_GREEN,
    COLOR_GREEN_HOVER, COLOR_RED, COLOR_YELLOW, COLOR_PURPLE, COLOR_BORDER,
    FONT_FAMILY, FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_BODY_BOLD,
    FONT_DIALOGUE, FONT_SPEAKER, FONT_CHOICE, FONT_SMALL, FONT_MONO,
    StyledButton, get_image
)
from vn_widgets import TopStatusBar, DialogueBox, show_knowledge_popup, show_save_slots_dialog
from save_manager import save_game
from data import MOHPROM_STEPS_INFO

THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]
THAI_DAYS = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]

def generate_appointment_dates(max_days=90):
    """สร้างรายการวันที่นัดหมายล่วงหน้าได้สูงสุด 3 เดือน (90 วัน) จากวันจริงที่เปิดใช้งานระบบ"""
    today = datetime.date.today()
    dates = []
    for i in range(1, max_days + 1):
        d = today + datetime.timedelta(days=i)
        # เปิดรับนัดหมายวันจันทร์ - เสาร์ (เว้นวันอาทิตย์)
        if d.weekday() < 6:
            thai_year = d.year + 543
            month_name = THAI_MONTHS[d.month]
            day_name = THAI_DAYS[d.weekday()]
            dates.append(f"{d.day} {month_name} {thai_year} ({day_name})")
    return dates

ALL_HOSPITAL_DEPARTMENTS = [
    "แผนกเวชศาสตร์ฟื้นฟูและกายภาพบำบัด (Physical Medicine & Rehab)",
    "แผนกกระดูกและข้อ (ศัลยศาสตร์ออร์โธปิดิกส์ - Orthopedics)",
    "แผนกอายุรกรรมทั่วไป (General Medicine)",
    "แผนกศัลยกรรมทั่วไป (General Surgery)",
    "แผนกจักษุ (ตา) (Ophthalmology)",
    "แผนกหู คอ จมูก (Otolaryngology - ENT)",
    "แผนกผิวหนังและเลเซอร์ (Dermatology)",
    "แผนกทันตกรรม (Dental Clinic)",
    "แผนกสุขภาพจิตและจิตเวช (Psychiatry)",
    "แผนกสูติ-นรีเวชกรรม (Obstetrics & Gynecology)",
    "แผนกกุมารเวชกรรม (Pediatrics)",
    "แผนกโรคหัวใจและหลอดเลือด (Cardiology)",
    "แผนกทางเดินอาหารและตับ (Gastroenterology)",
    "แผนกเวชศาสตร์ครอบครัว / ตรวจสุขภาพ (Family Medicine / Checkup)",
    "แผนกอุบัติเหตุและฉุกเฉิน (Emergency Department - ER)"
]

ALL_HOSPITALS = [
    "โรงพยาบาลจุฬาลงกรณ์ สภากาชาดไทย",
    "โรงพยาบาลศิริราช",
    "โรงพยาบาลรามาธิบดี",
    "โรงพยาบาลราชวิถี",
    "โรงพยาบาลพระมงกุฎเกล้า",
    "โรงพยาบาลธรรมศาสตร์เฉลิมพระเกียรติ",
    "โรงพยาบาลตำรวจ",
    "โรงพยาบาลวชิรพยาบาล",
    "โรงพยาบาลมหาราชนครเชียงใหม่",
    "โรงพยาบาลศรีนครินทร์ (ขอนแก่น)",
    "โรงพยาบาลสงขลานครินทร์ (หาดใหญ่)"
]

class Scene3MohpromtFrame(tk.Frame):
    def __init__(self, parent, game_state, on_finish_game, on_exit_to_menu):
        super().__init__(parent, bg=COLOR_BG)
        self.parent = parent
        self.game_state = game_state
        self.on_finish_game = on_finish_game
        self.on_exit_to_menu = on_exit_to_menu

        self.dialogue_index = 0
        self.phone_step = 1

        # Form variables for Mohpromt
        available_dates = generate_appointment_dates(90)
        default_date = available_dates[0] if available_dates else "วันพรุ่งนี้"

        self.province_var = tk.StringVar(value="กรุงเทพมหานคร")
        self.district_var = tk.StringVar(value="ปทุมวัน")
        self.hospital_var = tk.StringVar(value=ALL_HOSPITALS[0])
        self.dept_var = tk.StringVar(value=ALL_HOSPITAL_DEPARTMENTS[0])
        self.date_var = tk.StringVar(value=default_date)
        self.doctor_var = tk.StringVar(value="ไม่ระบุแพทย์ (รวดเร็วที่สุด)")
        self.time_var = tk.StringVar(value="10:00 - 11:00 น.")
        self.symptom_var = tk.StringVar(value="ปวดสะบัก หลังส่วนล่าง และคอบ่าไหล่เรื้อรังจากออฟฟิศซินโดรม / ตัดโมเดล")
        self.service_type_var = tk.StringVar(value="โรงพยาบาล")

        # Top Bar
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

        self.current_bg = "bg_restaurant.jpg"
        self.current_char_pose = "none"
        self.bg_canvas = tk.Canvas(self.stage_container, bg=COLOR_BG, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.bind("<Configure>", self._on_bg_resize)

        # Dialogue box
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
            "ฉากที่ 3: จบไฟนอล & นัดหมอผ่านแอปหมอพร้อม",
            self.game_state["score"],
            self.game_state["relationship"]
        )

    def handle_manual_save(self):
        self.game_state["current_scene"] = "scene3"
        show_save_slots_dialog(self, self.game_state, on_saved=lambda sid: self.update_top_bar())

    def render_background_and_character(self, bg_file="bg_restaurant.jpg", char_pose="none"):
        self.current_bg = bg_file
        self.current_char_pose = char_pose
        self.bg_canvas.delete("all")
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        if w < 100:
            w = 1000
            h = 450

        # พื้นหลังร้านอาหาร
        bg_img = get_image(bg_file, (w, h))
        if bg_img:
            self.bg_canvas.create_image(0, 0, anchor="nw", image=bg_img)
            self.bg_canvas.image = bg_img

        # ตัวละครที
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
    # เนื้อเรื่องฉาก 3: บทสนทนาในร้านราเมงหลังสอบเสร็จ
    # -------------------------------------------------------------
    def init_intro_dialogues(self):
        pname = self.game_state["player_name"]
        self.story_scripts = [
            ("บรรยาย", "สองสัปดาห์ต่อมา... ฤดูกาลส่งแบบโมเดลและสอบไฟนอลอันแสนทรหดได้สิ้นสุดลงในที่สุด!", COLOR_TEXT_MUTED, "none"),
            ("บรรยาย", "คุณและทีมานั่งแช่อยู่ในร้านราเมงเจ้าโปรด กลิ่นซุปกระดูกหมูหอมกรุ่นควันฉุย แต่สภาพร่างกายของทั้งคู่เหมือนซอมบี้ที่เพิ่งฟื้นจากหลุม...", COLOR_TEXT_MUTED, "none"),
            ("ที", "ซู้ดดด... ราเมงชามนี้คือรางวัลชีวิตหลังจากอดนอน 4 วันเต็ม... แต่โอ๊ยยย หลังฉัน... คอบ่าไหล่เหมือนโดนซีเมนต์ทับ แข็งเกร็งจนหันคอไม่ได้แล้ว...", "#38bdf8", "sleepy"),
            (pname, "อย่าบ่นคนเดียวสิวะ ฉันก็นั่งพิมพ์รายงานมือหงิก ไหล่ตึงเปรี๊ยะจนปวดร้าวขึ้นศีรษะเนี่ย! อาการออฟฟิศซินโดรมชัดๆ เลยที", "#fb923c", "sleepy"),
            ("ที", "อยากไปหาหมอกายภาพกับตรวจกระดูกมากเลยแก... แต่แค่คิดว่าต้องตื่นตี 5 ไปต่อแถวเบียดเสียดยื่นบัตรคิวที่โรงพยาบาล ขาก็ก้าวไม่ออกแล้วอะ...", "#38bdf8", "sleepy"),
            (pname, "ยุคดิจิทัลแล้วเจ้าที! ใครเขาไปยืนรอคิวตั้งแต่ไก่โห่กันเล่า เดี๋ยวนี้กระทรวงสาธารณสุขเขามีระบบนัดหมายออนไลน์ (MOPH Appointment Center) จองคิวล่วงหน้าได้สบายๆ!", "#fb923c", "happy"),
            ("ที", "เฮ้ยจริงดิ!? ผ่านช่องทางไหนบ้างอะ ต้องเดินทางไปทำเรื่องก่อนมั้ย?", "#38bdf8", "happy"),
            (pname, "จองได้ทั้ง 2 ช่องทางเลย! ทั้งผ่าน 'แอปพลิเคชันหมอพร้อม' และผ่าน 'LINE Official Account (@Mohpromt)' แค่มีสมาร์ทโฟนเครื่องเดียวก็เลือกวัน เวลา และแผนกได้ทันที!", "#fb923c", "happy"),
            ("ที", "เจ๋งเป้ง! ถ้างั้นเราเปิดจองคิวกายภาพพร้อมกันที่โต๊ะอาหารนี้เลยเถอะ สอนฉันทำหน่อย!", "#38bdf8", "happy"),
            ("ระบบ", "เข้าสู่การจำลองการใช้งานระบบ 'หมอพร้อม' (MOHPROMT) เพื่อจองคิวตรวจรักษาโรคและกายภาพบำบัด", COLOR_PURPLE, "none")
        ]

    def show_current_dialogue(self):
        if self.dialogue_index < len(self.story_scripts):
            speaker, text, color, char_pose = self.story_scripts[self.dialogue_index]
            self.render_background_and_character("bg_restaurant.jpg", char_pose)
            self.dialogue_box.set_dialogue(speaker, text, color, show_next_btn=True)
            self.dialogue_box.on_next = self.advance_story
        else:
            self.dialogue_box.pack_forget()
            self.render_phone_screen()

    def advance_story(self):
        self.dialogue_index += 1
        self.show_current_dialogue()

    # -------------------------------------------------------------
    # จำลองหน้าจอสมาร์ทโฟน (Phone Simulator)
    # -------------------------------------------------------------
    def render_phone_screen(self):
        for w in self.stage_container.winfo_children():
            w.destroy()

        # พื้นหลังร้านอาหาร (Graph & Tee นั่งทำรายการที่โต๊ะ)
        bg_canvas = tk.Canvas(self.stage_container, bg=COLOR_BG, highlightthickness=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        w = self.stage_container.winfo_width() or 1000
        h = self.stage_container.winfo_height() or 600
        bg_img = get_image("bg_restaurant.jpg", (w, h))
        if bg_img:
            bg_canvas.create_image(0, 0, anchor="nw", image=bg_img)

        # ปุ่มดูแผนผังขั้นตอนทางการของ สธ.
        btn_guide = StyledButton(
            self.stage_container, text="📖 ดูแผนผังขั้นตอนทางการ (MOPH Guide)",
            font=FONT_BODY_BOLD, bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=14, pady=6, command=self.show_moph_guide_modal
        )
        btn_guide.place(x=25, y=20)

        # Phone Device Frame (Center) - Responsive for small/large screens
        phone_h = min(560, max(460, int(h * 0.92)))
        phone_w = min(430, max(350, int(phone_h * 0.74)))
        phone_wrapper = tk.Frame(self.stage_container, bg="#020617", bd=4, relief="ridge")
        phone_wrapper.place(relx=0.5, rely=0.5, anchor="center", width=phone_w, height=phone_h)

        # Notch / Camera Bar
        notch_bar = tk.Frame(phone_wrapper, bg="#0284c7", height=28)
        notch_bar.pack(fill="x")
        notch_bar.pack_propagate(False)
        tk.Label(notch_bar, text="09:41", font=(FONT_FAMILY, 9, "bold"), fg="white", bg="#0284c7").pack(side="left", padx=10)
        tk.Label(notch_bar, text="● ● ●", font=(FONT_FAMILY, 7), fg="#bae6fd", bg="#0284c7").pack(side="left", expand=True)
        tk.Label(notch_bar, text="MOHPROMT 5G 🔋", font=(FONT_FAMILY, 9), fg="white", bg="#0284c7").pack(side="right", padx=10)

        # Inner Screen
        self.app_content = tk.Frame(phone_wrapper, bg="#f8fafc")
        self.app_content.pack(fill="both", expand=True)

        if self.phone_step == 1:
            self.render_step_1()
        elif self.phone_step == 2:
            self.render_step_2()
        elif self.phone_step == 3:
            self.render_step_3()
        elif self.phone_step == 4:
            self.render_step_4()

    def show_moph_guide_modal(self):
        """เปิดหน้าต่างแสดงแผนผังขั้นตอนทางการของ สธ. (App Flow & LINE Flow)"""
        top = tk.Toplevel(self)
        top.title("📖 แผนผังขั้นตอนการนัดหมายออนไลน์ (MOPH Appointment Center)")
        top.geometry("780x620")
        top.configure(bg=COLOR_BG)
        top.transient(self.winfo_toplevel())
        top.grab_set()

        top.update_idletasks()
        rx = self.winfo_toplevel().winfo_rootx() + (self.winfo_toplevel().winfo_width() // 2) - 390
        ry = self.winfo_toplevel().winfo_rooty() + (self.winfo_toplevel().winfo_height() // 2) - 310
        top.geometry(f"+{rx}+{ry}")

        header = tk.Frame(top, bg=COLOR_SURFACE, pady=10, padx=16, bd=1, relief="solid")
        header.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        header.pack(fill="x")

        tk.Label(
            header, text="🏥 คู่มือระบบนัดหมายออนไลน์ MOPH Appointment Center",
            font=FONT_HEADING, fg=COLOR_YELLOW, bg=COLOR_SURFACE
        ).pack(side="left")

        StyledButton(
            header, text="✕ ปิด (Esc)", font=FONT_SMALL,
            bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_RED, hover_fg=COLOR_TEXT_MAIN,
            padx=10, pady=3, command=top.destroy
        ).pack(side="right")

        # Tab buttons
        tab_frame = tk.Frame(top, bg=COLOR_BG, pady=6)
        tab_frame.pack(fill="x", padx=16)

        img_label = tk.Label(top, bg=COLOR_SURFACE, bd=1, relief="ridge")
        img_label.pack(fill="both", expand=True, padx=16, pady=4)

        desc_label = tk.Label(top, text="", font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, justify="center")
        desc_label.pack(fill="x", padx=16, pady=(0, 8))

        def update_view(view_mode):
            if view_mode == "app":
                btn_app.config(bg=COLOR_ACCENT, fg=COLOR_BG)
                btn_line.config(bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN)
                img = get_image("mohpromt_app_flow.png", (720, 420))
                desc_label.config(text="📱 ผ่านแอปหมอพร้อม: 1. นัดหมายออนไลน์ ➔ 2. จองคิวหมอ ➔ 3. ระบุ รพ./แผนก/วันเวลา/อาการ ➔ 4. ยืนยัน ➔ 5. รับใบนัด")
            else:
                btn_app.config(bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN)
                btn_line.config(bg=COLOR_GREEN, fg=COLOR_TEXT_MAIN)
                img = get_image("mohpromt_line_flow.png", (720, 420))
                desc_label.config(text="💬 ผ่าน LINE OA (@Mohpromt): 1. นัดหมายออนไลน์ ➔ 2. ยืนยัน PIN ➔ 3. ระบุ รพ./แผนก/อาการ ➔ 4. ยืนยัน ➔ 5. รับใบนัด")

            if img:
                img_label.config(image=img)
                img_label.image = img

        btn_app = StyledButton(
            tab_frame, text="📱 ขั้นตอนผ่าน แอปพลิเคชัน หมอพร้อม",
            font=FONT_BODY_BOLD, bg=COLOR_ACCENT, fg=COLOR_BG,
            hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=12, pady=4, command=lambda: update_view("app")
        )
        btn_app.pack(side="left", padx=(0, 8))

        btn_line = StyledButton(
            tab_frame, text="💬 ขั้นตอนผ่าน LINE Official Account (@Mohpromt)",
            font=FONT_BODY_BOLD, bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN,
            hover_bg=COLOR_GREEN_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=12, pady=4, command=lambda: update_view("line")
        )
        btn_line.pack(side="left")

        update_view("app")
        top.bind("<Escape>", lambda e: top.destroy())

    # Step 1: หน้าแรกแอป
    def render_step_1(self):
        for w in self.app_content.winfo_children():
            w.destroy()

        header = tk.Frame(self.app_content, bg="#0284c7", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="🏥 หมอพร้อม (MOHPROMT)", font=FONT_SUBTITLE, fg="white", bg="#0284c7").pack()
        tk.Label(header, text=f"บัญชี: {self.game_state['player_name']} (สิทธิบัตรทอง/ประกันสังคม)", font=FONT_SMALL, fg="#e0f2fe", bg="#0284c7").pack()

        inst_box = tk.Frame(self.app_content, bg="#e0f2fe", padx=10, pady=8)
        inst_box.pack(fill="x", padx=15, pady=10)
        tk.Label(
            inst_box,
            text="📱 ขั้นตอนที่ 1/4:\nเพื่อทำการนัดล่วงหน้า ให้แตะเลือกเมนู 'นัดหมายออนไลน์'",
            font=FONT_BODY_BOLD, fg="#0369a1", bg="#e0f2fe", justify="center"
        ).pack()

        grid = tk.Frame(self.app_content, bg="#f8fafc")
        grid.pack(fill="both", expand=True, padx=20, pady=5)

        menu_items = [
            ("💉 ข้อมูลวัคซีน", False),
            ("📋 ตรวจสุขภาพ", False),
            ("📅 นัดหมายออนไลน์", True),
            ("💊 ร้านยาใกล้บ้าน", False),
            ("🛡️ เช็คสิทธิรักษา", False),
            ("☎️ สายด่วนสุขภาพ", False)
        ]

        for i, (label, is_target) in enumerate(menu_items):
            r = i // 2
            c = i % 2
            btn_bg = "#0284c7" if is_target else "#e2e8f0"
            btn_fg = "white" if is_target else "#1e293b"
            h_bg = "#0369a1" if is_target else "#cbd5e1"
            h_fg = "white" if is_target else "#0f172a"

            b = StyledButton(
                grid, text=label, font=FONT_BODY_BOLD,
                bg=btn_bg, fg=btn_fg, hover_bg=h_bg, hover_fg=h_fg,
                pady=12,
                command=lambda t=is_target: self.handle_step1_click(t)
            )
            b.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            grid.grid_columnconfigure(c, weight=1)
            grid.grid_rowconfigure(r, weight=1)

    def handle_step1_click(self, is_target):
        if is_target:
            self.game_state["score"] += 15
            self.update_top_bar()
            self.phone_step = 2
            self.render_phone_screen()
        else:
            show_knowledge_popup(
                self, "เลือกเมนูไม่ตรงเป้าหมาย", "แอปหมอพร้อม",
                "สำหรับขั้นตอนการจองคิวล่วงหน้า ให้เลือกที่เมนู 'นัดหมายออนไลน์' ครับ"
            )

    # Step 2: เลือกประเภทการนัด
    def render_step_2(self):
        for w in self.app_content.winfo_children():
            w.destroy()

        header = tk.Frame(self.app_content, bg="#0284c7", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="📅 นัดหมายออนไลน์", font=FONT_HEADING, fg="white", bg="#0284c7").pack()

        inst_box = tk.Frame(self.app_content, bg="#e0f2fe", padx=10, pady=8)
        inst_box.pack(fill="x", padx=15, pady=10)
        tk.Label(
            inst_box,
            text="📱 ขั้นตอนที่ 2/4:\nเลือก 'จองคิวหมอ' เพื่อระบุสถานพยาบาลและแพทย์",
            font=FONT_BODY_BOLD, fg="#0369a1", bg="#e0f2fe", justify="center"
        ).pack()

        options = [
            ("🩺 จองคิวหมอ (ตรวจรักษาโรค)", True),
            ("📄 ประวัติการนัดหมายของฉัน", False),
            ("💉 นัดหมายฉีดวัคซีน", False),
            ("🏥 จองโปรแกรมตรวจสุขภาพ", False)
        ]

        for label, is_target in options:
            btn_bg = "#0284c7" if is_target else "#e2e8f0"
            btn_fg = "white" if is_target else "#1e293b"
            h_bg = "#0369a1" if is_target else "#cbd5e1"
            h_fg = "white" if is_target else "#0f172a"

            b = StyledButton(
                self.app_content, text=label, font=FONT_BODY_BOLD,
                bg=btn_bg, fg=btn_fg, hover_bg=h_bg, hover_fg=h_fg,
                pady=10,
                command=lambda t=is_target: self.handle_step2_click(t)
            )
            b.pack(fill="x", padx=20, pady=6)

    def handle_step2_click(self, is_target):
        if is_target:
            self.game_state["score"] += 15
            self.update_top_bar()
            self.phone_step = 3
            self.render_phone_screen()
        else:
            show_knowledge_popup(
                self, "เลือกเมนูไม่ตรงเป้าหมาย", "แอปหมอพร้อม",
                "สำหรับตรวจรักษาอาการปวดหลัง/กล้ามเนื้อ ให้เลือก 'จองคิวหมอ'"
            )

    # Step 3: กรอกฟอร์มการนัดหมาย
    def render_step_3(self):
        for w in self.app_content.winfo_children():
            w.destroy()

        header = tk.Frame(self.app_content, bg="#0284c7", pady=6)
        header.pack(fill="x")
        tk.Label(header, text="📝 ระบุข้อมูลการนัดหมาย (3/4)", font=FONT_HEADING, fg="white", bg="#0284c7").pack()

        canvas = tk.Canvas(self.app_content, bg="#f8fafc", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.app_content, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg="#f8fafc", padx=12, pady=5)

        form_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")

        def _on_canvas_configure(e):
            canvas.itemconfig(form_window, width=e.width)

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _on_canvas_configure)
        form_frame.bind("<Configure>", _on_frame_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mouse wheel support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        form_frame.bind("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def add_field(label_text, var, options):
            tk.Label(form_frame, text=label_text, font=FONT_SMALL, fg="#475569", bg="#f8fafc").pack(anchor="w", pady=(4, 1))
            cb = ttk.Combobox(form_frame, textvariable=var, values=options, state="readonly", font=FONT_SMALL)
            cb.pack(fill="x", pady=(0, 4))
            return cb

        available_dates = generate_appointment_dates(90)
        add_field("1. จังหวัด:", self.province_var, ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "ชลบุรี", "สงขลา", "นครราชสีมา"])
        add_field("2. เขต / อำเภอ:", self.district_var, ["ปทุมวัน", "พญาไท", "บางรัก", "จตุจักร", "เมืองเชียงใหม่", "หาดใหญ่"])
        add_field("3. โรงพยาบาล:", self.hospital_var, ALL_HOSPITALS)
        add_field("4. แผนกการรักษา (ครอบคลุมทุกสาขา):", self.dept_var, ALL_HOSPITAL_DEPARTMENTS)
        add_field("5. วันที่นัดหมายล่วงหน้า (สูงสุด 3 เดือนจากวันจริง):", self.date_var, available_dates)
        add_field("6. แพทย์ (สามารถเลือกไม่ระบุได้):", self.doctor_var, [
            "ไม่ระบุแพทย์ (รวดเร็วที่สุด)",
            "นพ.วิชัย ปราชญ์กระดูก (เชี่ยวชาญกระดูกสันหลัง)",
            "พญ.อรพินท์ กายภาพบำบัด (เวชศาสตร์ฟื้นฟู)",
            "นพ.ธีรเดช เวชศาสตร์การกีฬา"
        ])
        add_field("7. เวลานัดหมาย:", self.time_var, [
            "08:30 - 09:30 น.",
            "09:30 - 10:30 น.",
            "10:30 - 11:30 น.",
            "13:00 - 14:00 น.",
            "14:00 - 15:00 น.",
            "15:00 - 16:00 น."
        ])

        tk.Label(form_frame, text="8. อาการเบื้องต้น:", font=FONT_SMALL, fg="#475569", bg="#f8fafc").pack(anchor="w", pady=(4, 1))
        entry_symptom = tk.Entry(form_frame, textvariable=self.symptom_var, font=FONT_SMALL)
        entry_symptom.pack(fill="x", pady=(0, 6))

        tk.Label(form_frame, text="9. รูปแบบการรับบริการ:", font=FONT_SMALL, fg="#475569", bg="#f8fafc").pack(anchor="w", pady=(4, 1))
        radio_frame = tk.Frame(form_frame, bg="#f8fafc")
        radio_frame.pack(fill="x", pady=(0, 10))
        tk.Radiobutton(radio_frame, text="ไปโรงพยาบาล", variable=self.service_type_var, value="โรงพยาบาล", bg="#f8fafc", font=FONT_SMALL).pack(side="left")
        tk.Radiobutton(radio_frame, text="พบแพทย์ออนไลน์", variable=self.service_type_var, value="ออนไลน์", bg="#f8fafc", font=FONT_SMALL).pack(side="left", padx=10)

        StyledButton(
            form_frame, text="✅ ยืนยันการจองคิว", font=FONT_BODY_BOLD,
            bg=COLOR_GREEN, fg="white", hover_bg=COLOR_GREEN_HOVER, hover_fg="white",
            command=self.handle_step3_submit
        ).pack(fill="x", pady=(5, 20))

    def handle_step3_submit(self):
        self.game_state["score"] += 30
        self.update_top_bar()
        self.phone_step = 4
        show_knowledge_popup(
            self, "การจองสำเร็จ!", "ระบบหมอพร้อม",
            "คุณทำการจองคิวตรวจเรียบร้อยแล้ว!\nระบบได้ส่งข้อมูลไปยังโรงพยาบาล และสร้างใบนัดหมายดิจิทัลให้คุณเรียบร้อย"
        )
        self.render_phone_screen()

    # Step 4: ใบนัดหมาย
    def render_step_4(self):
        for w in self.app_content.winfo_children():
            w.destroy()

        header = tk.Frame(self.app_content, bg=COLOR_GREEN, pady=8)
        header.pack(fill="x")
        tk.Label(header, text="✓ บันทึกการนัดหมายสำเร็จ", font=FONT_HEADING, fg="white", bg=COLOR_GREEN).pack()

        card = tk.Frame(self.app_content, bg="white", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=12, pady=10)

        tk.Label(card, text="🏥 ใบนัดหมายออนไลน์ (E-Appointment)", font=FONT_BODY_BOLD, fg="#0f172a", bg="white").pack(pady=(8, 2))
        tk.Label(card, text="[ ระบบบริการสาธารณสุข กระทรวงสาธารณสุข ]", font=FONT_SMALL, fg="#64748b", bg="white").pack(pady=(0, 8))

        details = [
            f"👤 ชื่อผู้ป่วย: {self.game_state['player_name']}",
            f"🏥 สถานพยาบาล: {self.hospital_var.get()}",
            f"🏨 แผนก: {self.dept_var.get()}",
            f"📅 วันที่: {self.date_var.get()}",
            f"⏰ เวลา: {self.time_var.get()}",
            f"🩺 แพทย์: {self.doctor_var.get()}",
            f"📍 สถานที่: {self.service_type_var.get()}",
            f"💬 อาการ: {self.symptom_var.get()[:28]}..."
        ]

        for d in details:
            tk.Label(card, text=d, font=FONT_SMALL, fg="#1e293b", bg="white", anchor="w").pack(fill="x", padx=12, pady=1)

        # จำลอง QR Code
        qr_box = tk.Frame(card, bg="#f1f5f9", height=50, relief="groove", bd=1)
        qr_box.pack(fill="x", padx=15, pady=8)
        qr_box.pack_propagate(False)
        tk.Label(qr_box, text="[ ||| | |||| | ||| | || ]  คิวหมายเลข #042\nกรุณาแสดงบาร์โค้ดนี้เมื่อถึงแผนกคัดกรอง", font=FONT_SMALL, fg="#334155", bg="#f1f5f9").pack(expand=True)

        StyledButton(
            card, text="ดูบทสรุปตอนจบของเกม 🏆", font=FONT_BODY_BOLD,
            bg=COLOR_ACCENT, fg=COLOR_BG, hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
            command=self.show_final_ending
        ).pack(fill="x", padx=15, pady=(4, 10))

    # -------------------------------------------------------------
    # ฉากจบและสรุปผลทั้งเกม
    # -------------------------------------------------------------
    def show_final_ending(self):
        for w in self.stage_container.winfo_children():
            w.destroy()

        if "scene3" not in self.game_state["completed_scenes"]:
            self.game_state["completed_scenes"].append("scene3")
        self.game_state["current_scene"] = "finished"
        save_game(self.game_state, "auto")

        # พื้นหลัง
        bg_canvas = tk.Canvas(self.stage_container, bg=COLOR_BG, highlightthickness=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        w = self.stage_container.winfo_width() or 1000
        h = self.stage_container.winfo_height() or 600
        bg_img = get_image("bg_dorm.jpg", (w, h))
        if bg_img:
            bg_canvas.create_image(0, 0, anchor="nw", image=bg_img)

        # Character Tee smiling happily on left side directly on canvas with clean transparency
        if w >= 880:
            char_h = min(460, int(h * 0.82))
            char_w = int(char_h * (300 / 447))
            char_img = get_image("tee_happy.png", (char_w, char_h))
            if char_img:
                bg_canvas.create_image(30, max(20, h - char_h - 20), anchor="nw", image=char_img)
                bg_canvas.char_img = char_img

        # Card on the right (on large screens) or full frame (on small screens)
        card = tk.Frame(self.stage_container, bg=COLOR_SURFACE, bd=2, relief="solid")
        card.config(highlightbackground=COLOR_ACCENT, highlightthickness=2)

        if w >= 880:
            card.place(relx=0.98, rely=0.5, anchor="e", relwidth=0.62, relheight=0.92)
        else:
            card.pack(fill="both", expand=True, padx=20, pady=12)

        # Header Title
        tk.Label(
            card, text="🎓 ภารกิจเสร็จสมบูรณ์ - จบเกม!",
            font=FONT_TITLE, fg=COLOR_YELLOW, bg=COLOR_SURFACE, pady=8
        ).pack(fill="x")

        # Action Buttons Pinned to Bottom (Guaranteed Visible on All Screen Sizes)
        btn_box = tk.Frame(card, bg=COLOR_SURFACE)
        btn_box.pack(side="bottom", fill="x", padx=15, pady=10)

        StyledButton(
            btn_box, text="🏠 กลับสู่หน้าจอหลัก",
            font=FONT_BODY_BOLD, bg=COLOR_ACCENT, fg=COLOR_BG,
            hover_bg=COLOR_ACCENT_HOVER, hover_fg=COLOR_TEXT_MAIN,
            padx=18, pady=8,
            command=self.on_exit_to_menu
        ).pack(fill="x")

        # กำหนดฉายาความสัมพันธ์
        rel = self.game_state["relationship"]
        if rel >= 85:
            rank_title = "🌟 ระดับ S: สุดยอดคู่หูรูมเมทตลอดกาล"
            rank_desc = "ทีซาบซึ้งใจในตัวคุณมาก คุณไม่เพียงแต่ช่วยชีวิตเขาไว้จากความซุ่มซ่าม แต่ยังช่วยตัดโมเดลและพาไปหาหมอด้วยกันอีกด้วย!"
            rank_col = COLOR_GREEN
        elif rel >= 65:
            rank_title = "⭐ ระดับ A: สหายร่วมรบผ่านศึกมหาลัย"
            rank_desc = "ทีนับถือและไว้ใจคุณมาก คุณเป็นเพื่อนแท้ที่พึ่งพาได้เสมอในยามคับขันของชีวิตเด็กหอ"
            rank_col = COLOR_ACCENT
        else:
            rank_title = "🌱 ระดับ B: รูมเมทคู่กัดสุดป่วน"
            rank_desc = "ถึงจะบ่นและแอบเคืองในความเอ๋อของที แต่คุณก็ไม่เคยทิ้งเพื่อนและรอดชีวิตไปด้วยกัน!"
            rank_col = COLOR_YELLOW

        eval_frame = tk.Frame(card, bg=COLOR_SURFACE_LIGHT, padx=12, pady=8)
        eval_frame.pack(fill="x", padx=15, pady=4)

        tk.Label(eval_frame, text=rank_title, font=FONT_HEADING, fg=rank_col, bg=COLOR_SURFACE_LIGHT).pack(anchor="w")
        tk.Label(eval_frame, text=rank_desc, font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, wraplength=520, justify="left").pack(anchor="w", pady=(2, 4))

        stats_txt = f"🏆 คะแนนความรู้สุขภาพ: {self.game_state['score']} แต้ม  |  ❤️ ความสัมพันธ์กับที: {rel} แต้ม"
        tk.Label(eval_frame, text=stats_txt, font=FONT_BODY_BOLD, fg=COLOR_YELLOW, bg=COLOR_SURFACE_LIGHT).pack(anchor="w")

        # ทบทวนความรู้
        edu_box = tk.Frame(card, bg=COLOR_SURFACE_LIGHT, padx=12, pady=6)
        edu_box.pack(fill="both", expand=True, padx=15, pady=6)

        tk.Label(edu_box, text="📚 4 บทเรียนสำคัญที่คุณได้เรียนรู้:", font=FONT_BODY_BOLD, fg=COLOR_ACCENT, bg=COLOR_SURFACE_LIGHT).pack(anchor="w")

        lessons = (
            "1. ยาสามัญประจำบ้าน 7 หมวด: พาราเซตามอล, ยาแก้แพ้เซทิริซีน, ผงเกลือแร่ ORS, น้ำเกลือ 0.9%, เบตาดีน, ซิลเวอร์เดิร์ม, ผ้าก๊อซ\n"
            "2. การตรวจยาเสื่อม: สังเกตยาเม็ดแตกร่วน ยาน้ำตกตะกอนแข็ง และเก็บในที่แห้งพ้นแสงแดด\n"
            "3. น้ำร้อนลวก: ล้างน้ำสะอาดอุณหภูมิห้อง 10-15 นาที ห้ามเจาะตุ่มน้ำ ห้ามทายาสีฟันหรือน้ำปลา\n"
            "4. แอปหมอพร้อม: นัดหมายออนไลน์ -> จองคิวหมอ -> นัดล่วงหน้าได้สูงสุด 3 เดือนจากวันจริง -> รับใบนัด สะดวก รวดเร็ว"
        )
        tk.Label(edu_box, text=lessons, font=FONT_SMALL, fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE_LIGHT, justify="left").pack(anchor="w", pady=2)
