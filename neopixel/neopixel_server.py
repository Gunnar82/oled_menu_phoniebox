#!/usr/bin/env python3
import socket
import os
import json
import signal
from rpi_ws281x import PixelStrip, Color
import time
import threading

SOCKET_PATH = "/tmp/neopixel.sock"
LED_COUNT = 8
GPIO_PIN = 21

class NeoPixelDaemon:
    def __init__(self):
        self.BRIGHTNESS = 10

        self.strip = PixelStrip(LED_COUNT, GPIO_PIN, brightness=self.BRIGHTNESS)
        self.strip.begin()
        self.clear()


        self.blink_thread = None
        self.blink_stop = threading.Event()
        self.client_connected = threading.Event()

        # Starte Knight-Rider Effekt beim Startup
        self.startup_knightrider(color=[255,0,0], speed=0.15)

    # Hilfsfunktion: physikalische Reihenfolge spiegeln
    def hw_index(self, i):
        return self.strip.numPixels() - 1 - i

    # Einfach alles füllen
    def fill(self, r, g, b):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(self.hw_index(i), Color(r, g, b))
        self.strip.show()

    def set_brightness(self, value):
        self.strip.setBrightness(max(0, min(255, value)))
        self.strip.show()

    def clear(self):
        self.fill(0, 0, 0)

    # Startup-Knight-Rider
    def startup_knightrider(self, color=[255,0,0], speed=0.1):
        def effect():
            n = self.strip.numPixels()
            pos = 0
            direction = 1
            while not self.client_connected.is_set():
                self.clear()
                self.strip.setPixelColor(self.hw_index(pos), Color(*color))
                self.strip.show()
                time.sleep(speed)
                pos += direction
                if pos == n-1 or pos == 0:
                    direction *= -1
        threading.Thread(target=effect, daemon=True).start()

    # -------- Batterieanzeige --------
    def battery(self, percent, color=None, gradient=None, steps=5, delay=0.05, brightness=None):
        if brightness is not None:
            self.set_brightness(brightness)

        n = self.strip.numPixels()

        # LED-Anzahl korrekt runden
        leds_on = round((percent / 100) * n)
        leds_on = max(0, min(n, leds_on))

        # Stoppe vorheriges Blinken
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_stop.set()
            self.blink_thread.join()
        self.blink_stop.clear()

        # Farben berechnen
        all_colors = []
        if gradient:
            for i in range(n):
                pos = i / max(n-1,1)
                seg_len = 1 / (len(gradient)-1)
                seg_index = min(int(pos/seg_len), len(gradient)-2)
                t = (pos - seg_index*seg_len)/seg_len
                r1,g1,b1 = gradient[seg_index]
                r2,g2,b2 = gradient[seg_index+1]
                r = int(r1 + (r2-r1)*t)
                g = int(g1 + (g2-g1)*t)
                b = int(b1 + (b2-b1)*t)
                all_colors.append([r,g,b])
        elif color:
            all_colors = [color]*n
        else:
            default_gradient = [[255,0,0],[255,255,0],[0,255,0]]
            for i in range(n):
                pos = i / max(n-1,1)
                seg_len = 1 / (len(default_gradient)-1)
                seg_index = min(int(pos/seg_len), len(default_gradient)-2)
                t = (pos - seg_index*seg_len)/seg_len
                r1,g1,b1 = default_gradient[seg_index]
                r2,g2,b2 = default_gradient[seg_index+1]
                r = int(r1 + (r2-r1)*t)
                g = int(g1 + (g2-g1)*t)
                b = int(b1 + (b2-b1)*t)
                all_colors.append([r,g,b])

        # Unter 5% → letzte LED blinkt in normaler Farbe
        if leds_on <= 1:
            blink_color = all_colors[0]
            def blink():
                while not self.blink_stop.is_set():
                    self.clear()
                    self.strip.setPixelColor(self.hw_index(0), Color(*blink_color))
                    self.strip.show()
                    time.sleep(0.5)
                    self.strip.setPixelColor(self.hw_index(0), Color(0,0,0))
                    self.strip.show()
                    time.sleep(0.5)
            self.blink_thread = threading.Thread(target=blink, daemon=True)
            self.blink_thread.start()
            return

        # Normale Anzeige
        self.clear()

        current_colors = [self.strip.getPixelColor(i) for i in range(n)]

        for step in range(steps):
            for i in range(n):
                if i < leds_on:
                    r_target, g_target, b_target = all_colors[i]
                else:
                    r_target, g_target, b_target = 0, 0, 0

                c = current_colors[i]
                r_current = (c >> 16) & 0xFF
                g_current = (c >> 8) & 0xFF
                b_current = c & 0xFF

                r_new = int(r_current + (r_target - r_current) * (step + 1) / steps)
                g_new = int(g_current + (g_target - g_current) * (step + 1) / steps)
                b_new = int(b_current + (b_target - b_current) * (step + 1) / steps)

                self.strip.setPixelColor(
                    self.hw_index(i),
                    Color(r_new, g_new, b_new)
                )

            self.strip.show()
            time.sleep(delay)

def cleanup(signum=None, frame=None):
    try:
        daemon.clear()
    except:
        pass
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    exit(0)


daemon = NeoPixelDaemon()
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
os.chmod(SOCKET_PATH, 0o666)
server.listen(1)

print("NeoPixel daemon running (Knight Rider Red until first client)")

while True:
    conn, _ = server.accept()
    if not daemon.client_connected.is_set():
        daemon.client_connected.set()
    data = conn.recv(2048).decode()
    conn.close()
    try:
        cmd = json.loads(data)
        if cmd["cmd"]=="battery":
            percent = cmd.get("percent",100)
            color = cmd.get("color",None)
            gradient = cmd.get("gradient",None)
            steps = cmd.get("steps",5)
            delay = cmd.get("delay",0.05)
            daemon.battery(percent,color,gradient,steps,delay)
        elif cmd["cmd"]=="fill":
            daemon.fill(cmd["r"],cmd["g"],cmd["b"])
        elif cmd["cmd"]=="brightness":
            daemon.set_brightness(cmd["value"])
        elif cmd["cmd"]=="clear":
            daemon.clear()
    except:
        pass
