void setup() {
  // Initialisation de la communication série avec le moniteur série et Serial3 pour le capteur
  Serial.begin(9600);    // Pour afficher les données sur le moniteur série
  Serial3.begin(9600);   // Communication avec le capteur via Serial3 (assure-toi que le capteur utilise bien 9600 bauds)

  while (!Serial) {
    ; // Attendre que la communication soit prête
  }

  Serial.println("Début de la lecture des données du capteur (format hexadécimal).");
}

void loop() {
  if (Serial3.available() > 0) {
    // Lire le byte reçu
    byte incomingByte = Serial3.read();

    // Afficher la donnée reçue en format hexadécimal
    Serial.print("Donnée reçue: 0x");
    if (incomingByte < 0x10) {
      Serial.print("0");  // Ajouter un zéro devant les valeurs hexadécimales inférieures à 16
    }
    Serial.println(incomingByte, HEX);  // Afficher la valeur hexadécimale
  }
}
