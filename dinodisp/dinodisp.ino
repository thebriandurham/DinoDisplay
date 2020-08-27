#include <LiquidCrystal.h>

const int SETUP_TIME = 500;
const int DELAY_TIME = 1000;

const int rs_pin = 7;
const int en_pin = 8;
const int d4_pin = 9;
const int d5_pin = 10;
const int d6_pin = 11;
const int d7_pin = 12;

// LEARNING VARS TODO: DELETE
String cpu_string;
String gpu_string;
const String valid_response = "OK\n";
const String invalid_response = "ERR\n";

char test_char = 'A';

LiquidCrystal lcd(rs_pin,en_pin,d4_pin,d5_pin,d6_pin,d7_pin);

void setup() {

  // DEBUG Functioning Indicator Use
  pinMode(LED_BUILTIN, OUTPUT);
  
  Serial.begin(9600);
  delay(SETUP_TIME);
  lcd.begin(16,2);
}

void loop() {
    
//  while( Serial.available() == 0){
//    // DEBUG Functioning Indicator
//    // Blink while waiting for serial input!
//    digitalWrite(LED_BUILTIN,HIGH);
//    delay(500);
//    digitalWrite(LED_BUILTIN,LOW);
//    delay(500);
//  }

  if (Serial.available() > 0){
    char inByte = Serial.read();
    lcd.clear();
    lcd.print("RCV");
    Serial.print("OK");
  }

  lcd.setCursor(0,0);
  lcd.clear();
  lcd.print("NO RCV");

  delay(100);

 // cpu_string = Serial.readString();
  //lcd.setCursor(0,0);
 // lcd.print(cpu_string);
    // Print to LCD
   // lcd.setCursor(0,1);
    //lcd.print(gpu_string);
}
