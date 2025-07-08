import dxcam, uuid, cv2, time, keyboard, pygame, os

# Inicializa o mixer do pygame
pygame.mixer.init()
som_captura = pygame.mixer.Sound("DMO_SCRIPTS/sfx/print.wav")

# Região ajustada
REGIAO_FOTO = [980, 30, 44, 40]  # x, y, w, h

# Pasta de saída
PASTA_SAIDA = "DMO_SCRIPTS/model"
os.makedirs(PASTA_SAIDA, exist_ok=True)

# Inicia a câmera DXCam
camera = dxcam.create(output_color="BGR")
camera.start()

print("🖼️ Pressione F9 para capturar template.")
print("🔊 Efeito sonoro será tocado.")
print("❌ Pressione CTRL+C para sair.")

try:
    while True:
        if keyboard.is_pressed("f9"):
            frame = camera.get_latest_frame()
            if frame is None:
                continue

            x, y, w, h = REGIAO_FOTO
            recorte = frame[y:y+h, x:x+w]

            # Salva imagem
            nome_arquivo = f"{uuid.uuid4().hex[:8]}.png"
            caminho = os.path.join(PASTA_SAIDA, nome_arquivo)
            cv2.imwrite(caminho, recorte)

            # Toca som
            som_captura.play()
            print(f"📸 Template salvo em: {caminho}")

            time.sleep(0.5)  # Evita múltiplas capturas seguidas

except KeyboardInterrupt:
    print("\n⛔ Encerrado pelo usuário.")
    camera.stop()
