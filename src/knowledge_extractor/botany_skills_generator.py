import os
import sys
import json
import shutil
import re

# Reconfigure stdout/stderr to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

LOCAL_KB_DIR = "botany_knowledge_base"
EXTERNAL_KB_DIR = r"G:\botany_knowledge_base"

# Subfolders inside botany_knowledge_base
DEVICES_SUBDIR = os.path.join(LOCAL_KB_DIR, "devices")
CHEMISTRY_SUBDIR = os.path.join(LOCAL_KB_DIR, "chemistry")
PLANTS_SUBDIR = os.path.join(LOCAL_KB_DIR, "plants")

def ensure_dirs():
    os.makedirs(LOCAL_KB_DIR, exist_ok=True)
    os.makedirs(DEVICES_SUBDIR, exist_ok=True)
    os.makedirs(CHEMISTRY_SUBDIR, exist_ok=True)
    os.makedirs(PLANTS_SUBDIR, exist_ok=True)

def load_synthesis_json(filepath):
    """Loads nlm JSON output and extracts the raw unescaped markdown answer."""
    if not os.path.exists(filepath):
        return ""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                if "value" in data and isinstance(data["value"], dict):
                    return data["value"].get("answer", "")
                else:
                    return data.get("answer", data.get("value", ""))
            else:
                return str(data)
    except Exception:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

def clean_filename(name):
    """Cleans a string to make it a safe Windows filename."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip().replace(" ", "_").lower()
    return name or "unnamed"

def parse_and_slice_devices(content):
    """Slices devices synthesis into separate grow device cards."""
    if not content:
        return []
        
    blocks = content.split("#### [DEVICE]")
    devices_list = []
    
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if not lines:
            continue
        dev_name = lines[0].strip()
        dev_content = "\n".join(lines[1:]).strip()
        
        filename = clean_filename(dev_name) + ".md"
        filepath = os.path.join(DEVICES_SUBDIR, filename)
        
        # Determine device category
        category = "Оборудование / Свет"
        if any(w in dev_content.lower() for w in ["led", "лампа", "спектр", "ppfd", "досвет"]):
            category = "Фитолампы / Освещение"
        elif any(w in dev_content.lower() for w in ["sensor", "датчик", "влажнос", "zigbee"]):
            category = "Датчики / Автоматика"
        elif any(w in dev_content.lower() for w in ["полив", "насос", "клапан", "система"]):
            category = "Системы полива"
            
        formatted = f"""# ⚙️ Прибор: {dev_name}

<div style="background: linear-gradient(135deg, #041208 0%, #010402 100%); border-radius: 12px; padding: 22px; border: 1px solid #145a32; margin-bottom: 20px; font-family: 'Outfit', 'Segoe UI', sans-serif; color: #ffffff; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid rgba(0, 255, 136, 0.15); padding-bottom: 10px;">
    <span style="font-size: 1.5em; font-weight: bold; background: linear-gradient(90deg, #00ff88, #a3e4d7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚙️ {dev_name}</span>
    <span style="background: rgba(0, 255, 136, 0.12); border: 1px solid #00ff88; border-radius: 20px; padding: 3px 12px; font-size: 0.85em; color: #00ffc4; font-weight: 600;">{category}</span>
  </div>
  
  <div style="color: #d5ebd5; line-height: 1.6; font-size: 1.05em; margin-bottom: 15px;">
{dev_content}
  </div>
</div>

Теги: #Botany_Device #{category.replace(' / ', '_').replace(' ', '_')}

---
🔗 **Навигация:** [[Botany_Grow_Hub|Главная ботанического хаба]]
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted)
            
        devices_list.append({
            "name": dev_name,
            "filename": filename,
            "category": category,
            "ref": f"[[devices/{filename[:-3]}|{dev_name}]]"
        })
        print(f"[BOTANY-SLICER] Сгенерирована карточка прибора: devices/{filename}")
        
    return devices_list

def parse_and_slice_chemistry(content):
    """Slices chemistry/soils RAG report into cards."""
    if not content:
        return []
        
    blocks = content.split("#### [CHEMISTRY]")
    chem_list = []
    
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if not lines:
            continue
        chem_name = lines[0].strip()
        chem_content = "\n".join(lines[1:]).strip()
        
        filename = clean_filename(chem_name) + ".md"
        filepath = os.path.join(CHEMISTRY_SUBDIR, filename)
        
        category = "Агрохимия / Грунты"
        if any(w in chem_content.lower() for w in ["торф", "кокос", "перлит", "вермикулит", "пон", "почв", "субстрат"]):
            category = "Грунты / Субстраты"
        elif any(w in chem_content.lower() for w in ["удобрен", "npk", "хелат", "азот", "калий", "фосфор"]):
            category = "Удобрения / NPK"
        elif any(w in chem_content.lower() for w in ["актара", "вредител", "клещ", "фунгицид", "инсектицид", "масло"]):
            category = "Защита растений"
        elif any(w in chem_content.lower() for w in ["hb-101", "стимулятор", "паста", "гормон"]):
            category = "Стимуляторы роста"
            
        formatted = f"""# 🧪 Вещество / Рецепт: {chem_name}

<div style="background: linear-gradient(135deg, #021a0c 0%, #010603 100%); border-radius: 12px; padding: 22px; border: 1px solid #117a65; margin-bottom: 20px; font-family: 'Outfit', 'Segoe UI', sans-serif; color: #ffffff; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid rgba(0, 255, 136, 0.15); padding-bottom: 10px;">
    <span style="font-size: 1.5em; font-weight: bold; background: linear-gradient(90deg, #00ff88, #a3e4d7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🧪 {chem_name}</span>
    <span style="background: rgba(0, 255, 136, 0.12); border: 1px solid #00ff88; border-radius: 20px; padding: 3px 12px; font-size: 0.85em; color: #00ffc4; font-weight: 600;">{category}</span>
  </div>
  
  <div style="color: #d5ebd5; line-height: 1.6; font-size: 1.05em; margin-bottom: 15px;">
{chem_content}
  </div>
</div>

Теги: #Botany_Chemistry #{category.replace(' / ', '_').replace(' ', '_')}

---
🔗 **Навигация:** [[Botany_Grow_Hub|Главная ботанического хаба]]
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted)
            
        chem_list.append({
            "name": chem_name,
            "filename": filename,
            "category": category,
            "ref": f"[[chemistry/{filename[:-3]}|{chem_name}]]"
        })
        print(f"[BOTANY-SLICER] Сгенерирована карточка агрохимии: chemistry/{filename}")
        
    return chem_list

def parse_and_slice_plants(content):
    """Slices plant guide into separate plant cards."""
    if not content:
        return []
        
    blocks = content.split("#### [PLANT]")
    plants_list = []
    
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if not lines:
            continue
        plant_name = lines[0].strip()
        plant_content = "\n".join(lines[1:]).strip()
        
        filename = clean_filename(plant_name) + ".md"
        filepath = os.path.join(PLANTS_SUBDIR, filename)
        
        category = "Растение / Культура"
        if any(w in plant_name.lower() for w in ["аллоказия", "alocasia"]):
            category = "Аллоказии (Rare foliage)"
        elif any(w in plant_name.lower() for w in ["монстера", "monstera"]):
            category = "Лиственные монстеры"
        elif any(w in plant_name.lower() for w in ["лимон", "цитрус", "инжир", "плодонос"]):
            category = "Плодоносящие комнатные"
            
        formatted = f"""# 🌿 Культура: {plant_name}

<div style="background: linear-gradient(135deg, #0b2e13 0%, #040d06 100%); border-radius: 12px; padding: 22px; border: 1px solid #196f3d; margin-bottom: 20px; font-family: 'Outfit', 'Segoe UI', sans-serif; color: #ffffff; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid rgba(0, 255, 136, 0.15); padding-bottom: 10px;">
    <span style="font-size: 1.5em; font-weight: bold; background: linear-gradient(90deg, #00ff88, #85c1e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🌿 {plant_name}</span>
    <span style="background: rgba(0, 255, 136, 0.12); border: 1px solid #00ff88; border-radius: 20px; padding: 3px 12px; font-size: 0.85em; color: #00ffc4; font-weight: 600;">{category}</span>
  </div>
  
  <div style="color: #cbd5e1; line-height: 1.6; font-size: 1.05em; margin-bottom: 15px;">
{plant_content}
  </div>
</div>

Теги: #Botany_Plant #{category.replace(' / ', '_').replace(' ', '_')}

---
🔗 **Навигация:** [[Botany_Grow_Hub|Главная ботанического хаба]]
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted)
            
        plants_list.append({
            "name": plant_name,
            "filename": filename,
            "category": category,
            "ref": f"[[plants/{filename[:-3]}|{plant_name}]]"
        })
        print(f"[BOTANY-SLICER] Сгенерирована карточка культуры: plants/{filename}")
        
    return plants_list

def generate_botany_grow_hub(devices, chem, plants, index_content):
    """Generates the emerald-themed dashboard Botany_Grow_Hub.md."""
    devices_refs = "\n".join([f"- **{d['ref']}** — *{d['category']}*" for d in devices])
    chem_refs = "\n".join([f"- **{c['ref']}** — *{c['category']}*" for c in chem])
    plants_refs = "\n".join([f"- **{p['ref']}** — *{p['category']}*" for p in plants])
    
    dashboard_html = f"""
<div style="background: linear-gradient(135deg, #041208 0%, #010402 100%); border-radius: 16px; padding: 30px; border: 1px solid #145a32; font-family: 'Outfit', 'Segoe UI', sans-serif; color: #ffffff; box-shadow: 0 8px 32px rgba(0,0,0,0.5); margin-bottom: 30px;">
  
  <div style="text-align: center; margin-bottom: 25px;">
    <h1 style="margin: 0; font-size: 2.2em; font-weight: 800; background: linear-gradient(90deg, #00ff88, #3498db); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(0,255,136,0.2);">🌿 BOTANY & GROW HUB (2026)</h1>
    <p style="margin: 5px 0 0 0; color: #a3e4d7; font-size: 1.1em; letter-spacing: 1px;">ДОМАШНЕЕ РАСТЕНИЕВОДСТВО И АГРОХИМИЯ</p>
  </div>

  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;">
    <div style="background: rgba(0,255,136,0.02); border: 1px solid rgba(0,255,136,0.08); border-radius: 10px; padding: 15px; text-align: center;">
      <div style="font-size: 1.8em; font-weight: 800; color: #00ff88;">300+</div>
      <div style="color: #a3e4d7; font-size: 0.8em; font-weight: 600; text-transform: uppercase; margin-top: 5px;">Источников Botany</div>
    </div>
    <div style="background: rgba(0,255,136,0.02); border: 1px solid rgba(0,255,136,0.08); border-radius: 10px; padding: 15px; text-align: center;">
      <div style="font-size: 1.8em; font-weight: 800; color: #f4d03f;">{len(plants)}</div>
      <div style="color: #a3e4d7; font-size: 0.8em; font-weight: 600; text-transform: uppercase; margin-top: 5px;">Зеленых Культур</div>
    </div>
    <div style="background: rgba(0,255,136,0.02); border: 1px solid rgba(0,255,136,0.08); border-radius: 10px; padding: 15px; text-align: center;">
      <div style="font-size: 1.8em; font-weight: 800; color: #58d68d;">{len(chem)}</div>
      <div style="color: #a3e4d7; font-size: 0.8em; font-weight: 600; text-transform: uppercase; margin-top: 5px;">Удобрений / Грунтов</div>
    </div>
    <div style="background: rgba(0,255,136,0.02); border: 1px solid rgba(0,255,136,0.08); border-radius: 10px; padding: 15px; text-align: center;">
      <div style="font-size: 1.8em; font-weight: 800; color: #5dade2;">{len(devices)}</div>
      <div style="color: #a3e4d7; font-size: 0.8em; font-weight: 600; text-transform: uppercase; margin-top: 5px;">Фитоламп & Приборов</div>
    </div>
  </div>

  <div style="border-top: 1px solid rgba(0,255,136,0.1); padding-top: 20px;">
    <p style="margin: 0; color: #cbd5e1; font-size: 1em; line-height: 1.6; text-align: center;">
      Единый эко-центр знаний по комнатному выращиванию редких Аллоказий, подбору освещения по спектрам, смешиванию субстратов и NPK-управлению.
    </p>
  </div>
</div>
"""
    
    content = f"""# 🌿 ПУТЕВОДИТЕЛЬ: ДОМАШНЯЯ ОРАНЖЕРЕЯ И КУЛЬТУРЫ (2026)

{dashboard_html}

> [!NOTE]
> База знаний оранжерейного конвейера. Перекрестный RAG-анализ ботанических YouTube-материалов силами Google NotebookLM.

Теги: #Botany_Hub #Home_Growing #Alocasia_Care #NPK_Chemistry

---

## 🌀 1. Карты Связей и Литература
* 🗺️ [[botany_knowledge_map|Интерактивная Mermaid-карта приборов и растений]]
* 📚 [[plants_science_books|Научная литература: Агрономия, геология и грунтоведение (6 книг)]]
* 📊 Для просмотра интерактивного 3D-графа связей оранжереи нажмите **Ctrl+Alt+G**

---

## 🌿 2. Зеленые Культуры (Всего: {len(plants)})
> [!TIP]
> Подробные руководства по уходу, поливу, температуре и размножению:

{plants_refs or "_Пока нет карточек редких растений._"}

---

## 🧪 3. Агрохимия, Удобрения & Субстраты (Всего: {len(chem)})
> [!IMPORTANT]
> Рецепты субстратов, пропорции лечуза-пон, NPK-удобрения и защита от трипсов/клещей:

{chem_refs or "_Пока нет карточек удобрений и грунтов._"}

---

## ⚙️ 4. Фитолампы досветки & Датчики умного дома (Всего: {len(devices)})
> [!NOTE]
> Справочник настройки ламп досветки (PPFD), Zigbee-датчиков влажности почвы и систем автополива:

{devices_refs or "_Пока нет карточек ламп и приборов._"}

---

## 📑 5. Глобальный ботанический путеводитель
{index_content or "_Загрузка глобального путеводителя по комнатным культурам..._"}

"""
    with open(os.path.join(LOCAL_KB_DIR, "Botany_Grow_Hub.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("[BOTANY-HUB] Создана центральная оранжерейная панель: Botany_Grow_Hub.md")

def generate_botany_knowledge_map(devices, chem, plants):
    """Generates botany knowledge map."""
    devices_nodes = "\n    ".join([f"D{i}[\"{d['name']}\"] -.->|Прибор| Hub" for i, d in enumerate(devices[:8])])
    chem_nodes = "\n    ".join([f"C{i}[\"{c['name']}\"] -->|Химия| Hub" for i, c in enumerate(chem[:8])])
    plants_nodes = "\n    ".join([f"P{i}[\"{p['name']}\"] -->|Культура| Hub" for i, p in enumerate(plants[:8])])
    
    content = f"""# 🌀 Ботаническая Mermaid Карта Знаний

```mermaid
graph TD
    Hub["🌿 Панель Управления (Botany_Grow_Hub)"] -->|Грунты| Soils["🧪 Субстраты и NPK"]
    Hub -->|Свет| Lights["⚙️ Датчики и Лампы"]
    
    subgraph "⚙️ Фитолампы & Приборы"
    {devices_nodes or "Devices"}
    end
    
    subgraph "🧪 Удобрения & Химия"
    {chem_nodes or "Chemistry"}
    end
    
    subgraph "🌿 Комнатные Культуры"
    {plants_nodes or "Plants"}
    end
```
"""
    with open(os.path.join(LOCAL_KB_DIR, "botany_knowledge_map.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("[BOTANY-MAP] Создана ботаническая Mermaid-карта: botany_knowledge_map.md")

def sync_to_external():
    print(f"[BOTANY-SYNC] Синхронизация файлов в {EXTERNAL_KB_DIR}...")
    if not os.path.exists(EXTERNAL_KB_DIR):
        print(f"[SYNC-WARNING] Внешний путь {EXTERNAL_KB_DIR} не существует. Создаем папку...")
        try:
            os.makedirs(EXTERNAL_KB_DIR, exist_ok=True)
        except Exception as e:
            print(f"[SYNC-ERROR] Не удалось создать внешний ботанический каталог: {e}")
            return
            
    ext_devices = os.path.join(EXTERNAL_KB_DIR, "devices")
    ext_chem = os.path.join(EXTERNAL_KB_DIR, "chemistry")
    ext_plants = os.path.join(EXTERNAL_KB_DIR, "plants")
    os.makedirs(ext_devices, exist_ok=True)
    os.makedirs(ext_chem, exist_ok=True)
    os.makedirs(ext_plants, exist_ok=True)
    
    def copy_dir_files(src, dest):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dest, item)
            if os.path.isfile(s) and item.endswith(".md"):
                shutil.copy2(s, d)
                print(f"[SYNC-SUCCESS] Скопирован: {os.path.basename(src)}/{item}")
                
    copy_dir_files(LOCAL_KB_DIR, EXTERNAL_KB_DIR)
    copy_dir_files(DEVICES_SUBDIR, ext_devices)
    copy_dir_files(CHEMISTRY_SUBDIR, ext_chem)
    copy_dir_files(PLANTS_SUBDIR, ext_plants)

def main():
    ensure_dirs()
    
    # Load 4 reports
    content_devices = load_synthesis_json(os.path.join("scratch", "botany_synthesis_devices.md"))
    content_chem = load_synthesis_json(os.path.join("scratch", "botany_synthesis_chemistry.md"))
    content_plants = load_synthesis_json(os.path.join("scratch", "botany_synthesis_plants.md"))
    content_index = load_synthesis_json(os.path.join("scratch", "botany_synthesis_index.md"))
    
    # Self-healing global report parsing if separate reports not found
    if not content_devices or not content_plants:
        print("[BOTANY-GENERATOR] Отдельные отчеты не найдены. Активируем резервный парсинг из глобального файла...")
        # Since this is a new run, we check if global report exists, else use templates
        global_synthesis = load_synthesis_json(os.path.join("scratch", "botany_synthesis_global.md"))
        if global_synthesis:
            dev_match = re.search(r'\[START_DEVICES\](.*?)\[END_DEVICES\]', global_synthesis, re.DOTALL)
            if dev_match: content_devices = dev_match.group(1).strip()
            
            chem_match = re.search(r'\[START_CHEMISTRY\](.*?)\[END_CHEMISTRY\]', global_synthesis, re.DOTALL)
            if chem_match: content_chem = chem_match.group(1).strip()
            
            plants_match = re.search(r'\[START_PLANTS\](.*?)\[END_PLANTS\]', global_synthesis, re.DOTALL)
            if plants_match: content_plants = plants_match.group(1).strip()
            
            content_index = "Глобальный путеводитель по растениеводству (Резервная копия)."
            
    # Slice reports
    print("\n[BOTANY-SLICER] Нарезка приборов и ламп...")
    devices_list = parse_and_slice_devices(content_devices)
    
    print("\n[BOTANY-SLICER] Нарезка агрохимии и грунтов...")
    chem_list = parse_and_slice_chemistry(content_chem)
    
    print("\n[BOTANY-SLICER] Нарезка зеленых культур...")
    plants_list = parse_and_slice_plants(content_plants)
    
    # Create hubs
    print("\n[BOTANY-HUB] Сборка оранжерейной панели...")
    generate_botany_grow_hub(devices_list, chem_list, plants_list, content_index)
    generate_botany_knowledge_map(devices_list, chem_list, plants_list)
    
    # Sync everything
    sync_to_external()
    print("\n[BOTANY-GENERATOR] Сборка ботанической базы успешно завершена!")

if __name__ == "__main__":
    main()
