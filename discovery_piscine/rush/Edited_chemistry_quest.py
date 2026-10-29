#!/usr/bin/env python3
"""CHEMISTRY QUEST — CHALLENGE EDITION (Rush00).

Educational chemistry-symbol puzzles, not real-world reaction instructions.
Works in a UTF-8 terminal using only the Python standard library.
"""

import json
import math
import os
import random
import sys
import time
from pathlib import Path

SAVE_FILE = Path(__file__).resolve().parent / "chemistry_quest_save.json"#ให้ไฟล์ไปเชื่อม
FAST = os.environ.get("CQ_FAST") == "1" or not sys.stdout.isatty()#เช็คว่าteminalรันโหมดเร็วไหม/เช็คว่ารันผ่านteminalไหม
COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
RESET = "\033[0m" if COLOR else ""#รหัสพิเศษให้teminalเปลี่ยนสี
CYAN = "\033[96m" if COLOR else ""
GREEN = "\033[92m" if COLOR else ""
YELLOW = "\033[93m" if COLOR else ""
RED = "\033[91m" if COLOR else ""
MAGENTA = "\033[95m" if COLOR else ""
DIM = "\033[90m" if COLOR else ""
BOLD = "\033[1m" if COLOR else ""

ATOMS = {
    "H": "ไฮโดรเจน", "O": "ออกซิเจน", "C": "คาร์บอน",
    "Fe": "เหล็ก", "N": "ไนโตรเจน", "Ca": "แคลเซียม",
}

# ข้อมูลราคาขายของการ์ดแต่ละชนิด (ผันแปรตามความหายากของด่าน)
CARD_PRICES = {
    "H": 2, "O": 2, "C": 3, "Fe": 5, "N": 5, "Ca": 8
}
#dic
ATOM_INFO = {
    "H": {"mass": 1, "proton": 1},
    "O": {"mass": 16, "proton": 8},
    "C": {"mass": 12, "proton": 6},
    "Fe": {"mass": 56, "proton": 26},
    "N": {"mass": 14, "proton": 7},
    "Ca": {"mass": 40, "proton": 20},
}

RECIPES = {
    "water": {
        "name": "น้ำ", "formula": "H₂O", "needs": {"H": 2, "O": 1}, "xp": 30,
        "knowledge": 10, "fact": "โมเดล H₂O มี H 2 อะตอม และ O 1 อะตอม",
    },
    "co2": {
        "name": "คาร์บอนไดออกไซด์", "formula": "CO₂", "needs": {"C": 1, "O": 2},
        "xp": 35, "knowledge": 12, "fact": "CO₂ มี C 1 อะตอม และ O 2 อะตอม",
    },
    "methane": {
        "name": "มีเทน", "formula": "CH₄", "needs": {"C": 1, "H": 4},
        "xp": 40, "knowledge": 14, "fact": "CH₄ มี C 1 อะตอม และ H 4 อะตอม",
    },
    "iron_oxide": {
        "name": "เหล็ก(III)ออกไซด์", "formula": "Fe₂O₃", "needs": {"Fe": 2, "O": 3},
        "xp": 55, "knowledge": 18, "fact": "Fe₂O₃ มี Fe 2 อะตอม และ O 3 อะตอม",
    },
    "ammonia": {
        "name": "แอมโมเนีย", "formula": "NH₃", "needs": {"N": 1, "H": 3},
        "xp": 50, "knowledge": 16, "fact": "NH₃ มี N 1 อะตอม และ H 3 อะตอม",
    },
    "limestone": {
        "name": "แคลเซียมคาร์บอเนต", "formula": "CaCO₃",
        "needs": {"Ca": 1, "C": 1, "O": 3}, "xp": 60, "knowledge": 20,
        "fact": "CaCO₃ มี Ca 1, C 1 และ O 3 อะตอมต่อหนึ่งหน่วยสูตร",
    },
}

ZONES = [
    {"name": "ซากห้องทดลอง", "cost": 3, "level": 1, "requires": [],
     "finds": {"H": 3, "O": 2}, "story": "เก็บการ์ด H และ O ใต้แผงควบคุมที่พัง!"},
    {"name": "เรือนกระจกหมอกหนา", "cost": 4, "level": 1, "requires": [],
     "finds": {"C": 2, "O": 3}, "story": "พบชุดการ์ดธาตุใต้ต้นไม้ทดลอง!"},
    {"name": "เหมืองแม่เหล็ก", "cost": 5, "level": 2, "requires": ["water", "co2"],
     "finds": {"Fe": 2, "O": 3}, "story": "พบแร่สัญลักษณ์เหล็กหลังประตูอิเล็กทรอนิกส์!"},
    {"name": "คลังไนโตรเจน", "cost": 5, "level": 2, "requires": ["water", "co2"],
     "finds": {"N": 2, "H": 4}, "story": "เปิดกล่องการ์ด N และ H ในคลังเสมือน!"},
    {"name": "ถ้ำหินปูนโบราณ", "cost": 6, "level": 3,
     "requires": ["methane", "iron_oxide", "ammonia"],
     "finds": {"Ca": 1, "C": 1, "O": 3}, "story": "พบตัวอักษร Ca บนแท่นหินโบราณ!"},
]

DIFFICULTIES = {
    "1": {"name": "Explorer (เริ่มต้น)", "integrity": 60, "energy": 30,
          "supplies": 2, "decay": 2, "rest_decay": 2, "fail_decay": 3,
          "hazard": .50, "multiplier": .85, "rounds": 1, "recover": 20},
    "2": {"name": "Researcher (ท้าทาย)", "integrity": 50, "energy": 25,
          "supplies": 1, "decay": 3, "rest_decay": 3, "fail_decay": 5,
          "hazard": .65, "multiplier": 1.0, "rounds": 2, "recover": 15},
    "3": {"name": "Nightmare (ยากมาก)", "integrity": 40, "energy": 20,
          "supplies": 0, "decay": 4, "rest_decay": 4, "fail_decay": 7,
          "hazard": .80, "multiplier": 1.15, "rounds": 3, "recover": 10},
}

MAX_HP = 30
MAX_ENERGY = 30

def paint(text, color):
    return f"{color}{text}{RESET}"

def clear_screen():
    if sys.stdout.isatty() and os.environ.get("CQ_FAST") != "1":
        os.system("cls" if os.name == "nt" else "clear")

def slow_print(message, color=""):
    if FAST:
        print(paint(message, color) if color else message)
        return
    if color:
        sys.stdout.write(color)
    for character in message:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(.005)
    if color:
        sys.stdout.write(RESET)
    print()

def user_input(prompt="❯ "):
    try:
        return input(paint(prompt, YELLOW)).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nยกเลิก / ออกจากเกม")
        return "0"

def get_number(prompt, min_number=1, max_number=None, allow_back=True):
    while True:
        raw = user_input(prompt)
        if raw == "0" and allow_back:
            return None
        try:
            number = int(raw)
        except ValueError:
            print(paint("✗ ต้องกรอกจำนวนเต็มเท่านั้น", RED))
            continue
        if number < min_number or (max_number is not None and number > max_number):
            print(paint("✗ ตัวเลขอยู่นอกช่วงที่กำหนด", RED))
            continue
        return number

def wait_for_enter():
    user_input("\n[Enter เพื่อดำเนินการต่อ] ")

def heading(title):
    print(paint("\n" + "━" * 51, CYAN))
    print(paint("  " + title, BOLD + CYAN))
    print(paint("━" * 51, CYAN))

def banner():
    print(paint("╔══════════════════════════════════════════════════╗", MAGENTA))
    print(paint("║                CHEMISTRY QUEST                   ║", MAGENTA))
    print(paint("║            ★ CHALLENGE EDITION ★                ║", MAGENTA))
    print(paint("║               LOST LABORATORY                    ║", MAGENTA))
    print(paint("╚══════════════════════════════════════════════════╝", MAGENTA))
    print("  ⚗️  สำรวจ • คิดวิเคราะห์ • เอาชีวิตรอด • กู้เครื่องปฏิกรณ์")

def bar(value, maximum=30, length=15):
    filled = max(0, min(length, round(value / maximum * length)))
    color = GREEN if value > maximum * .45 else YELLOW if value > maximum * .2 else RED
    return paint("█" * filled, color) + paint("░" * (length - filled), DIM)

def create_game(name, difficulty="2"):
    config = DIFFICULTIES[difficulty]
    return {
        "schema_version": 2,
        "difficulty": difficulty,
        "status": "playing",
        "player": {"name": name[:24] or "Scientist", "hp": MAX_HP,
                   "energy": config["energy"], "xp": 0, "knowledge": 0},
        "integrity": config["integrity"],
        "max_integrity": config["integrity"],
        "supplies": config["supplies"], 
        "stabilizers": 0, # เริ่มต้นไม่มีชุดซ่อมแล้ว
        "credits": 0,     # เริ่มต้นเงิน 0
        "inventory": {"H": 0, "O": 0, "C": 0, "Fe": 0, "N": 0, "Ca": 0}, # เริ่มต้นการ์ด 0 ใบ
        "discovered": [], "journal": [], "next_note_id": 1,
        "stats": {"explorations": 0, "quiz_correct": 0, "quiz_wrong": 0,
                  "hazards": 0, "repairs": 0, "rests": 0},
    }

def get_level(state):
    return 1 + state["player"]["xp"] // 60

def show_hud(state):
    p = state["player"]
    max_integrity = state.get("max_integrity", 60)
    credits = state.get("credits", 0)
    print(f"  {p['name']} | LV {get_level(state)} | XP {p['xp']} | {DIFFICULTIES[state['difficulty']]['name']}")
    print(f"  ❤️  HP        {bar(p['hp'], MAX_HP)}  {p['hp']}/{MAX_HP} | 💰 {credits} Credits")
    print(f"  ⚡ ENERGY    {bar(p['energy'], MAX_ENERGY)}  {p['energy']}/{MAX_ENERGY}")
    print(f"  ☢️  REACTOR   {bar(state['integrity'], max_integrity)}  {state['integrity']}/{max_integrity}")
    print(f"  🧠 KNOWLEDGE {p['knowledge']} | 🔧 ชุดซ่อม {state['stabilizers']} | 🥫 อาหาร {state['supplies']}")
    print(f"  📘 วิจัยสำเร็จ {len(state['discovered'])}/{len(RECIPES)}")

def main_menu(state):
    clear_screen()
    banner()
    show_hud(state)
    heading("MAIN MENU — CHALLENGE")
    print("  [1] 🗺️  สำรวจพื้นที่ (เลือกเส้นทางปลอดภัย/เสี่ยง)")
    print("  [2] 🎒  กระเป๋าการ์ดอะตอม")
    print("  [3] ⚗️  ทดลองไขปริศนาเคมีหลายด่าน")
    print("  [4] 📝  สมุดบันทึกนักวิจัย")
    print("  [5] 📖  สารานุกรมเคมี")
    print("  [6] 🏕️  แคมป์ / ซ่อมเครื่องปฏิกรณ์")
    print("  [7] 🏆  ภารกิจและสถิติ")
    print("  [8] 💾  บันทึกเกม")
    print("  [9] 📂  โหลดเกม")
    print(" [10] 🚨  ด่านบอส: กู้เครื่องปฏิกรณ์")
    print(" [11] 📜  คู่มือและบทเรียนเคมี (Manual & Tutorial)")
    print(paint(" [12] 🛒  ร้านค้าศูนย์วิจัย (Trade/Shop)", YELLOW))
    print("  [0] 🚪  ออก")
    return user_input("\n🎮 เลือกเมนู >> ")

# ================= ฟังก์ชันร้านค้า (Trade / Shop) ================= #
def shop_menu(state):
    while True:
        clear_screen()
        heading("SUPPLY SHOP — ศูนย์การค้าวิจัย")
        credits = state.get("credits", 0)
        print(paint(f"  💰 เงินทุนวิจัย (Credits) ปัจจุบัน: {credits}", YELLOW))
        print(f"  🥫 เสบียง: {state['supplies']} | 🔧 ชุดซ่อม: {state['stabilizers']} | ❤️ HP: {state['player']['hp']}")
        print("\n  [1] 💎 ขายการ์ดธาตุเคมี (แลกเป็น Credits)")
        print("  [2] 🥫 ซื้อ เสบียง (ราคา: 25 Credits) - ใช้พักฟื้น HP/Energy ในแคมป์")
        print("  [3] 🔧 ซื้อ ชุดซ่อม REACTOR (ราคา: 80 Credits) - ใช้เพิ่มค่าความเสถียรในแคมป์")
        print("  [4] 💊 ซื้อ ยารักษาฉุกเฉิน (ราคา: 30 Credits) - กดซื้อแล้วเพิ่ม HP +10 ทันที")
        print("  [0] กลับเมนูหลัก")
        
        choice = user_input("\nเลือกเมนูร้านค้า >> ")
        
        if choice == "1":
            while True:
                heading("ขายการ์ดธาตุเคมี")
                inventory = state["inventory"]
                has_cards = False
                symbols = list(ATOMS.keys())
                
                for i, symbol in enumerate(symbols, 1):
                    count = inventory[symbol]
                    price = CARD_PRICES[symbol]
                    if count > 0:
                        has_cards = True
                    print(f"  [{i}] {symbol:<2} (มี {count} ใบ) - รับซื้อใบละ {price} Credits")
                
                if not has_cards:
                    print(paint("  คุณไม่มีการ์ดให้ขายแล้ว", YELLOW))
                    wait_for_enter()
                    break
                    
                selected = get_number("\nเลือกหมายเลขธาตุที่ต้องการขาย (0=ยกเลิก) >> ", max_number=len(symbols))
                if selected is None:
                    break
                
                symbol = symbols[selected - 1]
                if inventory[symbol] == 0:
                    print(paint("✗ คุณไม่มีการ์ดชนิดนี้", RED))
                    continue
                
                amount = get_number(f"จำนวน {symbol} ที่ต้องการขาย (1-{inventory[symbol]}) >> ", max_number=inventory[symbol])
                if amount is None:
                    continue
                
                total_earnings = amount * CARD_PRICES[symbol]
                inventory[symbol] -= amount
                state["credits"] += total_earnings
                print(paint(f"✓ ขาย {symbol} จำนวน {amount} ใบ ได้รับ {total_earnings} Credits!", GREEN))
                print(paint(f"💰 ยอดเงินปัจจุบัน: {state['credits']} Credits", YELLOW))
                wait_for_enter()
                
        elif choice == "2":
            if state["credits"] >= 25:
                state["credits"] -= 25
                state["supplies"] += 1
                print(paint("✓ ซื้อเสบียงสำเร็จ! นำไปใช้พักผ่อนในแคมป์ได้", GREEN))
            else:
                print(paint("✗ Credits ไม่พอ (ต้องการ 25)", RED))
            wait_for_enter()
            
        elif choice == "3":
            if state["credits"] >= 80:
                state["credits"] -= 80
                state["stabilizers"] += 1
                print(paint("✓ ซื้อชุดซ่อม REACTOR สำเร็จ!", GREEN))
            else:
                print(paint("✗ Credits ไม่พอ (ต้องการ 80)", RED))
            wait_for_enter()
            
        elif choice == "4":
            if state["credits"] >= 30:
                if state["player"]["hp"] >= MAX_HP:
                    print(paint("✗ HP ของคุณเต็มอยู่แล้ว ไม่จำเป็นต้องใช้ยา", YELLOW))
                else:
                    state["credits"] -= 30
                    gain = min(10, MAX_HP - state["player"]["hp"])
                    state["player"]["hp"] += gain
                    print(paint(f"✓ ใช้ยารักษาฉุกเฉิน HP +{gain} ทันที!", GREEN))
            else:
                print(paint("✗ Credits ไม่พอ (ต้องการ 30)", RED))
            wait_for_enter()
            
        elif choice == "0":
            break
        else:
            print(paint("✗ ไม่พบเมนู", RED))
            wait_for_enter()

def generate_dynamic_questions(recipe=None, rounds=3, is_boss=False):
    questions = []
    
    # ---------------- ชุดคำถามสำหรับด่านบอส ---------------- #
    if is_boss:
        for _ in range(rounds):
            q_type = random.randint(1, 4)
            n = random.randint(2, 6) * 2
            
            if q_type == 1:
                questions.append((f"การดุลสมการ: {n}H₂ + {n//2}O₂ → ?H₂O\n  จะได้ H₂O ทั้งหมดกี่โมเลกุล?", n, f"สัมประสิทธิ์ H₂O เท่ากับ H₂ คือ {n} โมเลกุล"))
            elif q_type == 2:
                questions.append((f"ปฏิกิริยา: C + O₂ → CO₂\n  ถ้ามี C {n} อะตอม และ O₂ มากเพียงพอ จะสร้าง CO₂ ได้กี่โมเลกุล?", n, f"อัตราส่วน 1:1 จะได้ {n} โมเลกุล"))
            elif q_type == 3:
                # คำใบ้ตายตัวสำหรับบอส CaCO3
                hint = "\n  💡 คำใบ้: น้ำหนักอะตอม Ca=40, C=12, O=16"
                questions.append((f"มวลของ CaCO₃ จำนวน {n} โมล เท่ากับกี่กรัม?{hint}", n * 100, f"{n} โมล × 100 กรัม/โมล = {n * 100} กรัม"))
            elif q_type == 4:
                ans = int(n * 1.5)
                questions.append((f"จากสมการดุล N₂ + 3H₂ → 2NH₃\n  หากต้องการสร้าง NH₃ {n} โมเลกุล ต้องใช้ H₂ กี่โมเลกุล?", ans, f"สัดส่วน H₂ : NH₃ คือ 3 : 2 จึงต้องใช้ H₂ = {n} × (3/2) = {ans} โมเลกุล"))
        return questions

    # ---------------- ชุดคำถามสำหรับด่านทดลองทั่วไป ---------------- #
    needs = recipe["needs"]
    elements = list(needs.keys())
    molar_mass = sum(ATOM_INFO[e]["mass"] * count for e, count in needs.items())
    
    # ระบบสร้าง String คำใบ้น้ำหนักอะตอมอัตโนมัติตามธาตุที่มีในสูตร
    hint_parts = [f"{e}={ATOM_INFO[e]['mass']}" for e in elements]
    mass_hint = f"\n  💡 คำใบ้: น้ำหนักอะตอม {', '.join(hint_parts)}"
    
    for _ in range(rounds):
        q_type = random.randint(1, 6)
        n = random.randint(2, 12)
        
        if q_type == 1:
            elem = random.choice(elements)
            ans = n * needs[elem]
            questions.append((f"สาร {recipe['formula']} จำนวน {n} โมเลกุล\n  มีอะตอมของธาตุ {elem} รวมทั้งหมดกี่อะตอม?", ans, f"{n} โมเลกุล × {needs[elem]} อะตอม = {ans}"))
            
        elif q_type == 2:
            total_atoms = sum(needs.values())
            ans = n * total_atoms
            questions.append((f"สาร {recipe['formula']} จำนวน {n} โมเลกุล\n  มีจำนวนอะตอมรวมทั้งหมดกี่อะตอม?", ans, f"{n} โมเลกุล × {total_atoms} อะตอมรวม = {ans}"))
            
        elif q_type == 3:
            ans = n * molar_mass
            questions.append((f"สาร {recipe['formula']} จำนวน {n} โมล\n  มีน้ำหนักรวมกี่กรัม?{mass_hint}", ans, f"{n} โมล × {molar_mass} g/mol = {ans} กรัม"))
            
        elif q_type == 4:
            elem = random.choice(elements)
            elem_mass = ATOM_INFO[elem]["mass"] * needs[elem]
            ans = round((elem_mass / molar_mass) * 100)
            questions.append((f"ธาตุ {elem} คิดเป็นร้อยละโดยมวล (% weight) เท่าใดใน {recipe['formula']}?\n  (ตอบเป็นจำนวนเต็มปัดเศษ){mass_hint}", ans, f"({elem_mass} / {molar_mass}) × 100 ≈ {ans}%"))
            
        elif q_type == 5:
            if len(elements) >= 2:
                elem1, elem2 = elements[0], elements[1]
                avail1 = n * needs[elem1] + random.randint(1, 5) 
                avail2 = n * needs[elem2]                         
                ans = n
                questions.append((f"ถ้ามี {elem1} {avail1} อะตอม และมี {elem2} {avail2} อะตอม\n  จะประกอบ {recipe['formula']} ได้สูงสุดกี่โมเลกุล?", ans, f"{elem2} จะถูกใช้หมดก่อนที่ {n} โมเลกุล"))
            else:
                ans = n * needs[elements[0]]
                questions.append((f"หากต้องการประกอบ {recipe['formula']} จำนวน {n} โมเลกุล\n  ต้องใช้สารตั้งต้น {elements[0]} กี่อะตอม?", ans, f"ต้องใช้ {needs[elements[0]]} ตัวต่อโมเลกุล × {n} = {ans}"))
                
        elif q_type == 6:
            total_protons = sum(ATOM_INFO[e]["proton"] * count for e, count in needs.items())
            ans = total_protons
            
            # ระบบสร้าง String คำใบ้โปรตอน (เลขอะตอม) อัตโนมัติ
            proton_hint_parts = [f"{e}={ATOM_INFO[e]['proton']}" for e in elements]
            proton_hint = f"\n  💡 คำใบ้: เลขอะตอม (จำนวนโปรตอน) {', '.join(proton_hint_parts)}"
            
            questions.append((f"โมเลกุลของ {recipe['formula']} 1 โมเลกุล\n  มีจำนวนโปรตอน (Protons) รวมทั้งหมดกี่ตัว?{proton_hint}", ans, f"ผลรวมเลขอะตอมของธาตุองค์ประกอบทั้งหมดคือ {ans} ตัว"))
            
    return questions

def manual_and_tutorial():
    while True:
        clear_screen()
        heading("GAME MANUAL & CHEMISTRY TUTORIAL")
        print("  [1] 📖 เป้าหมายและคู่มือการเล่น (Game Objectives)")
        print("  [2] ⚗️ บทเรียนเคมีเชิงลึก (Chemistry 101) พร้อมโจทย์ทดสอบ")
        print("  [0] กลับเมนูหลัก")
        choice = user_input("เลือก >> ")
        
        if choice == "1":
            heading("เป้าหมายและคู่มือการเล่น")
            print("  🎯 เป้าหมายหลัก:")
            print("    คุณคือนักวิทยาศาสตร์ที่ต้องกู้เครื่องปฏิกรณ์ (Reactor) ที่กำลังจะพังทลาย")
            print("    ค้นหาการ์ดธาตุเคมี (H, O, C, Fe, N, Ca) จากพื้นที่ต่างๆ")
            print("    นำมาประกอบกันเพื่อไขปริศนาสูตรเคมีให้ครบทั้ง 6 สูตร")
            print("\n  🕹️ วิธีการเล่น:")
            print("    1. [สำรวจพื้นที่] เพื่อหาการ์ดธาตุ (ระวัง ค่าพลังงานและ HP มีจำกัดที่ 30!)")
            print("    2. [ทดลองเคมี] เมื่อการ์ดครบ ให้ตอบคำถามเพื่อปลดล็อกสูตร")
            print("    3. [พักแคมป์ / ร้านค้า] ฟื้นฟูสภาพร่างกาย ซื้อเสบียงและขายการ์ดเหลือใช้")
            print("    4. หากสูตรครบ 6 อย่าง ให้เข้าสู้ [ด่านบอส] ก่อน Reactor เหลือ 0")
            wait_for_enter()
        elif choice == "2":
            heading("บทเรียนเคมีเชิงลึก (Chemistry 101)")
            print("  ⚛️ 1. การอ่านสูตรเคมี และ สัมประสิทธิ์")
            print("     - ตัวเลขห้อย (Subscript) บอกจำนวนอะตอม เช่น CO₂ มี C=1, O=2")
            print("     - ตัวเลขหน้าสูตร (Coefficient) บอกจำนวนโมเลกุล เช่น 3H₂O มี H = 3×2 = 6 อะตอม")
            print("\n  ⚖️ 2. มวลโมเลกุล (Molar Mass) และ % มวล")
            print("     - มวลรวมของโมเลกุลหาได้จากผลรวมมวลอะตอม (มวลมาตรฐาน: H=1, C=12, N=14, O=16, Ca=40, Fe=56)")
            print("     - เช่น H₂O = (1×2) + 16 = 18 กรัม/โมล")
            print("     - % มวล = (มวลของธาตุนั้นในโมเลกุล / มวลโมเลกุลรวม) × 100")
            print("\n  🧪 3. สารกำหนดปริมาณ (Limiting Reagent)")
            print("     - ในปฏิกิริยา สารตั้งต้นที่ 'หมดก่อน' จะเป็นตัวกำหนดว่าเกิดผลิตภัณฑ์ได้เท่าใด")
            print("     - เช่น ต้องการสร้าง H₂O (ใช้ H 2 ตัว, O 1 ตัว) ถ้ามี H 4 ตัว แต่ O 1 ตัว จะสร้างน้ำได้แค่ 1 โมเลกุล (เพราะ O หมดก่อน)")
            print("\n  🔬 4. อนุภาคมูลฐาน (Protons)")
            print("     - ผลรวมโปรตอนในโมเลกุล คือผลรวม 'เลขอะตอม' (เลขโปรตอน: H=1, C=6, N=7, O=8, Ca=20, Fe=26)")
            
            print(paint("\n  📝 ลองทำโจทย์ทดสอบความเข้าใจเชิงลึก (Mini Practice):", CYAN))
            
            ans1 = get_number("  ข้อที่ 1: CO₂ จำนวน 1 โมเลกุล มีมวลโมเลกุลรวมเท่าใด? (ตอบเป็นตัวเลข) >> ", max_number=1000)
            if ans1 is None:
                continue
            elif ans1 == 44:
                print(paint("  ✓ ถูกต้อง! มวล C(12) + O(16×2) = 44", GREEN))
            else:
                print(paint("  ✗ ยังไม่ถูกนะ คำตอบคือ 44 (12 + 32 = 44)", RED))
                
            ans2 = get_number("  ข้อที่ 2: ถ้ามี H 6 อะตอม และ O 2 อะตอม จะประกอบเป็น H₂O ได้สูงสุดกี่โมเลกุล? >> ", max_number=1000)
            if ans2 is None:
                continue
            elif ans2 == 2:
                print(paint("  ✓ ถูกต้อง! O หมดก่อน จึงสร้างได้แค่ 2 โมเลกุล (ใช้ H ไป 4 เหลือ 2 ตัว)", GREEN))
            else:
                print(paint("  ✗ ยังไม่ถูกนะ คำตอบคือ 2 (เพราะ O มีแค่ 2 ตัว จึงเป็นสารกำหนดปริมาณ สร้างน้ำได้แค่ 2 โมเลกุล)", RED))
                
            wait_for_enter()
        elif choice == "0":
            break
        else:
            print(paint("✗ ไม่พบเมนู", RED))
            wait_for_enter()

def change_integrity(state, amount):
    max_int = state.get("max_integrity", 60)
    state["integrity"] = max(0, min(max_int, state["integrity"] + amount))
    if state["integrity"] == 0 and state["status"] == "playing":
        state["status"] = "lost"
        print(paint("\n💥 GAME OVER! เครื่องปฏิกรณ์หยุดทำงาน!", RED))
        print("   เลือกเริ่มเกมใหม่หรือโหลดเซฟเพื่อแก้มือ")
        return False
    return True

def take_damage(state, amount):
    p = state["player"]
    p["hp"] = max(0, p["hp"] - amount)
    if p["hp"] == 0:
        print(paint("  🚑 HP หมด! หน่วยกู้ภัยพากลับแคมป์ แต่ REACTOR -10", RED))
        p["hp"] = 10 
        p["energy"] = max(p["energy"], 10)
        return change_integrity(state, -10)
    return True

def add_atoms(state, rewards):
    for symbol, count in rewards.items():
        state["inventory"][symbol] += count
    return sum(rewards.values())

def zone_open(state, zone):
    return (get_level(state) >= zone["level"] and
            all(key in state["discovered"] for key in zone["requires"]))

def explore(state):
    heading("WORLD MAP — เลือกเส้นทางและยอมรับความเสี่ยง")
    for index, zone in enumerate(ZONES, 1):
        status = "🔓" if zone_open(state, zone) else "🔒"
        print(f"  [{index}] {status} {zone['name']} | ENERGY {zone['cost']} | LV {zone['level']}")
    print("  [0] กลับ")
    selection = get_number("เลือกพื้นที่ >> ", max_number=len(ZONES))
    if selection is None:
        return
    zone = ZONES[selection - 1]
    if not zone_open(state, zone):
        required = [RECIPES[k]["formula"] for k in zone["requires"]
                    if k not in state["discovered"]]
        print(paint(f"🔒 ต้อง LV {zone['level']} และค้นพบสูตร: " +
                    (", ".join(required) if required else "ครบแล้ว"), RED))
        return

    print("  [1] ปลอดภัย: โอกาสเจออันตรายต่ำ")
    print("  [2] เสี่ยง: การ์ดโบนัส แต่เสี่ยงเจ็บตัวรุนแรงถึง 12 ดาเมจ (HP มีแค่ 30)")
    route = get_number("เลือกเส้นทาง (0=กลับ) >> ", max_number=2)
    if route is None:
        return
    
    config = DIFFICULTIES[state["difficulty"]]
    cost = math.ceil(zone["cost"] * config["multiplier"]) + (2 if route == 2 else 0)
    
    if state["player"]["energy"] < cost:
        print(paint(f"⚡ ต้องใช้ ENERGY {cost} แต่มีไม่พอ ไปพักแคมป์ก่อน", RED))
        return
    state["player"]["energy"] -= cost
    if not change_integrity(state, -config["decay"]):
        return
    state["stats"]["explorations"] += 1
    slow_print("  กำลังสำรวจซากอาคาร ...", CYAN)
    print(paint("  " + zone["story"], GREEN))
    
    rewards = {symbol: count + (1 if route == 2 else 0)
               for symbol, count in zone["finds"].items()}
    print(paint(f"  🎒 ได้การ์ด {add_atoms(state, rewards)} ใบ: " +
                ", ".join(f"{k}+{v}" for k, v in rewards.items()), GREEN))
    
    hazard_chance = config["hazard"] * (0.2 if route == 1 else 1)
    if random.random() < hazard_chance:
        damage = random.randint(2, 4) if route == 1 else random.randint(8, 12)
        state["stats"]["hazards"] += 1
        print(paint(f"  ⚠️  กับดัก! เลเซอร์ระเบิดใส่ตัว HP -{damage}", RED))
        if not take_damage(state, damage):
            return

# ถอดระบบทิ้งการ์ดออกจากหน้า Inventory เพราะผู้เล่นจะเอาไปขายใน Shop แทน
def show_inventory(state):
    heading("INVENTORY — การ์ดอะตอม")
    inventory = state["inventory"]
    for symbol, count in sorted(inventory.items()):
        print(f"  {symbol:>2}: {ATOMS[symbol]} — {count} ใบ")
    print(paint(f"  ทั้งหมด {sum(inventory.values())} ใบ", GREEN))
    print("  💡 (ไปที่เมนู [12] ร้านค้า เพื่อขายการ์ดแลก Credits)")
    wait_for_enter()

def missing_atoms(inventory, needs):
    return {symbol: count - inventory.get(symbol, 0)
            for symbol, count in needs.items()
            if inventory.get(symbol, 0) < count}

def solve_questions(state, questions, rounds, fail_decay):
    for i, (question, correct, explanation) in enumerate(questions, 1):
        print(paint(f"\n  🧠 คำถาม {i}/{rounds}", CYAN))
        print("  " + question)
        guess = get_number("  ตอบเป็นตัวเลข (0=ยกเลิก) >> ", max_number=1000000)
        if guess is None:
            print("  ยกเลิกด่าน: พลังงานที่เริ่มใช้ไปแล้วไม่คืน")
            return False
        if guess != correct:
            state["stats"]["quiz_wrong"] += 1
            print(paint(f"  ✗ ไม่ถูกต้อง! เฉลย: {correct} — {explanation}", RED))
            print(paint(f"  ☢️  REACTOR -{fail_decay} | HP -4", RED))
            if change_integrity(state, -fail_decay):
                take_damage(state, 4)
            return False
        state["stats"]["quiz_correct"] += 1
        print(paint("  ✓ ตอบถูก! " + explanation, GREEN))
        
        # เพิ่มโบนัสเล็กน้อยเมื่อตอบถูก
        bonus_credits = random.randint(1, 3)
        state["credits"] += bonus_credits
        print(paint(f"  💰 ได้รับรางวัลตอบถูก +{bonus_credits} Credits", YELLOW))
        
    return True

def lab(state):
    heading("VIRTUAL LAB — MULTI-STAGE CHEMISTRY CHALLENGE")
    keys = list(RECIPES)
    for i, key in enumerate(keys, 1):
        recipe = RECIPES[key]
        marker = "★" if key in state["discovered"] else "?"
        print(f"  [{i}] {marker} {recipe['name']} ({recipe['formula']})")
    print("  [0] กลับ")
    choice = get_number("เลือกโมเดล >> ", max_number=len(keys))
    if choice is None:
        return
    key = keys[choice - 1]
    recipe = RECIPES[key]
    missing = missing_atoms(state["inventory"], recipe["needs"])
    print("  การ์ดที่ต้องใช้: " + ", ".join(f"{s}×{n}" for s, n in recipe["needs"].items()))
    if missing:
        print(paint("  ✗ การ์ดไม่พอ: " + ", ".join(f"{s} ขาด {n}" for s, n in missing.items()), RED))
        return
    config = DIFFICULTIES[state["difficulty"]]
    cost = 3 + (config["rounds"] - 1) * 2
    if state["player"]["energy"] < cost:
        print(paint(f"  ✗ ต้องมี ENERGY อย่างน้อย {cost}", RED))
        return
    print(f"  ด่านนี้ต้องตอบถูกต่อเนื่อง {config['rounds']} ข้อ | ENERGY -{cost}")
    confirmed = user_input("  ยืนยันเริ่ม (y/N) >> ").lower()
    if confirmed != "y":
        return
    state["player"]["energy"] -= cost
    
    dynamic_qs = generate_dynamic_questions(recipe, config["rounds"])
    if not solve_questions(state, dynamic_qs, config["rounds"], config["fail_decay"]):
        return
        
    for symbol, count in recipe["needs"].items():
        state["inventory"][symbol] -= count
    slow_print("  วิเคราะห์แบบจำลององค์ประกอบ ...", CYAN)
    print(paint(f"  ✅ ปลดล็อกโมเดล {recipe['formula']} สำเร็จ!", GREEN))
    print("  📚 " + recipe["fact"])
    if key not in state["discovered"]:
        old_level = get_level(state)
        state["discovered"].append(key)
        state["player"]["xp"] += recipe["xp"]
        state["player"]["knowledge"] += recipe["knowledge"]
        print(paint(f"  ⭐ XP +{recipe['xp']} / KNOWLEDGE +{recipe['knowledge']}", YELLOW))
        if get_level(state) > old_level:
            print(paint(f"  ✨ LEVEL UP! LV {get_level(state)}", MAGENTA))
        if len(state["discovered"]) in (2, 5):
            state["stabilizers"] += 1
            print(paint("  🔧 รางวัลภารกิจ: ชุดซ่อม REACTOR +1", GREEN))
        if len(state["discovered"]) == len(RECIPES):
            print(paint("  🚨 สูตรครบแล้ว! ไปเมนู [10] เพื่อกู้เครื่องปฏิกรณ์", YELLOW))
    else:
        print("  ฝึกซ้ำสำเร็จ (จะไม่ได้ XP / ชุดซ่อมซ้ำ)")

def journal_menu(state):
    while True:
        heading("RESEARCH JOURNAL — สมุดบันทึกนักวิจัย")
        notes = state["journal"]
        for note in notes:
            print(f"  #{note['id']} {note['title']}")
        if not notes:
            print("  ยังไม่มีบันทึก")
        print("  [1] เพิ่ม  [2] อ่าน/ค้นหา  [3] แก้ไข  [4] ลบ  [0] กลับ")
        choice = user_input("เลือก >> ")
        if choice == "0":
            return
        elif choice == "1":
            if len(notes) >= 100:
                print(paint("✗ บันทึกครบ 100 รายการแล้ว", RED))
            else:
                title = user_input("ชื่อบันทึก (1-50 ตัวอักษร) >> ")
                content = user_input("เนื้อหา (1-500 ตัวอักษร) >> ")
                if not title or title == "0" or len(title) > 50 or not content or content == "0" or len(content) > 500:
                    print(paint("✗ ชื่อ/เนื้อหาไม่ถูกต้อง", RED))
                else:
                    notes.append({"id": state["next_note_id"], "title": title, "text": content})
                    state["next_note_id"] += 1
                    print(paint("✓ เพิ่มบันทึกแล้ว", GREEN))
        elif choice == "2":
            term = user_input("ค้นหา (Enter=ทั้งหมด) >> ").lower()
            matches = [note for note in notes if term in note["title"].lower()
                       or term in note["text"].lower()]
            print(f"  พบ {len(matches)} รายการ")
            for note in matches:
                print(f"  #{note['id']} {note['title']} — {note['text']}")
        elif choice in ("3", "4"):
            note_id = get_number("ID บันทึก (0=ยกเลิก) >> ")
            if note_id is None:
                continue
            note = next((n for n in notes if n["id"] == note_id), None)
            if note is None:
                print(paint("✗ ไม่พบ ID นี้", RED))
            elif choice == "3":
                title = user_input("ชื่อใหม่ (Enter=คงเดิม) >> ")
                content = user_input("เนื้อหาใหม่ (Enter=คงเดิม) >> ")
                if len(title) > 50 or len(content) > 500:
                    print(paint("✗ ข้อมูลยาวเกินไป", RED))
                else:
                    if title:
                        note["title"] = title
                    if content:
                        note["text"] = content
                    print(paint("✓ อัปเดตบันทึกสำเร็จ", GREEN))
            elif user_input("ยืนยันลบ (y/N) >> ").lower() == "y":
                notes.remove(note)
                print(paint("✓ ลบบันทึกสำเร็จ", GREEN))
        else:
            print(paint("✗ ไม่พบเมนู", RED))
        wait_for_enter()

def encyclopedia(state):
    heading("ENCYCLOPEDIA — ค้นหาความรู้")
    print("  [1] เรียงชื่อ  [2] เรียงจำนวนอะตอม  [3] ค้นหาสูตร  [0] กลับ")
    choice = user_input("เลือก >> ")
    records = list(RECIPES.items())
    if choice == "1":
        records.sort(key=lambda pair: pair[1]["name"])
    elif choice == "2":
        records.sort(key=lambda pair: sum(pair[1]["needs"].values()))
    elif choice == "3":
        term = user_input("ค้นหาชื่อ สูตร หรือธาตุ >> ").lower()
        records = [(key, rec) for key, rec in records
                   if term in rec["name"].lower() or term in rec["formula"].lower()
                   or term in " ".join(rec["needs"]).lower()]
    elif choice == "0":
        return
    else:
        print(paint("✗ ไม่พบเมนู", RED))
        return
    print(f"  พบ {len(records)} สูตร")
    for key, rec in records:
        mark = "★" if key in state["discovered"] else "○"
        print(f"  {mark} {rec['name']} ({rec['formula']}) — {rec['fact']}")

def camp(state):
    heading("CAMP — บริหารทรัพยากร")
    print(f"  🥫 เสบียง {state['supplies']} | 🔧 ชุดซ่อม {state['stabilizers']}")
    print("  [1] พักด้วยเสบียง (ENERGY เพิ่ม, HP เพิ่ม)")
    print("  [2] พักฉุกเฉิน (ไม่ใช้เสบียง แต่ REACTOR ลดมาก)")
    print("  [3] ซ่อม REACTOR (+15, ใช้ชุดซ่อม 1)")
    print("  [0] กลับ")
    choice = user_input("เลือก >> ")
    config = DIFFICULTIES[state["difficulty"]]
    if choice == "1":
        if state["supplies"] == 0:
            print(paint("✗ เสบียงหมด ใช้การพักฉุกเฉินได้ แต่มีความเสี่ยง", RED))
            return
        if state["player"]["hp"] == MAX_HP and state["player"]["energy"] == MAX_ENERGY:
            print("  HP และ ENERGY เต็มแล้ว ไม่ต้องใช้เสบียง")
            return
        state["supplies"] -= 1
        state["stats"]["rests"] += 1
        if not change_integrity(state, -config["rest_decay"]):
            return
        gain_energy = min(config["recover"], MAX_ENERGY - state["player"]["energy"])
        gain_hp = min(15, MAX_HP - state["player"]["hp"])
        state["player"]["energy"] += gain_energy
        state["player"]["hp"] += gain_hp
        print(paint(f"✓ ENERGY +{gain_energy}, HP +{gain_hp}", GREEN))
    elif choice == "2":
        print(paint("  ⚠️  การพักฉุกเฉิน: REACTOR -8 และ HP -5", RED))
        if user_input("ยืนยัน (y/N) >> ").lower() != "y":
            return
        state["stats"]["rests"] += 1
        if not change_integrity(state, -8):
            return
        if not take_damage(state, 5):
            return
        state["player"]["energy"] = min(MAX_ENERGY, state["player"]["energy"] + 15)
        print(paint("✓ ENERGY +15", GREEN))
    elif choice == "3":
        if state["stabilizers"] == 0:
            print(paint("✗ ไม่มีชุดซ่อม (ได้เป็นรางวัลเมื่อค้นพบ 2 และ 5 สูตร)", RED))
            return
        max_int = state.get("max_integrity", 60)
        if state["integrity"] == max_int:
            print("  เครื่องปฏิกรณ์เสถียรสุดแล้ว ไม่ต้องซ่อม")
            return
        state["stabilizers"] -= 1
        state["stats"]["repairs"] += 1
        before = state["integrity"]
        change_integrity(state, +15)
        print(paint(f"✓ REACTOR +{state['integrity'] - before}", GREEN))
    elif choice != "0":
        print(paint("✗ ไม่พบเมนู", RED))

def show_quests(state):
    heading("QUEST LOG — ภารกิจหลัก")
    show_hud(state)
    for key, recipe in RECIPES.items():
        mark = "✔" if key in state["discovered"] else "○"
        print(f"  {mark} {recipe['name']} ({recipe['formula']})")
    print("  เป้าหมาย: ค้นพบครบ 6 สูตร → เมนู 10 → ตอบปริศนาบอส")
    print(f"  สำรวจ {state['stats']['explorations']} ครั้ง | ถูก {state['stats']['quiz_correct']} "
          f"| ผิด {state['stats']['quiz_wrong']} | กับดัก {state['stats']['hazards']}")
    print(f"  พัก {state['stats']['rests']} | ซ่อม {state['stats']['repairs']} "
          f"| การ์ด {sum(state['inventory'].values())} | บันทึก {len(state['journal'])}")
    if state["status"] == "won":
        print(paint("  🏆 ภารกิจสำเร็จ: กู้ห้องทดลองได้แล้ว", GREEN))

def final_boss(state):
    heading("FINAL BOSS — REACTOR CORE")
    if len(state["discovered"]) != len(RECIPES):
        print(paint(f"  🔒 ต้องค้นพบครบ {len(RECIPES)} สูตรก่อน (ตอนนี้ {len(state['discovered'])})", RED))
        return
    if state["status"] == "won":
        print("  🏆 คุณกู้เครื่องปฏิกรณ์สำเร็จไปแล้ว!")
        return
    cost = 8 
    if state["player"]["energy"] < cost:
        print(paint(f"  ✗ ต้องมี ENERGY อย่างน้อย {cost}", RED))
        return
    rounds = {"1": 3, "2": 4, "3": 5}[state["difficulty"]]
    print(f"  ⚠️  ตอบถูกต่อเนื่อง {rounds} ข้อ | ENERGY -{cost}")
    print("  ถ้าพลาด ต้องเริ่มด่านบอสใหม่ และเสีย REACTOR")
    if user_input("  เข้าสู่ด่านบอส? (y/N) >> ").lower() != "y":
        return
    state["player"]["energy"] -= cost
    fail_decay = DIFFICULTIES[state["difficulty"]]["fail_decay"] + 2
    
    dynamic_qs = generate_dynamic_questions(rounds=rounds, is_boss=True)
    
    if not solve_questions(state, dynamic_qs, rounds, fail_decay):
        return
    slow_print("  [██████████] ระบบควบคุมกลับมาทำงาน ...", CYAN)
    state["status"] = "won"
    print(paint("\n  🏆 MISSION COMPLETE! คุณกู้เครื่องปฏิกรณ์ได้สำเร็จ!", YELLOW))
    print(f"  🧑‍🔬 {state['player']['name']} คือผู้พิทักษ์แห่ง CHEMISTRY QUEST!")

def save_game(state):
    try:
        with SAVE_FILE.open("w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(paint(f"✓ บันทึกข้อมูล: {SAVE_FILE.name}", GREEN))
    except OSError as error:
        print(paint(f"✗ บันทึกไม่สำเร็จ: {error}", RED))

def upgrade_legacy_state(raw):
    if not isinstance(raw, dict) or "schema_version" in raw:
        return raw
    if not all(k in raw for k in ("player", "inventory", "discovered", "journal", "next_note_id")):
        return raw
    updated = create_game("Scientist", "2")
    updated["player"] = raw["player"]
    updated["inventory"].update(raw["inventory"] if isinstance(raw["inventory"], dict) else {})
    updated["discovered"] = raw["discovered"]
    updated["journal"] = raw["journal"]
    updated["next_note_id"] = raw["next_note_id"]
    return updated

def validate_loaded_state(raw):
    raw = upgrade_legacy_state(raw)
    if not isinstance(raw, dict) or raw.get("schema_version") != 2:
        raise ValueError("รูปแบบไฟล์เซฟไม่รองรับ")
    if raw.get("difficulty") not in DIFFICULTIES or raw.get("status") not in ("playing", "won", "lost"):
        raise ValueError("ระดับความยากหรือสถานะเกมไม่ถูกต้อง")
    p = raw.get("player")
    if not isinstance(p, dict) or not isinstance(p.get("name"), str) or not 1 <= len(p["name"]) <= 24:
        raise ValueError("ข้อมูลผู้เล่นผิดรูปแบบ")
    for key in ("hp", "energy", "xp", "knowledge"):
        maximum = 100 if key in ("hp", "energy") else 1000000
        if type(p.get(key)) is not int or not 0 <= p[key] <= maximum:
            raise ValueError("ตัวเลขสถานะผู้เล่นไม่ถูกต้อง")
    for key, maximum in (("integrity", 120), ("supplies", 1000),
                         ("stabilizers", 1000), ("next_note_id", 10000000), ("credits", 1000000)):
        if type(raw.get(key)) is not int or not 0 <= raw[key] <= maximum:
            # ถ้าเป็นไฟล์เก่าไม่มี credits ให้ข้ามไปเติมทีหลังได้
            if key != "credits" or "credits" in raw:
                raise ValueError("ค่าทรัพยากรไม่ถูกต้อง")
    if raw["next_note_id"] == 0:
        raise ValueError("ID บันทึกไม่ถูกต้อง")
    bag = raw.get("inventory")
    if not isinstance(bag, dict) or set(bag) != set(ATOMS):
        raise ValueError("ข้อมูลกระเป๋าไม่ถูกต้อง")
    if any(type(v) is not int or not 0 <= v <= 1000000 for v in bag.values()):
        raise ValueError("จำนวนการ์ดไม่ถูกต้อง")
    unlocked = raw.get("discovered")
    if (not isinstance(unlocked, list) or any(not isinstance(k, str) or k not in RECIPES for k in unlocked)
            or len(unlocked) != len(set(unlocked))):
        raise ValueError("รายการค้นพบไม่ถูกต้อง")
    if raw["status"] == "won" and len(unlocked) != len(RECIPES):
        raise ValueError("บันทึกผลชนะไม่ถูกต้อง")
    if raw["status"] == "lost" and raw["integrity"] != 0:
        raise ValueError("บันทึกผลแพ้ไม่ถูกต้อง")
    if raw["status"] == "playing" and raw["integrity"] == 0:
        raise ValueError("ข้อมูล REACTOR ไม่ถูกต้อง")
    journal = raw.get("journal")
    if not isinstance(journal, list) or len(journal) > 100:
        raise ValueError("สมุดบันทึกไม่ถูกต้อง")
    ids = set()
    for note in journal:
        if not isinstance(note, dict):
            raise ValueError("รายการบันทึกผิดรูปแบบ")
        nid, title, content = note.get("id"), note.get("title"), note.get("text")
        if (type(nid) is not int or nid < 1 or nid in ids
                or not isinstance(title, str) or not 1 <= len(title) <= 50
                or not isinstance(content, str) or not 1 <= len(content) <= 500):
            raise ValueError("ข้อมูลบันทึกไม่ถูกต้อง")
        ids.add(nid)
    if raw["next_note_id"] <= max(ids, default=0):
        raise ValueError("ID บันทึกถัดไปไม่ถูกต้อง")
    stats = raw.get("stats")
    expected = {"explorations", "quiz_correct", "quiz_wrong", "hazards", "repairs", "rests"}
    if not isinstance(stats, dict) or set(stats) != expected:
        raise ValueError("สถิติผิดรูปแบบ")
    if any(type(v) is not int or not 0 <= v <= 1000000 for v in stats.values()):
        raise ValueError("ค่าสถิติไม่ถูกต้อง")
    return raw

def load_game(state):
    try:
        with SAVE_FILE.open("r", encoding="utf-8") as f:
            loaded = validate_loaded_state(json.load(f))
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        print(paint(f"✗ โหลดเกมไม่สำเร็จ: {error}", RED))
        return
    state.clear()
    state.update(loaded)
    
    if state["player"]["hp"] > MAX_HP:
        state["player"]["hp"] = MAX_HP
    if state["player"]["energy"] > MAX_ENERGY:
        state["player"]["energy"] = MAX_ENERGY
    if "max_integrity" not in state:
        state["max_integrity"] = 60
        state["integrity"] = min(state["integrity"], 60)
    if "credits" not in state:
        state["credits"] = 0
        
    print(paint("✓ โหลดข้อมูลสำเร็จ (รองรับเซฟเวอร์ชันเดิม และปรับสเกลใหม่แล้ว)", GREEN))

def start_game():
    clear_screen()
    banner()
    slow_print("\nปี 2086 เครื่องปฏิกรณ์ของห้องทดลองเสื่อมสภาพลงทุกครั้งที่คุณเดินทาง...", CYAN)
    print("คุณต้องรวบรวมการ์ดสูตรเคมีให้ครบ 6 ชนิด ก่อน REACTOR เหลือ 0")
    print(paint("* การ์ดและปฏิกิริยาเป็นแบบจำลองเพื่อเรียนรู้ ไม่ใช่การทดลองจริง *", YELLOW))
    name = user_input("\nตั้งชื่อตัวละคร (Enter=Scientist) >> ") or "Scientist"
    heading("DIFFICULTY SELECT")
    for key, config in DIFFICULTIES.items():
        print(f"  [{key}] {config['name']} | ข้อสอบ/ด่าน {config['rounds']} | REACTOR {config['integrity']}")
    choice = get_number("ระดับความยาก (0=Researcher) >> ", max_number=3)
    if choice is None:
        choice = 2
    return create_game(name, str(choice))

def main():
    state = start_game()
    while True:
        if state["status"] == "lost":
            heading("GAME OVER — เลือกวิธีเล่นต่อ")
            print("  [1] เริ่มใหม่  [2] โหลดเซฟ  [0] ออกจากเกม")
            choice = user_input("เลือก >> ")
            if choice == "1":
                state = start_game()
            elif choice == "2":
                load_game(state)
            elif choice == "0":
                return
            else:
                print(paint("✗ เลือก 0, 1 หรือ 2 เท่านั้น", RED))
            continue
        choice = main_menu(state)
        if choice == "0":
            print("\nขอบคุณที่เล่น! อย่าลืมบันทึกเกม (เมนู 8)")
            return
        elif choice == "1":
            explore(state)
        elif choice == "2":
            show_inventory(state)
        elif choice == "3":
            lab(state)
        elif choice == "4":
            journal_menu(state)
        elif choice == "5":
            encyclopedia(state)
        elif choice == "6":
            camp(state)
        elif choice == "7":
            show_quests(state)
        elif choice == "8":
            save_game(state)
        elif choice == "9":
            load_game(state)
        elif choice == "10":
            final_boss(state)
        elif choice == "11":
            manual_and_tutorial()
        elif choice == "12":
            shop_menu(state)
        else:
            print(paint("✗ ไม่พบเมนูนี้ เลือก 0–12", RED))
        if state["status"] != "lost":
            wait_for_enter()

if __name__ == "__main__":
    main()