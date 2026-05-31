import os
import sys
import subprocess

# Reconfigure stdout/stderr to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

NLM_PATH = r"C:\Users\lavik\AppData\Roaming\Python\Python314\Scripts\nlm.exe"

def run_cmd(cmd):
    print(f"\n[SYNC-RUNNER] Выполнение: {' '.join(cmd)}")
    res = subprocess.run(cmd, text=True, errors="ignore")
    return res.returncode == 0

def check_and_ensure_auth():
    print("\n[🔑 BOTANY-AUTH] Проверка сессии Google/NotebookLM...")
    cmd_check = [NLM_PATH, "login", "--check"]
    try:
        res = subprocess.run(cmd_check, capture_output=True, text=True, errors="ignore")
        if res.returncode == 0:
            print("[🔑 BOTANY-AUTH-OK] Сессия активна! Доступ подтвержден.")
            return True
        else:
            print("[🔑 BOTANY-AUTH-EXPIRED] Сессия Google NotebookLM истекла. Требуется вход.")
    except Exception as e:
        print(f"[🔑 BOTANY-AUTH-WARNING] Ошибка проверки авторизации: {e}")
        
    # Trigger login automatically
    print("\n" + "="*60)
    print("🔮 ВНИМАНИЕ: ТРЕБУЕТСЯ ВХОД В GOOGLE ДЛЯ BOTANY PIPELINE")
    print("Сейчас автоматически откроется окно браузера Chrome.")
    print("Пожалуйста, выполните вход в Google-аккаунт в открывшемся окне.")
    print("="*60 + "\n")
    
    cmd_login = [NLM_PATH, "login", "--clear", "--force"]
    res_login = subprocess.run(cmd_login, text=True, errors="ignore")
    if res_login.returncode == 0:
        print("[🔑 BOTANY-AUTH-SUCCESS] Вход выполнен успешно!")
        return True
    else:
        print("[🔑 BOTANY-AUTH-ERROR] Не удалось авторизоваться.")
        return False

def main():
    print("🔄 Запуск локального конвейера растениеводства 'Botany & Indoor Grow'...")
    
    if not check_and_ensure_auth():
        print("[ERROR] Синхронизация прервана из-за отсутствия авторизации.")
        sys.exit(1)
        
    # Шаг 1. Делаем git pull
    print("\n[1/4] Обновление реестра ботанических ссылок из Git...")
    if not run_cmd(["git", "pull"]):
        print("[WARNING] Не удалось выполнить git pull. Продолжаем с локальным реестром...")

    # Шаг 2. Запуск оркестратора NotebookLM для Botany
    print("\n[2/4] Загрузка источников в Botany Vault и RAG-синтез...")
    orchestrator_script = os.path.join("src", "knowledge_extractor", "botany_orchestrator.py")
    if not run_cmd([sys.executable, orchestrator_script]):
        print("[ERROR] Сбой на этапе Botany NotebookLM-анализа.")
        sys.exit(1)

    # Шаг 3. Запуск генератора Obsidian для Botany
    print("\n[3/4] Сборка карточек приборов, удобрений и культур в Obsidian...")
    generator_script = os.path.join("src", "knowledge_extractor", "botany_skills_generator.py")
    if not run_cmd([sys.executable, generator_script]):
        print("[ERROR] Сбой на этапе генерации Botany Obsidian-заметок.")
        sys.exit(1)
        
    print("\n🎉 [SUCCESS] Бот-синхронизация успешно завершена! Ботанический хаб обновлен!")

if __name__ == "__main__":
    main()
