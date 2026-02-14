import requests
import webbrowser
import platform
import os
import threading
import asyncio
import aiohttp
import concurrent.futures
from datetime import datetime as dt
from time import sleep as s
from time import time as t
from pystyle import Colors, Colorate
from colorama import Fore, Style, init
import sys

init()

BLUE = Fore.LIGHTBLUE_EX
RED = Fore.LIGHTRED_EX
GREEN = Fore.LIGHTGREEN_EX
YELLOW = Fore.LIGHTYELLOW_EX
MAGENTA = Fore.LIGHTMAGENTA_EX
CYAN = Fore.LIGHTCYAN_EX
RESET = Fore.RESET
BRIGHT = Style.BRIGHT
DIM = Style.DIM

name = platform.system()
total_traffic = 0
is_running = True

def clear_screen():
    os.system('cls' if name == 'Windows' else 'clear')

def print_logo():
    logo = f'''
{BRIGHT}{RED}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                                                          ║  
║                                                          ║ 
║ ▄█████ ▄▄▄▄▄  ▄▄▄▄ ██████ ▄▄▄▄   ▄▄▄  ▄▄▄▄▄ ▄▄▄▄▄ ▄▄  ▄▄▄▄ 
║ ▀▀▀▄▄▄ ██▄▄  ██▀▀▀   ██   ██▄█▄ ██▀██ ██▄▄  ██▄▄  ██ ██▀▀▀ 
║ █████▀ ██▄▄▄ ▀████   ██   ██ ██ ██▀██ ██    ██    ██ ▀████ 
║                                                           
║                                                          ║
║  {GREEN}by Walum{RED}                                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{RESET}
'''
    print(logo)

def display_stats():
    global total_traffic
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    traffic = total_traffic
    unit_index = 0
    
    while traffic >= 1024 and unit_index < len(units) - 1:
        traffic /= 1024
        unit_index += 1
    
    stats = f'''
{BRIGHT}{GREEN}╔══════════════════════════════════════════════════════════╗{RESET}
{BRIGHT}{GREEN}║                    {YELLOW}ТРАФИК СТАТИСТИКА{GREEN}                         ║{RESET}
{BRIGHT}{GREEN}╠══════════════════════════════════════════════════════════╣{RESET}
{BRIGHT}{GREEN}║  {CYAN}Общий потреблённый трафик: {BRIGHT}{MAGENTA}{traffic:.2f} {units[unit_index]}{GREEN}                        ║{RESET}
{BRIGHT}{GREEN}║  {CYAN}Текущее время: {BRIGHT}{YELLOW}{dt.now().strftime("%H:%M:%S")}{GREEN}                                       ║{RESET}
{BRIGHT}{GREEN}║  {CYAN}Дата: {BRIGHT}{YELLOW}{dt.now().strftime("%d.%m.%Y")}{GREEN}                                                ║{RESET}
{BRIGHT}{GREEN}╚══════════════════════════════════════════════════════════╝{RESET}
'''
    print(stats)

async def download_file_async(session, url, file_size_mb):
    try:
        async with session.get(url, timeout=30) as response:
            bytes_downloaded = 0
            chunk_size = 1024 * 1024  
            
            while bytes_downloaded < file_size_mb * 1024 * 1024:
                chunk = await response.content.read(chunk_size)
                if not chunk:
                    break
                bytes_downloaded += len(chunk)
                update_traffic(len(chunk))
                
    except Exception as e:
        print(f"{RED} [!] Ошибка при загрузке: {str(e)}{RESET}")

def update_traffic(bytes_count):
    global total_traffic
    total_traffic += bytes_count

def download_worker(url, size_mb, worker_id):
    global is_running
    
    print(f"{BLUE} [~] SecTraffic {worker_id} запущен для {size_mb}MB{RESET}")
    
    while is_running:
        try:
            start_time = t()
            response = requests.get(url, stream=True, timeout=30)
            
            downloaded = 0
            target_bytes = size_mb * 1024 * 1024
            
            for chunk in response.iter_content(chunk_size=8192):
                if not is_running or downloaded >= target_bytes:
                    break
                
                downloaded += len(chunk)
                update_traffic(len(chunk))
                
                if downloaded % (10 * 1024 * 1024) == 0:
                    mb_downloaded = downloaded / (1024 * 1024)
                    elapsed = t() - start_time
                    speed = mb_downloaded / elapsed if elapsed > 0 else 0
                    
                    print(f"{GREEN} [✓] SecTraffic {worker_id}: {mb_downloaded:.1f}MB | "
                          f"Скорость: {speed:.1f} MB/s{RESET}")
            
            if downloaded > 0:
                elapsed = t() - start_time
                speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                print(f"{CYAN} [ℹ] SecTraffic {worker_id} завершил цикл: {downloaded/(1024*1024):.1f}MB "
                      f"за {elapsed:.1f}сек ({speed:.1f} MB/s){RESET}")
                
        except Exception as e:
            print(f"{RED} [!] Ошибка в SecTraffic {worker_id}: {str(e)}{RESET}")
            s(1)  

def start_traffic_attack(size_mb, threads=10, duration=None):
    global is_running, total_traffic
    
    print(f"\n{BRIGHT}{MAGENTA}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BRIGHT}{MAGENTA}║           {YELLOW}ЗАПУСК ПОТРЕБЛЕНИЯ ТРАФИКА{MAGENTA}                  ║{RESET}")
    print(f"{BRIGHT}{MAGENTA}╠══════════════════════════════════════════════════════════╣{RESET}")
    print(f"{BRIGHT}{MAGENTA}║  {CYAN}Размер файла: {BRIGHT}{YELLOW}{size_mb}MB{MAGENTA}                               ║{RESET}")
    print(f"{BRIGHT}{MAGENTA}║  {CYAN}Количество потоков: {BRIGHT}{YELLOW}{threads}{MAGENTA}                          ║{RESET}")
    print(f"{BRIGHT}{MAGENTA}║  {CYAN}Длительность: {BRIGHT}{YELLOW}{'∞' if duration is None else f'{duration}сек'}{MAGENTA}                          ║{RESET}")
    print(f"{BRIGHT}{MAGENTA}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    
    urls = [
        'https://speedtest.selectel.ru/10MB',
        'https://github.com/Nealcly/MuTual/archive/master.zip',
    ]
    
    is_running = True
    total_traffic = 0
    start_time = t()
    
    thread_list = []
    for i in range(threads):
        url = urls[i % len(urls)]
        thread = threading.Thread(
            target=download_worker,
            args=(url, size_mb, i+1),
            daemon=True
        )
        thread.start()
        thread_list.append(thread)
    
    try:
        while is_running:
            s(2)
            
            clear_screen()
            print_logo()
            display_stats()
            
            elapsed = t() - start_time
            if duration and elapsed >= duration:
                print(f"{YELLOW} [ℹ] Время атаки истекло!{RESET}")
                break
            
            traffic_mb = total_traffic / (1024 * 1024)
            speed = traffic_mb / elapsed if elapsed > 0 else 0
            
            print(f"\n{BRIGHT}{CYAN} [ℹ] Текущая скорость: {speed:.1f} MB/s")
            print(f" [ℹ] Прошло времени: {elapsed:.0f} секунд")
            print(f" [ℹ] Всего скачано: {traffic_mb:.1f} MB{RESET}")
            print(f"\n{BRIGHT}{YELLOW} [⚠] Нажмите Ctrl+C для остановки{RESET}")
            
    except KeyboardInterrupt:
        print(f"\n{RED} [✗] Остановка атаки по запросу пользователя...{RESET}")
    
    finally:
        is_running = False
        s(3)
        print(f"{GREEN} [✓] Атака остановлена!{RESET}")
        print(f"{GREEN} [✓] Итоговый трафик: {total_traffic/(1024*1024):.1f} MB{RESET}")
        returner()

def returner():
    print(f"\n{BRIGHT}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BRIGHT}{CYAN}║                   {YELLOW}ГЛАВНОЕ МЕНЮ{CYAN}                       ║{RESET}")
    print(f"{BRIGHT}{CYAN}╠══════════════════════════════════════════════════════════╣{RESET}")
    print(f"{BRIGHT}{CYAN}║  {GREEN}1. {YELLOW}Вернуться в главное меню{CYAN}                     ║{RESET}")
    print(f"{BRIGHT}{CYAN}║  {GREEN}2. {YELLOW}Запустить еще одну атаку{CYAN}                     ║{RESET}")
    print(f"{BRIGHT}{CYAN}║  {RED}3. {YELLOW}Выйти из программы{CYAN}                          ║{RESET}")
    print(f"{BRIGHT}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}")
    
    choice = input(f"\n{BRIGHT}{BLUE} [!] Выберите опцию (1-3): {RESET}").strip()
    
    if choice == '1':
        clear_screen()
        main()
    elif choice == '2':
        clear_screen()
        show_attack_menu()
    elif choice == '3':
        print(f"\n{RED} [!] Выход из программы...{RESET}")
        s(2)
        exit()
    else:
        print(f"{RED} [!] Неправильный выбор!{RESET}")
        s(1)
        returner()

def show_attack_menu():
    clear_screen()
    print_logo()
    
    menu = f'''
{BRIGHT}{MAGENTA}╔══════════════════════════════════════════════════════════╗{RESET}
{BRIGHT}{MAGENTA}║              {YELLOW}ВЫБОР ПАРАМЕТРОВ АТАКИ{MAGENTA}                  ║{RESET}
{BRIGHT}{MAGENTA}╠══════════════════════════════════════════════════════════╣{RESET}
{BRIGHT}{MAGENTA}║  {GREEN}1. {YELLOW}Лёгкая атака (10MB файлы, 5 потоков){MAGENTA}           ║{RESET}
{BRIGHT}{MAGENTA}║  {GREEN}2. {YELLOW}Средняя атака (100MB файлы, 10 потоков){MAGENTA}        ║{RESET}
{BRIGHT}{MAGENTA}║  {GREEN}3. {YELLOW}Мощная атака (1GB файлы, 20 потоков){MAGENTA}           ║{RESET}
{BRIGHT}{MAGENTA}║  {RED}4. {YELLOW}ЭКСТРЕМАЛЬНАЯ атака (10GB файлы, 50 потоков){MAGENTA}  ║{RESET}
{BRIGHT}{MAGENTA}║  {CYAN}5. {YELLOW}Кастомная настройка{MAGENTA}                          ║{RESET}
{BRIGHT}{MAGENTA}╚══════════════════════════════════════════════════════════╝{RESET}
'''
    print(menu)
    
    choice = input(f"\n{BRIGHT}{BLUE} [!] Выберите тип атаки (1-5): {RESET}").strip()
    
    configs = {
        '1': {'size': 10, 'threads': 5, 'duration': 60},
        '2': {'size': 100, 'threads': 10, 'duration': 120},
        '3': {'size': 1024, 'threads': 20, 'duration': 300},
        '4': {'size': 10240, 'threads': 50, 'duration': None},  # Бесконечная
    }
    
    if choice in configs:
        config = configs[choice]
        start_traffic_attack(
            size_mb=config['size'],
            threads=config['threads'],
            duration=config['duration']
        )
    
    elif choice == '5':
        try:
            size_mb = int(input(f"{BRIGHT}{BLUE} [!] Размер файла (MB): {RESET}"))
            threads = int(input(f"{BRIGHT}{BLUE} [!] Количество потоков: {RESET}"))
            duration_input = input(f"{BRIGHT}{BLUE} [!] Длительность (сек, Enter для ∞): {RESET}")
            duration = int(duration_input) if duration_input.strip() else None
            
            start_traffic_attack(size_mb, threads, duration)
            
        except ValueError:
            print(f"{RED} [!] Ошибка ввода!{RESET}")
            s(2)
            show_attack_menu()
    
    else:
        print(f"{RED} [!] Неправильный выбор!{RESET}")
        s(1)
        show_attack_menu()

def main():
    clear_screen()
    print_logo()
    
    print(f"\n{BRIGHT}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BRIGHT}{CYAN}║                {YELLOW}ГЛАВНОЕ МЕНЮ{CYAN}                         ║{RESET}")
    print(f"{BRIGHT}{CYAN}╠══════════════════════════════════════════════════════════╣{RESET}")
    print(f"{BRIGHT}{CYAN}║  {GREEN}1. {YELLOW}Начать потребление трафика{CYAN}                       ║{RESET}")
    print(f"{BRIGHT}{CYAN}║  {GREEN}2. {YELLOW}Информация о программе{CYAN}                       ║{RESET}")
    print(f"{BRIGHT}{CYAN}║  {GREEN}3. {YELLOW}Показать статистику{CYAN}                          ║{RESET}")
    print(f"{BRIGHT}{CYAN}║  {RED}4. {YELLOW}Выйти{CYAN}                                       ║{RESET}")
    print(f"{BRIGHT}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}")
    
    choice = input(f"\n{BRIGHT}{BLUE} [!] Выберите опцию (1-4): {RESET}").strip()
    
    if choice == '1':
        show_attack_menu()
    elif choice == '2':
        clear_screen()
        print_logo()
        print(f'''
{BRIGHT}{YELLOW}╔══════════════════════════════════════════════════════════╗{RESET}
{BRIGHT}{YELLOW}║                  {CYAN}ИНФОРМАЦИЯ{YELLOW}                          ║{RESET}
{BRIGHT}{YELLOW}╠══════════════════════════════════════════════════════════╣{RESET}
{BRIGHT}{YELLOW}║  {GREEN}Название: {CYAN}SecTraffic by Walu{YELLOW}                       ║{RESET}
{BRIGHT}{YELLOW}║  {GREEN}Версия: {CYAN}1.0{YELLOW}                                         ║{RESET}
{BRIGHT}{YELLOW}║  {GREEN}Назначение: {CYAN}Генерация трафика{YELLOW}   ║{RESET}
{BRIGHT}{YELLOW}║  {GREEN}ОС: {CYAN}{name}{YELLOW}                                             ║{RESET}
{BRIGHT}{YELLOW}╚══════════════════════════════════════════════════════════╝{RESET}
''')
        input(f"\n{BRIGHT}{BLUE} [!] Нажмите Enter для возврата... {RESET}")
        main()
    elif choice == '3':
        clear_screen()
        print_logo()
        display_stats()
        input(f"\n{BRIGHT}{BLUE} [!] Нажмите Enter для возврата... {RESET}")
        main()
    elif choice == '4':
        print(f"\n{RED} [!] Выход из программы...{RESET}")
        s(2)
        exit()
    else:
        print(f"{RED} [!] Неправильный выбор!{RESET}")
        s(1)
        main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED} [!] Программа завершена пользователем{RESET}")
        exit()
    except Exception as e:
        print(f"{RED} [!] Критическая ошибка: {str(e)}{RESET}")
        exit()
