import cv2, os, time, pyautogui, base64, requests, pyperclip, pygame, sys, dxcam
from pytesseract import pytesseract
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Map.config import SFX_PATH

camera = dxcam.create()

pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

resolucoes_automaticas = 0

pygame.mixer.init()
som_aviso = pygame.mixer.Sound(SFX_PATH["Start"])

def image_to_base64(path):
    with open(path, "rb") as f:
        print('[WARN] Gerando imagem Base 64')
        return base64.b64encode(f.read()).decode("utf-8")

def responder_capcha_interface(texto, x, y):
    print(f"[INFO] Posicionando mouse em ({x}, {y}) e respondendo capcha com: {texto}")
    pyperclip.copy(texto)
    pyautogui.moveTo(x, y, duration=0.3)
    time.sleep(0.3)
    pyautogui.click(button='left')
    time.sleep(0.3)
    pyautogui.write(texto, interval=0.05)
    time.sleep(0.3)
    pyautogui.press("enter")
    time.sleep(10)
    identificar_teste_macro()

def solicitar_resposta_API(image_path, desafio):
    print("[INFO] CONECTANDO A API 2CAPCHA")
    image_b64 = image_to_base64(image_path)

    CREATE_URL = "https://api.2captcha.com/createTask"
    RESULT_URL = "https://api.2captcha.com/getTaskResult"

    JSON_2CAPCHA = {
        "clientKey": "ff6268640f6ab8ebe060e6cd625061fd",
        "task": {
            "type": "ImageToTextTask",
            "body": image_b64,
            "phrase": False,
            "case": False,
            "numeric": 0,
            "math": False,
            "minLength": 0,
            "maxLength": 0,
            "comment": desafio
        },
        "languagePool": "en"
    }

    print("[INFO] Enviando imagem para 2Captcha (createTask)...")
    create_resp = requests.post(CREATE_URL, json=JSON_2CAPCHA)
    create_result = create_resp.json()

    if create_result.get("errorId") != 0:
        raise Exception(f"[ERRO] Falha ao criar task: {create_result}")

    task_id = create_result["taskId"]
    print(f"[INFO] Task criada com sucesso. ID: {task_id}")

    for _ in range(5):
        time.sleep(10)
        check_payload = {
            "clientKey": JSON_2CAPCHA["clientKey"],
            "taskId": task_id
        }
        check_resp = requests.post(RESULT_URL, json=check_payload)
        result = check_resp.json()

        if result.get("status") == "ready":
            texto_resolvido = result["solution"]["text"]
            return texto_resolvido
        elif result.get("status") == "processing":
            print("[INFO] Aguardando resposta...")
        else:
            raise Exception(f"[ERRO] Erro inesperado: {result}")

    raise TimeoutError("Tempo excedido aguardando resolução do captcha.")

def identificar_teste_macro():

    global resolucoes_automaticas

    print('[INFO] Inicio da verificacao')

    img = camera.grab()

    # Caminho base de Assets
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(base_dir, "..", "Assets"))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Salvar Tela Inteira em Logs
    pasta_logs = os.path.join(f"{assets_dir}/Macro_logs")
    os.makedirs(pasta_logs, exist_ok=True)
    print_inicial = os.path.join(pasta_logs, f"macro_log_{timestamp}.png")
    cv2.imwrite(print_inicial, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    dados_extraidos = pytesseract.image_to_data(
        img,
        lang="eng",
        output_type="data.frame",
        pandas_config={"on_bad_lines": "warn"}
    )

    palavras_validas = dados_extraidos[
        (dados_extraidos["level"] == 5) &
        (dados_extraidos["conf"] > 20) &
        (dados_extraidos["text"].notnull()) &
        (dados_extraidos["text"].str.strip() != "") &
        (dados_extraidos["text"].str.len() >= 4) &
        (dados_extraidos["text"].str.len() <= 10)
    ]

    palavras_validas.loc[:, "text"] = palavras_validas["text"].str.strip().str.lower()
    palavras_alvo = ["macro"]
    palavras_filtradas = palavras_validas[palavras_validas["text"].isin(palavras_alvo)]

    if palavras_filtradas.empty:
        print("[WARN] Teste de macro não detectado \n[WARN] Encerrando Verificação")
        resolucoes_automaticas = 0
        time.sleep(1)
        return False

    for _, row in palavras_validas.iterrows():
        texto = row["text"].strip().lower()
        if texto == "macro":

            print("[WARN] Macro detectado")

            # Coordenadas da palavra na tela
            x_macro = int(row["left"] + row["width"] // 2)
            y_macro = int(row["top"] + row["height"] // 2) + 370

            # Coordenadas para recorte
            x1 = max(0, int(row["left"]) - 215)
            y1 = max(0, int(row["top"]) + 150)
            x2 = min(img.shape[1], int(row["left"] + row["width"]) + 100)
            y2 = min(img.shape[0], int(row["top"] + row["height"]) + 375)

            recorte_macro = img[y1:y2, x1:x2]
            recorte_macro_bgr = cv2.cvtColor(recorte_macro, cv2.COLOR_RGB2BGR)

            pasta_report = os.path.join(f"{assets_dir}/Macro_filtrado")
            os.makedirs(pasta_report, exist_ok=True)
            print_filtrado = os.path.join(pasta_report, f"macro_detectado_{timestamp}.png")

            cv2.imwrite(print_filtrado, recorte_macro_bgr)

            # VERIFICAR A INSTRUCAO DE RESPOSTA
            instrucao_rgb = cv2.cvtColor(recorte_macro_bgr, cv2.COLOR_BGR2RGB)
            texto_instrucao = pytesseract.image_to_string(instrucao_rgb, lang="eng").lower()

            #print(f"[DEBUG] Instrução capturada: {texto_instrucao.strip()}")

            if "number" in texto_instrucao:
                desafio = "Enter only the NUMBERS you see in the image (no letters or special characters)"
            elif "english" in texto_instrucao:
                desafio = "Enter only the LETTERS you see in the image (no numbers or special characters)"
            elif "fonts" in texto_instrucao:
                desafio = "Enter ALL CHARACTERS, NUMBERS and SIMBOLS exactly as shown in the image (letters, numbers and symbols)"
            else:
                desafio = "Enter the characters that match the instruction below the image"

            print(f"[INFO] Comentário gerado para a API: {desafio}")

            try:
                # CHAMA VERIFICACAO MANUAL SE DER ERRADO 3 VEZES
                if resolucoes_automaticas == 4:
                    som_aviso.play()
                    print("[WARN] Limite de tentativas alcancado, aguardando input manual")
                    time.sleep(7)
                    sys.exit()

                resolucoes_automaticas += 1
                print(f"[WARN] NUMERO DE TENTATIVAS: {resolucoes_automaticas}")
                texto_captcha = solicitar_resposta_API(print_filtrado, desafio)
                print(f"[INFO] API retornou a resposta: {texto_captcha}")
                responder_capcha_interface(texto_captcha, x_macro, y_macro)
                
            except Exception as e:
                print(f"[ERROR] Não foi possível resolver ou responder o Capcha: {e}")
                sys.exit()
