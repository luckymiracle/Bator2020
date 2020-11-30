/*
  Incubator
  ctrl + alt + s or Export Compiled Binary
  avrdude -c gpio -p m328p -U flash:w:incubator.ino.standard.hex
*/

#include <Adafruit_Sensor.h>
#include <SPI.h>
#include <Adafruit_MAX31855.h>
#include <math.h>
#include <Servo.h>
#include "Adafruit_HTU21DF.h"

#define VBATTPIN A0

#define HOTFANPIN 9
#define COLDFANPIN 8

#define ROTSERVOPIN 6
#define PELTIERPIN 5
#define CLKPIN 4
#define D0PIN 3
#define CSPIN 2

#define ONEANGLETIME 60 // Turn one degree every 60 seconds

Adafruit_MAX31855 thermocouple(CLKPIN, CSPIN, D0PIN);

Adafruit_HTU21DF htu = Adafruit_HTU21DF();

Servo rot_servo;

String inputString = "";

uint32_t dhtdelayMS;

unsigned int cold_duty_cycle = 255;
unsigned int rot_servo_angle = 3;
unsigned int rotation_int_count = 0;

float ktype_therm_limit = 37.5;
float rh_limit = 41;
float k_type_therm;
float htu_temp;
float htu_rh;
float amb_temp;

bool incubator_on = false;
bool debug_on = false;
bool rotation_on = true;
bool rotate_right = false;


void setup() {
  pinMode(PELTIERPIN, OUTPUT);
  pinMode(COLDFANPIN, OUTPUT);
  pinMode(HOTFANPIN, OUTPUT);
  
  Serial.begin(115200);
  inputString.reserve(10);
  
  if (!htu.begin()) {
    Serial.println("Couldn't find HTU21DF sensor!");
  }
  
  dhtdelayMS = 500;

}

void loop() {
  
  delay(dhtdelayMS);

  if(incubator_on) {
    incubator(incubator_on);  
  }
}

void debug_menu(void){    
  Serial.println("------------------------------------");
  Serial.println("Incubator commands:");
  Serial.println(" 01 Enable cold fan");
  Serial.println(" 00 Disable cold fan");
  Serial.println(" 11 Enable hot fan");
  Serial.println(" 10 Disable hot fan");
  Serial.println(" 21 Enable Peltier transducer");
  Serial.println(" 20 Disable Peltier transducer");
  Serial.println(" 31 Enable debug");
  Serial.println(" 30 Disable debug");
  Serial.println(" 32x Modify temperature limit by x");
  Serial.println(" 33x Modify RH limit by x");
  Serial.println(" 34 Peak RH and temperature limit");
  Serial.println(" 41 Enable incubator");
  Serial.println(" 40 Disable incubator");
  Serial.println(" 50 Detach rotation servo");
  Serial.println(" 51 Attach rotation servo");
  Serial.println(" 52 Rotation servo at 3 degrees");
  Serial.println(" 53 Rotation servo at 180 degrees");
  Serial.println(" 54x Rotation servo at x degrees");
  Serial.println(" 55 Disable rotations");
  Serial.println(" 56 Enable rotations");
  Serial.println(" 6 Get incubator status data");
  Serial.println("------------------------------------");
}

void incubator(bool on){
    
  if( on == true){
    k_type_therm = thermocouple.readCelsius();
    amb_temp = thermocouple.readInternal();

    htu_temp = htu.readTemperature();
    htu_rh = htu.readHumidity();
    
    if(k_type_therm >= ktype_therm_limit || htu_temp >= ktype_therm_limit){ // 37.5C, 99.5 F
      digitalWrite(PELTIERPIN, LOW);
    } else {
      digitalWrite(PELTIERPIN, HIGH);
    }

    if(rotation_on){
      if(rotate_right and rotation_int_count >= ONEANGLETIME){
        rotation_int_count = 0;
        rot_servo_angle += 1;
        if(rot_servo_angle >= 180){
          rotate_right = false;
        }
        rot_servo.write(rot_servo_angle);
      } else if(rotation_int_count >= ONEANGLETIME) {
        rotation_int_count = 0;
        rot_servo_angle -= 1;
        if(rot_servo_angle <= 3){
          rotate_right = true;
        }
        rot_servo.write(rot_servo_angle);
      }
  
      rotation_int_count += 1;
    }
    
    if (htu_rh <= rh_limit || k_type_therm >= (ktype_therm_limit+1)){
      digitalWrite(COLDFANPIN, HIGH);
    } else {
      digitalWrite(COLDFANPIN, LOW);
    }

    if(debug_on == true){
      Serial.println(" IT C  RH %   KT C   Am C");
      Serial.print(htu_temp);
      Serial.print("  ");
      Serial.print(htu_rh);
      Serial.print("  ");
      Serial.print(k_type_therm);
      Serial.print("  ");
      Serial.println(amb_temp);
      Serial.println();
    }
  }
  
}

void serialEvent(){
  String cmd, subcmd;
  int cmd_i, subcmd_i, subcmd_j;
  
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
  }

  if(inputString.length() >= 3){
    cmd = inputString.substring(0, 1);
    cmd_i = cmd.toInt();
    subcmd = inputString.substring(1, 2);
    subcmd_i = subcmd.toInt();
    if(inputString.length() >= 3){
      subcmd = inputString.substring(2, inputString.length());
      subcmd_j = subcmd.toFloat();
      // Serial.println(subcmd);
      // Serial.println(subcmd_j);
    } else {
      subcmd_j = 90;
    }
    
    switch(cmd_i){
      case 0:
        if(subcmd_i == 1){
          digitalWrite(COLDFANPIN, HIGH);
        } else {
          digitalWrite(COLDFANPIN, LOW);
        }
        break;

      case 1:
        if(subcmd_i == 1){
          digitalWrite(HOTFANPIN, HIGH);
        } else {
          digitalWrite(HOTFANPIN, LOW);
        }
        break;
     
      case 2:
        if(subcmd_i == 1){
          digitalWrite(PELTIERPIN, HIGH);
        } else {
          digitalWrite(PELTIERPIN, LOW);
        }
        break;

      case 3:
        if(subcmd_i == 1){
          debug_on = true;
        } else if(subcmd_i == 0) {
          debug_on = false;
        } else if(subcmd_i == 2) {
          ktype_therm_limit = subcmd_j;          
        } else if(subcmd_i == 3) {
          rh_limit = subcmd_j;
        } else if(subcmd_i == 4) {
          Serial.print("rh_limit = ");
          Serial.print(rh_limit);
          Serial.print(" ktype_therm_limit = ");
          Serial.println(ktype_therm_limit);
        }
        break;

      case 4:
        if(subcmd_i == 1){
          incubator_on = true;
          digitalWrite(HOTFANPIN, HIGH);
          rot_servo.attach(ROTSERVOPIN);
          rot_servo_angle = 90;
          rotate_right = true;
          Serial.println("Turning on Incubator");
        } else {
          Serial.println("Turning off Incubator");
          digitalWrite(HOTFANPIN, LOW);
          digitalWrite(COLDFANPIN, LOW);
          digitalWrite(PELTIERPIN, LOW);
          incubator_on = false;
        }
        break;

      case 5:
        if(subcmd_i == 0){
          rot_servo.detach();
        } else if(subcmd_i == 1){
          rot_servo.attach(ROTSERVOPIN);
        } else if(subcmd_i == 2){
          rot_servo.write(3);
        } else if(subcmd_i == 3){
          rot_servo.write(180);
        } else if(subcmd_i == 4){
          rot_servo.write(subcmd_j);
        } else if(subcmd_i == 5){
          rotation_on = false;
          rot_servo.detach();
        } else if(subcmd_i == 6){
          rotation_on = true;
          rot_servo.attach(ROTSERVOPIN);
        }
        break;

      case 6:
        if(incubator_on == false){
          k_type_therm = thermocouple.readCelsius();
          amb_temp = thermocouple.readInternal();
          htu_temp = htu.readTemperature();
          htu_rh = htu.readHumidity();          
        }
        
        Serial.print(htu_temp);
        Serial.print(" ");
        Serial.print(htu_rh);
        Serial.print(" ");
        Serial.print(k_type_therm);
        Serial.print(" ");
        Serial.print(amb_temp);
        Serial.print(" ");
        if(incubator_on == true){
          Serial.println(1);
        }else{
          Serial.println(0);
        }
        break;

      default:
        Serial.println("Unsupported command");
        debug_menu();
    }
    
  } else {
    Serial.println("Short string length");
  }

  if(debug_on == true){
    Serial.println("serialEvent");
    Serial.print(inputString);
  }
  inputString = "";
}
