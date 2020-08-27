#include <LiquidCrystal.h>

// Meta vars
const int SETUP_TIME = 500;


// Module pinouts
const int rs_pin = 7;
const int en_pin = 8;
const int d4_pin = 9;
const int d5_pin = 10;
const int d6_pin = 11;
const int d7_pin = 12;
const int button_pin = 4;

// Strings for parsing and display
String cpu_string = "RDY"; // Default to RDY for visual confirmation system is working
String gpu_string;
String time_string;
String in_string;

// Page tracking for "menu" expansion
int cur_page = 0;
const int min_page = 0;
const int max_page = 1;

// Declare LiquidCrystal instance
LiquidCrystal lcd(rs_pin,en_pin,d4_pin,d5_pin,d6_pin,d7_pin);

void setup() {

  // Pin modes
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(button_pin,INPUT_PULLUP);

  // Begin serial, delay by SETUP_TIME, begin LCD
  Serial.begin(9600);
  delay(SETUP_TIME);
  lcd.begin(16,2);
}

void loop() {
  // Check if button is pressed, increment current "menu" page accordingly
  if (digitalRead(button_pin) == LOW){
    digitalWrite(LED_BUILTIN,HIGH);
    cur_page++;
    delay(300); // Allow button debounce
  } else{
    digitalWrite(LED_BUILTIN,LOW);
  }

  // Wrap-around current page to the beginning to keep logic within defined pages
  if (cur_page > max_page){
    cur_page = min_page;
  }

  // While there is serial data in the rx buffer
  if (Serial.available() > 0){
    // Turn on board LED to indicate RX
    digitalWrite(LED_BUILTIN,HIGH);
    
    // Read the string from the buffer
    in_string = Serial.readString();

    // Split the string and assign it to the appropriate display vars
    cpu_string = getValue(in_string,';',0);
    gpu_string = getValue(in_string,';',1);
    time_string = getValue(in_string,';',2);

    // Send OK back to python script
    Serial.print("OK\n");
  }

  // While not receiving, keep the screen updated
  lcd.clear();
  lcd.setCursor(0,0);

  // Temps Page
  if (cur_page == 0){
    lcd.print(cpu_string);
    lcd.setCursor(0,1);
    lcd.print(gpu_string);
  } 
  else if (cur_page == 1){ // Clock page
    lcd.print(time_string);
  }
  delay(375); // Arbitrary delay to prevent LCD flicker
}

// Pulled from StackOverflow because I loathe C and don't want to have to innovate such a basic function
String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
