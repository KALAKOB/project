import fitz
from PIL import Image
import numpy as np
import os

os.makedirs("assets/med_items", exist_ok=True)
os.makedirs("assets/long_pdf", exist_ok=True)

# 1. Open long.pdf and get page 0
doc = fitz.open("assets/long.pdf")
page = doc[0]

# Render high-resolution page
zoom = 300 / 72
pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
full_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# Find non-white poster bounding box
arr = np.array(full_img)
non_white = np.any(arr < 245, axis=2)
rows = np.where(non_white.any(axis=1))[0]
cols = np.where(non_white.any(axis=0))[0]

poster = full_img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
poster.save("assets/long_pdf/poster_hq.png")
pw, ph = poster.size
print(f"HQ Poster saved: {pw}x{ph}")

# Function to crop from poster using relative coordinates
def crop_rel(x0_pct, y0_pct, x1_pct, y1_pct, out_path):
    box = (int(pw * x0_pct), int(ph * y0_pct), int(pw * x1_pct), int(ph * y1_pct))
    c = poster.crop(box)
    c.save(out_path)
    return c

# Save high-res category banners
categories = {
    "cat_01_stomach": (0.04, 0.086, 0.96, 0.264),
    "cat_02_diarrhea": (0.04, 0.264, 0.50, 0.368),
    "cat_03_pain_fever": (0.50, 0.264, 0.96, 0.368),
    "cat_04_laxative": (0.04, 0.368, 0.96, 0.474),
    "cat_05_cough": (0.04, 0.474, 0.96, 0.602),
    "cat_06_dizziness": (0.04, 0.602, 0.96, 0.713),
    "cat_07_throat": (0.04, 0.713, 0.50, 0.812),
    "cat_08_eye": (0.50, 0.713, 0.63, 0.812),
    "cat_09_muscle": (0.63, 0.713, 0.96, 0.812),
    "cat_10_wound": (0.04, 0.812, 0.57, 0.912),
    "cat_11_skin": (0.57, 0.812, 0.96, 0.912),
    "cat_12_notice": (0.04, 0.912, 0.96, 0.985)
}

for name, coords in categories.items():
    crop_rel(coords[0], coords[1], coords[2], coords[3], f"assets/med_items/{name}.png")

# Now crop individual medicine items with their labels
items = {
    "med_paracetamol_tab": (0.55, 0.275, 0.72, 0.365),
    "med_paracetamol_syrup": (0.72, 0.275, 0.94, 0.365),
    "med_ors": (0.06, 0.275, 0.28, 0.365),
    "med_carbon": (0.28, 0.275, 0.48, 0.365),
    "med_antacil_tab": (0.06, 0.095, 0.23, 0.190),
    "med_mahahing": (0.23, 0.095, 0.43, 0.190),
    "med_eno": (0.43, 0.095, 0.63, 0.190),
    "med_air_x": (0.63, 0.095, 0.94, 0.190),
    "med_red_mixture": (0.06, 0.190, 0.25, 0.262),
    "med_antacid_gel": (0.25, 0.190, 0.65, 0.262),
    "med_gaviscon": (0.65, 0.190, 0.94, 0.262),
    "med_cough_syrup": (0.06, 0.485, 0.60, 0.600),
    "med_brown_cough": (0.60, 0.485, 0.94, 0.600),
    "med_ammonia": (0.06, 0.615, 0.25, 0.710),
    "med_inhaler_vicks": (0.25, 0.615, 0.58, 0.710),
    "med_motion_sickness": (0.58, 0.615, 0.94, 0.710),
    "med_gentian_violet": (0.06, 0.725, 0.25, 0.810),
    "med_strepsils": (0.25, 0.725, 0.49, 0.810),
    "med_opsar_eye": (0.50, 0.725, 0.63, 0.810),
    "med_tiger_balm": (0.63, 0.725, 0.95, 0.810),
    "med_tincture_iodine": (0.06, 0.820, 0.23, 0.910),
    "med_betadine": (0.23, 0.820, 0.40, 0.910),
    "med_saline": (0.40, 0.820, 0.50, 0.910),
    "med_alcohol": (0.50, 0.820, 0.57, 0.910),
    "med_calamine": (0.58, 0.820, 0.95, 0.910),
    "med_official_badge": (0.23, 0.925, 0.53, 0.970)
}

for name, coords in items.items():
    crop_rel(coords[0], coords[1], coords[2], coords[3], f"assets/med_items/{name}.png")

print(f"Extracted {len(items)} individual item crops into assets/med_items/")
