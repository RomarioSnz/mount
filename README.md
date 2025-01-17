# 🖥 Автоматическое монтирование NTFS-разделов и профилей пользователей Windows в домене

## 📌 Описание

Этот скрипт предназначен для автоматического монтирования NTFS-разделов Windows в **доменной среде Linux**.  
Основное назначение — обеспечить пользователям доступ к их личным файлам с Windows, смонтировав **личные каталоги** (`C:\Users\Имя`) в их **домашние папки** в Linux.

✅ **Основные функции:**
- Определяет всех пользователей **в домене** (из каталога `/home/SILS` или другого, указанного в `USERS_ROOT_DIR`).
- Находит все **NTFS-разделы** на дисках.
- Определяет **системный раздел Windows (`C:`)**.
- Монтирует системный раздел Windows в `/mnt/windows_c`.
- **Монтирует личные каталоги Windows-пользователей** (`C:\Users\Имя`) в их домашние папки в Linux.
- **Создаёт символические ссылки** на дополнительные NTFS-диски (`D:`, `E:` и т. д.) на рабочих столах пользователей.

## ⚠️ Важные условия для работы

1️⃣ **Linux-клиент должен быть в домене.**  
   Скрипт предназначен для среды, где **пользователи Linux совпадают с именами профилей Windows**.

2️⃣ **Имена пользователей должны совпадать.**  
   - В Windows: `C:\Users\ivan`  
   - В Linux: `/home/SILS/ivan`  
   Если имена отличаются, монтирование **не произойдёт**.

3️⃣ **Windows не должен быть в режиме гибернации.**  
   - Если Windows был выключен в гибернацию, разделы могут быть заблокированы.
   - Для исправления выполните в Windows **от имени администратора**:
     ```sh
     powercfg /h off
     ```

## 🛠 Требования

Перед запуском убедитесь, что:

- Вы используете **Linux** (тестировалось на Ubuntu, Debian).
- Установлен пакет **ntfs-3g** для работы с NTFS-разделами:
  ```sh
  sudo apt update
  sudo apt install ntfs-3g
Скрипт запускается от имени root (sudo).
📥 Установка
1️⃣ Клонируйте репозиторий:

sh
Копировать
Редактировать
git clone https://github.com/your-repo/mount-ntfs.git
cd mount-ntfs
2️⃣ Настройте переменные в скрипте (USERS_ROOT_DIR), если каталог пользователей отличается от /home/SILS.

3️⃣ Сделайте скрипт исполняемым:

sh
Копировать
Редактировать
chmod +x mount_ntfs.py
🚀 Использование
Запустите команду:

sh
Копировать
Редактировать
sudo python3 mount_ntfs.py
Скрипт выполнит следующие шаги:

Проверит, запущен ли он от root.
Найдёт пользователей в каталоге USERS_ROOT_DIR (по умолчанию /home/DOMAIN).
Определит все NTFS-разделы (lsblk).
Проверит системный раздел Windows (C:) и смонтирует его в /mnt/windows_c.
Найдёт личные папки пользователей Windows (C:\Users\Имя) и смонтирует их на рабочий стол соответствующего пользователя в Linux.
Монтирует дополнительные NTFS-диски (D:, E:, и т. д.).
Создаст символические ссылки на рабочем столе каждого пользователя.
⚙ Настройки
Если каталог пользователей отличается от /home/SILS, измените переменную USERS_ROOT_DIR:
python
Копировать
Редактировать
USERS_ROOT_DIR = "/home/YOUR_DIRECTORY"
Автоматический запуск
Если требуется автоматически монтировать NTFS-разделы при старте системы, добавьте запуск в rc.local или systemd.
🔥 Возможные ошибки и решения
Ошибка	Возможная причина	Решение
Скрипт необходимо запускать с правами суперпользователя (sudo).	Скрипт запущен без sudo.	Запустите sudo python3 mount_ntfs.py.
Каталог /home/SILS не найден.	Указан неверный каталог пользователей.	Измените USERS_ROOT_DIR в коде.
Ошибка монтирования раздела с remove_hiberfile	Windows не выключен корректно (гибернация).	Отключите гибернацию в Windows: powercfg /h off.
Каталог пользователя не найден на диске C.	Имя пользователя в Linux не совпадает с именем в Windows.	Проверьте соответствие имён пользователей.
👨‍💻 Автор
Разработано для автоматического монтирования NTFS-разделов и профилей пользователей Windows в доменной среде Linux.

📜 Лицензия
MIT License.
