#!/usr/bin/env python3
"""Island Survival - Python terminal game for Rush 00.

Run: python3 main.py
No additional libraries required.
"""

import random


RECIPES = {
    "1": {"name": "เพิงพัก", "cost": {"ไม้": 3, "หิน": 2}},
    "2": {"name": "กองไฟส่งสัญญาณ", "cost": {"ไม้": 4, "หิน": 3}},
}

FOODS = {
    "1": {"name": "มะพร้าว", "hunger": 20, "thirst": 15},
    "2": {"name": "กล้วย", "hunger": 30, "thirst": 0},
    "3": {"name": "น้ำจืด", "hunger": 0, "thirst": 40},
}


# inventory เป็น list ของ dictionary เช่น [{"name": "ไม้", "quantity": 2}]
def get_quantity(inventory, name):
    for item in inventory:
        if item["name"] == name:
            return item["quantity"]
    return 0


def add_item(inventory, name, quantity):
    if quantity <= 0:
        return False
    for item in inventory:
        if item["name"] == name:
            item["quantity"] += quantity  # อัปเดต record เดิม
            return True
    inventory.append({"name": name, "quantity": quantity})  # เพิ่ม record
    return True


def remove_item(inventory, name, quantity):
    if quantity <= 0:
        return False
    for item in inventory:
        if item["name"] == name:
            if item["quantity"] < quantity:
                return False
            item["quantity"] -= quantity  # อัปเดตจำนวน
            if item["quantity"] == 0:
                inventory.remove(item)  # ลบ record เมื่อของหมด
            return True
    return False


def read_positive_int(message):
    while True:
        raw = input(message).strip()
        try:
            number = int(raw)
            if number > 0:
                return number
        except ValueError:
            pass
        print("กรุณากรอกจำนวนเต็มที่มากกว่า 0")


def show_status(player, inventory, buildings):
    print("\n========== สถานะผู้รอดชีวิต ==========")
    print("วันที่:", player["day"])
    print("พลังชีวิต:", player["health"], "/ 100")
    print("ความหิว:", player["hunger"], "/ 100 (ยิ่งมากยิ่งหิว)")
    print("ความกระหาย:", player["thirst"], "/ 100 (ยิ่งมากยิ่งกระหาย)")
    print("พลังงาน:", player["energy"], "/ 100")
    print("\n--- กระเป๋า (เรียงจากจำนวนมากไปน้อย) ---")
    if not inventory:
        print("ยังไม่มีไอเทม")
    else:
        sorted_items = sorted(inventory, key=lambda item: item["quantity"], reverse=True)
        total = 0
        for item in sorted_items:
            print(f"{item['name']}: {item['quantity']} ชิ้น")
            total += item["quantity"]
        print("จำนวนไอเทมรวม:", total, "ชิ้น")
    print("\nสิ่งปลูกสร้าง:", ", ".join(buildings) if buildings else "ยังไม่มี")


def explore(player, inventory):
    if player["energy"] < 20:
        print("พลังงานไม่พอ! ต้องมีอย่างน้อย 20 แต้ม ลองจบวันเพื่อพักผ่อน")
        return

    discoveries = [
        ("ไม้", 2),
        ("หิน", 2),
        ("มะพร้าว", 2),
        ("กล้วย", 2),
        ("น้ำจืด", 2),
    ]
    name, quantity = random.choice(discoveries)
    add_item(inventory, name, quantity)
    player["energy"] -= 20
    player["hunger"] = min(100, player["hunger"] + 7)
    player["thirst"] = min(100, player["thirst"] + 10)
    print(f"\nออกสำรวจสำเร็จ! พบ {name} จำนวน {quantity} ชิ้น")

    if random.randint(1, 10) == 1:
        player["health"] = max(0, player["health"] - 10)
        print("ระหว่างทางถูกหนามตำ! พลังชีวิต -10")


def eat_or_drink(player, inventory):
    print("\n--- ใช้เสบียง ---")
    for key, food in FOODS.items():
        print(f"{key}. {food['name']} (มี {get_quantity(inventory, food['name'])})")
    choice = input("เลือกเสบียง (0 = ย้อนกลับ): ").strip()
    if choice == "0":
        return
    if choice not in FOODS:
        print("ไม่มีตัวเลือกนี้")
        return

    food = FOODS[choice]
    if not remove_item(inventory, food["name"], 1):
        print("เสบียงชนิดนี้ไม่เพียงพอ")
        return
    player["hunger"] = max(0, player["hunger"] - food["hunger"])
    player["thirst"] = max(0, player["thirst"] - food["thirst"])
    print(f"ใช้ {food['name']} แล้ว ความหิว/กระหายลดลง!")


def can_craft(inventory, cost):
    for name, quantity in cost.items():
        if get_quantity(inventory, name) < quantity:
            return False
    return True


def craft(inventory, buildings):
    print("\n--- สร้างสิ่งปลูกสร้าง ---")
    for key, recipe in RECIPES.items():
        material_text = ", ".join(
            f"{name} {quantity}" for name, quantity in recipe["cost"].items()
        )
        print(f"{key}. {recipe['name']} (ใช้ {material_text})")
    choice = input("เลือกสิ่งที่จะสร้าง (0 = ย้อนกลับ): ").strip()
    if choice == "0":
        return
    if choice not in RECIPES:
        print("ไม่มีสิ่งปลูกสร้างที่เลือก")
        return

    recipe = RECIPES[choice]
    if recipe["name"] in buildings:
        print("สร้างสิ่งนี้ไว้แล้ว ไม่สามารถสร้างซ้ำได้")
    elif not can_craft(inventory, recipe["cost"]):
        print("วัตถุดิบไม่เพียงพอ")
    else:
        for name, quantity in recipe["cost"].items():
            remove_item(inventory, name, quantity)
        buildings.append(recipe["name"])
        print("สร้าง", recipe["name"], "สำเร็จ!")


def search_item(inventory):
    keyword = input("พิมพ์ชื่อไอเทมที่ต้องการค้นหา: ").strip()
    if not keyword:
        print("กรุณาพิมพ์คำค้นหา")
        return
    found = False
    for item in inventory:
        if keyword in item["name"]:
            print(f"พบ: {item['name']} จำนวน {item['quantity']} ชิ้น")
            found = True
    if not found:
        print("ไม่พบไอเทมที่ค้นหา")


def discard_item(inventory):
    if not inventory:
        print("กระเป๋าว่าง ไม่มีอะไรให้ทิ้ง")
        return
    print("\n--- ทิ้งไอเทม ---")
    for item in inventory:
        print(f"{item['name']}: {item['quantity']} ชิ้น")
    name = input("ชื่อไอเทมที่ต้องการทิ้ง (เว้นว่างเพื่อยกเลิก): ").strip()
    if not name:
        return
    if get_quantity(inventory, name) == 0:
        print("ไม่มีไอเทมชื่อนี้ในกระเป๋า")
        return
    quantity = read_positive_int("ทิ้งกี่ชิ้น: ")
    if remove_item(inventory, name, quantity):
        print(f"ทิ้ง {name} จำนวน {quantity} ชิ้นแล้ว")
    else:
        print("จำนวนที่ต้องการทิ้งมากกว่าที่มี")


def end_day(player, buildings):
    player["day"] += 1
    player["energy"] = 100
    player["hunger"] = min(100, player["hunger"] + 15)
    player["thirst"] = min(100, player["thirst"] + 20)

    damage = 0
    if player["hunger"] >= 80:
        damage += 12
    if player["thirst"] >= 80:
        damage += 18
    if "เพิงพัก" not in buildings and random.randint(1, 4) == 1:
        damage += 8
        print("กลางคืนฝนตกหนัก! ไม่มีเพิงพักจึงเสียพลังชีวิต 8 แต้ม")
    player["health"] = max(0, player["health"] - damage)
    print(f"\nเริ่มวันที่ {player['day']} | นอนพักจนพลังงานเต็ม")
    if damage:
        print("เสียพลังชีวิตรวม", damage, "แต้มในคืนนี้")


def main():
    player = {"day": 1, "health": 100, "hunger": 15, "thirst": 15, "energy": 100}
    inventory = [
        {"name": "มะพร้าว", "quantity": 1},
        {"name": "ไม้", "quantity": 2},
    ]
    buildings = []

    print("\n🏝️  ISLAND SURVIVAL - เอาชีวิตรอดบนเกาะร้าง")
    print("เป้าหมาย: อยู่รอดจนถึงวันที่ 6 และสร้างกองไฟส่งสัญญาณขอความช่วยเหลือ!")

    while True:
        if player["health"] <= 0:
            print("\n💀 GAME OVER! คุณไม่สามารถเอาชีวิตรอดได้")
            break
        if player["day"] >= 6 and "กองไฟส่งสัญญาณ" in buildings:
            print("\n🎉 YOU WIN! เรือกู้ภัยเห็นกองไฟและมารับคุณแล้ว!")
            break

        print("\n========== MENU ==========")
        print("1. ออกสำรวจเกาะ")
        print("2. ดูสถานะและกระเป๋า")
        print("3. กินอาหาร / ดื่มน้ำ")
        print("4. สร้างสิ่งปลูกสร้าง")
        print("5. ค้นหาไอเทม")
        print("6. ทิ้งไอเทม")
        print("7. พักผ่อน / จบวัน")
        print("0. ออกจากเกม")
        choice = input("เลือกเมนู: ").strip()

        if choice == "1":
            explore(player, inventory)
        elif choice == "2":
            show_status(player, inventory, buildings)
        elif choice == "3":
            eat_or_drink(player, inventory)
        elif choice == "4":
            craft(inventory, buildings)
        elif choice == "5":
            search_item(inventory)
        elif choice == "6":
            discard_item(inventory)
        elif choice == "7":
            end_day(player, buildings)
        elif choice == "0":
            print("บันทึกความทรงจำไว้ในใจ แล้วพบกันใหม่!")
            break
        else:
            print("เมนูไม่ถูกต้อง กรุณาเลือกใหม่ (0-7)")


if __name__ == "__main__":
    main()