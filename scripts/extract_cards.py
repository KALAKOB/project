import fitz
from PIL import Image
import numpy as np
import os
from scipy.ndimage import label, find_objects

os.makedirs("assets/med_cards", exist_ok=True)
os.makedirs("assets/med_items", exist_ok=True)
os.makedirs("assets/long_pdf", exist_ok=True)

# 1. Render poster from long.pdf
doc = fitz.open("assets/long.pdf")
page = doc[0]
zoom = 300 / 72
pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
full_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

arr = np.array(full_img)
non_white = np.any(arr < 245, axis=2)
rows = np.where(non_white.any(axis=1))[0]
cols = np.where(non_white.any(axis=0))[0]

poster = full_img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
poster.save("assets/long_pdf/poster_hq.png")
# Also save an optimized version for faster game rendering
poster.resize((660, 1640), Image.Resampling.LANCZOS).save("assets/long_pdf/poster_display.png")
pw, ph = poster.size
print(f"HQ Poster size: {pw}x{ph}")

arr_poster = np.array(poster)
is_navy = (arr_poster[:, :, 0] < 35) & (arr_poster[:, :, 2] > 60)
labeled, num_features = label(~is_navy)
objs = find_objects(labeled)
large_objs = [b for b in objs if (b[0].stop - b[0].start) > 100 and (b[1].stop - b[1].start) > 150]
large_objs_sorted = sorted(large_objs, key=lambda b: (b[0].start, b[1].start))

card_names = [
    ("card_01_stomach", "กลุ่มยาแก้ปวดท้อง ท้องอืด ท้องเฟ้อ"),
    ("card_02_diarrhea", "กลุ่มยาแก้ท้องเสีย"),
    ("card_03_pain_fever", "กลุ่มยาบรรเทาอาการปวดลดไข้"),
    ("card_04_laxatives", "กลุ่มยาระบาย"),
    ("card_05_cough", "กลุ่มยาแก้ไอขับเสมหะ"),
    ("card_06_dizziness", "กลุ่มยายาดมหรือยาทาแก้วิงเวียน"),
    ("card_07_throat", "ยาสำหรับโรคปากและลำคอ"),
    ("card_08_eye", "กลุ่มยาโรคตา"),
    ("card_09_muscle", "กลุ่มยาบรรเทาอาการปวดกล้ามเนื้อ แมลงกัดต่อย"),
    ("card_10_wound", "กลุ่มยาใส่แผล ล้างแผล"),
    ("card_11_skin", "กลุ่มยาโรคผิวหนัง"),
]

for i, (name, title) in enumerate(card_names):
    if i < len(large_objs_sorted):
        ys, xs = large_objs_sorted[i]
        card_img = poster.crop((xs.start, ys.start, xs.stop, ys.stop))
        card_img.save(f"assets/med_cards/{name}.png")
        print(f"Saved {name}.png ({card_img.size}) - {title}")

# Header title banner
banner = poster.crop((0, 0, pw, 285))
banner.save("assets/med_cards/banner_title.png")

# Bottom warning banner
footer = poster.crop((0, 2990, pw, ph))
footer.save("assets/med_cards/banner_footer.png")

print("All medical cards and banners from long.pdf saved successfully!")
