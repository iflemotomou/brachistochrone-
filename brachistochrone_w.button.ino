// Βραχυστόχρονο – απλό χρονόμετρο
// Πατάς το κουμπί -> ξεκινά η χρονομέτρηση
// Κάθε σφαίρα που περνά από τον αισθητήρα της -> τυπώνεται ο χρόνος της

const byte BUTTON = 9;                       // κουμπί εκκίνησης
const byte IR[3]  = {7, 6, 5};               // ευθεία, κυκλοειδής, πολυώνυμο
const char* NAME[3] = {"Ευθεία", "Κυκλοειδής", "Πολυώνυμο"};

const int BUTTON_PRESSED = HIGH;  // αν δεν ξεκινά με το πάτημα, άλλαξε σε LOW
const int IR_DETECT      = LOW;   // αν οι χρόνοι βγαίνουν ~0, άλλαξε σε HIGH

int run = 0;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON, INPUT);
  for (byte i = 0; i < 3; i++) pinMode(IR[i], INPUT);
  Serial.println("Πάτα το κουμπί για να ξεκινήσει η χρονομέτρηση");
}

void loop() {
  // περιμένουμε το πάτημα του κουμπιού
  while (digitalRead(BUTTON) != BUTTON_PRESSED) { }
  unsigned long t0 = micros();

  run++;
  Serial.print("--- Δοκιμή ");
  Serial.print(run);
  Serial.println(" ---");

  bool done[3] = {false, false, false};
  byte count = 0;

  // χρονομέτρηση μέχρι να περάσουν και οι 3 σφαίρες (ή 5 s)
  while (count < 3 && micros() - t0 < 5000000UL) {
    for (byte i = 0; i < 3; i++) {
      if (!done[i] && digitalRead(IR[i]) == IR_DETECT) {
        float t = (micros() - t0) / 1000.0;   // σε ms
        done[i] = true;
        count++;
        Serial.print(NAME[i]);
        Serial.print(": ");
        Serial.print(t, 1);
        Serial.println(" ms");
      }
    }
  }

  for (byte i = 0; i < 3; i++) {
    if (!done[i]) {
      Serial.print(NAME[i]);
      Serial.println(": δεν ανιχνεύθηκε");
    }
  }

  // περιμένουμε να αφήσεις το κουμπί και να ηρεμήσουν οι σφαίρες
  while (digitalRead(BUTTON) == BUTTON_PRESSED) { }
  delay(1000);
  Serial.println("Έτοιμο για την επόμενη δοκιμή");
}
