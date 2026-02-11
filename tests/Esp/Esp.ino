#include <WiFi.h>
#include <ModbusIP_ESP8266.h>
#include <Arduino.h>

#define SSID ""
#define PASSWORD ""

#define Pin1 35
#define Pin2 27
#define Pin3 26
#define Pin4 25
#define Pin5 16
#define Pin6 4
#define Pin7 2

#define Atuador1 23
#define Atuador2 22
#define Atuador3 21
#define Atuador4 19
#define Atuador5 18
#define Atuador6 17
#define Atuador7 5

#define OFS_Pin1 300
#define OFS_Pin2 301
#define OFS_Pin3 302
#define OFS_Pin4 303
#define OFS_Pin5 304
#define OFS_Pin6 305
#define OFS_Pin7 306


#define OFS_Flag 400

#define OFS_Atuador1 500
#define OFS_Atuador2 501
#define OFS_Atuador3 502
#define OFS_Atuador4 503
#define OFS_Atuador5 504
#define OFS_Atuador6 505
#define OFS_Atuador7 506

IPAddress local_IP(XXXXXXXXXX);
IPAddress gateway(XXXXXXXXXX);    
IPAddress subnet(XXXXXXXXXX);

ModbusIP mb;

struct Sensor {
  int pin;
  int reg;
  int anterior;
  volatile bool changed;
};

volatile Sensor s1 = {Pin1, OFS_Pin1, -1, false};
volatile Sensor s2 = {Pin2, OFS_Pin2, -1, false};
volatile Sensor s3 = {Pin3, OFS_Pin3, -1, false};
volatile Sensor s4 = {Pin4, OFS_Pin4, -1, false};
volatile Sensor s5 = {Pin5, OFS_Pin5, -1, false};
volatile Sensor s6 = {Pin6, OFS_Pin6, -1, false};
volatile Sensor s7 = {Pin7, OFS_Pin7, -1, false};

void IRAM_ATTR isr1() { s1.changed = true; }
void IRAM_ATTR isr2() { s2.changed = true; }
void IRAM_ATTR isr3() { s3.changed = true; }
void IRAM_ATTR isr4() { s4.changed = true; }
void IRAM_ATTR isr5() { s5.changed = true; }
void IRAM_ATTR isr6() { s6.changed = true; }
void IRAM_ATTR isr7() { s7.changed = true; }

void SetupWiFi() {
  
  WiFi.config(local_IP, gateway, subnet);

  WiFi.begin(SSID, PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
  }

}

void setup() {
  
  pinMode(s1.pin, INPUT);
  pinMode(s2.pin, INPUT);
  pinMode(s3.pin, INPUT);
  pinMode(s4.pin, INPUT);
  pinMode(s5.pin, INPUT);
  pinMode(s6.pin, INPUT);
  pinMode(s7.pin, INPUT);
  
  pinMode(Atuador1, OUTPUT);
  pinMode(Atuador2, OUTPUT);
  pinMode(Atuador3, OUTPUT);
  pinMode(Atuador4, OUTPUT);
  pinMode(Atuador5, OUTPUT);
  pinMode(Atuador6, OUTPUT);
  pinMode(Atuador7, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(s1.pin), isr1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(s2.pin), isr2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(s3.pin), isr3, CHANGE);
  attachInterrupt(digitalPinToInterrupt(s4.pin), isr4, CHANGE);
  attachInterrupt(digitalPinToInterrupt(s5.pin), isr5, CHANGE);
  attachInterrupt(digitalPinToInterrupt(s6.pin), isr6, CHANGE);
  attachInterrupt(digitalPinToInterrupt(s7.pin), isr7, CHANGE);

  SetupWiFi();
  mb.server(8009);

  mb.addIreg(OFS_Pin1);
  mb.addIreg(OFS_Pin2);
  mb.addIreg(OFS_Pin3);
  mb.addIreg(OFS_Pin4);
  mb.addIreg(OFS_Pin5);
  mb.addIreg(OFS_Pin6);
  mb.addIreg(OFS_Pin7);
  mb.addHreg(OFS_Flag, 0);
  mb.addHreg(OFS_Atuador1, 0);
  mb.addHreg(OFS_Atuador2, 0);
  mb.addHreg(OFS_Atuador3, 0);
  mb.addHreg(OFS_Atuador4, 0);
  mb.addHreg(OFS_Atuador5, 0);
  mb.addHreg(OFS_Atuador6, 0);
  mb.addHreg(OFS_Atuador7, 0);

  mb.Ireg(OFS_Pin1, digitalRead(s1.pin));
  mb.Ireg(OFS_Pin2, digitalRead(s2.pin));
  mb.Ireg(OFS_Pin3, digitalRead(s3.pin));
  mb.Ireg(OFS_Pin4, digitalRead(s4.pin));
  mb.Ireg(OFS_Pin5, digitalRead(s5.pin));
  mb.Ireg(OFS_Pin6, digitalRead(s6.pin));
  mb.Ireg(OFS_Pin7, digitalRead(s7.pin));

  s1.anterior = digitalRead(s1.pin);
  s2.anterior = digitalRead(s2.pin);
  s3.anterior = digitalRead(s3.pin);
  s4.anterior = digitalRead(s4.pin);
  s5.anterior = digitalRead(s5.pin);
  s6.anterior = digitalRead(s6.pin);
  s7.anterior = digitalRead(s7.pin);

}

void loop() {
  mb.task();

  uint16_t estadoAtuador1 = mb.Hreg(OFS_Atuador1);
  uint16_t estadoAtuador2 = mb.Hreg(OFS_Atuador2);
  uint16_t estadoAtuador3 = mb.Hreg(OFS_Atuador3);
  uint16_t estadoAtuador4 = mb.Hreg(OFS_Atuador4);
  uint16_t estadoAtuador5 = mb.Hreg(OFS_Atuador5);
  uint16_t estadoAtuador6 = mb.Hreg(OFS_Atuador6);
  uint16_t estadoAtuador7 = mb.Hreg(OFS_Atuador7);
  if (estadoAtuador1 == 1) {
    digitalWrite(Atuador1, HIGH);
  } else if(estadoAtuador1 == 0){
    digitalWrite(Atuador1, LOW);
  }
  if (estadoAtuador2 == 1) {
    digitalWrite(Atuador2, HIGH);
  } else if(estadoAtuador2 == 0){
    digitalWrite(Atuador2, LOW);
  }
  if (estadoAtuador3 == 1) {
    digitalWrite(Atuador3, HIGH);
  } else if(estadoAtuador3 == 0){
    digitalWrite(Atuador3, LOW);
  }
  if (estadoAtuador4 == 1) {
    digitalWrite(Atuador4, HIGH);
  } else if(estadoAtuador4 == 0){
    digitalWrite(Atuador4, LOW);
  }
  if (estadoAtuador5 == 1) {
    digitalWrite(Atuador5, HIGH);
  } else if(estadoAtuador5 == 0){
    digitalWrite(Atuador5, LOW);
  }
  if (estadoAtuador6 == 1) {
    digitalWrite(Atuador6, HIGH);
  } else if(estadoAtuador6 == 0){
    digitalWrite(Atuador6, LOW);
  }
  if (estadoAtuador7 == 1) {
    digitalWrite(Atuador7, HIGH);
  } else if(estadoAtuador7 == 0){
    digitalWrite(Atuador7, LOW);
  }

  if (mb.Hreg(OFS_Flag) == 0) {
    if (s1.changed) {
      int val = digitalRead(s1.pin);
      if(val != s1.anterior){
        mb.Ireg(s1.reg, val);
        mb.Hreg(OFS_Flag, s1.reg);
        s1.changed = false;
        s1.anterior = val;
      }
    } 
    /*else if (s2.changed) {
      int val = digitalRead(s2.pin);
      if(val != s2.anterior){
        mb.Ireg(s2.reg, val);
        mb.Hreg(OFS_Flag, s2.reg);
        s2.changed = false;
        s2.anterior = val;
      }
    }
    else if (s3.changed) {
      int val = digitalRead(s3.pin);
      if(val != s3.anterior){
        mb.Ireg(s3.reg, val);
        mb.Hreg(OFS_Flag, s3.reg);
        s3.changed = false;
        s3.anterior = val;
      }
    }*/
    else if (s4.changed) {
      int val = digitalRead(s4.pin);
      if(val != s4.anterior){
        mb.Ireg(s4.reg, val);
        mb.Hreg(OFS_Flag, s4.reg);
        s4.changed = false;
        s4.anterior = val;
      }    
    }
    /*else if (s5.changed) {
      int val = digitalRead(s5.pin);
      if(val != s5.anterior){
        mb.Ireg(s5.reg, val);
        mb.Hreg(OFS_Flag, s5.reg);
        s5.changed = false;
        s5.anterior = val;
      }
    }
    else if (s6.changed) {
      int val = digitalRead(s6.pin);
      if(val != s6.anterior){
        mb.Ireg(s6.reg, val);
        mb.Hreg(OFS_Flag, s6.reg);
        s6.changed = false;
        s6.anterior = val;
      }
    }
    else if (s7.changed) {
      int val = digitalRead(s7.pin);
      if(val != s7.anterior){ 
        mb.Ireg(s7.reg, val);
        mb.Hreg(OFS_Flag, s7.reg);
        s7.changed = false;
        s7.anterior = val;
      }
    }*/
  }
}
