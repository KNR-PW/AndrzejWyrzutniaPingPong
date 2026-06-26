#Autor - Filip Maziarka
#Kod powstał na podstawie kodu https://github.com/morswin499
#Komunikacja z Andrzejem za pomocą pada do PS4. Można TYLKO strzelać.
import pygame
import serial
import time

# Konfiguracja portu Bluetooth
BT_PORT = "COM12"   # zmień jeśli inny port
BAUDRATE = 115200

# Inicjalizacja połączenia Bluetooth
try:
    bt = serial.Serial(BT_PORT, BAUDRATE, write_timeout=1)
    print(f"✅ Połączono z HC-06 na {BT_PORT}")
except serial.SerialException as e:
    print(f"❌ Błąd połączenia: {e}")
    exit(1)

def mapToByte(x, l, r, l2, r2):
    return int((x-l)/(r-l)*(r2-l2)+l2)

# Inicjalizacja pygame i joysticka
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ Brak wykrytego kontrolera Xbox! Upewnij się, że jest sparowany przez Bluetooth.")
    exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Wykryto kontroler: {joystick.get_name()}")

# Konwersja osi joysticka na prędkość -250...250
def axis_to_speed(value, deadzone=0.15):
    if abs(value) < deadzone:
        return 0
    return int(max(min(value * 250, 250), -250))

# Tworzenie ramki 8-bajtowej
def format_frame(left_speed, right_speed):
    left_sign = '0' if left_speed >= 0 else '1'
    right_sign = '0' if right_speed >= 0 else '1'

    l_val = abs(left_speed)
    r_val = abs(right_speed)

    l_str = f"{l_val:03}"
    r_str = f"{r_val:03}"
    return (l_str + r_str + left_sign + right_sign).encode('ascii')

# Główna pętla
try:
    while True:
        pygame.event.pump()
        #dodatnie w prawo i w górę, dodatnie do przodu
        forward = 0
        #forward = mapToByte(joystick.get_axis(5)-joystick.get_axis(4), -2, 2, 0, 255)
        turn = 0
        gunRotation = mapToByte(joystick.get_axis(0), -1, 1, 0, 255)
        gunElevation = mapToByte(joystick.get_axis(1), -1, 1, 0, 255)
        #gunElevation = 0
        #gunRotation = mapToByte(joystick.get_axis(0), -1, 1, 0, 255)
        #gunRotation = 0
        przyciski = 0x00
        for i in range(0, 6):#Najniższy bit - ?/Share/Tri/Sq/O/X/NIC/NIC - najwyższy bit
            przyciski = (przyciski << 1) | joystick.get_button(i)
        #print(joystick.get_button(5))
        przyciski = 16*joystick.get_button(0)
        print(f"L: {forward}  R: {turn} UP:  {gunElevation} ROT: {gunRotation} P: {przyciski}")
        bt.write([127,127, gunElevation, gunRotation,przyciski,0,0,0])

        time.sleep(0.02)

except KeyboardInterrupt:
    print("🛑 Zamykanie...")
finally:
    bt.close()
    pygame.quit()
