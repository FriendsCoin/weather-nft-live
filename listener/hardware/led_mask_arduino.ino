/*
 * NESCIENCE - LED Mask Control
 *
 * For WS2812B LED strip (NeoPixel compatible)
 * Connected to ESP32 or Arduino
 *
 * Receives OSC commands via Serial from Python/TouchDesigner
 *
 * Hardware:
 * - ESP32 or Arduino Nano/Uno
 * - WS2812B LED strip (60-144 LEDs)
 * - 5V power supply (separate from microcontroller)
 * - 470Ω resistor on data line
 * - 1000μF capacitor on power
 *
 * Wiring:
 * - LED Data → GPIO 5 (or pin 6 on Arduino)
 * - LED 5V → External 5V supply
 * - LED GND → Common ground
 *
 * Protocol (via Serial at 115200 baud):
 * Format: "brightness,breathing_rate\n"
 * Example: "128,50\n" = 50% brightness, slow breathing
 *
 * NOT flashing colors. NOT gamification.
 * Subtle, contemplative presence.
 */

#include <FastLED.h>

// LED Configuration
#define LED_PIN     5        // GPIO pin (ESP32) or 6 (Arduino)
#define NUM_LEDS    60       // Number of LEDs in your strip
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];

// State variables
uint8_t global_brightness = 64;  // 0-255 (default 25%)
uint8_t breathing_speed = 50;    // 0-255 (slower = more contemplative)
float breathing_phase = 0.0;

// Breathing effect
unsigned long last_update = 0;
const int UPDATE_INTERVAL = 20;  // ms (50 FPS)

void setup() {
  // Serial communication
  Serial.begin(115200);

  // Initialize LEDs
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(global_brightness);

  // Start with dim warm white
  fill_solid(leds, NUM_LEDS, CRGB(255, 200, 150));
  FastLED.show();

  Serial.println("NESCIENCE LED Mask Ready");
}

void loop() {
  // Check for serial commands
  if (Serial.available()) {
    parseSerialCommand();
  }

  // Update breathing effect
  unsigned long now = millis();
  if (now - last_update > UPDATE_INTERVAL) {
    last_update = now;
    updateBreathing();
  }
}

void parseSerialCommand() {
  String command = Serial.readStringUntil('\n');
  command.trim();

  // Parse format: "brightness,breathing_rate"
  int comma_index = command.indexOf(',');
  if (comma_index > 0) {
    String brightness_str = command.substring(0, comma_index);
    String breathing_str = command.substring(comma_index + 1);

    global_brightness = constrain(brightness_str.toInt(), 0, 255);
    breathing_speed = constrain(breathing_str.toInt(), 0, 255);

    // Debug
    Serial.print("Brightness: ");
    Serial.print(global_brightness);
    Serial.print(", Breathing: ");
    Serial.println(breathing_speed);
  }
}

void updateBreathing() {
  // Breathing phase (0 to 2*PI)
  float speed_factor = map(breathing_speed, 0, 255, 5, 100) / 1000.0;
  breathing_phase += speed_factor;
  if (breathing_phase > TWO_PI) {
    breathing_phase -= TWO_PI;
  }

  // Breathing curve (smooth sine wave)
  float breathing_value = (sin(breathing_phase) + 1.0) / 2.0;  // 0-1

  // Map to brightness (keep minimum at 20% to stay visible)
  uint8_t breath_brightness = map(breathing_value * 100, 0, 100,
                                  global_brightness * 0.2,
                                  global_brightness);

  // Apply to LEDs
  FastLED.setBrightness(breath_brightness);

  // Monochrome warm white (contemplative, not colorful)
  // Very subtle warm tone (not bright white)
  fill_solid(leds, NUM_LEDS, CRGB(255, 220, 180));

  FastLED.show();
}

/*
 * Alternative Visual Modes
 * Uncomment to use different aesthetics
 */

// Mode 1: Gradient (subtle variation across strip)
void modeGradient() {
  for (int i = 0; i < NUM_LEDS; i++) {
    float position = (float)i / NUM_LEDS;
    uint8_t value = 150 + sin(position * PI) * 100;
    leds[i] = CRGB(value, value * 0.9, value * 0.8);
  }
  FastLED.show();
}

// Mode 2: Pulse (single pulse traveling)
void modePulse() {
  static float pulse_position = 0.0;
  pulse_position += 0.1;
  if (pulse_position > NUM_LEDS) pulse_position = 0;

  fadeToBlackBy(leds, NUM_LEDS, 20);  // Trail
  int pos = (int)pulse_position;
  leds[pos] = CRGB(255, 220, 180);

  FastLED.show();
}

// Mode 3: Meditation Depth Visualization
// Call this from Python with depth value 0-1
void setMeditationDepth(float depth) {
  // Deeper meditation = slower, dimmer, calmer
  breathing_speed = map(depth * 100, 0, 100, 100, 20);  // Slower when deep
  global_brightness = map(depth * 100, 0, 100, 100, 40); // Dimmer when deep
}
