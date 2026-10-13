"""
Save and Load System for Pharmacy Afterlife Visual Novel Game
จัดการระบบบันทึกและโหลดสถานะเกม รองรับระบบหลายช่องเซฟ (Multi-slot Save System)
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "saves")
os.makedirs(SAVE_DIR, exist_ok=True)

DEFAULT_STATE = {
    "player_name": "นักศึกษาหัวร้อน",
    "score": 0,
    "relationship": 50,  # ค่าความสนิทเริ่มต้น 50
    "current_scene": "scene1",  # scene1, scene2, scene3, finished
    "scene_step": 0,
    "completed_scenes": [],
    "inventory": [],
    "remaining_budget": 1000,
    "playtime_notes": "เริ่มการเดินทางในหอพัก",
    "saved_at": ""
}

def get_slot_path(slot_id):
    """ส่งคืนที่อยู่ไฟล์ของเซฟสล็อตที่กำหนด (slot1, slot2, slot3, auto)"""
    filename = f"save_{slot_id}.json"
    return os.path.join(SAVE_DIR, filename)

def save_game(game_state, slot_id="slot1"):
    """บันทึกข้อมูลสถานะเกมลงในไฟล์สล็อตที่กำหนด"""
    try:
        state = game_state.copy()
        state["saved_at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        filepath = get_slot_path(slot_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=4)
        
        # สำหรับความเข้ากันได้ย้อนหลังกับ savegame.json
        legacy_path = os.path.join(BASE_DIR, "savegame.json")
        with open(legacy_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=4)
            
        return True
    except Exception as e:
        print(f"Error saving game to {slot_id}: {e}")
        return False

def load_game(slot_id="slot1"):
    """โหลดข้อมูลจากไฟล์เซฟสล็อตที่กำหนด"""
    filepath = get_slot_path(slot_id)
    if not os.path.exists(filepath):
        # ถ้าไม่มีในโฟลเดอร์ saves ลองหา legacy savegame.json
        legacy_path = os.path.join(BASE_DIR, "savegame.json")
        if slot_id == "slot1" and os.path.exists(legacy_path):
            filepath = legacy_path
        else:
            return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = DEFAULT_STATE.copy()
            merged.update(data)
            return merged
    except Exception as e:
        print(f"Error loading save file {slot_id}: {e}")
        return None

def has_save(slot_id=None):
    """ตรวจสอบว่ามีไฟล์เซฟอยู่หรือไม่ (ถ้าไม่ระบุ slot_id ให้ตรวจว่ามีเซฟใดๆ หรือไม่)"""
    if slot_id:
        return os.path.exists(get_slot_path(slot_id)) or (slot_id == "slot1" and os.path.exists(os.path.join(BASE_DIR, "savegame.json")))
    
    # ตรวจสอบทุกสล็อต
    for s in ["slot1", "slot2", "slot3", "auto"]:
        if os.path.exists(get_slot_path(s)):
            return True
    return os.path.exists(os.path.join(BASE_DIR, "savegame.json"))

def get_all_slots_info():
    """ส่งคืนรายการข้อมูลสรุปของทุกช่องเซฟเพื่อใช้แสดงในหน้าต่าง Save/Load UI"""
    slots = [
        ("slot1", "ช่องเซฟที่ 1 (Slot 1)"),
        ("slot2", "ช่องเซฟที่ 2 (Slot 2)"),
        ("slot3", "ช่องเซฟที่ 3 (Slot 3)"),
        ("auto", "เซฟอัตโนมัติ (Auto-Save)")
    ]
    results = []
    scene_titles = {
        "scene1": "ฉากที่ 1: ตู้ยาสามัญ & ห้างสรรพสินค้า",
        "scene2": "ฉากที่ 2: วิกฤตน้ำร้อนลวกในห้องครัว",
        "scene3": "ฉากที่ 3: ร้านราเมน & แอปหมอพร้อม",
        "finished": "🎓 จบเกมสมบูรณ์"
    }

    for slot_id, slot_name in slots:
        data = load_game(slot_id)
        if data:
            sc_code = data.get("current_scene", "scene1")
            results.append({
                "slot_id": slot_id,
                "slot_name": slot_name,
                "is_empty": False,
                "player_name": data.get("player_name", "นักศึกษา"),
                "scene_title": scene_titles.get(sc_code, sc_code),
                "score": data.get("score", 0),
                "relationship": data.get("relationship", 50),
                "saved_at": data.get("saved_at", "ไม่ระบุเวลา"),
                "data": data
            })
        else:
            results.append({
                "slot_id": slot_id,
                "slot_name": slot_name,
                "is_empty": True,
                "player_name": "-",
                "scene_title": "ว่าง (ไม่มีข้อมูล)",
                "score": 0,
                "relationship": 0,
                "saved_at": "-",
                "data": None
            })
    return results

def delete_save(slot_id="slot1"):
    """ลบไฟล์เซฟในสล็อตที่กำหนด"""
    filepath = get_slot_path(slot_id)
    success = False
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            success = True
        except Exception:
            pass
    if slot_id == "slot1":
        legacy_path = os.path.join(BASE_DIR, "savegame.json")
        if os.path.exists(legacy_path):
            try:
                os.remove(legacy_path)
                success = True
            except Exception:
                pass
    return success
