#include <LiquidCrystal.h>

const int SETUP_TIME = 500;
const int DELAY_TIME = 1000;

const int rs_pin = 7;
const int en_pin = 8;
const int d4_pin = 9;
const int d5_pin = 10;
const int d6_pin = 11;
const int d7_pin = 12;

LiquidCrystal lcd(rs_pin,en_pin,d4_pin,d5_pin,d6_pin,d7_pin);

void setup() {
  Serial.begin(9600);
  delay(SETUP_TIME);
  lcd.begin(16,2);
}

void loop() {

  // TODO: Fill this out
  // Print to LCD
  lcd.setCursor(0,0);
  lcd.print("Hello World");

  delay(1000);
  lcd.clear();
}
