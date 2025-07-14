import dxcam
import cv2
import numpy as np

# Inicializa a câmera
camera = dxcam.create(output_idx=0)

# Inicial: valores estimados — ajuste manual aqui
x, y, w, h = 205, 122, 8, 10

print("[INFO] Pressione ESC para sair")

while True:
    frame = camera.grab()

    if frame is None:
        continue

    frame = np.array(frame)

    # Desenha um retângulo vermelho
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Mostra na tela
    cv2.imshow("Ajuste SELF_DIGIMON_HP", frame)

    # Espera por tecla
    key = cv2.waitKey(1)

    if key == 27:  # ESC
        break

cv2.destroyAllWindows()
