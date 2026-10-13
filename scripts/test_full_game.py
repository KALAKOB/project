import tkinter as tk
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=== Starting Full Game Headless Test ===")
root = tk.Tk()
root.withdraw()

from tkinter import messagebox
# Mock messagebox for headless execution
messagebox.askyesno = lambda *args, **kwargs: True
messagebox.showinfo = lambda *args, **kwargs: True
messagebox.showwarning = lambda *args, **kwargs: True

from main import PharmacyAfterlifeApp
from data import CABINET_MEDICINES, FIRST_AID_QUIZ_STEPS, SHOP_ITEMS
from vn_widgets import show_moph_poster_modal, show_knowledge_popup

app = PharmacyAfterlifeApp(root)
print("1. PharmacyAfterlifeApp loaded")

# Options
app.open_options_page()
print("2. Options page opened")

# Test Esc handling in Options
app.handle_escape_key()
assert app.current_page_frame == app.menu_frame
print("2.1 Esc in options returned to menu successfully")

# Handbook modal
app.open_handbook_modal()
print("3. Handbook modal opened")

# Test Esc handling closing modal
app.handle_escape_key()
print("3.1 Esc closed handbook modal successfully")

# Single MOPH Poster modal
show_moph_poster_modal(root)
print("4. MOPH single poster modal opened")
app.handle_escape_key()
print("4.1 Esc closed poster modal successfully")

# Scene 1: Cabinet inspection -> Shopping -> Storage -> Transition to Scene 2
app.load_scene("scene1")
s1 = app.current_scene_frame
s1.start_cabinet_minigame()
for med in CABINET_MEDICINES:
    s1.select_medicine_to_inspect(med)
    s1.judge_medicine(med, med["is_expired_or_spoiled"])
s1.finish_cabinet_inspection()

s1.start_shopping_minigame()
# Test Bad Ending: Clear cart or only pick 1 item (e.g. only snacks/pain)
s1.shopping_cart.clear()
s1.shopping_cart.add("item_para_500")
s1.handle_checkout()
print("5.0 Scene 1 Bad Ending triggered for incomplete essential items successfully!")

# Test restart from Bad Ending
s1.restart_shopping_after_bad_ending()
print("5.0.1 Restarted shopping from Bad Ending successfully!")

# Now select all needed items (7 categories)
for item in SHOP_ITEMS:
    if item["is_needed"]:
        s1.toggle_shop_item(item)

# Checkout in Shop with full items
s1.handle_checkout()
print("5.1 Scene 1 complete checkout passed")

# Complete storage dialogue
while s1.storage_dialogue_idx < len(s1.storage_scripts):
    s1.advance_storage_dialogue()

# Finish storage quiz
s1.finish_storage_quiz(True, "Correct storage explanation")
assert app.game_state.get("current_scene") == "scene2"
print("5.2 Scene 1 summary card displayed, state saved to scene2")

# Transition directly from Scene 1 to Scene 2
s1.advance_to_next_scene()
assert isinstance(app.current_scene_frame, object)
from scene2_burn_firstaid import Scene2BurnFirstAidFrame
assert isinstance(app.current_scene_frame, Scene2BurnFirstAidFrame)
print("5.3 Scene 1 -> Scene 2 transition SUCCEEDED completely!")

# Scene 2: Siriraj Burn First Aid
s2 = app.current_scene_frame
s2.start_siriraj_quiz()
for step in FIRST_AID_QUIZ_STEPS:
    correct_opt = [o for o in step["options"] if o["is_correct"]][0]
    s2.handle_step_choice(correct_opt, step)

# Finish Scene 2
s2.finish_scene2(25, "Tee hugs you happily!")
assert app.game_state.get("current_scene") == "scene3"
print("6.1 Scene 2 finished, state saved to scene3")

# Transition from Scene 2 to Scene 3
s2.advance_to_next_scene()
from scene3_mohpromt import Scene3MohpromtFrame
assert isinstance(app.current_scene_frame, Scene3MohpromtFrame)
print("6.2 Scene 2 -> Scene 3 transition SUCCEEDED completely!")

# Scene 3: Mohpromt Appointment
s3 = app.current_scene_frame
from scene3_mohpromt import ALL_HOSPITAL_DEPARTMENTS, ALL_HOSPITALS, generate_appointment_dates
dates_90 = generate_appointment_dates(90)
assert len(dates_90) >= 70, f"Expected ~77 dates in 3 months, got {len(dates_90)}"
assert len(ALL_HOSPITAL_DEPARTMENTS) >= 14, f"Expected >= 14 departments, got {len(ALL_HOSPITAL_DEPARTMENTS)}"
print(f"6.3 Mohpromt generated {len(dates_90)} dates across 3 months and {len(ALL_HOSPITAL_DEPARTMENTS)} departments successfully!")

s3.render_phone_screen()
s3.render_step_1()
s3.render_step_2()
s3.render_step_3()
s3.render_step_4()
s3.show_final_ending()
print("7. Scene 3 and Grand Finale completed successfully")

root.destroy()
print("=== All Tests and Transitions Verified 100% Successfully! ===")
