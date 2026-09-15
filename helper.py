import os
import subprocess
import psutil
import json
import msvcrt
import ctypes
import urllib.request
import shutil
from ctypes import wintypes

 ### НАСТРОЙКИ ОБНОВЛЕНИЯ ###
UPDATE_URL = "https://raw.githubusercontent.com/Purplix-co/Bot/refs/heads/main/data/assistant_data.json"
UPDATE_FILE_URL = "https://raw.githubusercontent.com/Purplix-co/Bot/refs/heads/main/helper.py"

# === ОБНОВЛЕНИЕ JSON ===
def ensure_version_in_data():
    """Проверяет, есть ли поле version в JSON. Если нет — добавляет."""
    data = load_data()
    if "version" not in data:
        data["version"] = "1.0.0.3"
        save_data(data)
    return data

def get_current_version():
    """Читает текущую версию из JSON"""
    data = load_data()
    return data.get("version", "1.0.0.3")

def set_version(new_version):
    """Записывает версию в JSON"""
    data = load_data()
    data["version"] = new_version
    save_data(data)

def get_latest_version():
    """Скачивает последнюю версию с сервера (из version.json)"""
    try:
        # ИСПРАВЛЕНО: Заменили UPDATE_JSON_URL на UPDATE_URL
        with urllib.request.urlopen(UPDATE_URL, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("version", None)
    except Exception as e:
        # Для отладки можно временно раскомментировать строку ниже, чтобы видеть реальную ошибку:
        # print(f"Debug error: {e}")
        return None


def check_for_updates():
    """Проверяет обновления и предлагает обновиться"""
    t = get_text
    print(t("checking_updates"))
    
    current = get_current_version()
    latest = get_latest_version()
    
    if latest is None:
        print(t("no_internet"))
        return
    
    if current == latest:
        print(t("latest_version").format(current))
        return
    
    print(t("new_version_available").format(latest, current))
    choice = input(t("update_question")).strip().lower()
    
    if choice == "y":
        download_update(latest)
    else:
        print(t("update_no"))

def download_update(new_version):
    """Скачивает новую версию и заменяет файлы"""
    t = get_text
    print(t("update_yes"))
    
    try:
        # Скачиваем новый helper.py
        with urllib.request.urlopen(UPDATE_FILE_URL, timeout=10) as response:
            new_code = response.read().decode("utf-8")
        
        # Сохраняем как временный файл
        temp_file = os.path.join(SCRIPT_DIR, "helper_new.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(new_code)
        
        # Записываем новую версию в JSON
        set_version(new_version)
        
        # Заменяем старый файл
        old_file = os.path.join(SCRIPT_DIR, "helper.py")
        shutil.move(temp_file, old_file)
        
        print(t("update_success").format(new_version))
        print(t("update_restart"))
        input(t("update_press_enter"))
        exit()
        
    except Exception as e:
        print(t("update_error").format(e))
        input(t("update_press_enter_continue"))

# === НАСТРОЙКИ ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
MEMORY_FILE = os.path.join(DATA_DIR, "assistant_data.json")
RUST_FINDER = os.path.join(SCRIPT_DIR, "rust_finder", "target", "release", "finder.exe")
ADMIN_PASSWORD = "789456123"

# Создаём папку data, если её нет
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# === ФУНКЦИЯ ДЛЯ СКРЫТОГО ВВОДА С * ===
def get_password(prompt="🔑 Enter admin password: "):
    print(prompt, end="", flush=True)
    password = ""
    while True:
        ch = msvcrt.getch()
        if ch in (b'\r', b'\n'):
            print()
            break
        elif ch == b'\x08':
            if len(password) > 0:
                password = password[:-1]
                print("\b \b", end="", flush=True)
        else:
            try:
                char = ch.decode('utf-8')
                password += char
                print("*", end="", flush=True)
            except:
                pass
    return password

# === ЗАГРУЗКА ДАННЫХ ===
def load_data():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Если нет поля version — добавляем
                if "version" not in data:
                    data["version"] = "1.0.0.3"
                return data
        except:
            return {"version": "1.0.0.3", "language": "en", "programs": {}}
    return {"version": "1.0.0.3", "language": "en", "programs": {}}

def save_data(data):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

# === ЗАГРУЗКА ЯЗЫКА ===
data = load_data()
LANGUAGE = data.get("language", "en")

# === ПЕРЕВОДЫ ===
translations = {
    "en": {
        "help_title": "🤖 ASSISTANT (enter command)",
        "help_commands": [
            "  open <name>    - open program (auto-search)",
            "  open <path>    - open by path (e.g. open C:/file.exe)",
            "  close <name>   - close program",
            "  run <command>  - execute CMD command",
            "  list           - list processes",
            "  find <name>    - find program path (fast Rust search)",
            "  search <text>  - search files on disk (slow)",
            "  site <url>     - open website in browser",
            "  note <text>    - create note in Notepad",
            "  remember <name> - remember program path",
            "  forget <name>   - forget program",
            "  mem            - show remembered programs",
            "  lang           - change language (en/ru/pl)",
            "  tutorial       - show step-by-step guide",
            "  cls            - clear screen",
            "  help           - show this menu",
            "  exit           - exit"
            "test"
        ],
        "admin_title": "🛠️ ADMIN PANEL - All commands",
        "admin_commands": [
            "📌 BASIC:",
            "  open <name/path>  - open program or file",
            "  close <name>      - close program",
            "  run <command>     - execute CMD command",
            "",
            "📌 SYSTEM:",
            "  list              - show running processes",
            "  find <name>       - find program path (fast)",
            "  search <text>     - search files on disk (slow)",
            "  site <url>        - open website",
            "  note <text>       - create note in Notepad",
            "  lock              - lock screen",
            "  shutdown          - shutdown PC (asks confirmation)",
            "  restart           - restart PC (asks confirmation)",
            "",
            "📌 MEMORY:",
            "  remember <name>   - save program path",
            "  forget <name>     - remove program from memory",
            "  mem               - show all remembered programs",
            "",
            "📌 LANGUAGE:",
            "  lang <en/ru/pl>   - change language (saved)",
            "  lang              - show current language",
            "",
            "📌 OTHER:",
            "  help              - show basic help",
            "  tutorial          - step-by-step guide",
            "  admin             - show this panel (password required)",
            "  cls               - clear screen",
            "  exit              - exit program"
        ],
        "admin_end": "📌 Type 'help' for basic commands or 'exit' to quit",
        "admin_wrong": "❌ Wrong password! Access denied.",
        "rust_activated": "🦀 Rust search activated...",
        "rust_success": "✅ Rust search completed successfully.",
        "admin_enter": "🔑 Enter admin password: ",
        "opened": "✅ Opened: {}",
        "not_found": "❌ Not found: {}",
        "remembered": "✅ Remembered: {} -> {}",
        "forgotten": "🗑️ Forgotten: {}",
        "memory_list": "📋 Remembered programs:",
        "no_memory": "❌ No remembered programs",
        "enter_path": "📝 Enter program path (or drag file here): ",
        "lang_changed": "🌍 Language changed to: {}",
        "current_lang": "🌍 Current language: {}",
        "not_found_try": "❌ Not found. Try:\n  - write exact name\n  - check installation\n  - use remember to save path",
        "searching": "🔍 Searching: {}...",
        "search_location": "  📌 Searching in:",
        "found": "✅ Found: {}",
        "debug_step1": "  📍 1. Checking remembered programs",
        "debug_step2": "  📍 2. Rust-finder (fast search)",
        "debug_step3": "  📍 3. Python-finder (slow search)",
        "not_found_final": "  ❌ Nothing found",
        "rust_not_found": "❌ Rust-finder not found. Build it: cargo build --release",
        "rust_error": "⚠️ Rust error: {}",
        "path_not_exists": "❌ Path does not exist: {}",
        "save_error": "❌ Failed to save",
        "tutorial_title": "📖 TUTORIAL",
        "tutorial_steps": [
            "1️⃣ OPEN: open <name>  (e.g. open chrome)",
            "2️⃣ REMEMBER: remember <name>  (then paste path)",
            "3️⃣ CLOSE: close <name>  (e.g. close chrome)",
            "4️⃣ RUN: run <command>  (e.g. run ipconfig)",
            "5️⃣ FIND: find <name>   (fast Rust search)",
            "6️⃣ SEARCH: search <text> (slow file search)",
            "7️⃣ SITE: site <url>  (e.g. site youtube.com)",
            "8️⃣ LANGUAGE: lang <en/ru/pl>",
            "💡 Tip: drag file into console to get its path"
        ],
        "tutorial_end": "📌 Type 'help' to see all commands",
        "lang_not_found": "❌ Language not found. Available: en, ru, pl",
        "lang_available": "🌍 Available languages: en, ru, pl",
        "unknown_command": "❌ Unknown command. Type 'help'",
        "find_activating": "⚡ Fast Rust search activated...",
        "find_found": "✅ Found: {}",
        "find_not_found": "❌ Not found: {}",
        "find_in_memory": "📂 Found in memory: {}",
        "find_specify_name": "❌ Specify program name, e.g. find Roblox",
        "checking_updates": "🔍 Checking for updates...",
        "no_internet": "⚠️ Could not check for updates (no internet?)",
        "latest_version": "✅ You have the latest version: {}",
        "new_version_available": "📢 New version available: {} (you have {})",
        "update_question": "❓ Update? (y/n): ",
        "update_yes": "📥 Downloading update...",
        "update_no": "👌 Continuing without update",
        "update_success": "✅ Update installed! Version: {}",
        "update_restart": "🔄 Restart the bot to apply changes.",
        "update_press_enter": "📌 Press Enter to exit...",
        "update_error": "❌ Update error: {}",
        "update_press_enter_continue": "📌 Press Enter to continue...",
    },
    "ru": {
        "help_title": "🤖 ПОМОЩНИК (введи команду)",
        "help_commands": [
            "  open <имя>     - открыть программу (автопоиск)",
            "  open <путь>    - открыть по пути (например: open C:/file.exe)",
            "  close <имя>    - закрыть программу",
            "  run <команда>  - выполнить CMD-команду",
            "  list           - список процессов",
            "  find <имя>     - найти путь к программе (быстрый Rust-поиск)",
            "  search <текст> - поиск файлов на диске (медленный)",
            "  site <url>     - открыть сайт в браузере",
            "  note <текст>   - создать заметку в блокноте",
            "  remember <имя> - запомнить путь к программе",
            "  forget <имя>   - забыть программу",
            "  mem            - показать запомненные программы",
            "  lang           - сменить язык (en/ru/pl)",
            "  tutorial       - показать пошаговую инструкцию",
            "  cls            - очистить экран",
            "  help           - показать это меню",
            "  exit           - выйти"
        ],
        "admin_title": "🛠️ АДМИН-ПАНЕЛЬ - Все команды",
        "admin_commands": [
            "📌 ОСНОВНЫЕ:",
            "  open <имя/путь>  - открыть программу или файл",
            "  close <имя>      - закрыть программу",
            "  run <команда>    - выполнить CMD-команду",
            "",
            "📌 СИСТЕМА:",
            "  list              - показать запущенные процессы",
            "  find <имя>        - найти путь к программе (быстро)",
            "  search <текст>    - поиск файлов на диске (медленно)",
            "  site <url>        - открыть сайт",
            "  note <текст>      - создать заметку в блокноте",
            "  lock              - заблокировать экран",
            "  shutdown          - выключить ПК (спросит подтверждение)",
            "  restart           - перезагрузить ПК (спросит подтверждение)",
            "",
            "📌 ПАМЯТЬ:",
            "  remember <имя>    - сохранить путь к программе",
            "  forget <имя>      - удалить программу из памяти",
            "  mem               - показать все запомненные программы",
            "",
            "📌 ЯЗЫК:",
            "  lang <en/ru/pl>   - сменить язык (сохраняется)",
            "  lang              - показать текущий язык",
            "",
            "📌 ДРУГОЕ:",
            "  help              - показать базовую справку",
            "  tutorial          - пошаговое руководство",
            "  admin             - показать эту панель (требуется пароль)",
            "  cls               - очистить экран",
            "  exit              - выйти из программы"
        ],
        "admin_end": "📌 Напиши 'help' для базовых команд или 'exit' для выхода",
        "admin_wrong": "❌ Неверный пароль! Доступ запрещён.",
        "rust_activated": "🦀 Rust-поиск активирован...",
        "rust_success": "✅ Rust-поиск завершён успешно.",
        "admin_enter": "🔑 Введи пароль администратора: ",
        "opened": "✅ Открыл: {}",
        "not_found": "❌ Не найдено: {}",
        "remembered": "✅ Запомнил: {} -> {}",
        "forgotten": "🗑️ Забыл: {}",
        "memory_list": "📋 Запомненные программы:",
        "no_memory": "❌ Нет запомненных программ",
        "enter_path": "📝 Введи путь к программе (или перетащи файл сюда): ",
        "lang_changed": "🌍 Язык изменён на: {}",
        "current_lang": "🌍 Текущий язык: {}",
        "not_found_try": "❌ Не найдено. Попробуй:\n  - написать точное название\n  - проверить установку\n  - использовать remember для запоминания",
        "searching": "🔍 Ищу: {}...",
        "search_location": "  📌 Поиск по:",
        "found": "✅ Найдено: {}",
        "debug_step1": "  📍 1. Проверка запомненных программ",
        "debug_step2": "  📍 2. Rust-поисковик (быстрый)",
        "debug_step3": "  📍 3. Python-поиск (медленный)",
        "not_found_final": "  ❌ Ничего не найдено",
        "rust_not_found": "❌ Rust-поисковик не найден. Собери его: cargo build --release",
        "rust_error": "⚠️ Ошибка Rust: {}",
        "path_not_exists": "❌ Путь не существует: {}",
        "save_error": "❌ Не удалось сохранить",
        "tutorial_title": "📖 ТУТОРИАЛ",
        "tutorial_steps": [
            "1️⃣ ОТКРЫТЬ: open <имя>  (например: open chrome)",
            "2️⃣ ЗАПОМНИТЬ: remember <имя>  (затем вставь путь)",
            "3️⃣ ЗАКРЫТЬ: close <имя>  (например: close chrome)",
            "4️⃣ ВЫПОЛНИТЬ: run <команда>  (например: run ipconfig)",
            "5️⃣ НАЙТИ: find <имя>  (быстрый Rust-поиск)",
            "6️⃣ ПОИСК: search <текст> (медленный поиск файлов)",
            "7️⃣ САЙТ: site <url>  (например: site youtube.com)",
            "8️⃣ ЯЗЫК: lang <en/ru/pl>",
            "💡 Совет: перетащи файл в консоль, чтобы получить его путь"
        ],
        "tutorial_end": "📌 Напиши 'help' чтобы увидеть все команды",
        "lang_not_found": "❌ Язык не найден. Доступны: en, ru, pl",
        "lang_available": "🌍 Доступные языки: en, ru, pl",
        "unknown_command": "❌ Неизвестная команда. Напиши 'help'",
        "find_activating": "⚡ Быстрый Rust-поиск активирован...",
        "find_found": "✅ Найдено: {}",
        "find_not_found": "❌ Не найдено: {}",
        "find_in_memory": "📂 Найдено в памяти: {}",
        "find_specify_name": "❌ Укажи имя программы, например: find Roblox",
        "checking_updates": "🔍 Проверяю обновления...",
        "no_internet": "⚠️ Не удалось проверить обновления (нет интернета?)",
        "latest_version": "✅ У тебя последняя версия: {}",
        "new_version_available": "📢 Доступна новая версия: {} (у тебя {})",
        "update_question": "❓ Обновить? (y/n): ",
        "update_yes": "📥 Скачиваю обновление...",
        "update_no": "👌 Продолжаем без обновления",
        "update_success": "✅ Обновление установлено! Версия: {}",
        "update_restart": "🔄 Перезапусти бота, чтобы применить изменения.",
        "update_press_enter": "📌 Нажми Enter для выхода...",
        "update_error": "❌ Ошибка обновления: {}",
        "update_press_enter_continue": "📌 Нажми Enter для продолжения...",
    },
    "pl": {
        "help_title": "🤖 ASYSTENT (wprowadź komendę)",
        "help_commands": [
            "  open <nazwa>   - otwórz program (autowyszukiwanie)",
            "  open <ścieżka> - otwórz program po ścieżce (np. open C:/file.exe)",
            "  close <nazwa>  - zamknij program",
            "  run <komenda>  - wykonaj komendę CMD",
            "  list           - lista procesów",
            "  find <nazwa>   - znajdź ścieżkę programu (szybki Rust)",
            "  search <tekst> - szukaj plików na dysku (wolne)",
            "  site <url>     - otwórz stronę w przeglądarce",
            "  note <tekst>   - utwórz notatkę w Notatniku",
            "  remember <nazwa> - zapamiętaj ścieżkę do programu",
            "  forget <nazwa>   - zapomnij program",
            "  mem            - pokaż zapamiętane programy",
            "  lang           - zmień język (en/ru/pl)",
            "  tutorial       - pokaż instrukcję krok po kroku",
            "  cls            - wyczyść ekran",
            "  help           - pokaż to menu",
            "  exit           - wyjdź"
        ],
        "admin_title": "🛠️ PANEL ADMINA - Wszystkie komendy",
        "admin_commands": [
            "📌 PODSTAWOWE:",
            "  open <nazwa/ścieżka>  - otwórz program lub plik",
            "  close <nazwa>         - zamknij program",
            "  run <komenda>         - wykonaj komendę CMD",
            "",
            "📌 SYSTEM:",
            "  list              - pokaż uruchomione procesy",
            "  find <nazwa>      - znajdź ścieżkę programu (szybko)",
            "  search <tekst>    - szukaj plików na dysku (wolno)",
            "  site <url>        - otwórz stronę",
            "  note <tekst>      - utwórz notatkę w Notatniku",
            "  lock              - zablokuj ekran",
            "  shutdown          - wyłącz komputer (pyta o potwierdzenie)",
            "  restart           - zrestartuj komputer (pyta o potwierdzenie)",
            "",
            "📌 PAMIĘĆ:",
            "  remember <nazwa>    - zapisz ścieżkę do programu",
            "  forget <nazwa>      - usuń program z pamięci",
            "  mem                - pokaż wszystkie zapamiętane programy",
            "",
            "📌 JĘZYK:",
            "  lang <en/ru/pl>   - zmień język (zapisuje się)",
            "  lang              - pokaż aktualny język",
            "",
            "📌 INNE:",
            "  help              - pokaż podstawową pomoc",
            "  tutorial          - instrukcja krok po kroku",
            "  admin             - pokaż ten panel (wymagane hasło)",
            "  cls               - wyczyść ekran",
            "  exit              - wyjdź z programu"
        ],
        "admin_end": "📌 Wpisz 'help' dla podstawowych komend lub 'exit' aby wyjść",
        "admin_wrong": "❌ Złe hasło! Dostęp zabroniony.",
        "rust_activated": "🦀 Rust search aktywowany...",
        "rust_success": "✅ Rust search zakończony pomyślnie.",
        "admin_enter": "🔑 Wprowadź hasło administratora: ",
        "opened": "✅ Otworzyłem: {}",
        "not_found": "❌ Nie znaleziono: {}",
        "remembered": "✅ Zapamiętano: {} -> {}",
        "forgotten": "🗑️ Zapomniano: {}",
        "memory_list": "📋 Zapamiętane programy:",
        "no_memory": "❌ Brak zapamiętanych programów",
        "enter_path": "📝 Wprowadź ścieżkę do programu (lub przeciągnij plik tutaj): ",
        "lang_changed": "🌍 Język zmieniony na: {}",
        "current_lang": "🌍 Aktualny język: {}",
        "not_found_try": "❌ Nie znaleziono. Spróbuj:\n  - wpisać dokładną nazwę\n  - sprawdzić instalację\n  - użyć remember do zapamiętania",
        "searching": "🔍 Szukam: {}...",
        "search_location": "  📌 Szukanie w:",
        "found": "✅ Znaleziono: {}",
        "debug_step1": "  📍 1. Sprawdzanie zapamiętanych programów",
        "debug_step2": "  📍 2. Rust-finder (szybkie wyszukiwanie)",
        "debug_step3": "  📍 3. Python-finder (wolne wyszukiwanie)",
        "not_found_final": "  ❌ Nic nie znaleziono",
        "rust_not_found": "❌ Rust-finder nie znaleziony. Zbuduj go: cargo build --release",
        "rust_error": "⚠️ Błąd Rust: {}",
        "path_not_exists": "❌ Ścieżka nie istnieje: {}",
        "save_error": "❌ Nie udało się zapisać",
        "tutorial_title": "📖 TUTORIAL",
        "tutorial_steps": [
            "1️⃣ OTWORZYĆ: open <nazwa>  (np. open chrome)",
            "2️⃣ ZAPAMIĘTAĆ: remember <nazwa>  (potem wklej ścieżkę)",
            "3️⃣ ZAMKNĄĆ: close <nazwa>  (np. close chrome)",
            "4️⃣ WYKONAĆ: run <komenda>  (np. run ipconfig)",
            "5️⃣ ZNAJDŹ: find <nazwa>   (szybki Rust)",
            "6️⃣ SZUKAJ: search <tekst> (wolne szukanie plików)",
            "7️⃣ STRONA: site <url>  (np. site youtube.com)",
            "8️⃣ JĘZYK: lang <en/ru/pl>",
            "💡 Wskazówka: przeciągnij plik do konsoli, aby uzyskać jego ścieżkę"
        ],
        "tutorial_end": "📌 Wpisz 'help' aby zobaczyć wszystkie komendy",
        "lang_not_found": "❌ Język nie znaleziony. Dostępne: en, ru, pl",
        "lang_available": "🌍 Dostępne języki: en, ru, pl",
        "unknown_command": "❌ Nieznana komenda. Wpisz 'help'",
        "find_activating": "⚡ Szybkie wyszukiwanie Rust aktywowane...",
        "find_found": "✅ Znaleziono: {}",
        "find_not_found": "❌ Nie znaleziono: {}",
        "find_in_memory": "📂 Znaleziono w pamięci: {}",
        "find_specify_name": "❌ Podaj nazwę programu, np. find Roblox",
        "checking_updates": "🔍 Sprawdzam aktualizacje...",
        "no_internet": "⚠️ Nie udało się sprawdzić aktualizacji (brak internetu?)",
        "latest_version": "✅ Masz najnowszą wersję: {}",
        "new_version_available": "📢 Dostępna nowa wersja: {} (masz {})",
        "update_question": "❓ Zaktualizować? (y/n): ",
        "update_yes": "📥 Pobieram aktualizację...",
        "update_no": "👌 Kontynuuję bez aktualizacji",
        "update_success": "✅ Aktualizacja zainstalowana! Wersja: {}",
        "update_restart": "🔄 Uruchom bota ponownie, aby zastosować zmiany.",
        "update_press_enter": "📌 Naciśnij Enter, aby wyjść...",
        "update_error": "❌ Błąd aktualizacji: {}",
        "update_press_enter_continue": "📌 Naciśnij Enter, aby kontynuować...",
    }
}

def get_text(key):
    return translations[LANGUAGE].get(key, key)

# === ВЫЗОВ RUST (БЫСТРЫЙ ПОИСК) ===
def find_with_rust(name):
    if not os.path.exists(RUST_FINDER):
        print("❌ Rust-поисковик не найден. Собери его: cargo build --release")
        return None
    
    print(get_text("rust_activated"))
    
    try:
        result = subprocess.run(
            [RUST_FINDER, name, MEMORY_FILE],
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout.strip()
        if output and not output.startswith("❌"):
            print(get_text("rust_success"))
            return output
        return None
    except subprocess.TimeoutExpired:
        print("⏰ Rust-поиск превысил время ожидания (таймаут).")
        return None
    except Exception as e:
        print(f"⚠️ Ошибка Rust: {e}")
        return None

# === ПАМЯТЬ ===
def remember_program(name, path):
    if not os.path.exists(path):
        print(get_text("path_not_exists").format(path))
        return
    
    data = load_data()
    data["programs"][name.lower()] = path
    if save_data(data):
        print(get_text("remembered").format(name, path))
    else:
        print(get_text("save_error"))

def forget_program(name):
    data = load_data()
    if name.lower() in data["programs"]:
        del data["programs"][name.lower()]
        save_data(data)
        print(get_text("forgotten").format(name))
    else:
        print(get_text("not_found").format(name))

def show_memory():
    data = load_data()
    memory = data.get("programs", {})
    if memory:
        print(get_text("memory_list"))
        for name, path in memory.items():
            print(f"  {name} -> {path}")
    else:
        print(get_text("no_memory"))

# === ПОИСК ПРОГРАММ (с использованием Rust) ===
def find_app_path(name, debug=False):
    name_lower = name.lower()
    t = get_text
    
    if debug:
        print(f"🔎 {t('searching').format(name)}")
    
    if os.path.exists(name):
        return name
    if os.path.exists(name + ".exe"):
        return name + ".exe"
    if os.path.exists(name + ".lnk"):
        return name + ".lnk"
    
    if debug:
        print(t("debug_step1"))
    
    data = load_data()
    memory = data.get("programs", {})
    if name_lower in memory:
        path = memory[name_lower]
        if os.path.exists(path):
            if debug:
                print(f"     ✅ {t('found').format(path)} (from memory)")
            return path
        else:
            del memory[name_lower]
            data["programs"] = memory
            save_data(data)
    
    # ===== БЫСТРЫЙ RUST-ПОИСК =====
    if debug:
        print(t("debug_step2"))
    
    rust_result = find_with_rust(name_lower)
    if rust_result:
        if debug:
            print(f"     ✅ {t('found').format(rust_result)} (Rust)")
        return rust_result
    
    # ===== МЕДЛЕННЫЙ PYTHON-ПОИСК =====
    if debug:
        print(t("debug_step3"))
    
    try:
        cmd = f'powershell -Command "Get-Command *{name}* | Select-Object -ExpandProperty Source"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        for p in result.stdout.strip().split("\n"):
            if p and p.endswith(".exe"):
                if name_lower in p.lower() or os.path.basename(p).lower().startswith(name_lower):
                    return p
    except:
        pass
    
    common_folders = [
        "C:/Program Files",
        "C:/Program Files (x86)",
        f"C:/Users/{os.getlogin()}/AppData/Local",
        f"C:/Users/{os.getlogin()}/AppData/Roaming",
        f"C:/Users/{os.getlogin()}/AppData/Local/Programs",
        "C:/ProgramData",
    ]
    
    for folder in common_folders:
        if not os.path.exists(folder):
            continue
        try:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(".exe") and name_lower in file.lower():
                        return os.path.join(root, file)
        except:
            pass
    
    if debug:
        print(t("not_found_final"))
    
    return None

def find_program(name):
    t = get_text
    if not name:
        print(t("find_specify_name"))
        return
    
    name_lower = name.lower()
    
    # Проверяем память
    data = load_data()
    if name_lower in data.get("programs", {}):
        path = data["programs"][name_lower]
        if os.path.exists(path):
            print(t("find_in_memory").format(path))
            return
        else:
            del data["programs"][name_lower]
            save_data(data)
    
    # Ищем через Rust
    print(t("find_activating"))
    path = find_with_rust(name_lower)
    
    if path:
        # Запоминаем найденный путь
        data = load_data()
        data["programs"][name_lower] = path
        save_data(data)
        print(t("find_found").format(path))
    else:
        print(t("find_not_found").format(name))

def open_app(name):
    t = get_text
    
    manual_apps = {
        "notepad": "notepad.exe",
        "calc": "calc.exe",
        "cmd": "cmd.exe",
        "explorer": "explorer.exe",
    }
    
    if os.path.exists(name):
        try:
            os.startfile(name)
            print(t("opened").format(name))
            return
        except:
            pass
    
    name_lower = name.lower()
    if name_lower in manual_apps:
        try:
            os.startfile(manual_apps[name_lower])
            print(t("opened").format(name))
            return
        except:
            pass
    
    print(t("searching").format(name))
    print(t("search_location"))
    
    path = find_app_path(name_lower, debug=True)
    
    if path:
        try:
            if path.endswith(".lnk"):
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    class SHELLEXECUTEINFO(ctypes.Structure):
                        _fields_ = [
                            ("cbSize", wintypes.DWORD),
                            ("fMask", wintypes.DWORD),
                            ("hwnd", wintypes.HWND),
                            ("lpVerb", wintypes.LPCWSTR),
                            ("lpFile", wintypes.LPCWSTR),
                            ("lpParameters", wintypes.LPCWSTR),
                            ("lpDirectory", wintypes.LPCWSTR),
                            ("nShow", wintypes.INT),
                            ("hInstApp", wintypes.HINSTANCE),
                            ("lpIDList", wintypes.LPVOID),
                            ("lpClass", wintypes.LPCWSTR),
                            ("hkeyClass", wintypes.HKEY),
                            ("dwHotKey", wintypes.DWORD),
                            ("hIcon", wintypes.HANDLE),
                            ("hProcess", wintypes.HANDLE),
                        ]
                    
                    sei = SHELLEXECUTEINFO()
                    sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
                    sei.fMask = 0x00000040
                    sei.lpVerb = "open"
                    sei.lpFile = path
                    sei.nShow = 1
                    
                    if ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei)):
                        print(t("opened").format(name))
                        return
                    else:
                        subprocess.Popen(['start', path], shell=True)
                        print(t("opened").format(name))
                        return
                except:
                    subprocess.Popen(['start', path], shell=True)
                    print(t("opened").format(name))
                    return
            else:
                os.startfile(path)
                print(t("opened").format(name))
                return
        except Exception as e:
            print(f"❌ {e}")
            return
    
    print(t("not_found_try"))

def close_app(name):
    killed = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and name.lower() in proc.info['name'].lower():
            proc.kill()
            killed = True
    if killed:
        print(get_text("opened").format(name))
    else:
        print(get_text("not_found").format(name))

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout or result.stderr
        print(output if output else "✅ OK")
    except Exception as e:
        print(f"❌ Error: {e}")

def find_files(text):
    print(f"🔍 Searching for '{text}'... (this may take a while)")
    found = []
    for root, _, files in os.walk("C:/"):
        for file in files:
            if text.lower() in file.lower():
                found.append(os.path.join(root, file))
                if len(found) >= 10:
                    break
        if len(found) >= 10:
            break
    if found:
        for f in found:
            print(f"  {f}")
    else:
        print("❌ Nothing found")

def open_site(url):
    if not url.startswith("http"):
        url = "https://" + url
    os.system(f"start {url}")
    print(f"🌐 Opened: {url}")

def create_note(text):
    with open("note.txt", "w", encoding="utf-8") as f:
        f.write(text)
    os.startfile("note.txt")
    print("📝 Note created and opened")

def show_help():
    t = get_text
    print("\n" + "="*50)
    print(t("help_title"))
    print("="*50)
    for line in t("help_commands"):
        print(line)
    print("="*50)
    print(t("current_lang").format(LANGUAGE))

def show_admin():
    t = get_text
    print("\n" + "="*50)
    print(t("admin_title"))
    print("="*50)
    for line in t("admin_commands"):
        print(line)
    print("="*50)
    print(t("admin_end"))

def show_tutorial():
    t = get_text
    print("\n" + "="*50)
    print(t("tutorial_title"))
    print("="*50)
    for line in t("tutorial_steps"):
        print(line)
    print("="*50)
    print(t("tutorial_end"))

def change_language(new_lang):
    global LANGUAGE
    t = get_text
    if new_lang in translations:
        LANGUAGE = new_lang
        data = load_data()
        data["language"] = new_lang
        save_data(data)
        print(t("lang_changed").format(new_lang))
    else:
        print(t("lang_not_found"))
        print(t("lang_available"))

def main():
    ensure_version_in_data()  # <-- создаёт version, если нет
    check_for_updates()       # <-- проверяет обновления
    show_help()
    show_help()
    while True:
        try:
            cmd = input("\n👉 ").strip()
            if not cmd:
                continue
            parts = cmd.split(maxsplit=1)
            command = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if command == "exit":
                print("👋 Bye!")
                break
            elif command == "help":
                show_help()
            elif command == "admin":
                password = get_password(get_text("admin_enter"))
                if password == ADMIN_PASSWORD:
                    show_admin()
                else:
                    print(get_text("admin_wrong"))
            elif command == "tutorial":
                show_tutorial()
            elif command == "lang":
                if arg:
                    change_language(arg)
                else:
                    print(get_text("lang_available"))
                    print(get_text("current_lang").format(LANGUAGE))
            elif command == "cls":
                os.system("cls")
            elif command == "open":
                open_app(arg)
            elif command == "close":
                close_app(arg)
            elif command == "run":
                run_cmd(arg)
            elif command == "list":
                names = []
                for proc in psutil.process_iter(['name']):
                    try:
                        names.append(proc.info['name'])
                    except:
                        pass
                for n in sorted(set(names))[:30]:
                    print(f"  {n}")
            elif command == "find":
                find_program(arg)
            elif command == "search":
                find_files(arg)
            elif command == "site":
                open_site(arg)
            elif command == "note":
                create_note(arg)
            elif command == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                print("🔒 Screen locked")
            elif command == "shutdown":
                confirm = input("❓ Shutdown? (y/n): ")
                if confirm.lower() == "y":
                    os.system("shutdown /s /t 10")
                    print("🔄 Shutting down in 10 seconds...")
                    break
            elif command == "restart":
                confirm = input("❓ Restart? (y/n): ")
                if confirm.lower() == "y":
                    os.system("shutdown /r /t 10")
                    print("🔄 Restarting in 10 seconds...")
                    break
            elif command == "remember":
                if not arg:
                    print(get_text("enter_path"))
                    path = input().strip().strip('"')
                    if path:
                        name = os.path.basename(path).replace(".exe", "").replace(".lnk", "")
                        remember_program(name, path)
                else:
                    print(get_text("enter_path"))
                    path = input().strip().strip('"')
                    if path:
                        remember_program(arg, path)
            elif command == "forget":
                if arg:
                    forget_program(arg)
                else:
                    print("❌ Specify name, e.g. forget Viber")
            elif command == "mem":
                show_memory()
            else:
                print(get_text("unknown_command"))
        except KeyboardInterrupt:
            print("\n👋 Bye!")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
    print("\n📌 Press Enter to exit...")
    input()
