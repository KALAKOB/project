"""
Stay Alive, Tee! (เมทข้าต้องรอด) - Core Data Module
ออกแบบโครงสร้างข้อมูลแบบ Single Source of Truth สำหรับ 3 มินิเกมหลัก:
  - มินิเกมที่ 1: การตรวจตู้ยาหอพัก และการซื้อยา/ของใช้ประจำหอพัก (งบ 1,000 บาท)
  - มินิเกมที่ 2: การปฐมพยาบาลแผลน้ำร้อนลวกตามมาตรฐาน รพ.ศิริราช
  - มินิเกมที่ 3: แบบจำลองการนัดหมายแพทย์ผ่านระบบหมอพร้อม
"""

# =============================================================================
# 1. ฐานข้อมูลสินค้าและยาหลัก (PRODUCTS - Single Source of Truth)
# =============================================================================
# เก็บข้อมูลผลิตภัณฑ์ที่ใช้ในเนื้อเรื่องเกมเพียงแหล่งเดียว
# จำแนกสถานะ: 'essential' (ยาจำเป็นพื้นฐาน), 'optional' (ยาทางเลือก/บรรเทาอาการ),
#              'specialized' (ยาเฉพาะทาง), 'dorm_supply' (ของใช้/ของกินในหอพัก)
PRODUCTS = {
    # --- ยาจำเป็นพื้นฐานและยาทางเดินอาหาร ---
    "para_tab": {
        "id": "para_tab",
        "name": "ยาพาราเซตามอล 500 มก.",
        "generic_name": "Paracetamol 500mg (ชนิดเม็ด)",
        "category": "ยาบรรเทาปวด ลดไข้",
        "cat_key": "pain",
        "role": "essential",
        "description": "ยาแก้ปวดลดไข้สามัญประจำบ้าน สำหรับไข้ ปวดศีรษะ ปวดเมื่อย",
        "image": "paracetamol_tab.png",
        "storage_rule": "เก็บที่อุณหภูมิห้องต่ำกว่า 30°C ในที่แห้ง พ้นแสงแดด"
    },
    "para_syrup": {
        "id": "para_syrup",
        "name": "ยาพาราเซตามอลน้ำเชื่อม (รสสตรอว์เบอร์รี)",
        "generic_name": "Paracetamol Syrup 120mg/5ml",
        "category": "ยาบรรเทาปวด ลดไข้",
        "cat_key": "pain",
        "role": "essential",
        "description": "ยาน้ำลดไข้ชนิดเชื่อม สำหรับผู้ที่กลืนยาเม็ดลำบากหรือเด็ก",
        "image": "paracetamol_syrup.png",
        "storage_rule": "เก็บที่อุณหภูมิห้อง ปิดฝาให้สนิท ห้ามแช่ช่องฟรีซ"
    },
    "cetirizine": {
        "id": "cetirizine",
        "name": "ยาแก้แพ้ เซทิริซีน 10 มก. (สูตรไม่ง่วง)",
        "generic_name": "Cetirizine HCl 10mg",
        "category": "ยาแก้แพ้ ลดน้ำมูก",
        "cat_key": "allergy",
        "role": "essential",
        "description": "บรรเทาอาการแพ้อากาศ ลมพิษ คัน จาม น้ำมูกไหล ไม่ง่วงซึม",
        "image": "motion_sickness.png",
        "storage_rule": "เก็บในที่แห้ง พ้นจากแสงแดดและความร้อน"
    },
    "cpm": {
        "id": "cpm",
        "name": "ยาแก้แพ้ คลอร์เฟนิรามีน 2 มก. (สูตรดั้งเดิม)",
        "generic_name": "Chlorpheniramine Maleate 2mg (CPM)",
        "category": "ยาแก้แพ้ ลดน้ำมูก",
        "cat_key": "allergy",
        "role": "essential",
        "description": "ยาแก้แพ้ลดน้ำมูก ลดจาม มีผลข้างเคียงทำให้ง่วงซึม",
        "image": "antacil_tab.png",
        "storage_rule": "เก็บในภาชนะปิดสนิท พ้นความชื้นและแสงแดด"
    },
    "ors": {
        "id": "ors",
        "name": "ผงเกลือแร่โออาร์เอส (ORS)",
        "generic_name": "Oral Rehydration Salts (ORS ท้องเสีย)",
        "category": "ยาแก้ท้องเสียและชดเชยน้ำ",
        "cat_key": "ors",
        "role": "essential",
        "description": "ชดเชยน้ำและเกลือแร่ที่สูญเสียจากอาการท้องร่วงหรืออาเจียน",
        "image": "ors.png",
        "storage_rule": "เก็บในที่แห้ง ปิดซองให้สนิท หากละลายน้ำแล้วดื่มไม่หมดใน 24 ชม. ให้ทิ้ง"
    },
    "carbon": {
        "id": "carbon",
        "name": "ยาผงถ่านรักษาอาการท้องเสีย (คาร์บอน)",
        "generic_name": "Activated Charcoal Capsules",
        "category": "ยาแก้ท้องเสียและขับสารพิษ",
        "cat_key": "stomach",
        "role": "optional",
        "description": "ดูดซับสารพิษและแก๊สในทางเดินอาหาร ทานห่างจากยาอื่นอย่างน้อย 2 ชม.",
        "image": "carbon.png",
        "storage_rule": "เก็บในที่แห้ง ป้องกันความชื้น"
    },
    "antacid_rabbit": {
        "id": "antacid_rabbit",
        "name": "ยาธาตุน้ำขาว ตรากระต่ายบิน",
        "generic_name": "Salol & Menthol White Mixture",
        "category": "ยาลดกรด เคลือบกระเพาะ ขับลม",
        "cat_key": "stomach",
        "role": "essential",
        "description": "บรรเทาอาการปวดท้อง แน่นจุกเสียด ขับลม และฆ่าเชื้ออ่อนๆ ในลำไส้",
        "image": "antacid_gel.png",
        "storage_rule": "เขย่าขวดก่อนใช้ เก็บที่อุณหภูมิห้อง ไม่ต้องแช่เย็น"
    },
    "red_mixture": {
        "id": "red_mixture",
        "name": "ยาธาตุน้ำแดง (สูตรขับลม)",
        "generic_name": "Carminative Mixture",
        "category": "ยาขับลม แก้ท้องอืด",
        "cat_key": "stomach",
        "role": "optional",
        "description": "ยาน้ำใสสีแดง กลิ่นหอมการบูรและเปปเปอร์มินต์ ช่วยขับลม แก้ท้องอืดเฟ้อ",
        "image": "red_mixture.png",
        "storage_rule": "เก็บที่อุณหภูมิห้อง พ้นแสงแดด ปิดฝาให้สนิท"
    },

    # --- ยาใส่แผล เวชภัณฑ์ และการปฐมพยาบาล ---
    "saline": {
        "id": "saline",
        "name": "น้ำเกลือล้างแผล 0.9% NSS (100 มล.)",
        "generic_name": "Normal Saline Solution 0.9% (Sterile)",
        "category": "น้ำยาล้างแผลและเวชภัณฑ์",
        "cat_key": "nss",
        "role": "essential",
        "description": "น้ำเกลือปราศจากเชื้อ ไอโซโทนิก ไม่แสบเนื้อเยื่อ ใช้ล้างแผลสด ล้างตา (เปิดแล้วใช้ได้ 30 วัน)",
        "image": "saline.png",
        "storage_rule": "เก็บที่อุณหภูมิห้อง เมื่อเปิดขวดแล้วมีอายุใช้งานได้ 30 วันเท่านั้น"
    },
    "betadine": {
        "id": "betadine",
        "name": "ยาใส่แผล โพวิโดน-ไอโอดีน (15 มล.)",
        "generic_name": "Povidone-Iodine 10% Antiseptic",
        "category": "ยาฆ่าเชื้อใส่แผลสด",
        "cat_key": "betadine",
        "role": "essential",
        "description": "น้ำยาฆ่าเชื้อสีน้ำตาล สำหรับทาแผลสด แผลถลอก ป้องกันการติดเชื้อ",
        "image": "betadine.png",
        "storage_rule": "เก็บในที่แห้ง พ้นแสงแดด ปิดฝาให้แน่นสนิท"
    },
    "gauze_kit": {
        "id": "gauze_kit",
        "name": "ชุดทำแผลและผ้าก๊อซปลอดเชื้อ",
        "generic_name": "Sterile Gauze Pads & Micropore Tape",
        "category": "อุปกรณ์ทำแผลและเวชภัณฑ์",
        "cat_key": "gauze",
        "role": "essential",
        "description": "ผ้าก๊อซฆ่าเชื้อพร้อมเทปแต่งแผล ใช้ปิดคลุมแผลสด แผลถลอก และแผลไฟไหม้กันเชื้อโรค",
        "image": "saline.png",
        "storage_rule": "เก็บในที่แห้ง ซองต้องปิดสนิทไม่ฉีกขาดหรือขึ้นรา"
    },
    "burn_cream": {
        "id": "burn_cream",
        "name": "ซิลเวอร์เดิร์ม ครีมทาแผลไฟไหม้ (25 กรัม)",
        "generic_name": "Silver Sulfadiazine 1% Cream",
        "category": "ยาทาแผลไฟไหม้น้ำร้อนลวก (ยาทางเลือกเสริม)",
        "cat_key": "burn",
        "role": "specialized",
        "description": "ครีมต้านเชื้อแบคทีเรียสำหรับแผลไหม้ที่มีตุ่มพอง (ไม่ใช่สิ่งจำเป็นบังคับของทุกบ้าน ขั้นแรกคือแช่น้ำสะอาด 15-20 นาที)",
        "image": "tincture_iodine.png",
        "storage_rule": "เก็บที่อุณหภูมิต่ำกว่า 30°C พ้นแสงแดด ปิดฝาหลอดให้สนิท"
    },
    "plaster": {
        "id": "plaster",
        "name": "พลาสเตอร์ยาปิดแผลสำเร็จรูป",
        "generic_name": "Adhesive Plasters / Bandages",
        "category": "อุปกรณ์ทำแผลและเวชภัณฑ์",
        "cat_key": "gauze",
        "role": "essential",
        "description": "พลาสเตอร์ปิดแผลพร้อมแผ่นซับ สำหรับบาดแผลขนาดเล็ก มีดบาด หรือแผลถลอก",
        "image": "tincture_iodine.png",
        "storage_rule": "เก็บในที่แห้ง ไม่ร้อนชื้น ป้องกันกาวละลายเสื่อมสภาพ"
    },

    # --- ยาใช้ภายนอกเพื่อบรรเทาอาการ ---
    "tiger_balm": {
        "id": "tiger_balm",
        "name": "ยาหม่องขี้ผึ้งสมุนไพร",
        "generic_name": "Herbal Analgesic Balm",
        "category": "ยาบรรเทาอาการภายนอก",
        "cat_key": "muscle",
        "role": "optional",
        "description": "ทาถูนวดบรรเทาอาการปวดเมื่อย เคล็ดขัดยอก และแมลงสัตว์กัดต่อย",
        "image": "tiger_balm.png",
        "storage_rule": "เก็บที่อุณหภูมิห้อง ปิดฝาให้สนิท ป้องกันเนื้อยาแห้งระเหย"
    },
    "muscle_cream": {
        "id": "muscle_cream",
        "name": "ครีมบรรเทาปวดกล้ามเนื้อ (สูตรร้อน)",
        "generic_name": "Analgesic Cream (Methyl Salicylate & Menthol)",
        "category": "ยาบรรเทาอาการภายนอก",
        "cat_key": "muscle",
        "role": "optional",
        "description": "ครีมทาบรรเทาอาการปวดตึงกล้ามเนื้อจากการยกของหรือออกกำลังกาย",
        "image": "tiger_balm.png",
        "storage_rule": "เก็บที่อุณหภูมิต่ำกว่า 30°C ปิดฝาให้สนิท ระวังอย่าให้เข้าตา"
    },
    "calamine": {
        "id": "calamine",
        "name": "คาลาไมน์โลชั่น ทาผดผื่นคัน",
        "generic_name": "Calamine Lotion",
        "category": "ยาใช้ภายนอกสำหรับผิวหนัง",
        "cat_key": "skin",
        "role": "optional",
        "description": "ยาน้ำแขวนตะกอนทาผิว บรรเทาอาการคัน ผดผื่น ลมพิษ แมลงสัตว์กัดต่อย",
        "image": "calamine.png",
        "storage_rule": "เขย่าขวดก่อนใช้ เก็บที่อุณหภูมิห้อง ไม่แช่เย็น"
    },

    # --- สินค้าและของใช้จำเป็น/ฟุ่มเฟือยในหอพัก (Non-medicine dorm supplies) ---
    "caffeine": {
        "id": "caffeine",
        "name": "กาแฟสกัดเข้มข้นแพ็ค 6 (ทีแอบหยิบลงตะกร้า)",
        "generic_name": "Canned Coffee 6-Pack",
        "category": "ของกิน/ของใช้หอพัก",
        "cat_key": None,
        "role": "dorm_supply",
        "description": "กาแฟกระป๋องที่ทีบอกว่าจำเป็นต่อการโต้รุ่งทำโมเดลส่งอาจารย์ (ไม่ใช่ยา)",
        "image": None,
        "storage_rule": "แช่เย็นหรือเก็บในที่แห้ง"
    },
    "snack": {
        "id": "snack",
        "name": "มันฝรั่งทอดกรอบ + ชานมไข่มุกกระป๋อง",
        "generic_name": "Potato Chips & Milk Tea",
        "category": "ของกิน/ของใช้หอพัก",
        "cat_key": None,
        "role": "dorm_supply",
        "description": "ของกินเล่นตอนดึก โซเดียมสูง ไม่ใช่ยารักษาโรค",
        "image": None,
        "storage_rule": "เก็บในที่แห้ง"
    },
    "gacha": {
        "id": "gacha",
        "name": "กล่องสุ่มโมเดลแมวเหมียวหน้าร้านยา",
        "generic_name": "Cat Figurine Blind Box",
        "category": "ของเล่นฟุ่มเฟือย",
        "cat_key": None,
        "role": "dorm_supply",
        "description": "ของเล่นสะสมตั้งโต๊ะ ทีเห็นแล้วตาเป็นประกายอยากได้เป็นกำลังใจทำงาน",
        "image": None,
        "storage_rule": "ตั้งโชว์บนโต๊ะทำงาน"
    }
}


# =============================================================================
# 2. สถานะสิ่งของในตู้ยาหอพัก (CABINET INVENTORY STATE)
# =============================================================================
# เก็บเฉพาะสภาพทางกายภาพ วันหมดอายุ และปัญหาของยา 8 ชิ้นในตู้ยาหอพักของที
# โดยอ้างอิงรหัสผลิตภัณฑ์จาก PRODUCTS เพื่อไม่ให้ข้อมูลซ้ำซ้อน
CABINET_INVENTORY = [
    {
        "slot_id": "med1",
        "product_id": "para_tab",
        "quantity": "1 แผง (เหลือ 6 เม็ด)",
        "expiry_date": "หมดอายุเมื่อ 3 เดือนก่อน",
        "packaging_condition": "แผงฟอยล์ฉีกขาด มีความชื้นซึมเข้า",
        "storage_condition": "วางไว้บนหลังตู้เย็นที่โดนความร้อนสะสมตลอดเวลา",
        "appearance": "เม็ดยาเปลี่ยนเป็นสีเหลือง มีจุดด่างสีน้ำตาล เม็ดยาบวมชื้นและแตกร่วนเป็นผง",
        "is_spoiled": True,
        "spoilage_reason": "เม็ดยาชื้น บวม แตกหัก และหมดอายุ ตัวยาเสื่อมสภาพไม่สามารถออกฤทธิ์ได้ ต้องทิ้งทันที!"
    },
    {
        "slot_id": "med2",
        "product_id": "para_syrup",
        "quantity": "1 ขวด (เหลือประมาณครึ่งขวด)",
        "expiry_date": "เหลืออีก 6 เดือน (ยังไม่ถึงวันหมดอายุบนฉลาก)",
        "packaging_condition": "ขวดแก้ว ปิดฝาไม่สนิท มีคราบน้ำเชื่อมเกาะเหนียวปากขวด",
        "storage_condition": "เก็บในตู้ยาในห้องน้ำที่มีไอน้ำและความชื้นสูง",
        "appearance": "น้ำยาแยกเป็น 2 ชั้นชัดเจน ด้านล่างตกตะกอนแข็งแน่น เขย่าแรงๆ นานกว่า 1 นาทีก็ไม่ยอมละลาย",
        "is_spoiled": True,
        "spoilage_reason": "ยาน้ำแขวนตะกอนตกตะกอนแข็งเขย่าไม่กระจายตัว ถือว่าเสื่อมคุณภาพอย่างถาวร ห้ามรับประทาน!"
    },
    {
        "slot_id": "med3",
        "product_id": "red_mixture",
        "quantity": "1 ขวด (ปริมาณเต็มขวด 180 มล.)",
        "expiry_date": "หมดอายุอีก 1 ปีข้างหน้า",
        "packaging_condition": "ขวดแก้วสีชา ฝาเกลียวปิดสนิท ฉลากสมบูรณ์",
        "storage_condition": "เก็บในตู้ยาแห้ง พ้นแสงแดด อุณหภูมิห้องปกติ",
        "appearance": "น้ำยาสีแดงใสสม่ำเสมอ ไม่มีตะกอน ไม่มีสิ่งแปลกปลอม กลิ่นหอมการบูรเปปเปอร์มินต์ปกติ",
        "is_spoiled": False,
        "spoilage_reason": "สารละลายใส สีสม่ำเสมอ กลิ่นปกติ และยังไม่หมดอายุ สภาพสมบูรณ์พร้อมใช้งาน"
    },
    {
        "slot_id": "med4",
        "product_id": "cpm",
        "quantity": "1 ซองยาแบ่งบรรจุ (10 เม็ด)",
        "expiry_date": "ไม่มีวันหมดอายุระบุชัดเจน (แบ่งบรรจุใส่ซองยา)",
        "packaging_condition": "ซองพลาสติกยับเยิน ปากซองซิปปิดไม่สนิท",
        "storage_condition": "วางไว้ริมหน้าต่างห้องนอน โดนแสงแดดส่องโดยตรง",
        "appearance": "เม็ดยาเยิ้มเหนียวติดก้นซอง เม็ดยาบวมพองและเริ่มมีราสีขาวเกาะขอบ",
        "is_spoiled": True,
        "spoilage_reason": "ยาชื้นจนเหนียว บวมพอง และมีเชื้อราขึ้น จัดเป็นยาเสื่อมคุณภาพและปนเปื้อน ต้องทิ้งทันที!"
    },
    {
        "slot_id": "med5",
        "product_id": "betadine",
        "quantity": "1 ขวด (เหลือ 1 ใน 4 ขวด)",
        "expiry_date": "หมดอายุเมื่อ 1 ปีครึ่งก่อน",
        "packaging_condition": "ขวดพลาสติกเปื้อนคราบกรัง ปากขวดแห้งติดเกลียว",
        "storage_condition": "วางปนกับเครื่องสำอางและความชื้นในห้องน้ำ",
        "appearance": "ปากขวดมีคราบแห้งกรัง น้ำยาสีเหลืองซีดจางมากจนเกือบใส ไม่มีสีน้ำตาลแดงเข้มเหมือนเดิม",
        "is_spoiled": True,
        "spoilage_reason": "ไอโอดีนสลายตัวจนหมดฤทธิ์ฆ่าเชื้อ และหมดอายุ หากนำไปใส่อาจทำให้แผลติดเชื้อ ต้องทิ้งทันที!"
    },
    {
        "slot_id": "med6",
        "product_id": "tiger_balm",
        "quantity": "1 ตลับ (19.4 กรัม ปริมาณเกือบเต็ม)",
        "expiry_date": "หมดอายุอีก 1 ปีครึ่ง",
        "packaging_condition": "ตลับแก้ว ฝาเกลียวโลหะปิดแน่นหนาสมบูรณ์",
        "storage_condition": "เก็บในลิ้นชักโต๊ะเขียนแบบ พ้นแสงแดดและความร้อน",
        "appearance": "เนื้อขี้ผึ้งเนียนละเอียด สีขาวอมเขียวสม่ำเสมอ กลิ่นการบูรหอมระเหยปกติ ฝาปิดแน่นหนา",
        "is_spoiled": False,
        "spoilage_reason": "เนื้อยาไม่แยกชั้น ไม่เหม็นหืน ยังไม่หมดอายุ สภาพพร้อมใช้งาน"
    },
    {
        "slot_id": "med7",
        "product_id": "saline",
        "quantity": "1 ขวดใหญ่ (500 มล. เหลือเกือบเต็ม)",
        "expiry_date": "วันหมดอายุที่ก้นขวดเหลือ 1 ปี (แต่เปิดใช้เกิน 30 วันแล้ว)",
        "packaging_condition": "ขวดพลาสติกถูกเปิดจุกทิ้งไว้ มีฝุ่นจับรอบปากขวด",
        "storage_condition": "วางทิ้งไว้บนขอบอ่างล้างหน้า มีสติกเกอร์เขียนเปิดใช้เมื่อ 6 เดือนก่อน",
        "appearance": "ขวดถูกเปิดฝาค้างไว้ ปากขวดมีฝุ่นจับ มีสติกเกอร์เขียนเปิดใช้เมื่อ 6 เดือนก่อน",
        "is_spoiled": True,
        "spoilage_reason": "น้ำเกลือปราศจากเชื้อเมื่อเปิดใช้แล้วมีอายุเพียง 30 วัน เปิดทิ้งไว้ 6 เดือนจะปนเปื้อนเชื้อโรค ห้ามใช้เด็ดขาด!"
    },
    {
        "slot_id": "med8",
        "product_id": "plaster",
        "quantity": "1 กล่อง (เหลือ 3 ซอง)",
        "expiry_date": "หมดอายุเมื่อ 8 เดือนก่อน",
        "packaging_condition": "กล่องกระดาษเปียกชื้น มีคราบราสีดำซึมเข้าซองยา",
        "storage_condition": "เก็บใต้ซิงก์ล้างจานในห้องครัวที่มีความชื้นสูง",
        "appearance": "ซองกระดาษมีคราบราสีดำขึ้น กาวละลายเหนียวเยิ้มหลุดลุ่ย",
        "is_spoiled": True,
        "spoilage_reason": "พลาสเตอร์ขึ้นราและกาวเสื่อมสภาพ แผ่นซับแผลปนเปื้อนเชื้อรา ต้องทิ้งทันที!"
    }
]


# =============================================================================
# 3. แคตตาล็อกสินค้าในร้านชำ/ร้านยา (SHOP CATALOG)
# =============================================================================
# แยกข้อมูลทางการค้า (ราคา, สต็อก, ความจำเป็น) ออกจากข้อมูลตัวยา
SHOP_CATALOG = [
    {
        "shop_id": "item_para",
        "product_id": "para_tab",
        "display_name": "พาราเซตามอล 500mg (2 แผง)",
        "price": 35,
        "stock": 20,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_para_syrup",
        "product_id": "para_syrup",
        "display_name": "พาราเซตามอลน้ำเชื่อม (ขวดรสสตรอว์เบอร์รี)",
        "price": 45,
        "stock": 10,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_cetirizine",
        "product_id": "cetirizine",
        "display_name": "ยาแก้แพ้ เซทิริซีน 10mg (ไม่ง่วง)",
        "price": 40,
        "stock": 15,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_cpm",
        "product_id": "cpm",
        "display_name": "ยาแก้แพ้ คลอร์เฟนิรามีน 2mg",
        "price": 30,
        "stock": 25,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_ors",
        "product_id": "ors",
        "display_name": "ผงเกลือแร่ ORS แก้ท้องเสีย (แพ็ค 5 ซอง)",
        "price": 40,
        "stock": 30,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_carbon",
        "product_id": "carbon",
        "display_name": "ยาผงถ่านคาร์บอน (CA-R-BON)",
        "price": 35,
        "stock": 12,
        "is_essential": False,
        "is_available": True
    },
    {
        "shop_id": "item_antacid",
        "product_id": "antacid_rabbit",
        "display_name": "ยาธาตุน้ำขาว ตรากระต่ายบิน",
        "price": 55,
        "stock": 8,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_nss",
        "product_id": "saline",
        "display_name": "น้ำเกลือล้างแผล 0.9% NSS (100ml)",
        "price": 45,
        "stock": 18,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_betadine",
        "product_id": "betadine",
        "display_name": "โพวิโดน-ไอโอดีน (เบตาดีน 15ml)",
        "price": 50,
        "stock": 14,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_gauze_kit",
        "product_id": "gauze_kit",
        "display_name": "ชุดทำแผล (ผ้าก๊อซปลอดเชื้อ + เทปแต่งแผล)",
        "price": 75,
        "stock": 16,
        "is_essential": True,
        "is_available": True
    },
    {
        "shop_id": "item_burn_cream",
        "product_id": "burn_cream",
        "display_name": "ซิลเวอร์เดิร์ม ครีมรักษาแผลไฟไหม้ (25g)",
        "price": 65,
        "stock": 5,
        "is_essential": False,  # ยาเฉพาะทางทางเลือกเสริม
        "is_available": True
    },
    {
        "shop_id": "item_calamine",
        "product_id": "calamine",
        "display_name": "คาลาไมน์โลชั่น ทาผดผื่นคัน",
        "price": 35,
        "stock": 10,
        "is_essential": False,
        "is_available": True
    },
    {
        "shop_id": "item_counterpain",
        "product_id": "muscle_cream",
        "display_name": "ครีมบรรเทาปวดกล้ามเนื้อ (สูตรร้อน)",
        "price": 70,
        "stock": 8,
        "is_essential": False,
        "is_available": True
    },
    {
        "shop_id": "item_caffeine",
        "product_id": "caffeine",
        "display_name": "กาแฟสกัดเข้มข้นแพ็ค 6 (ทีแอบหยิบลงตะกร้า)",
        "price": 95,
        "stock": 5,
        "is_essential": False,
        "is_available": True
    },
    {
        "shop_id": "item_snack",
        "product_id": "snack",
        "display_name": "มันฝรั่งทอดกรอบ + ชานมไข่มุกกระป๋อง",
        "price": 120,
        "stock": 6,
        "is_essential": False,
        "is_available": True
    },
    {
        "shop_id": "item_gacha",
        "product_id": "gacha",
        "display_name": "กล่องสุ่มโมเดลแมวเหมียวหน้าร้านยา",
        "price": 290,
        "stock": 3,
        "is_essential": False,
        "is_available": True
    }
]


# แมปรูปการ์ดหมวดหมู่ยาสามัญประจำบ้าน (11 หมวด MOPH Poster)
CAT_CARD_IMAGES = {
    "pain": "card_03_pain_fever.png",
    "allergy": "card_06_dizziness.png",
    "ors": "card_02_diarrhea.png",
    "stomach": "card_01_stomach.png",
    "nss": "card_10_wound.png",
    "betadine": "card_10_wound.png",
    "gauze": "card_10_wound.png",
    "burn": "card_10_wound.png",
    "muscle": "card_09_muscle.png",
    "skin": "card_11_skin.png"
}


# =============================================================================
# 4. ตัวแปลงและเชื่อมโยงข้อมูลสำหรับ Game Engine (RESOLVER FUNCTIONS)
# =============================================================================
def get_cabinet_medicines():
    """สร้างรายการยาในตู้ยา (CABINET_MEDICINES) โดยรวมข้อมูลจาก PRODUCTS เข้ากับสถานะจริง"""
    medicines = []
    for item in CABINET_INVENTORY:
        prod = PRODUCTS.get(item["product_id"], {})
        cat_k = prod.get("cat_key")
        card_img = CAT_CARD_IMAGES.get(cat_k, "card_01_stomach.png")
        medicines.append({
            "id": item["slot_id"],
            "product_id": item["product_id"],
            "name": prod.get("name", "ยาไม่ระบุชื่อ"),
            "type": prod.get("category", "ยาสามัญทั่วไป"),
            "category": prod.get("category", "ยาสามัญทั่วไป"),
            "cat_key": cat_k,
            "appearance": item["appearance"],
            "expiry": item["expiry_date"],
            "expiry_date": item["expiry_date"],
            "quantity": item["quantity"],
            "packaging_condition": item["packaging_condition"],
            "storage_condition": item["storage_condition"],
            "is_expired_or_spoiled": item["is_spoiled"],
            "reason": item["spoilage_reason"],
            "image": prod.get("image", ""),
            "card_image": card_img,
            "short_effect": prod.get("description", ""),
            "classification": "ยาสามัญประจำบ้านแผนปัจจุบัน",
            "storage_rule": prod.get("storage_rule", "")
        })
    return medicines

def get_shop_items():
    """สร้างรายการสินค้าในร้านค้า (SHOP_ITEMS) สำหรับมินิเกมช้อปปิ้ง"""
    items = []
    for item in SHOP_CATALOG:
        prod = PRODUCTS.get(item["product_id"], {})
        cat_k = prod.get("cat_key")
        card_img = CAT_CARD_IMAGES.get(cat_k)
        items.append({
            "id": item["shop_id"],
            "product_id": item["product_id"],
            "name": item["display_name"],
            "desc": prod.get("description", ""),
            "short_effect": prod.get("description", ""),
            "price": item["price"],
            "stock_qty": item["stock"],
            "is_needed": item["is_essential"],
            "is_available": item["is_available"],
            "category": prod.get("category", "สินค้าทั่วไป"),
            "cat_key": cat_k,
            "image": prod.get("image"),
            "card_image": card_img,
            "is_syrup": item["product_id"] == "para_syrup",
            "classification": "ยาสามัญประจำบ้านแผนปัจจุบัน" if cat_k else "ของใช้หอพัก"
        })
    return items

def get_missing_medicines():
    """สร้างเช็คลิสต์ยาที่ต้องซื้อทดแทน จากยาที่เสื่อมสภาพหรือหมดอายุในตู้ยา"""
    missing = []
    for item in CABINET_INVENTORY:
        if item["is_spoiled"]:
            prod = PRODUCTS.get(item["product_id"], {})
            missing.append({
                "product_id": item["product_id"],
                "cat_key": prod.get("cat_key"),
                "name": prod.get("name", "ยาจำเป็น"),
                "reason": f"ยาเดิมในตู้เสื่อมสภาพ/หมดอายุ ({item['appearance'][:32]}...) ต้องซื้อใหม่มาทดแทน"
            })
    return missing


# ส่งออกตัวแปรสำหรับเชื่อมต่อกับ Scene 1
CABINET_MEDICINES = get_cabinet_medicines()
SHOP_ITEMS = get_shop_items()
MISSING_CABINET_MEDICINES = get_missing_medicines()


# =============================================================================
# 5. ข้อมูลการเสื่อมสภาพและการจัดเก็บยา (DRUG STORAGE KNOWLEDGE)
# =============================================================================
DRUG_STORAGE_KNOWLEDGE = {
    "correct_location": "เก็บในที่แห้ง อุณหภูมิห้องปกติ (< 25-30°C) พ้นจากแสงแดดและความร้อนโดยตรง และเก็บให้พ้นมือเด็ก",
    "bad_locations": [
        "ห้องน้ำ (ความชื้นสูงทำให้ยาเม็ดบวม ชื้น และขึ้นราได้ง่าย)",
        "ในตู้เย็น (เว้นแต่ฉลากระบุไว้ เพราะความชื้นและหยดน้ำในตู้เย็นทำให้ยาเสื่อมคุณภาพ)",
        "ริมหน้าต่างหรือหลังตู้เย็น (โดนแสงแดดและความร้อนสะสมตลอดเวลา)",
        "ในรถยนต์ (ความร้อนสะสมทำให้ตัวยาเสื่อมสลายอย่างรวดเร็ว)"
    ],
    "degradation_signs": {
        "tablet": "เม็ดยาเปลี่ยนสี มีจุดด่าง บวม แตกหัก ร่วนเป็นผง ชื้น หรือมีกลิ่นแปลกไป",
        "capsule": "เปลือกแคปซูลนิ่ม เหนียวติดกันเป็นก้อน หรือผงยาข้างในแข็งจับตัว",
        "suspension": "ยาน้ำแขวนตะกอนตกตะกอนแข็งแน่น เขย่าแรงๆ แล้วไม่ยอมละลายกระจายตัว",
        "ointment": "เนื้อครีมหรือขี้ผึ้งแยกชั้น น้ำมันลอย หรือมีกลิ่นเหม็นหืน",
        "saline": "น้ำเกลือสะอาดเปิดฝาใช้งานแล้วเกิน 30 วัน จะปนเปื้อนเชื้อโรค"
    }
}


# =============================================================================
# 6. มินิเกมที่ 2: ข้อมูลการปฐมพยาบาลแผลน้ำร้อนลวก (BURN FIRST AID DATA)
# =============================================================================
# ยึดตามมาตรฐานการแพทย์ รพ.ศิริราช:
# 1. ใช้น้ำสะอาดอุณหภูมิห้องไหลผ่าน 15-20 นาที (ห้ามใช้น้ำแข็ง/ยาสีฟัน/น้ำปลา)
# 2. ถอดเครื่องประดับรอบบาดแผลออกทันที ก่อนเนื้อเยื่อบวมน้ำ
# 3. ห้ามเจาะตุ่มน้ำพองใส ปล่อยไว้เป็นเกราะป้องกันเชื้อโรคตามธรรมชาติ
# 4. ปิดแผลด้วยผ้าก๊อซปลอดเชื้ออย่างหลวมๆ (ครีมซิลเวอร์เดิร์มเป็นทางเลือกเสริม ไม่ใช่ข้อบังคับสากล)
# 5. แผลที่มือ ใบหน้า อวัยวะสำคัญ หรือแผลกว้าง ต้องพาไปพบแพทย์ที่โรงพยาบาล

BURN_LEVELS = [
    {
        "level": 1,
        "name": "ระดับที่ 1 (First degree burn)",
        "depth": "ชั้นหนังกำพร้าเท่านั้น",
        "symptoms": "ผิวหนังแดง แห้ง ไม่มีตุ่มพองใส แสบร้อนเล็กน้อย (เช่น ผิวไหม้แดด)",
        "healing": "หายได้เองใน 7 วัน ไม่ทิ้งแผลเป็น",
        "is_correct_for_tee": False
    },
    {
        "level": 2,
        "name": "ระดับที่ 2 ชนิดตื้น (Superficial Second degree burn)",
        "depth": "หนังกำพร้า + หนังแท้ส่วนตื้น",
        "symptoms": "มีตุ่มพองใส (Blister) พื้นแผลสีชมพูชื้น ปวดแสบมาก",
        "healing": "หายใน 2-3 สัปดาห์ ไม่ทิ้งแผลเป็น (เคสของที)",
        "is_correct_for_tee": True
    },
    {
        "level": 3,
        "name": "ระดับที่ 2 ชนิดลึก (Deep Second degree burn)",
        "depth": "ไหม้ถึงหนังแท้ส่วนลึก",
        "symptoms": "แผลสีเหลืองขาว แห้ง และไม่ค่อยปวด (เส้นประสาทถูกทำลาย)",
        "healing": "หายใน 3-6 สัปดาห์ มีโอกาสเกิดแผลเป็น",
        "is_correct_for_tee": False
    },
    {
        "level": 4,
        "name": "ระดับที่ 3 (Third degree burn)",
        "depth": "ทำลายหนังกำพร้าและหนังแท้ทั้งหมด",
        "symptoms": "แผลสีขาว ซีด หรือดำเกรียม หนาแข็ง ไม่รู้สึกเจ็บปวดเลย",
        "healing": "ต้องผ่าตัดปลูกถ่ายผิวหนังที่โรงพยาบาลโดยด่วน",
        "is_correct_for_tee": False
    }
]

FIRST_AID_QUIZ_STEPS = [
    {
        "step_num": 1,
        "title": "ข้อ 1: การประเมินระดับความลึกของบาดแผล",
        "situation": "คุณวิ่งมาดูแผลที่หลังมือของที พบว่า ผิวหนังบวมแดง มีตุ่มพองใส (Blister) ผุดขึ้นชัดเจน พื้นแผลสีชมพูชื้น และทีร้องโอดครวญว่า 'ปวดแสบมาก!'\n\nแผลของทีจัดเป็นแผลไหม้ระดับใด?",
        "options": [
            {
                "text": "แผลระดับที่ 1 - ไหม้เฉพาะหนังกำพร้า ผิวแดง ไม่มีตุ่มพอง",
                "is_correct": False,
                "explanation": "ไม่ถูกต้อง! แผลระดับที่ 1 จะมีเพียงรอยแดงและแสบร้อน แต่ต้องไม่มีตุ่มน้ำพอง"
            },
            {
                "text": "แผลระดับที่ 2 ชนิดตื้น - มีตุ่มพองใส พื้นแผลชมพูชื้น ปวดแสบมาก",
                "is_correct": True,
                "explanation": "ถูกต้อง! แผลของทีไหม้ถึงหนังแท้ส่วนตื้น มีตุ่มพองใส และปวดแสบมาก จัดเป็นระดับที่ 2 ชนิดตื้น หายได้ใน 2-3 สัปดาห์"
            },
            {
                "text": "แผลระดับที่ 2 ชนิดลึก - แผลสีเหลืองขาว แห้ง และไม่ค่อยปวด",
                "is_correct": False,
                "explanation": "ไม่ถูกต้อง! ชนิดลึกจะไม่ค่อยมีตุ่มพอง แผลแห้งสีเหลืองขาว และไม่ค่อยปวด"
            },
            {
                "text": "แผลระดับที่ 3 - แผลดำเกรียมหนาแข็ง ไม่รู้สึกเจ็บปวดเลย",
                "is_correct": False,
                "explanation": "ไม่ถูกต้อง! ระดับที่ 3 แผลจะลึกถึงชั้นใต้ผิวหนัง สีขาวซีดหรือดำกร้าน และไม่เจ็บเพราะเส้นประสาทตายหมด"
            }
        ]
    },
    {
        "step_num": 2,
        "title": "ข้อ 2: การจัดการเครื่องประดับรอบบาดแผล",
        "situation": "ที่ข้อมือขวาของที มีนาฬิกาข้อมือ และที่นิ้วชี้มีแหวนเงินสวมอยู่ใกล้บริเวณที่น้ำร้อนลวก\n\nคุณต้องทำอย่างไรเป็นอันดับแรก?",
        "options": [
            {
                "text": "ปล่อยทิ้งไว้ก่อน อย่าเพิ่งไปยุ่ง ค่อยให้หมอถอดให้",
                "is_correct": False,
                "explanation": "ผิดอย่างยิ่ง! เมื่อเวลาผ่านไป ผิวหนังจะบวมน้ำอย่างรวดเร็ว แหวนจะรัดแน่นจนถอดไม่ออกและทำให้นิ้วขาดเลือดได้!"
            },
            {
                "text": "รีบถอดนาฬิกาและแหวนออกทันทีอย่างนุ่มนวล ก่อนที่เนื้อเยื่อจะบวม",
                "is_correct": True,
                "explanation": "ถูกต้อง! ต้องรีบถอดเครื่องประดับออกทันทีก่อนที่ผิวหนังจะบวมน้ำจนบีบรัดหลอดเลือด"
            },
            {
                "text": "เอาเชือกมารัดเหนือนิ้วไว้แน่นๆ กันไม่ให้บวม",
                "is_correct": False,
                "explanation": "อันตรายมาก! การรัดแน่นจะยิ่งทำให้เนื้อเยื่อส่วนปลายขาดเลือดอย่างรุนแรง"
            }
        ]
    },
    {
        "step_num": 3,
        "title": "ข้อ 3: การระบายและลดความร้อนของแผล",
        "situation": "ทีสะบัดมือด้วยความเจ็บปวด ร้องขอน้ำแข็งในตู้เย็นมาประคบ\n\nวิธีลดความร้อนที่ถูกต้องตามมาตรฐานการแพทย์คือข้อใด?",
        "options": [
            {
                "text": "หยิบน้ำแข็งก้อนมาประคบแผลโดยตรงทันที",
                "is_correct": False,
                "explanation": "ข้อห้ามร้ายแรง! การใช้น้ำแข็งทำให้หลอดเลือดหดตัวฉับพลัน แผลลึกขึ้น เนื้อเยื่อขาดเลือดตายซ้ำซ้อน!"
            },
            {
                "text": "เปิดก๊อกน้ำสะอาดอุณหภูมิห้อง ให้น้ำไหลผ่านบาดแผลเบาๆ 15-20 นาที",
                "is_correct": True,
                "explanation": "ถูกต้องที่สุด! ควรล้างด้วยน้ำสะอาดอุณหภูมิห้องไหลผ่านเบาๆ 15-20 นาที เพื่อระบายความร้อนสะสมอย่างปลอดภัย"
            },
            {
                "text": "คว้ายาสีฟัน น้ำปลา หรือซีอิ๊วมาชโลมหนาๆ บนแผล",
                "is_correct": False,
                "explanation": "ความเชื่อผิดๆ ที่อันตรายมาก! ยาสีฟันหรือน้ำปลาจะกักเก็บความร้อน ทำให้ติดเชื้อรุนแรง และล้างออกยากมาก!"
            },
            {
                "text": "ใช้น้ำอุ่นจัดล้าง เพื่อปรับสภาพผิวหนังให้ชิน",
                "is_correct": False,
                "explanation": "ผิดมหันต์! การใช้น้ำอุ่นจะยิ่งเพิ่มการบาดเจ็บและความร้อนให้เนื้อเยื่อลึกขึ้น"
            }
        ]
    },
    {
        "step_num": 4,
        "title": "ข้อ 4: การดูแลตุ่มน้ำพองใส",
        "situation": "หลังระบายความร้อน ตุ่มน้ำพองใสขนาดประมาณ 2 เซนติเมตรผุดขึ้นที่หลังมือ ทีทำท่าจะเอาเล็บไปจิกแกะออก\n\nคุณจะแนะนำและปฏิบัติต่อตุ่มน้ำพองนี้อย่างไร?",
        "options": [
            {
                "text": "เอาเข็มมาเจาะตุ่มน้ำให้แตก แล้วรีดน้ำใสๆ ออกให้หมด",
                "is_correct": False,
                "explanation": "ห้ามทำเด็ดขาด! การเจาะตุ่มน้ำจะเปิดช่องให้แบคทีเรียเข้าสู่เนื้อเยื่อ นำไปสู่การติดเชื้อเป็นหนอง!"
            },
            {
                "text": "ห้ามเจาะหรือแกะตุ่มน้ำพองเด็ดขาด ปล่อยตุ่มน้ำไว้ให้คงสภาพ",
                "is_correct": True,
                "explanation": "ถูกต้องสมบูรณ์แบบ! ตุ่มน้ำใสทำหน้าที่เป็นเกราะป้องกันเชื้อโรคตามธรรมชาติ ช่วยให้ผิวหนังใหม่สร้างตัวด้านล่าง"
            },
            {
                "text": "ใช้แอลกอฮอล์ 70% ราดลงบนตุ่มน้ำพองโดยตรงเพื่อฆ่าเชื้อ",
                "is_correct": False,
                "explanation": "ผิดอย่างรุนแรง! แอลกอฮอล์จะทำลายเซลล์ผิวหนังที่กำลังสร้างใหม่ แสบทรมานมาก และทำให้เนื้อเยื่อตายเพิ่ม"
            }
        ]
    },
    {
        "step_num": 5,
        "title": "ข้อ 5: การทายาและปิดแผล",
        "situation": "หลังจากซับผิวรอบแผลแห้งด้วยผ้าสะอาดแล้ว ควรทำขั้นตอนใดต่อไป?",
        "options": [
            {
                "text": "ใช้ก้อนสำลีแห้งแปะลงบนตุ่มน้ำโดยตรง แล้วพันผ้ารัดแน่นๆ",
                "is_correct": False,
                "explanation": "ผิดอย่างยิ่ง! ใยสำลีจะติดแน่นกับตุ่มน้ำ เมื่อลอกออกแผลจะฉีกขาด และการพันแน่นจะขัดขวางการไหลเวียนเลือด"
            },
            {
                "text": "ทายาครีมเฉพาะที่ (เช่น ซิลเวอร์ซัลฟาไดอาซีน) แล้วปิดหลวมๆ ด้วยผ้าก๊อซปลอดเชื้อ",
                "is_correct": True,
                "explanation": "ถูกต้องที่สุด! หากมีครีมต้านเชื้อเฉพาะที่สามารถทาบางๆ ได้ แล้วปิดด้วยผ้าก๊อซปลอดเชื้ออย่างหลวมๆ เพื่อกันฝุ่นและลดการเสียดสี (สิ่งสำคัญคือความสะอาดและการไม่รัดแน่น)"
            },
            {
                "text": "โรยแป้งทาตัวให้ทั่วแผล แล้วปล่อยเปิดทิ้งไว้",
                "is_correct": False,
                "explanation": "ผิดมหันต์! ผงแป้งจะทำให้แผลระคายเคือง จับตัวเป็นก้อนกรัง และกลายเป็นแหล่งสะสมเชื้อโรค"
            }
        ]
    },
    {
        "step_num": 6,
        "title": "ข้อ 6: เกณฑ์การประเมินเพื่อพาไปพบแพทย์ที่โรงพยาบาล",
        "situation": "ในกรณีใดบ้างที่แผลไฟไหม้น้ำร้อนลวก 'ต้องพาไปพบแพทย์ที่โรงพยาบาลโดยด่วน'?",
        "options": [
            {
                "text": "เมื่อแผลกว้างกว่า 2-3 นิ้ว, เกิดที่ใบหน้า ข้อพับ มือเท้า, หรือมีอาการปวดรุนแรง/มีไข้",
                "is_correct": True,
                "explanation": "ถูกต้อง! หากแผลไหม้มีขนาดใหญ่ เกิดที่อวัยวะสำคัญ (ใบหน้า มือ เท้า ข้อพับ) หรือมีอาการติดเชื้อ ต้องรีบพาไปพบแพทย์ทันที"
            },
            {
                "text": "ไม่ต้องไปโรงพยาบาลเลย แผลไฟไหม้น้ำร้อนลวกทุกชนิดหายเองได้ที่บ้าน",
                "is_correct": False,
                "explanation": "อันตรายมาก! แผลที่ลึกหรือกว้างหากไม่ได้รับการดูแลจากแพทย์อาจนำไปสู่ภาวะติดเชื้อในกระแสเลือดได้"
            },
            {
                "text": "ไปเฉพาะเมื่อแผลเริ่มมีหนองและมีกลิ่นหลังจากผ่านไป 1 สัปดาห์",
                "is_correct": False,
                "explanation": "สายเกินไป! ควรรีบไปพบแพทย์ตั้งแต่เริ่มแรกเพื่อรับการทำแผลที่ถูกวิธี ป้องกันไม่ให้แผลลุกลาม"
            }
        ]
    }
]


# =============================================================================
# 7. มินิเกมที่ 3: แบบจำลองขั้นตอนแอปพลิเคชันหมอพร้อม (MOHPROM STEPS INFO)
# =============================================================================
# จำลองขั้นตอนการนัดหมายแพทย์เพื่อการศึกษา (Simulation Only - ไม่มีการส่งข้อมูลส่วนบุคคลจริง)
MOHPROM_STEPS_INFO = [
    {
        "step": 1,
        "screen_title": "หน้าแรก (Home Dashboard)",
        "desc": "เปิดแอปพลิเคชันหมอพร้อม และเลือกเมนู 'นัดหมายออนไลน์' หรือ 'จองคิวหาหมอ'"
    },
    {
        "step": 2,
        "screen_title": "เลือกบริการนัดหมาย",
        "desc": "เลือกบริการ 'จองคิวหมอ' เพื่อเข้ารับการตรวจรักษาในโรงพยาบาล"
    },
    {
        "step": 3,
        "screen_title": "ระบุข้อมูลการนัดหมาย",
        "desc": "เลือกจังหวัด, โรงพยาบาล, แผนกตรวจรักษา, วันที่, ช่วงเวลา และระบุอาการเบื้องต้น"
    },
    {
        "step": 4,
        "screen_title": "ยืนยันและรับใบนัดหมาย",
        "desc": "ตรวจสอบข้อมูล กดยืนยันการจอง และบันทึก 'ใบนัดหมายดิจิทัล' เพื่อนำไปยื่นในวันตรวจ"
    }
]
