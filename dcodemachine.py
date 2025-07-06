import ctypes
import time
import keyboard
import threading

# Intervalo total entre repetições (em segundos)
intervalo = 1
executando = False

# Constantes para clique esquerdo
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("mi", MOUSEINPUT)]

def click_esquerdo():
    extra = ctypes.c_ulong(0)
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
    time.sleep(0.05)
    inp.mi.dwFlags = MOUSEEVENTF_LEFTUP
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

def macro():
    global executando
    while executando:
        click_esquerdo()
        time.sleep(1)
        keyboard.send("enter")
        time.sleep(intervalo - 1)

def alternar_macro():
    global executando
    executando = not executando
    if executando:
        threading.Thread(target=macro, daemon=True).start()
        print("Macro iniciada.")
    else:
        print("Macro parada.")

keyboard.add_hotkey("F8", alternar_macro)
print("Pressione F8 para iniciar/parar. ESC para sair.")
keyboard.wait("esc")
