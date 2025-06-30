import signal
import subprocess
import sys
import threading
import re
import time
from colorama import init, Fore, Style
import datetime
import argparse

init(autoreset=True) # Inicializar colorama
print_lock = threading.Lock() # bloqueo para los prints en los hilos
max_ip_length = 15
max_name_length = 30
max_mac_length = 17
def get_ip(interface_type, language):
    result = subprocess.run(['ipconfig'], stdout=subprocess.PIPE)
    output = result.stdout.decode('latin-1')
    if language == 'es':
        if interface_type == 1:
            pattern = r'Adaptador de LAN inalámbrica Wi-Fi:.*?Puerta de enlace predeterminada[^\d]*(\d+\.\d+\.\d+\.\d+)'
        elif interface_type == 2:
            pattern = r'Adaptador de Ethernet.*?Puerta de enlace predeterminada[^\d]*(\d+\.\d+\.\d+\.\d+)'
    elif language == 'en':
        if interface_type == 1:
            pattern = r'Wireless LAN adapter Wi-Fi:.*?Default Gateway[^\d]*(\d+\.\d+\.\d+\.\d+)'
        elif interface_type == 2:
            pattern = r'Ethernet adapter.*?Default Gateway[^\d]*(\d+\.\d+\.\d+\.\d+)'
    else:
        raise ValueError("Invalid language. Use 'es' for Spanish, 'en' for English.")
    match = re.search(pattern, output, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None

def ping_all_hosts(host_ip, retries=3):
    active_hosts = []
    inactive_hosts = []
    threads = []
    def ping_host(ip):
        result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], stdout=subprocess.DEVNULL)
        if result.returncode == 0:
            active_hosts.append(ip)
        else:
            inactive_hosts.append(ip)
    for _ in range(retries):
        for i in range(1, 255):
            ip = host_ip + str(i)
            thread = threading.Thread(target=ping_host, args=(ip,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    return active_hosts, inactive_hosts

def ctrl_c(signum, frame):
        print("\n\n[!] Saliendo...\n")
        time.sleep(2)
        sys.exit(1)

def scan(active_hosts, language, interface_type):
    print('\n[*] Iniciando escaneo... (Se recomienda que primero se ejecute un escaneo con "--mode ping" antes de realizar el escaneo normal)\n')
    time.sleep(2)
    tracer_threads = []
    signal.signal(signal.SIGINT, ctrl_c) # Ctrl+C
    def get_mac_hosts(ip_host, active_hosts):
        result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE)
        output = result.stdout.decode('latin-1')
        pattern = r'(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9-]+)\s+'
        matches = re.findall(pattern, output)
        mac_addresses = {}
        for ip, mac in matches:
            if ip in active_hosts:
                mac_addresses[ip] = mac
        return mac_addresses
        
    def tracer_host(ip, mac):
        result = subprocess.run(['tracert', ip], stdout=subprocess.PIPE)
        output = result.stdout.decode('latin-1')
        if language == 'es':
            pattern = r'Traza a ([\w\.-]+) \[\d+\.\d+\.\d+\.\d+\]'
        elif language == 'en':
            pattern = r'Tracing route to ([\w\.-]+) \[\d+\.\d+\.\d+\.\d+\]'
        match = re.search(pattern, output)
        ip = ip.ljust(max_ip_length)
        mac = mac.ljust(max_mac_length)
        with print_lock:
            if match:
                name = match.group(1)
                name = name.ljust(max_name_length)
                print(f"{Fore.CYAN}[+] HOST:{Fore.RESET} {ip} | {Fore.GREEN}NOMBRE:{Fore.RESET} {name} | {Fore.YELLOW}MAC:{Fore.RESET} {mac}")
            else:
                print(f"{Fore.CYAN}[+] HOST:{Fore.RESET} {ip} | {Fore.RED}Nombre no encontrado                                {Fore.RESET}   | {Fore.YELLOW}MAC:{Fore.RESET} {mac}")
    host_ip = get_ip(interface_type, language)
    try:
        host_ip = '.'.join(host_ip.split('.')[:-1]) + '.'
    except AttributeError:
        print(f"{Fore.RED}[!] Ocurrió un error durante la obtención de datos, revisa si es necesario el uso de argumentos para usar la interfaz de red o el lenguaje del sistema preferido.{Fore.RESET}")
        print("\nUsa el argumento -? o -h para obtener ayuda.\n")
        sys.exit(1)
    mac_addresses = get_mac_hosts(host_ip, active_hosts)
    for ip, mac in mac_addresses.items():
        thread = threading.Thread(target=tracer_host, args=(ip, mac,))
        tracer_threads.append(thread)
        thread.start()
    for thread in tracer_threads:
        thread.join()

def discovery_mode(active_hosts, inactive_hosts):
    print('\n[*] Iniciando escaneo con modo ping...\n')
    time.sleep(2)
    def sort_by_last_octet(ip): 
        return int(ip.split('.')[-1])
    all_hosts = {ip: 'active' for ip in active_hosts}
    all_hosts.update({ip: 'inactive' for ip in inactive_hosts})
    sorted_hosts = sorted(all_hosts.keys(), key=sort_by_last_octet)
    print("\nDispositivos:")
    for host in sorted_hosts:
        if all_hosts[host] == 'active':
            print(f"{Fore.GREEN}[+] {host} | ACTIVO")
        else:
            print(f"{Fore.RED}[-] {host} | INACTIVO")

def main():
    signal.signal(signal.SIGINT, ctrl_c)
    parser = argparse.ArgumentParser(
        description="Escáner de red local.",
        epilog="""
    Argumentos:
    es=español,
    en=inglés,
    ethernet=interfaz de red por cable,
    wireless=interfaz de red inalámbrica,
    ping = le hace un ping a todos los dispositivos a la red | escaner -L es -I ethernet | escaner -L en -I wireless -m ping
    """
    )
    parser.add_argument('-L', '--language', choices=['es', 'en'], default='es', help='Especifica el idioma del sistema operativo (español o inglés).')
    parser.add_argument('-I', '--interface', choices=['wireless', 'ethernet'], default='ethernet', help='Especifica la interfaz de red (wireless o ethernet).')
    parser.add_argument('-m', '--mode', choices=['ping', 'default'], default='default', help='Especifica el modo de operación (ping o default).')
    parser.add_argument('-?', action='help', help="Muestra esta ayuda y sale.")
    args = parser.parse_args()
    interface_type = 1 if args.interface == 'wireless' else 2
    host_ip = get_ip(interface_type, args.language)
    try:
        host_ip = '.'.join(host_ip.split('.')[:-1]) + '.'
    except AttributeError:
        print(f"{Fore.RED}[!] Ocurrió un error durante la obtención de datos, revisa si es necesario el uso de argumentos para usar la interfaz de red o el lenguaje del sistema preferido.{Fore.RESET}")
        print("\nUsa el argumento -? o -h para obtener ayuda.\n")
        sys.exit(1)
    active_hosts, inactive_hosts = ping_all_hosts(host_ip)
    if args.mode == 'ping':
        discovery_mode(active_hosts, inactive_hosts)
    else:
        scan(active_hosts, args.language, interface_type)
    print("\nEscaneo finalizado.", datetime.datetime.now(), "\n")

if __name__ == "__main__":
    main()