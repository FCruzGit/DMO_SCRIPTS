import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import ImageGrab
import time
import os
import keyboard
import settings
import threading
import pygame

# Estado global
bot_ativo = False
alarme_tocando = False

# Diretórios
PATHS = settings.diretorio
SCAN_DIR = PATHS["scans"]
TCR = PATHS["tesseract"]
ALARME_PATH = PATHS["alarme"]

digimon_alvo = "Lillymon"

# Inicializa o Tesseract
pytesseract.pytesseract.tesseract_cmd = TCR
os.makedirs(SCAN_DIR, exist_ok=True)

# Alarme com pygame
def tocar_alarme_em_loop():
    pygame.mixer.init()
    pygame.mixer.music.load(ALARME_PATH)
    pygame.mixer.music.play(loops=-1)
    print("🔊 Alarme tocando...")

def parar_alarme():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        print("🔇 Alarme parado.")

def detectar_macro():
    global alarme_tocando

    screenshot = pyautogui.screenshot()
    img_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    texto = pytesseract.image_to_string(img_rgb)

    if "anti-macro" in texto.lower():
        if not alarme_tocando:
            print("🚨 Anti-macro detectado! Tocando alarme e pausando tudo.")
            alarme_tocando = True
            threading.Thread(target=tocar_alarme_em_loop, daemon=True).start()

        time.sleep(7)  # Espera antes de verificar de novo
        return True  # Ainda em modo anti-macro

    elif alarme_tocando:
        print("✅ Anti-macro desapareceu. Retomando execução.")
        alarme_tocando = False
        parar_alarme()

    return False  # Sem anti-macro, seguir normalmente


def tirar_print():
    print("📸 Capturando tela...")
    imagem = ImageGrab.grab()
    caminho = os.path.join(SCAN_DIR, "screen.png")
    imagem.save(caminho)
    return caminho

giro_count = 0  # contador de giros consecutivos sem encontrar Lillymon

def procurar_digimon():
    global giro_count

    print("📸 Capturando tela com pyautogui...")
    screenshot = pyautogui.screenshot()
    screenshot_path = os.path.join(SCAN_DIR, "screen.png")
    screenshot.save(screenshot_path)

    img_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)

    contador = 0

    for i in range(len(data["text"])):
        texto_detectado = data["text"][i]
        if digimon_alvo.lower() in texto_detectado.lower():
            contador += 1

    if contador > 0:
        print(f"🎯 {digimon_alvo} detectado {contador} vez(es)! Atacando...")
        giro_count = 0  # resetar contador de giros após sucesso

        for i in range(contador):
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('1')
            time.sleep(1.5)

        return True

    # Se não encontrar Lillymon, girar a câmera
    giro_count += 1
    print(f"🔄 {digimon_alvo} não encontrado. Giro {giro_count}/3.")

    pyautogui.mouseDown(button='right')
    pyautogui.moveRel(160, 0, duration=0.6)  # ~180° ajustado
    pyautogui.mouseUp(button='right')
    time.sleep(0.5)

    if giro_count >= 3:
        print("🚶‍♂️ Realizando movimentação para frente após 3 giros sem resultado.")
        pyautogui.keyDown('w')
        time.sleep(1)
        pyautogui.keyUp('w')
        giro_count = 0

    return False


def macro_lillymon():
    while True:
        if not bot_ativo:
            time.sleep(0.1)
            continue

        detectar_macro()
        procurar_digimon()

def monitorar_tecla():
    global bot_ativo
    while True:
        keyboard.wait("F10")
        bot_ativo = not bot_ativo
        estado = "ATIVADO" if bot_ativo else "DESATIVADO"
        print(f"\n🟢 Bot {estado}\n")
        if not bot_ativo:
            parar_alarme()
        time.sleep(0.5)

if __name__ == "__main__":
    print("Pressione F10 para iniciar/parar o bot.")
    threading.Thread(target=monitorar_tecla, daemon=True).start()
    macro_lillymon()
