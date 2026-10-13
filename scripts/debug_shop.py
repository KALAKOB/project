import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui_theme import *
from data import SHOP_ITEMS

root = tk.Tk()
root.geometry("1000x680")
stage = tk.Frame(root, bg=COLOR_BG)
stage.pack(fill="both", expand=True)

body = tk.Frame(stage, bg=COLOR_BG)
body.pack(fill="both", expand=True)

left_shop = tk.Frame(body, bg=COLOR_SURFACE, bd=1, relief="solid")
left_shop.pack(side="left", fill="both", expand=True, padx=(0, 10))

canvas_shop = tk.Canvas(left_shop, bg=COLOR_SURFACE, highlightthickness=0)
scroll_shop = tk.Scrollbar(left_shop, orient="vertical", command=canvas_shop.yview)
items_frame = tk.Frame(canvas_shop, bg=COLOR_SURFACE)

items_frame.bind("<Configure>", lambda e: canvas_shop.configure(scrollregion=canvas_shop.bbox("all")))
win_id = canvas_shop.create_window((0, 0), window=items_frame, anchor="nw", width=540)
canvas_shop.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
scroll_shop.pack(side="right", fill="y", pady=5)

item = SHOP_ITEMS[0]
row = tk.Frame(items_frame, bg=COLOR_SURFACE_LIGHT, pady=3, padx=8)
row.pack(fill="x", pady=2)

lbl_icon = tk.Label(row, text="[ICON]", bg=COLOR_SURFACE_LIGHT)
lbl_icon.pack(side="left", padx=(0, 6))

tk.Label(row, text="[ยาจำเป็น]", font=FONT_SMALL, bg=COLOR_SURFACE_LIGHT, width=15, anchor="w").pack(side="left")
tk.Label(row, text=item["name"], font=FONT_BODY_BOLD, bg=COLOR_SURFACE_LIGHT, anchor="w").pack(side="left", padx=5)
tk.Label(row, text=str(item["price"]) + " B", font=FONT_BODY_BOLD, bg=COLOR_SURFACE_LIGHT, width=8).pack(side="left", padx=5)

btn = StyledButton(row, text="➕ หยิบใส่", font=FONT_SMALL, padx=8, pady=2)
btn.pack(side="right")

right_cart = tk.Frame(body, bg=COLOR_SURFACE, width=380, bd=1, relief="solid")
right_cart.pack(side="right", fill="both")
right_cart.pack_propagate(False)

root.update()
print("left_shop width:", left_shop.winfo_width())
print("canvas_shop width:", canvas_shop.winfo_width())
print("row width:", row.winfo_width())
print("btn x within row:", btn.winfo_x(), "btn width:", btn.winfo_width(), "total:", btn.winfo_x() + btn.winfo_width())
print("Visible in canvas?", (btn.winfo_x() + btn.winfo_width()) <= canvas_shop.winfo_width())
root.destroy()
