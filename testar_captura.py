import dxcam
import cv2
import numpy as np

# Captura SOMENTE a parte esquerda da tela (evita capturar a janela do OpenCV)
camera = dxcam.create(region=(0, 0, 1600, 1080), output_color="BGR")
camera.start()

# Região da interface de seleção (ok pela imagem)
REGION_SELECAO = (770, 5, 300, 150)

# Nova região do minimapa (ajustada pela imagem)
REGION_MINIMAPA = (1605, 25, 250, 250)

# Template (ex: nome ou ícone do digimon)
TEMPLATE_PATH = "C:\\Users\\Felippe Cruz\\Documents\\_Desenvolvimento\\Python\\DMO_SCRIPTS\\assets\\woodmon.png"
T_THRESHOLD = 0.7

template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
tpl_h, tpl_w = template.shape[:2]

print("🧪 Pressione ESC para sair da visualização.")

while True:
    frame = camera.get_latest_frame()
    if frame is None:
        continue

    vis = frame.copy()

    # Região da seleção do digimon (azul)
    x, y, w, h = REGION_SELECAO
    cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.putText(vis, "SELECAO", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Região do minimapa (amarelo) - pode estar fora da tela capturada, se for o caso, comente esta parte
    # x2, y2, w2, h2 = REGION_MINIMAPA
    # cv2.rectangle(vis, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 255), 2)
    # cv2.putText(vis, "MINIMAPA", (x2, y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Matching do template na seleção
    roi = frame[y:y+h, x:x+w]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)

    if res.max() >= T_THRESHOLD:
        max_loc = cv2.minMaxLoc(res)[3]
        top_left = (x + max_loc[0], y + max_loc[1])
        bottom_right = (top_left[0] + tpl_w, top_left[1] + tpl_h)
        cv2.rectangle(vis, top_left, bottom_right, (0, 0, 255), 2)
        cv2.putText(vis, "MATCH!", (top_left[0], top_left[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Calibracao Visual", vis)
    if cv2.waitKey(1) == 27:
        break

camera.stop()
cv2.destroyAllWindows()
