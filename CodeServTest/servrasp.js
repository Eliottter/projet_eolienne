const express = require('express');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const https = require('https');
const fs = require('fs');

const app = express();

// Chargement des certificats SSL
const options = {
    key: fs.readFileSync('/home/user/certificat/server.key'),
    cert: fs.readFileSync('/home/user/certificat/server.crt')
};

// Connexion à la base de données SQLite
const db = new sqlite3.Database('/var/www/html/BDD_meteo.db', (err) => {
    if (err) {
        console.error('Erreur de connexion à la base de données:', err.message);
    } else {
        console.log('Connexion à la base de données réussie.');
    }
});

// Servir les fichiers statiques
app.use(express.static(path.join(__dirname, 'public')));

// Route pour la page principale
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'BaseDeDonnees.html'));
});

// Route pour la page daccueil
app.get('/accueil', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'accueil.html'));
});

// API pour récupérer les données de la base de données
app.get('/api/donnees', (req, res) => {
    db.all('SELECT DateHeure, VitesseVent, Temperature, DirectionVentDegres,DirectionVentCardinal FROM meteo ORDER BY DateHeure DESC', [], (err, rows) => {
        if (err) {
            console.error('Erreur SQL:', err.message);
            return res.status(500).json({ error: 'Erreur interne', details: err.message });
        };
        console.log("Données récupérées :", rows);
        res.json(rows);
    });
});

// Création et démarrage du serveur HTTPS
const server = https.createServer(options, app);

server.listen(3000, '0.0.0.0', () => {
    console.log('Serveur HTTPS démarré sur https://172.90.93.66:3000');
});