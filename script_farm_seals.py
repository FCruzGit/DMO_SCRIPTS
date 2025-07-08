import dxcam
import cv2
import numpy as np
import time
import pyautogui
import threading
import keyboard
import os

# ─── CONFIGS ──────────────────────────────────────

# Regiões
REGION_SELECAO = (770, 5, 300, 150)
REGION_MINIMAPA = (1605, 25, 250, 250)

# Template alvo
TEMPLATE_DG_ALVO = cv2.imread("C:\\Users\\Felippe Cruz\\Documents\\_Desenvolvimento\\Python\\DMO_SCRIPTS\\assets\\woodmon.png", cv2.IMREAD_GRAYSCALE)
T_THRESHOLD = 0.9

# Retorno
BASE_POINT = (130, 130)  # relativo ao centro do minimapa
ROTATION_ANGLE = 90
MAX_ROTATIONS = 4

# Estado
bot_ativo = False
rotation_count = 0
failed_calls = 0

# ─── DXCAM SETUP ───────────────────────────────────

camera = dxcam.create(region=(0, 0, 1920, 1080), output_color="BGR")
camera.start()

# ─── FUNÇÕES ────────────────────────────────────────

def capturar_roi(frame, region):
    x, y, w, h = region
    return frame[y:y+h, x:x+w]

def identificar_alvos():
    """
    Procura digimons com TAB, se encontrar matching com template, ataca com '1'.
    """
    print("🔍 Buscando alvos...")
    for _ in range(8):  # tenta até 8 TABs
        pyautogui.press('tab')
        time.sleep(0.2)

        frame = camera.get_latest_frame()
        if frame is None:
            continue

        roi = capturar_roi(frame, REGION_SELECAO)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray, TEMPLATE_DG_ALVO, cv2.TM_CCOEFF_NORMED)

        if res.max() >= T_THRESHOLD:
            print("🎯 Alvo detectado! Atacando...")
            pyautogui.press('1')
            time.sleep(1.5)
            return True

    print("❌ Nenhum alvo encontrado.")
    return False

def movimentacao_camera():
    global rotation_count, failed_calls

    print(f"🔄 Girando câmera {ROTATION_ANGLE}°")
    pyautogui.mouseDown(button='right')
    pyautogui.moveRel(ROTATION_ANGLE, 0, duration=0.4)
    pyautogui.mouseUp(button='right')
    rotation_count = (rotation_count + 1) % MAX_ROTATIONS
    time.sleep(0.5)

    if identificar_alvos():
        rotation_count = 0
        failed_calls = 0
        return

    if rotation_count == 0:
        failed_calls += 1
        print(f"⚠️ Rotação completa sem sucesso ({failed_calls}/2)")
        if failed_calls >= 2:
            print("🏃 Retornando ao ponto base no minimapa.")
            frame = camera.get_latest_frame()
            minimap = capturar_roi(frame, REGION_MINIMAPA)
            cx, cy = minimap.shape[1] // 2, minimap.shape[0] // 2
            bx, by = BASE_POINT
            dx, dy = bx - cx, by - cy

            if dy < 0: pyautogui.keyDown('w'); time.sleep(abs(dy)/100); pyautogui.keyUp('w')
            if dy > 0: pyautogui.keyDown('s'); time.sleep(abs(dy)/100); pyautogui.keyUp('s')
            if dx < 0: pyautogui.keyDown('a'); time.sleep(abs(dx)/100); pyautogui.keyUp('a')
            if dx > 0: pyautogui.keyDown('d'); time.sleep(abs(dx)/100); pyautogui.keyUp('d')

            failed_calls = 0

def macro_loop():
    while True:
        if not bot_ativo:
            time.sleep(0.2)
            continue

        if not identificar_alvos():
            movimentacao_camera()

def monitorar_tecla():
    global bot_ativo
    while True:
        keyboard.wait("F10")
        bot_ativo = not bot_ativo
        estado = "ATIVADO" if bot_ativo else "DESATIVADO"
        print(f"\n🟢 Bot {estado}\n")
        time.sleep(0.5)  # evitar múltiplos triggers

# ─── EXECUÇÃO ──────────────────────────────────────

if __name__ == "__main__":
    print("⏳ Pressione F10 para iniciar ou parar o bot.")
    threading.Thread(target=monitorar_tecla, daemon=True).start()
    macro_loop()
