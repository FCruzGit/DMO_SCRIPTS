from pytesseract import pytesseract
from datetime import datetime
import dxcam, cv2, os, keyboard, time, pyautogui, base64, requests, pyperclip

pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def detectar_tipo_captcha_por_instrucao(caminho_img):
    imagem_bgr = cv2.imread(caminho_img)
    if imagem_bgr is None:
        raise ValueError(f"Erro ao carregar imagem: {caminho_img}")

    imagem_rgb = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)

    print("==== [DEBUG] TEXTO COMPLETO DETECTADO NA IMAGEM ====")
    texto_completo = pytesseract.image_to_string(imagem_rgb, lang="eng")
    print(texto_completo.strip())
    print("====================================================")

    # Recorta os últimos ~120 pixels da imagem (onde normalmente fica a instrução)
    altura = imagem_bgr.shape[0]
    largura = imagem_bgr.shape[1]
    parte_instrucao = imagem_bgr[altura - 120:altura, 0:largura]
    parte_instrucao_rgb = cv2.cvtColor(parte_instrucao, cv2.COLOR_BGR2RGB)

    texto_instrucao = pytesseract.image_to_string(parte_instrucao_rgb, lang="eng").lower()
    print(f"[DEBUG] Instrução detectada no OCR: {texto_instrucao.strip()}")

    if "number" in texto_instrucao:
        return "Enter only the numbers you see in the image"
    elif "english" in texto_instrucao:
        return "Enter only the English letters you see in the image (no numbers or special characters)"
    elif "font" in texto_instrucao or "character" in texto_instrucao or "all" in texto_instrucao:
        return "Enter all characters exactly as shown in the image (letters, numbers and symbols)"
    else:
        return "Enter only the characters that match the instruction below the image"

    
detectar_tipo_captcha_por_instrucao("C:\\_Desenvolvimento\\Python\\DMO_SCRIPTS\\Assets\\Macro_filtrado\\macro_detectado_20250714_005109.png")
