import dxcam
import cv2
import numpy as np
import os
from datetime import datetime

# ─── CONFIGURAÇÃO ─────────────────────────────

# Região da interface de seleção no topo (ajustada)
REGION_SELECAO = (770, 5, 300, 150)  # x, y, w, h
SALVAR_COMO = "template.png"  # nome do arquivo de saída

# ─── CAPTURA COM DXCAM ───────────────────────

camera = dxcam.create(region=(0, 0, 1920, 1080), output_color="BGR")
camera.start()
frame = None

print("🖼️ Aguardando frame...")
while frame is None:
    frame = camera.get_latest_frame()

x, y, w, h = REGION_SELECAO
template_img = frame[y:y+h, x:x+w]

# Salva imagem
cv2.imwrite(SALVAR_COMO, template_img)
camera.stop()

# Caminho completo
caminho_completo = os.path.abspath(SALVAR_COMO)
print(f"✅ Template salvo como '{SALVAR_COMO}' em:\n{caminho_completo}")
