#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <Preferences.h>

#define LED_PIN     22
#define BAUDRATE    115200
#define DEBUG 1  // 1 = Debug aktiv, 0 = Debug aus


struct RGB {
  uint8_t r;
  uint8_t g;
  uint8_t b;
};

#define RED     RGB{255, 0, 0}
#define GREEN   RGB{0, 255, 0}
#define BLUE    RGB{0, 0, 255}
#define YELLOW  RGB{255,255,0}
#define ORANGE RGB{255, 128, 0}
#define WHITE   RGB{255, 255, 255}
#define BLACK   RGB{0, 0, 0}
#define TURQUOISE RGB{0, 255, 255}   // 255 Grün + 255 Blau
#define PURPLE    RGB{255, 0, 255}   // 255 Rot  + 255 Blau


RGB colorFromName(const char* name) {
  if (!name) return WHITE;

  if (!strcasecmp(name, "RED"))   return RED;
  if (!strcasecmp(name, "GREEN")) return GREEN;
  if (!strcasecmp(name, "BLUE"))  return BLUE;
  if (!strcasecmp(name, "WHITE")) return WHITE;
  if (!strcasecmp(name, "ORANGE")) return ORANGE;
  if (!strcasecmp(name, "BLACK")) return BLACK;
  if (!strcasecmp(name, "YELLOW")) return YELLOW;
  if (!strcasecmp(name, "PURPLE")) return PURPLE;
  if (!strcasecmp(name, "TURQUOISE") || !strcasecmp(name, "CYAN")) return TURQUOISE;

  // unbekannt → default
  return WHITE;
}


RGB parseColor(JsonVariant v) {
  if (v.is<JsonArray>()) {
    JsonArray a = v.as<JsonArray>();
    if (a.size() == 3) {
      return RGB{
        (uint8_t)a[0].as<int>(),
        (uint8_t)a[1].as<int>(),
        (uint8_t)a[2].as<int>()
      };
    }
  }

  if (v.is<const char*>()) {
    return colorFromName(v.as<const char*>());
  }

  return WHITE;
}




// Default Gradient: rot → gelb → grün
const uint8_t DEFAULT_GRADIENT[][3] = {
  {255, 0, 0},
  {255, 255, 0},
  {0, 255, 0}
};
const int DEFAULT_GRADIENT_LEN = 3;

uint16_t LED_COUNT_RUNTIME;

// Preferences
Preferences prefs;
uint16_t loadLedCount() {
  prefs.begin("neopixel", true);
  uint16_t count = prefs.getUShort("led_count", 8);
  prefs.end();
  return count;
}

void saveLedCount(uint16_t count) {
  prefs.begin(
  "neopixel", false);
  prefs.putUShort("led_count", count);
  prefs.end();
}

class NeoPixelServer {
  public:
    NeoPixelServer(uint16_t count, uint8_t pin)
      : strip(count, pin, NEO_GRB + NEO_KHZ800),
        led_count(count),
        brightness(5) {}

    void begin() {
    

      // Serial erst verzögert starten
      delay(2000);
      Serial.begin(BAUDRATE);

      unsigned long t0 = millis();

      while (!Serial && millis() - t0 < 1000) delay(10);
      if (DEBUG) Serial.println("DEBUG: Serial bereit, JSON-Befehle möglich");

      if (Serial) {
        strip.begin();
        strip.show();
        startKnightRider(255, 0, 0, 0.15); // Knight-Rider beim Start
      }
      else
      {
        renderBatteryColorRGB(50, RED, BLUE);
        strip.show();
      }
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

      // Knight Rider läuft immer
      if (knightRiderActive && now - knightRiderTimer >= knightRiderSpeed) {
        clear();
        strip.setPixelColor(hw_index(knightRiderPos), knightRiderColor);
        strip.show();
        knightRiderPos += knightRiderDir;
        if (knightRiderPos >= led_count - 1 || knightRiderPos <= 0)
          knightRiderDir *= -1;
        knightRiderTimer = now;
      }

      // Blinken unter 5 % nur wenn JSON-Befehle empfangen
      if (json_client_connected && blink_low && blinkActive && now - lastBlink >= 500) {
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

    // Flag nur bei echtem JSON-Befehl vom Host
    bool json_client_connected = false;

    // Blink
    bool blink_low = true;
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
      if (DEBUG) Serial.println("DEBUG: Knight-Rider Animation gestartet");
    }

    // ---------- Default Gradient ----------
void renderBatteryGradientUnified(int percent, const uint8_t (*gradient)[3] = nullptr, int gradientLen = 0) {
    int leds_on = round((percent / 100.0) * led_count);
    leds_on = constrain(leds_on, 0, led_count);
    float scale = brightness / 255.0;

    // Falls kein Gradient übergeben → Default
    const uint8_t (*grad)[3] = gradient ? gradient : DEFAULT_GRADIENT;
    int gLen = gradient ? gradientLen : DEFAULT_GRADIENT_LEN;

    if (percent < 5 && gLen > 0) {
        int r0 = grad[0][0];
        int g0 = grad[0][1];
        int b0 = grad[0][2];

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

            int r = grad[idx][0] + (grad[idx + 1][0] - grad[idx][0]) * t;
            int g = grad[idx][1] + (grad[idx + 1][1] - grad[idx][1]) * t;
            int b = grad[idx][2] + (grad[idx + 1][2] - grad[idx][2]) * t;

            strip.setPixelColor(hw_index(i), strip.Color(r * scale, g * scale, b * scale));
        } else {
            strip.setPixelColor(hw_index(i), 0);
        }
    }
    strip.show();

    if (DEBUG) {
        Serial.print("DEBUG: Gradient gesetzt, ");
        Serial.print(percent);
        Serial.println("% LEDs");
    }
}



    void renderBatteryColorRGB(int percent, RGB c1, RGB c2 = RGB{0,0,0}) {
      renderBatteryColor(percent, c1.r, c1.g, c1.b, c2.r, c2.g, c2.b);
    }

    // ---------- Solid Color ----------
    void renderBatteryColor(int percent, int r, int g, int b, int r2=0, int g2=0, int b2=0) {
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
          i < leds_on ? strip.Color(r * scale, g * scale, b * scale) : strip.Color(r2 * scale, g2 * scale, b2 * scale) 
        );
      }

      strip.show();

      if (DEBUG) {
        Serial.print("DEBUG: Farbe gesetzt, ");
        Serial.print(percent);
        Serial.print("% LEDs, RGB(");
        Serial.print(r); Serial.print(",");
        Serial.print(g); Serial.print(",");
        Serial.print(b); Serial.println(")");
        Serial.print(b2); Serial.println(")");
        Serial.print(", RGB2(");
        Serial.print(r2); Serial.print(",");
        Serial.print(g2); Serial.print(",");
        Serial.print(b2); Serial.println(")");

      }
    }

    // ---------- Command ----------
    void handleCommand(const String &json) {
      if (DEBUG) {
        Serial.print("DEBUG: Befehl empfangen: ");
        Serial.println(json);
      }

      StaticJsonDocument<512> doc;
      if (deserializeJson(doc, json)) {
        if (DEBUG) Serial.println("DEBUG: JSON konnte nicht geparst werden!");
        uint8_t grad[3][3] = {
          {PURPLE.r, PURPLE.g, PURPLE.b},
          {TURQUOISE.r, TURQUOISE.g, TURQUOISE.b},
          {BLUE.r, BLUE.g, BLUE.b}
        };
        knightRiderActive = false;
        renderBatteryGradientUnified(100, grad, 3);
        return;
      }

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

      // Sobald ein echter JSON-Befehl kommt, stoppt Knight-Rider
      json_client_connected = true;
      knightRiderActive = false;

      if (DEBUG) Serial.println("DEBUG: JSON-Befehl empfangen, Knight-Rider gestoppt");

      int percent = doc["percent"] | 100;
      setBrightness(doc["brightness"] | brightness);

      if (doc.containsKey("blink_low"))
      {
        int blink = doc["blink_low"] | 1;
        blink_low = (blink == 1) ? true : false;
      }
      else
      {
        blink_low = true;
      }

      bool rendercolor2 = false;

     if (doc.containsKey("color2"))
      {
        rendercolor2 = true;
      }

      if (doc.containsKey("gradient")) {
        JsonArray jsonGrad = doc["gradient"].as<JsonArray>();
          int gLen = jsonGrad.size();

          // Erst ein echtes Array erzeugen
          uint8_t grad[gLen][3];
          for (int i = 0; i < gLen; i++) {
              JsonVariant v = jsonGrad[i];
              RGB c = parseColor(v);  // parseColor unterstützt jetzt String oder Array
              grad[i][0] = c.r;
              grad[i][1] = c.g;
              grad[i][2] = c.b;
          }

          // Dann aufrufen
         renderBatteryGradientUnified(percent, grad, gLen);  
      }
      else if (doc.containsKey("color"))
      {
        RGB c1 = parseColor(doc["color"]);
        RGB c2 = BLACK;

        if (rendercolor2 && doc.containsKey("color2")) {
          c2 = parseColor(doc["color2"]);
        }

        renderBatteryColor(
          percent,
          c1.r, c1.g, c1.b,
          c2.r, c2.g, c2.b
        );
      }
      else
      {
        renderBatteryGradientUnified(percent);
      }    
    }
};

// ---------- Global ----------
NeoPixelServer *server;

void setup() {
  LED_COUNT_RUNTIME = loadLedCount();
  server = new NeoPixelServer(LED_COUNT_RUNTIME, LED_PIN);
  server->begin();
}

void loop() {
  server->loop();
  server->update();
}
