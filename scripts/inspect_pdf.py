import fitz
import os

doc = fitz.open("assets/long.pdf")
page = doc[0]
print("Page dimensions:", page.rect)

# Save high-res rendered sections or full poster
os.makedirs("assets/long_pdf", exist_ok=True)
pix_full = page.get_pixmap(dpi=200)
pix_full.save("assets/long_pdf/household_meds_poster.png")
print(f"Saved full poster: {pix_full.width}x{pix_full.height}")

image_infos = page.get_image_info(xrefs=True)
sorted_imgs = sorted(image_infos, key=lambda x: (x["bbox"][1], x["bbox"][0]))
for i, item in enumerate(sorted_imgs):
    b = [round(v, 1) for v in item["bbox"]]
    print(f"{i+1:02d}: xref={item['xref']}, pos=({b[0]}, {b[1]} - {b[2]}, {b[3]}), size=({item['width']}x{item['height']})")

