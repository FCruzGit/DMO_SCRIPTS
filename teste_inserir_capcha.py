import easyocr
import pyautogui
import cv2
import numpy as np

# Caminho da imagem (use uma imagem que contenha o desafio macro)
img_path = 'DMO_SCRIPTS/logs/Captura de tela 2025-07-08 005934.png'
image = cv2.imread(img_path)

# Pré-processamento: converter para escala de cinza
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# Aplicar limiarização adaptativa (ajusta para fundo irregular)
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 4)

# Visualizar imagem tratada (opcional)
cv2.imshow("preprocessado", thresh)
cv2.waitKey(0)

# OCR com imagem tratada
reader = easyocr.Reader(['en'])
results = reader.readtext(thresh)

alvo = "Anti macro"

achou = False
for bbox, texto, conf in results:
    if alvo in texto.lower():
        achou = True
        print(f"✅ Texto encontrado: {texto} (confiança {conf:.2f})")
        
        # Coordenadas para clicar
        (tl, tr, br, bl) = bbox
        x = int((tl[0] + br[0]) / 2)
        y = int((tl[1] + br[1]) / 2)

        # Clicar e digitar
        pyautogui.moveTo(x, y)
        pyautogui.click()
        pyautogui.write("AB12C", interval=0.1)
        pyautogui.press("enter")
        break

if not achou:
    print("❌ Texto não encontrado. Tente ajustar brilho/contraste ou região.")
