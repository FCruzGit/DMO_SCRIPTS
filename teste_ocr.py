import dxcam
import cv2
import easyocr
import numpy as np
import time

# Região da tela para capturar o macro test (ajuste se necessário)
MACRO_SELECAO = (0, 0, 1920, 1080)

# Inicializa EasyOCR para inglês
reader = easyocr.Reader(['en'], gpu=False)

# Inicia captura da tela
camera = dxcam.create(region=MACRO_SELECAO, output_color="BGR")
camera.start()
time.sleep(1)

print("🧪 Capturando tela e tentando ler texto do macro test...")

frame = camera.get_latest_frame()
camera.stop()

if frame is None:
    print("❌ Erro ao capturar tela.")
    exit()

# Opcional: pré-processamento leve para melhorar OCR
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (3, 3), 0)

# OCR
results = reader.readtext(blur)

if results:
    print("✅ Textos detectados:")
    for (bbox, text, conf) in results:
        print(f"🔹 '{text}' (confiança: {conf:.2f})")

        # Opcional: desenhar na imagem
        pts = np.array(bbox, dtype=np.int32)
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        cv2.putText(frame, text, (pts[0][0], pts[0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
else:
    print("❌ Nenhum texto encontrado.")

# Exibe a imagem com os textos detectados
cv2.imshow("OCR Result", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
