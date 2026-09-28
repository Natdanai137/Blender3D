# Blender3D Character Demo

แบบฝึกหัดที่ 6: ตัวละคร 3D และฉากเดโม Godot 4.7

## เปิดเล่น

[เปิดเดโมบนเว็บ](https://natdanai137.github.io/Blender3D/)

คลิกปุ่ม **Idle, Walk, Run, Slash, Jump, Aim, Punch** เพื่อดูท่าต่าง ๆ ลากเมาส์เพื่อหมุนกล้อง และเลื่อนล้อเมาส์เพื่อซูม

## ไฟล์สำคัญ

- `source/Mira.blend` — โมเดลตัวละครที่สร้างใน Blender
- `assets/Mira.glb` — โมเดลที่ส่งออกพร้อมโครงกระดูก
- `assets/Mixamo BoneMap.tres` — แผนที่กระดูก Mixamo → Godot Humanoid
- `assets/MeleeLib.res` และ `assets/ShooterLib.res` — คลังท่าที่ใช้ในเดโม
- `assets/Mako-Quaternius-CC0.glb` — โมเดลประกอบฉาก
- `demo.tscn` และ `scripts/demo.gd` — ฉากและโค้ดควบคุม
- `web/` — ไฟล์ Web export พร้อมเปิดจากเซิร์ฟเวอร์ HTTP

## เปิดใน Godot

เปิด `project.godot` ด้วย Godot 4.7 แล้วรันโปรเจกต์ โครงกระดูกของ `Mira.glb` ถูกตั้งค่า retarget ผ่าน `assets/Mira.glb.import` ให้ใช้ `Mixamo BoneMap.tres` จากนั้น `AnimationPlayer` โหลดไลบรารี Melee และ Shooter ใน `scripts/demo.gd`

หากต้องการสร้าง GLB ใหม่ ให้เปิด `source/Mira.blend` ใน Blender แล้ว Export glTF 2.0 แบบ GLB หรือรัน `tools/build_character.py` ผ่าน Blender Background Mode

## ที่มาทรัพยากร

- [Mako โดย Quaternius บน Poly Pizza](https://poly.pizza/m/2urczqZ9Xf) — CC0 ตามหน้าโมเดล
- [Godot4 Open Animation Libraries](https://github.com/catprisbrey/Godot4-OpenAnimationLibraries) — ไลบรารีท่าทางและ BoneMap ที่ใช้ในงาน

ตัวละคร Mira โมเดลและฉากเดโมสร้างใหม่สำหรับงานนี้ ภาพใน `screenshots/` เป็นผลลัพธ์จาก Blender และ Web export
