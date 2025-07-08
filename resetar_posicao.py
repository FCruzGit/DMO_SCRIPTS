import dxcam, cv2, numpy as np, time, threading
import pyautogui, keyboard

# ─── CONFIGURAÇÃO ────────────────────────────────────────────────────────────

# Região do minimapa (x, y, w, h) — ajuste pro seu HUD
REGION_MINIMAPA = (1600, 50, 300, 300)

# Fatores de conversão deslocamento→tempo de tecla (teste e ajuste)
FACTOR_WASD = 0.005   # seg por pixel de y
FACTOR_AD   = 0.005   # seg por pixel de x

# Teclas de trigger e ligar/desligar
HOTKEY_TOGGLE = 'F10'
HOTKEY_TRIGGER = 'F9'

# ─── VARIÁVEIS GLOBAIS ────────────────────────────────────────────────────────

camera = dxcam.create(output_color="BGR")
camera.start(target_fps=60)

bot_ativo = False
ref_template = None
tpl_w = tpl_h = 0

# ─── FUNÇÕES ──────────────────────────────────────────────────────────────────

def capturar_minimapa():
    """Pega o frame atual e recorta o minimapa."""
    frame = camera.get_latest_frame()
    if frame is None:
        return None
    x, y, w, h = REGION_MINIMAPA
    return frame[y:y+h, x:x+w]

def set_reference():
    """Captura o minimapa atual como template de referência e conta 10 s."""
    global ref_template, tpl_w, tpl_h
    mini = None
    while mini is None:
        mini = capturar_minimapa()
    ref_template = cv2.cvtColor(mini, cv2.COLOR_BGR2GRAY)
    tpl_h, tpl_w = ref_template.shape
    print("📌 Ponto de referência salvo! Iniciando contagem de 10 s...")
    time.sleep(10)
    print("⏱️ 10 s se passaram, voltando ao ponto de referência...")
    voltar_para_referencia()

def voltar_para_referencia():
    """Encontra o template no minimapa atual e dirige o personagem de volta."""
    global ref_template, tpl_w, tpl_h
    if ref_template is None:
        print("⚠️ Nenhuma referência definida.")
        return

    mini = None
    # às vezes a primeira captura falha
    while mini is None:
        mini = capturar_minimapa()
    gray = cv2.cvtColor(mini, cv2.COLOR_BGR2GRAY)

    # template matching
    res = cv2.matchTemplate(gray, ref_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val < 0.6:
        print(f"❌ Referência não encontrada (confidence={max_val:.2f})")
        return

    # calcula centro do minimapa e posição alvo
    h, w = gray.shape
    cx, cy = w//2, h//2
    tx = max_loc[0] + tpl_w//2
    ty = max_loc[1] + tpl_h//2

    dx = tx - cx
    dy = ty - cy
    print(f"➡️  Offset detectado (dx={dx}, dy={dy}), movendo personagem...")

    # movem nas direções correspondentes
    # eixo Y: dy<0 → W, dy>0 → S
    if dy < 0:
        pyautogui.keyDown('w')
        time.sleep(abs(dy) * FACTOR_WASD)
        pyautogui.keyUp('w')
    elif dy > 0:
        pyautogui.keyDown('s')
        time.sleep(abs(dy) * FACTOR_WASD)
        pyautogui.keyUp('s')

    # eixo X: dx<0 → A, dx>0 → D
    if dx < 0:
        pyautogui.keyDown('a')
        time.sleep(abs(dx) * FACTOR_AD)
        pyautogui.keyUp('a')
    elif dx > 0:
        pyautogui.keyDown('d')
        time.sleep(abs(dx) * FACTOR_AD)
        pyautogui.keyUp('d')

    print("✅ Personagem voltou (aproximadamente) ao ponto de referência.")

def monitorar_teclas():
    """Thread que escuta as hotkeys."""
    global bot_ativo
    keyboard.add_hotkey(HOTKEY_TOGGLE, lambda: toggle_bot())
    keyboard.add_hotkey(HOTKEY_TRIGGER, lambda: threading.Thread(target=set_reference, daemon=True).start())
    # mantém a thread viva
    keyboard.wait('esc')

def toggle_bot():
    global bot_ativo
    bot_ativo = not bot_ativo
    estado = "ON" if bot_ativo else "OFF"
    print(f"🔄 Bot {estado}")

# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Pressione F10 para ligar/desligar o bot, F9 para definir trigger (set reference).")
    threading.Thread(target=monitorar_teclas, daemon=True).start()

    # Loop principal (pode incluir outras lógicas de farm)
    try:
        while True:
            if not bot_ativo:
                time.sleep(0.1)
                continue
            # aqui você pode colocar a lógica de farm enquanto não pressiona o trigger
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        camera.stop()
        print("👋 Encerrando.")
