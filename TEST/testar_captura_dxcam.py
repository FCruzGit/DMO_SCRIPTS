import dxcam
import cv2
import time
import keyboard
import pygame

# Inicializa o mixer do pygame
pygame.mixer.init()
pygame.mixer.music.load(SFX_PATH["Print"])

# Região inicial — ajuste conforme necessário
REGIAO_FOTO = [0, 0, 1920, 1080]

# Inicia a câmera DXCam
camera = dxcam.create(output_color="BGR")
camera.start()

print("🎯 Visualizador iniciado.")
print("🟩 Retângulo mostra a área de captura.")
print("🔊 Pressione F9 para tocar som.")
print("❌ Pressione ESC para sair.")

try:
    while True:
        frame = camera.get_latest_frame()
        if frame is None:
            continue

        x, y, w, h = REGIAO_FOTO
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Visualização da Região", frame)

        if keyboard.is_pressed("f9"):
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
                print("📸 Som de captura tocado.")
                time.sleep(0.5)

        key = cv2.waitKey(1)
        if key == 27:
            break

    cv2.destroyAllWindows()
    camera.stop()
except KeyboardInterrupt:
    cv2.destroyAllWindows()
    camera.stop()
