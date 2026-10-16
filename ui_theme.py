"""
UI Theme and Styles for Pharmacy Afterlife Visual Novel Game
ธีมสี ฟอนต์ การจัดแต่ง และตัวจัดการรูปภาพ (ImageManager)
"""

import os
import tkinter as tk
# pyrefly: ignore [missing-import]
from PIL import Image, ImageTk

# Base Directory & Photo Assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(BASE_DIR, "photo")

# Palette สีหลัก (ธีม Dark Modern Cyber-Clinic)
COLOR_BG = "#0b111b"             # สีพื้นหลังหลัก
COLOR_SURFACE = "#152033"        # สีการ์ดหรือแผงควบคุม
COLOR_SURFACE_LIGHT = "#1f2e47"  # สีพื้นหลังส่วนที่ต้องการเน้น
COLOR_TEXT_MAIN = "#f1f5f9"      # ข้อความสีขาวสว่าง
COLOR_TEXT_MUTED = "#94a3b8"     # ข้อความสีเทา/คำอธิบาย
COLOR_ACCENT = "#38bdf8"         # สีฟ้าไฮไลต์ (Health Blue)
COLOR_ACCENT_HOVER = "#0284c7"   # สีฟ้าเข้มเมื่อ Hover
COLOR_GREEN = "#10b981"          # สีเขียวสำเร็จ/หมอพร้อม
COLOR_GREEN_HOVER = "#059669"
COLOR_RED = "#ef4444"            # สีแดงเตือน/ผิดพลาด
COLOR_RED_HOVER = "#dc2626"
COLOR_YELLOW = "#f59e0b"         # สีเหลืองระวัง/คำใบ้
COLOR_PURPLE = "#a855f7"         # สีม่วงความสัมพันธ์ / ค่าพิเศษ
COLOR_BORDER = "#334155"         # สีกรอบเส้น

# ฟอนต์ที่รองรับภาษาไทยได้ดีใน Windows
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 24, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 16, "bold")
FONT_HEADING = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_DIALOGUE = (FONT_FAMILY, 13)
FONT_SPEAKER = (FONT_FAMILY, 14, "bold")
FONT_CHOICE = (FONT_FAMILY, 12, "bold")
FONT_MONO = ("Consolas", 10)

# แผนผังภาพตัวละครที (Tee Character Sprite Pose Map)
TEE_POSE_MAP = {
    "sleepy": "tee_sleepy.png",
    "surprise": "tee_surprise.png",
    "happy": "tee_surprise.png",
    "talk": "tee_surprise.png",
    "angry": "tee_surprise.png",
    "panicked": "tee_burn.png",
    "worried": "tee_sleepy.png",
    "burn": "tee_burn.png",
    "bandage": "tee_bandage.png"
}


# -------------------------------------------------------------
# ระบบแคชรูปภาพ (Image Cache)
# -------------------------------------------------------------
# เก็บภาพที่โหลดแล้วไว้ในหน่วยความจำ RAM เพื่อไม่ต้องโหลดซ้ำจากฮาร์ดดิสก์
_image_cache = {}

def get_image(filename, size=None):
    """
    โหลดและปรับขนาดรูปภาพ พร้อมระบบแคช (Image Cache):
    - filename: ชื่อไฟล์รูปภาพ เช่น "paracetamol_tab.png"
    - size: ขนาด (กว้าง, สูง) ที่ต้องการย่อหรือขยาย เช่น (100, 100)
    """
    if not filename:
        return None

    # ตรวจสอบในแคชก่อน ถ้าเคยโหลดขนาดนี้ไว้แล้ว ให้ดึงมาใช้ได้ทันที
    key = (filename, size)
    if key in _image_cache:
        return _image_cache[key]

    # หากระบุไฟล์ .jpg แต่มีไฟล์ .png อยู่ ให้ลองหา .png ก่อน เพื่อได้ภาพพื้นหลังโปร่งใส
    candidate_names = [filename]
    if filename.endswith(".jpg"):
        candidate_names.insert(0, filename[:-4] + ".png")
    elif filename.endswith(".png"):
        candidate_names.append(filename[:-4] + ".jpg")

    target_path = None
    # ค้นหาไฟล์ภาพในโฟลเดอร์ photo/ ตามหมวดย่อย (med, bg, tee, member) และโฟลเดอร์ assets/
    sub_folders = ["med", "bg", "tee", "member", ""]
    for name in candidate_names:
        for sub in sub_folders:
            p = os.path.join(PHOTO_DIR, sub, name) if sub else os.path.join(PHOTO_DIR, name)
            if os.path.exists(p):
                target_path = p
                break
        if not target_path:
            alt_assets = os.path.join(BASE_DIR, "assets", "members", name)
            if os.path.exists(alt_assets):
                target_path = alt_assets
        if target_path:
            break

    # ถ้าหาไฟล์รูปภาพไม่เจอ ให้คืนค่า None อย่างปลอดภัย
    if not target_path or not os.path.exists(target_path):
        return None

    try:
        # เปิดไฟล์ด้วย Pillow และย่อขนาดด้วย LANCZOS เพื่อความคมชัดสูงสุด
        pil_img = Image.open(target_path)
        if size:
            pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
        
        # แปลงเป็น PhotoImage ของ Tkinter เพื่อใช้วาดลงบน Label หรือ Canvas
        tk_img = ImageTk.PhotoImage(pil_img)
        _image_cache[key] = tk_img
        return tk_img
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        return None


class StyledButton(tk.Button):
    """
    ปุ่มกดดีไซน์โมเดิร์น พร้อม Effect เปลี่ยนสีเมื่อ Hover, กดคลิก, และรองรับการโฟกัสด้วยคีย์บอร์ด
    """
    def __init__(self, parent, text, command=None, bg=COLOR_SURFACE_LIGHT, fg=COLOR_TEXT_MAIN, 
                 hover_bg=COLOR_ACCENT, hover_fg=COLOR_BG, font=FONT_BODY_BOLD, 
                 padx=16, pady=8, width=None, height=None, **kwargs):
        
        self.default_bg = bg
        self.default_fg = fg
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg

        btn_kwargs = {
            "text": text,
            "command": command,
            "font": font,
            "bg": self.default_bg,
            "fg": self.default_fg,
            "activebackground": self.hover_bg,
            "activeforeground": self.hover_fg,
            "relief": "flat",
            "cursor": "hand2",
            "padx": padx,
            "pady": pady,
            "bd": 0,
            "takefocus": 1,
            "highlightthickness": 1,
            "highlightbackground": COLOR_BORDER,
            "highlightcolor": COLOR_ACCENT
        }
        if width:
            btn_kwargs["width"] = width
        if height:
            btn_kwargs["height"] = height
            
        btn_kwargs.update(kwargs)
        super().__init__(parent, **btn_kwargs)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Return>", self.on_key_activate)
        self.bind("<space>", self.on_key_activate)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def on_enter(self, event=None):
        if self["state"] != "disabled":
            self.configure(bg=self.hover_bg, fg=self.hover_fg)

    def on_leave(self, event=None):
        if self["state"] != "disabled":
            self.configure(bg=self.default_bg, fg=self.default_fg, highlightbackground=COLOR_BORDER)

    def on_press(self, event=None):
        if self["state"] != "disabled":
            self.configure(highlightbackground=COLOR_ACCENT)

    def on_release(self, event=None):
        if self["state"] != "disabled":
            self.configure(highlightbackground=COLOR_BORDER)

    def on_focus_in(self, event=None):
        if self["state"] != "disabled":
            self.configure(highlightbackground=COLOR_ACCENT)

    def on_focus_out(self, event=None):
        if self["state"] != "disabled":
            self.configure(highlightbackground=COLOR_BORDER)

    def on_key_activate(self, event=None):
        if self["state"] != "disabled" and self["command"]:
            self.invoke()
            return "break"

    def set_active_theme(self, bg, fg, hover_bg, hover_fg):
        self.default_bg = bg
        self.default_fg = fg
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.configure(bg=bg, fg=fg, activebackground=hover_bg, activeforeground=hover_fg)
