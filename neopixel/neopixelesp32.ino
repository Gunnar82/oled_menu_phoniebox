#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <Preferences.h>

#define LED_PIN     13
#define BAUDRATE    115200

// Default Gradient: rot → gelb → grün
const uint8_t DEFAULT_GRADIENT[][3] = {
  {255, 0, 0},
  {255, 255, 0},
  {0, 255, 0}
};
const int DEFAULT_GRADIENT_LEN = 3;

uint16_t LED_COUNT_RUNTIME;



//Preferences
Preferences prefs;
uint16_t loadLedCount() {
  prefs.begin("neopixel", true);
  uint16_t count = prefs.getUShort("led_count", 8);
  prefs.end();
  return count;
}

void saveLedCount(uint16_t count) {
  prefs.begin("neopixel", false);
  prefs.putUShort("led_count", count);
  prefs.end();
}


class NeoPixelServer {
  public:
    NeoPixelServer(uint16_t count, uint8_t pin)
      : strip(count, pin, NEO_GRB + NEO_KHZ800),
        led_count(count),
        brightness(20) {}

    void begin() {
      strip.begin();
      strip.show();
      startKnightRider(255, 0, 0, 0.15);
    }

    void loop() {
      while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
          handleCommand(buffer);
          buffer = "";
        } else {
          buffer += c;
        }
      }
    }

    void update() {
      unsigned long now = millis();

      // Knight Rider beim Start
      if (!client_connected && knightRiderActive && now - knightRiderTimer >= knightRiderSpeed) {
        clear();
        strip.setPixelColor(hw_index(knightRiderPos), knightRiderColor);
        strip.show();
        knightRiderPos += knightRiderDir;
        if (knightRiderPos >= led_count - 1 || knightRiderPos <= 0)
          knightRiderDir *= -1;
        knightRiderTimer = now;
      }

      // Blinken unter 5 %
      if (client_connected && blinkActive && now - lastBlink >= 500) {
        blinkState = !blinkState;
        strip.setPixelColor(hw_index(0), blinkState ? blinkColor : 0);
        strip.show();
        lastBlink = now;
      }
    }

  private:
    Adafruit_NeoPixel strip;
    uint16_t led_count;
    int brightness;
    String buffer;

    bool client_connected = false;

    // Blink
    bool blinkActive = false;
    bool blinkState = false;
    unsigned long lastBlink = 0;
    uint32_t blinkColor = 0;

    // Knight Rider
    bool knightRiderActive = false;
    uint32_t knightRiderColor;
    unsigned long knightRiderSpeed;
    unsigned long knightRiderTimer = 0;
    int knightRiderPos = 0;
    int knightRiderDir = 1;

    // ---------- Utils ----------
    uint16_t hw_index(uint16_t i) {
      return led_count - 1 - i;
    }

    void clear() {
      for (int i = 0; i < led_count; i++)
        strip.setPixelColor(i, 0);
      strip.show();
    }

    void setBrightness(int b) {
      brightness = constrain(b, 0, 255);
    }

    void startKnightRider(uint8_t r, uint8_t g, uint8_t b, float speed) {
      float scale = brightness / 255.0;
      knightRiderColor = strip.Color(r * scale, g * scale, b * scale);
      knightRiderSpeed = speed * 1000;
      knightRiderActive = true;
    }

    // ---------- Default Gradient ----------
    void renderBatteryDefaultGradient(int percent) {
      int leds_on = round((percent / 100.0) * led_count);
      leds_on = constrain(leds_on, 0, led_count);
      float scale = brightness / 255.0;

      if (percent < 5) {
        blinkActive = true;
        blinkColor = strip.Color(
          DEFAULT_GRADIENT[0][0] * scale,
          DEFAULT_GRADIENT[0][1] * scale,
          DEFAULT_GRADIENT[0][2] * scale
        );
        lastBlink = millis();
        clear();
        return;
      }
      blinkActive = false;

      for (int i = 0; i < led_count; i++) {
        if (i < leds_on) {
          float pos = (float)i / max(led_count - 1, 1);
          float segLen = 1.0 / (DEFAULT_GRADIENT_LEN - 1);
          int idx = min((int)(pos / segLen), DEFAULT_GRADIENT_LEN - 2);
          float t = (pos - idx * segLen) / segLen;

          int r = DEFAULT_GRADIENT[idx][0] +
                  (DEFAULT_GRADIENT[idx + 1][0] - DEFAULT_GRADIENT[idx][0]) * t;
          int g = DEFAULT_GRADIENT[idx][1] +
                  (DEFAULT_GRADIENT[idx + 1][1] - DEFAULT_GRADIENT[idx][1]) * t;
          int b = DEFAULT_GRADIENT[idx][2] +
                  (DEFAULT_GRADIENT[idx + 1][2] - DEFAULT_GRADIENT[idx][2]) * t;

          strip.setPixelColor(hw_index(i), strip.Color(r * scale, g * scale, b * scale));
        } else {
          strip.setPixelColor(hw_index(i), 0);
        }
      }
      strip.show();
    }

    // ---------- Gradient aus JSON ----------
    void renderBatteryGradient(int percent, JsonArray gradient) {
      int leds_on = round((percent / 100.0) * led_count);
      leds_on = constrain(leds_on, 0, led_count);
      float scale = brightness / 255.0;
      int gLen = gradient.size();

      // <5 % → blink letzte LED in ihrer normalen Farbe
      if (percent < 5 && gLen > 0) {
        JsonArray c0 = gradient[0];
        int r0 = c0[0].as<int>();
        int g0 = c0[1].as<int>();
        int b0 = c0[2].as<int>();

        blinkActive = true;
        blinkColor = strip.Color(r0 * scale, g0 * scale, b0 * scale);
        lastBlink = millis();
        clear();
        return;
      }
      blinkActive = false;

      for (int i = 0; i < led_count; i++) {
        if (i < leds_on) {
          float pos = (float)i / max(led_count - 1, 1);
          float segLen = 1.0 / (gLen - 1);
          int idx = min((int)(pos / segLen), gLen - 2);
          float t = (pos - idx * segLen) / segLen;

          JsonArray c1 = gradient[idx];
          JsonArray c2 = gradient[idx + 1];

          int r1 = c1[0].as<int>();
          int g1 = c1[1].as<int>();
          int b1 = c1[2].as<int>();
          int r2 = c2[0].as<int>();
          int g2 = c2[1].as<int>();
          int b2 = c2[2].as<int>();

          int r = r1 + (r2 - r1) * t;
          int g = g1 + (g2 - g1) * t;
          int b = b1 + (b2 - b1) * t;

          strip.setPixelColor(hw_index(i), strip.Color(r * scale, g * scale, b * scale));
        } else {
          strip.setPixelColor(hw_index(i), 0);
        }
      }
      strip.show();
    }

    // ---------- Solid Color ----------
    void renderBatteryColor(int percent, int r, int g, int b) {
      int leds_on = round((percent / 100.0) * led_count);
      leds_on = constrain(leds_on, 0, led_count);
      float scale = brightness / 255.0;

      if (percent < 5) {
        blinkActive = true;
        blinkColor = strip.Color(r * scale, g * scale, b * scale);
        lastBlink = millis();
        clear();
        return;
      }
      blinkActive = false;

      for (int i = 0; i < led_count; i++) {
        strip.setPixelColor(
          hw_index(i),
          i < leds_on ? strip.Color(r * scale, g * scale, b * scale) : 0
        );
      }
      strip.show();
    }

    // ---------- Command ----------
    void handleCommand(const String &json) {
      StaticJsonDocument<512> doc;
      if (deserializeJson(doc, json)) return;
      if (strcmp(doc["cmd"] | "", "config") == 0) {
        if (doc.containsKey("led")) {
          uint16_t newCount = doc["led"].as<int>();

          if (newCount >= 1 && newCount <= 300) {
            saveLedCount(newCount);
            Serial.println("{\"status\":\"reboot\"}");
            delay(100);
            ESP.restart();
          }
        }
        return;
      }
      if (strcmp(doc["cmd"] | "", "battery") != 0) return;

      client_connected = true;
      knightRiderActive = false;

      int percent = doc["percent"] | 100;
      setBrightness(doc["brightness"] | brightness);

      if (doc.containsKey("gradient")) {
        renderBatteryGradient(percent, doc["gradient"].as<JsonArray>());
      }
      else if (doc.containsKey("color")) {
        JsonArray c = doc["color"];
        renderBatteryColor(percent, c[0].as<int>(), c[1].as<int>(), c[2].as<int>());
      }
      else {
        renderBatteryDefaultGradient(percent);
      }
    }
};

// ---------- Global ----------
NeoPixelServer *server;

void setup() {
  Serial.begin(BAUDRATE);

  LED_COUNT_RUNTIME = loadLedCount();

  server = new NeoPixelServer(LED_COUNT_RUNTIME, LED_PIN);

  server->begin();
}

void loop() {
  server->loop();
  server->update();
}
