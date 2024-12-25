import socket
import socks
import threading
import time
import sys
from queue import Queue

# Nombre de threads
NUM_THREADS = 100
TIMEOUT = 5

# Queue pour les proxies à vérifier
proxy_queue = Queue()
live_proxies = []

def load_proxies(file_path):
    """Charge les proxies depuis un fichier texte."""
    try:
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file.readlines()]
            if not proxies:
                print("Le fichier de proxy est vide.")
                sys.exit(1)
            return proxies
    except FileNotFoundError:
        print(f"Erreur : fichier '{file_path}' introuvable.")
        sys.exit(1)

def save_live_proxies(file_path, proxies):
    """Sauvegarde les proxies vivants dans un fichier."""
    with open(file_path, 'w') as file:
        for proxy in proxies:
            file.write(proxy + "\n")
    print(f"Proxies vivants sauvegardés dans '{file_path}'.")

def check_proxy(proxy):
    """Teste si un proxy SOCKS5 est vivant."""
    try:
        ip, port = proxy.split(":")
        socks.set_default_proxy(socks.SOCKS5, ip, int(port))
        socket.socket = socks.socksocket
        s = socket.create_connection(("8.8.8.8", 53), timeout=TIMEOUT)  # Test DNS avec Google
        s.close()
        return True
    except Exception:
        return False

def worker():
    """Fonction exécutée par chaque thread."""
    while not proxy_queue.empty():
        proxy = proxy_queue.get()
        if check_proxy(proxy):
            print(f"[LIVE] {proxy}")
            live_proxies.append(proxy)
        else:
            print(f"[DEAD] {proxy}")
        proxy_queue.task_done()

def main():
    if len(sys.argv) != 2:
        print("Usage : python proxyCHK.py <proxy_list.txt>")
        sys.exit(1)

    proxy_file = sys.argv[1]
    proxies = load_proxies(proxy_file)

    print(f"Chargement de {len(proxies)} proxies...")
    for proxy in proxies:
        proxy_queue.put(proxy)

    print(f"Vérification des proxies avec {NUM_THREADS} threads...")
    threads = []
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # Attendre la fin du traitement
    proxy_queue.join()

    print(f"Proxies vivants trouvés : {len(live_proxies)}")
    save_live_proxies("proxy_live.txt", live_proxies)

if __name__ == "__main__":
    main()
