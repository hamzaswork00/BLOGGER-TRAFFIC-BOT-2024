from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random
import time
import sys
import socks
import socket
import os
import json

# Clé de chiffrement
KEY = b'x9y5Ay3vWNT6HJJhK8xDWG07xoDbx6fcz_JtYfklCQg='
cipher = Fernet(KEY)

# Message crypté contenant le mot de passe correct
ENCRYPTED_PASSWORD = cipher.encrypt(b'error_404_bot')

CONFIG_FILE = "config.json"

# Affiche le message pour obtenir le mot de passe
def get_password():
    print("To Get Password Contact me in Telegram: @error_404_ma")
    password = input("Enter Password: ")
    return password

# Vérifie si le mot de passe est correct
def verify_password(password):
    try:
        decrypted_password = cipher.decrypt(ENCRYPTED_PASSWORD).decode()
        return password == decrypted_password
    except:
        return False

# Charger la liste des proxies avec validation
def load_proxies(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Proxy file '{file_path}' not found.")
        sys.exit(1)

    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    
    if not proxies:
        print(f"Error: Proxy file '{file_path}' is empty.")
        sys.exit(1)
    
    return proxies

# Demande le chemin du fichier chromedriver.exe
def get_chromedriver_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            if "chromedriver_path" in config:
                return config["chromedriver_path"]

    print("Chromedriver path not found. Please provide it.")
    path = input("Enter the full path to your chromedriver.exe (e.g., C:/path/to/chromedriver.exe): ")
    with open(CONFIG_FILE, 'w') as file:
        json.dump({"chromedriver_path": path}, file)
    return path

# Configurer le proxy SOCKS5 pour Selenium
def set_proxy_chrome(proxy, options):
    ip, port = proxy.split(':')
    socks.set_default_proxy(socks.SOCKS5, ip, int(port))
    socket.socket = socks.socksocket
    options.add_argument(f"--proxy-server=socks5://{ip}:{port}")

# Configurer Selenium
def setup_driver(proxy, chromedriver_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    set_proxy_chrome(proxy, chrome_options)

    # Utilisation de Service pour charger le chromedriver
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Naviguer sur le site et effectuer des clics aléatoires
def random_clicks(driver, url):
    try:
        driver.get(url)
        print(f"Visited: {url}")
        time.sleep(random.randint(2, 5))  # Attendre que la page charge

        # Trouver tous les éléments cliquables
        clickable_elements = driver.find_elements(By.XPATH, "//*[self::a or self::button or @onclick]")
        if clickable_elements:
            element = random.choice(clickable_elements)
            ActionChains(driver).move_to_element(element).click().perform()
            print("Clicked on a random element.")
        else:
            print("No clickable elements found.")
    except Exception as e:
        print(f"Error during navigation: {e}")

# Script principal
def main():
    if len(sys.argv) != 3:
        print("Usage: python traffictbot.py <URL> <proxy_list.txt>")
        sys.exit(1)

    url = sys.argv[1]
    proxy_file = sys.argv[2]

    # Charger les proxies avec validation
    proxies = load_proxies(proxy_file)

    # Obtenir le chemin de chromedriver
    chromedriver_path = get_chromedriver_path()

    # Lancer le bot
    while True:
        proxy = random.choice(proxies)
        print(f"Using proxy: {proxy}")
        driver = None  # Initialisation du driver
        try:
            driver = setup_driver(proxy, chromedriver_path)
            random_clicks(driver, url)
        except Exception as e:
            print(f"Error with proxy {proxy}: {e}")
        finally:
            if driver:
                driver.quit()  # Fermer le driver uniquement s'il a été créé
        time.sleep(random.randint(10, 20))  # Pause entre les visites

# Exécution sécurisée
if __name__ == "__main__":
    password = get_password()
    if verify_password(password):
        print("Access granted. Starting the bot...")
        main()
    else:
        print("Invalid password. Exiting...")
