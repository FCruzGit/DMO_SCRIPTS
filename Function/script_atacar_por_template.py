import pyautogui, threading, keyboard, os, time, pygame, sys, dxcam, cv2, numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Map.config import TEMPLATE_DIGIMON_ALVO, SFX_PATH
from Map.mapeamento_1920x1080 import ENEMY_DIGIMON_HP, ENEMY_DIGIMON_SELECIONADO
from anti_macro import identificar_teste_macro

DIGIMONS_PROCURADOS = ["kunemon", "dokunemon", "candlemon", "demi-meramon"] 

camera = dxcam.create()

script_ativo = False

def capturar_roi(frame, region):                    
    x, y, w, h = region
    return frame[y:y+h, x:x+w]

def acao_verificar_macro(tempo_inicial, intervalo=10):
    tempo_decorrido = time.time() - tempo_inicial
    if tempo_decorrido >= intervalo:
        print("[INFO] Verificando tela contra macro")         
        identificar_teste_macro()
        return time.time()
    return tempo_inicial

def verificar_digimon_selecionado():
    print("[INFO] Iniciando verificação por template...")
    tempo_inicial = time.time()
    tempo_maximo = 10
    tentativas = 0

    templates_alvo = []
    for tpl in TEMPLATE_DIGIMON_ALVO:
        if tpl["name"].lower() in DIGIMONS_PROCURADOS:
            if os.path.exists(tpl["path"]):
                imagem = cv2.imread(tpl["path"], cv2.IMREAD_GRAYSCALE)
                templates_alvo.append({
                    "name": tpl["name"].lower(),
                    "img": imagem
                })
            else:
                print(f"[WARN] Template não encontrado: {tpl['path']}")

    if not templates_alvo:
        print("[ERRO] Nenhum template carregado para comparação!")
        return

    while script_ativo:

        frame = camera.grab()
        if frame is None:
            print("[WARN] Frame não capturado.")
            continue

        roi = capturar_roi(frame, ENEMY_DIGIMON_SELECIONADO)
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        encontrado = False

        for template in templates_alvo:
            res = cv2.matchTemplate(roi_gray, template["img"], cv2.TM_CCOEFF_NORMED)
            max_val = cv2.minMaxLoc(res)[1]

            if max_val >= 0.8:
                print(f"[INFO] Digimon detectado: {template['name'].upper()} (match={max_val:.2f})")
                pyautogui.press('1')
                time.sleep(1)
                encontrado = True
                tentativas = 0
                break

        if not encontrado:
            print("[INFO] Alvo não é desejado. Trocando com TAB...")
            pyautogui.press('tab')
            time.sleep(0.3)
            tentativas += 1

        if tentativas >= 5:
            print("[INFO] Nenhum alvo válido encontrado. Girando câmera...")
            pyautogui.mouseDown(button='right')
            pyautogui.moveRel(150, 0, duration=0.2)
            pyautogui.mouseUp(button='right')
            tentativas = 0
            time.sleep(1)

        tempo_decorrido = time.time() - tempo_inicial
        if tempo_decorrido >= tempo_maximo:
            print("[INFO] Checando se há macro na tela...")
            identificar_teste_macro()
            tempo_inicial = time.time()

def script_atacar_por_template():

    pygame.mixer.init()

    som_ativar = pygame.mixer.Sound(SFX_PATH["Start"])
    som_desativar = pygame.mixer.Sound(SFX_PATH["Stop"])

    print("[INFO] PARAMETROS GERAIS INICIALIZADOS")

    try:
        verificar_digimon_selecionado()
    except Exception as e:
        print(f"[ERROR] Erro: {e}")
        sys.exit()

def monitorar_tecla():

    global script_ativo

    while True:
        keyboard.wait("space")
        script_ativo = not script_ativo

        if script_ativo:
            print("\n✅ Script ATIVADO (Espaço pressionado)\n")
            threading.Thread(target=script_atacar_por_template, daemon=True).start()
        else:
            print("\n⛔ Script DESATIVADO (Espaço pressionado)\n")

        time.sleep(0.5)

# Início do monitoramento
if __name__ == "__main__":
    print("▶️ Pressione ESPAÇO para ativar/desativar o script.")
    threading.Thread(target=monitorar_tecla, daemon=True).start()

    while True:
        time.sleep(1)  # Mantém o script vivo
