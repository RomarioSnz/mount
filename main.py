import os
import subprocess

# Переменная для корневого каталога пользователей
USERS_ROOT_DIR = "/home/DOMAIN"  # Можно изменить на нужный путь

def check_root():
    """Проверка запуска с правами root"""
    if os.geteuid() != 0:
        print("Скрипт необходимо запускать с правами суперпользователя (sudo).")
        exit(1)

def get_users(directory=USERS_ROOT_DIR):
    """Получение списка пользователей"""
    try:
        return [user for user in os.listdir(directory) if os.path.isdir(os.path.join(directory, user))]
    except FileNotFoundError:
        print(f"Каталог {directory} не найден.")
        exit(1)

def get_ntfs_partitions():
    """Получение списка NTFS-разделов"""
    partitions = []
    try:
        result = subprocess.run(['lsblk', '-o', 'NAME,FSTYPE,SIZE,LABEL,UUID'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if 'ntfs' in line:
                parts = line.split()
                name = parts[0]
                size = parts[2]
                label = parts[3] if len(parts) > 3 else ""
                uuid = parts[-1]
                partitions.append({'name': name, 'size': size, 'label': label, 'uuid': uuid})
        return partitions
    except Exception as e:
        print(f"Ошибка при получении разделов: {e}")
        exit(1)

def unmount_partition_if_busy(mount_point):
    """Принудительно размонтировать раздел, если он занят"""
    try:
        if os.path.ismount(mount_point):
            result = subprocess.run(['umount', mount_point], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                subprocess.run(['umount', '-l', mount_point], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"Раздел {mount_point} был принудительно размонтирован.")
    except Exception as e:
        print(f"Ошибка при попытке размонтировать раздел {mount_point}: {e}")

def is_windows_system_partition(mount_point):
    """Проверяет, является ли раздел системным разделом Windows"""
    required_folders = ["Windows", "Program Files", "Users"]
    return all(os.path.exists(os.path.join(mount_point, folder)) for folder in required_folders)

def find_user_profile_path(users_directory, username):
    """Ищет путь к профилю пользователя в папке Users с учетом регистра"""
    for user_folder in os.listdir(users_directory):
        if user_folder.lower() == username.lower():
            return os.path.join(users_directory, user_folder)
    return None

def try_mount_partition(partition, mount_point, options):
    """Пытается смонтировать раздел с заданными параметрами"""
    mount_command = ['mount', '-t', 'ntfs-3g', '-o', options, f"UUID={partition['uuid']}", mount_point]
    return subprocess.run(mount_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def mount_user_profile(users_directory, user, desktop_path):
    """Монтирует профиль пользователя на его рабочий стол"""
    user_profile_path = find_user_profile_path(users_directory, user)
    if user_profile_path:
        mount_point = os.path.join(desktop_path, f"{user}_windows")
        os.makedirs(mount_point, exist_ok=True)
        mount_command = ['mount', '--bind', user_profile_path, mount_point]
        result = subprocess.run(mount_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"Профиль пользователя {user} успешно смонтирован в {mount_point}")
        else:
            print(f"Ошибка монтирования профиля пользователя {user}: {result.stderr.strip()}")
    else:
        print(f"Каталог пользователя {user} не найден на диске C.")

def mount_additional_ntfs_partitions(partitions, users):
    """Монтирует все дополнительные NTFS-разделы и создает символические ссылки на рабочем столе пользователей"""
    disk_label = ord('D')  
    for partition in partitions:
        if partition['label'].lower() != "windows":
            mount_point = f"/mnt/{chr(disk_label).lower()}_drive"
            unmount_partition_if_busy(mount_point)
            os.makedirs(mount_point, exist_ok=True)

            result = try_mount_partition(partition, mount_point, 'remove_hiberfile')
            if result.returncode != 0:
                print(f"Ошибка монтирования раздела {partition['name']} с remove_hiberfile: {result.stderr.strip()}")
                result = try_mount_partition(partition, mount_point, 'force')
                if result.returncode != 0:
                    print(f"Ошибка принудительного монтирования раздела {partition['name']}: {result.stderr.strip()}")
                    continue

            print(f"Раздел {partition['name']} успешно смонтирован в {mount_point}")

            for user in users:
                desktop_path = f"{USERS_ROOT_DIR}/{user}/Desktop"
                if not os.path.exists(desktop_path):
                    print(f"Каталог Desktop для пользователя {user} не найден: {desktop_path}")
                    continue

                symlink_path = os.path.join(desktop_path, chr(disk_label))
                try:
                    if os.path.islink(symlink_path) or os.path.exists(symlink_path):
                        os.remove(symlink_path)  
                    os.symlink(mount_point, symlink_path)
                    print(f"Символическая ссылка создана: {symlink_path} -> {mount_point}")
                except OSError as e:
                    print(f"Ошибка при создании символической ссылки {symlink_path}: {e}")

            disk_label += 1

def main():
    check_root()

    users = get_users()
    if not users:
        print(f"Не найдено пользователей в {USERS_ROOT_DIR}.")
        exit(1)

    partitions = get_ntfs_partitions()
    if not partitions:
        print("Не найдено NTFS-разделов.")
        exit(1)

    mount_point_c = "/mnt/windows_c"
    disk_c_mounted = False

    for partition in partitions:
        unmount_partition_if_busy(mount_point_c)
        os.makedirs(mount_point_c, exist_ok=True)

        result = try_mount_partition(partition, mount_point_c, 'remove_hiberfile')
        if result.returncode != 0:
            print(f"Ошибка монтирования раздела {partition['name']} с remove_hiberfile: {result.stderr.strip()}")
            result = try_mount_partition(partition, mount_point_c, 'force')
            if result.returncode != 0:
                print(f"Ошибка принудительного монтирования раздела {partition['name']}: {result.stderr.strip()}")
                continue

        if is_windows_system_partition(mount_point_c):
            disk_c_mounted = True
            print(f"Раздел Windows успешно смонтирован в {mount_point_c}")

            users_directory = os.path.join(mount_point_c, "Users")
            if os.path.exists(users_directory):
                for user in users:
                    desktop_path = f"{USERS_ROOT_DIR}/{user}/Desktop"
                    if not os.path.exists(desktop_path):
                        print(f"Каталог Desktop для пользователя {user} не найден: {desktop_path}")
                        continue

                    mount_user_profile(users_directory, user, desktop_path)
            else:
                print(f"Каталог Users не найден на диске C.")
            break
        else:
            print(f"Раздел {partition['name']} не является системным разделом Windows. Размонтируем...")
            unmount_partition_if_busy(mount_point_c)

    if not disk_c_mounted:
        print("Не удалось смонтировать диск C. Проверьте наличие системного раздела Windows.")

    mount_additional_ntfs_partitions(partitions, users)
    print("Монтирование завершено.")

if __name__ == "__main__":
    main()
