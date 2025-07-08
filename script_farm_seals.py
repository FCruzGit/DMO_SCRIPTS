import dxcam, cv2, numpy as np
import pyautogui, threading, keyboard, os, time, pygame, sys

# ─── CONFIGS ────────────────────────────────

REGION_SELECAO = (980, 30, 44, 40)
REGION_HP = (883, 46, 40, 15)

T_THRESHOLD = 0.9

MACRO_TEMPLATE_PATH = "DMO_SCRIPTS/assets/macro.png"
MACRO_SELECAO = (0, 0, 1920, 1080)
MACRO_INTERVALO = 30

SFX_START = "DMO_SCRIPTS/sfx/start.wav"
SFX_STOP = "DMO_SCRIPTS/sfx/stop.wav"
SFX_ALARME_MACRO = "DMO_SCRIPTS/sfx/alarme_03.mp3"  


# Templates com categorias
TEMPLATE_INFO = [
    {"path": "DMO_SCRIPTS/model/lillymon_boss.png", "tipo": "boss"},
    {"path": "DMO_SCRIPTS/model/lillymon_common.png", "tipo": "common"}
]

# Estado
bot_ativo = False

# Carrega templates categorizados
TEMPLATES = []
for info in TEMPLATE_INFO:
    if os.path.exists(info["path"]):
        tpl = cv2.imread(info["path"], cv2.IMREAD_GRAYSCALE)
        TEMPLATES.append({
            "imagem": tpl,
            "tipo": info["tipo"]
        })
    else:
        print(f"⚠️ Template de DIGIMON não encontrado: {info['path']}")

# ─── DXCAM ─────────────────────────────────

camera = dxcam.create(region=(0, 0, 1920, 1080), output_color="BGR")
camera.start()

# ─── SFX ───────────────────────────────────

def tocar_som(caminho):
    if os.path.exists(caminho):
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Erro ao tocar som: {e}")


# ─── MACRO ─────────────────────────────────

# Detectar o macro teste que vem um capcha para ser resolvido

# ─── FUNÇÕES ──────────────────────────────

def capturar_roi(frame, region):
    x, y, w, h = region
    return frame[y:y+h, x:x+w]

def detectar_tipo_alvo(frame):
    roi = capturar_roi(frame, REGION_SELECAO)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    for tpl_info in TEMPLATES:
        template = tpl_info["imagem"]
        tipo = tpl_info["tipo"]

        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        if res.max() >= T_THRESHOLD:
            return tipo
    return None

def calcular_hp(frame):
    hp_roi = capturar_roi(frame, REGION_HP)
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
            
            time.sleep(1.3)
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
    pyautogui.moveRel(90, 0, duration=0.4)
    pyautogui.mouseUp(button='right')
    time.sleep(0.5)
    identificar_alvos()

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

        if bot_ativo:
            tocar_som(SFX_START)
        else:
            tocar_som(SFX_STOP)

        time.sleep(0.5)


# ─── EXEC ────────────────────────────────

if __name__ == "__main__":
    print("▶️ Pressione F10 para ligar/desligar o bot.")
    
    pygame.mixer.init()

    threading.Thread(target=monitorar_tecla, daemon=True).start()

    try:
        macro_loop()
    except KeyboardInterrupt:
        print("🛑 Bot encerrado manualmente.")
        tocar_som(SFX_STOP)
        time.sleep(1)
        sys.exit()