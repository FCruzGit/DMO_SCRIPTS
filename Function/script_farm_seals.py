import dxcam, cv2, numpy as np
import pyautogui, threading, keyboard, os, time, pygame, sys

#### SCRIPT GERAL DE ATAQUE BASEADO EM TEMPLATE ####

camera = dxcam.create()
pygame.mixer.init()

T_THRESHOLD = 0.8

SFX_START = "sfx/start.wav"
SFX_STOP = "sfx/stop.wav"

script_ativo = False

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Map.config import TEMPLATE_DIGIMON_ALVO
from Map.mapeamento_1920x1080 import ENEMY_DIGIMON_HP, ENEMY_DIGIMON_SELECIONADO

som_ativar = pygame.mixer.Sound("C:\\_Desenvolvimento\\Python\\DMO_SCRIPTS\\SFX\\start.wav")
som_desativar = pygame.mixer.Sound("C:\\_Desenvolvimento\\Python\\DMO_SCRIPTS\\SFX\\stop.wav")

# Carrega templates categorizados
TEMPLATES = []
for info in TEMPLATE_DIGIMON_ALVO:
    if os.path.exists(info["path"]):
        tpl = cv2.imread(info["path"], cv2.IMREAD_GRAYSCALE)
        nome_digimon = info["name"]
        TEMPLATES.append({
            "name": nome_digimon,
            "img": tpl,
            "type": info["type"]
        })
    else:
        print(f"⚠️ Template de DIGIMON não encontrado: {info['path']}")

def capturar_roi(frame, region):
    x, y, w, h = region
    return frame[y:y+h, x:x+w]

def detectar_tipo_alvo(frame):
    roi = capturar_roi(frame, ENEMY_DIGIMON_SELECIONADO)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    for tpl_info in TEMPLATES:
        template = tpl_info["img"]
        tipo = tpl_info["type"]

        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        if res.max() >= T_THRESHOLD:
            return tipo
    return None

def calcular_hp(frame):
    hp_roi = capturar_roi(frame, ENEMY_DIGIMON_HP)
    hsv = cv2.cvtColor(hp_roi, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    total_pixels = hp_roi.shape[0] * hp_roi.shape[1]
    hp_pixels = cv2.countNonZero(mask)
    hp_percent = hp_pixels / total_pixels

    return hp_percent

def identificar_alvos():
    tentativas = 0
    while tentativas < 3:
        frame = camera.get_latest_frame()
        if frame is None:
            print("[DEBUG] Frame não capturado, tentando novamente...")
            continue

        hp = calcular_hp(frame)
        print(f"❤️ HP atual: {hp*100:.1f}%")

        if hp == 0:
            print("💀 HP zerado, trocando alvo...")
            pyautogui.press('tab')
            time.sleep(0.25)
            tentativas += 1
            continue

        tipo_alvo = detectar_tipo_alvo(frame)
        if tipo_alvo:
            print(f"🎯 Alvo detectado: {tipo_alvo.upper()}")

            if tipo_alvo == "boss":
                pyautogui.press('f2')
            elif tipo_alvo == "common":
                pyautogui.press('1')
            else:
                print("⚠️ Tipo desconhecido, ignorando...")
            
            time.sleep(1)
            tentativas = 0
        else:
            print("🔄 Nenhum match. Tentando nova seleção com TAB...")
            pyautogui.press('tab')
            time.sleep(0.25)
            tentativas += 1

    print("↩️ Tentativas esgotadas. Girando câmera...")
    return False

def movimentacao_camera():
    print("🔁 Girando câmera para tentar encontrar alvos...")
    pyautogui.mouseDown(button='right')
    pyautogui.moveRel(120, 0, duration=0.1)
    pyautogui.mouseUp(button='right')
    time.sleep(0.5)
    identificar_alvos()

def macro_loop():
    while True:
        if not script_ativo:
            time.sleep(0.2)
            continue
        if not identificar_alvos():
            movimentacao_camera()

def monitorar_tecla():
    global script_ativo
    while True:
        keyboard.wait("F10")
        script_ativo = not script_ativo
        estado = "ATIVADO" if script_ativo else "DESATIVADO"
        print(f"\n🟢 Bot {estado}\n")

        if script_ativo:
            som_ativar.play()

        else:
            som_desativar.play()

        time.sleep(0.5)

# ─── EXEC ────────────────────────────────

if __name__ == "__main__":

    print("▶️ Pressione F10 para ativar o script.")

    threading.Thread(target=monitorar_tecla, daemon=True).start()

    try:
        macro_loop()
    except KeyboardInterrupt:
        print("🛑 Bot encerrado manualmente.")
        som_desativar.play()
        time.sleep(1)
        sys.exit()