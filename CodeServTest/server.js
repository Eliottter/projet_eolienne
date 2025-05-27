const express = require('express');
const session = require('express-session');
const cookieParser = require('cookie-parser');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const https = require('https');
const fs = require('fs');
const mqtt = require('mqtt');
const WebSocket = require('ws');

const app = express();

// Charger les certificats SSL
const options = {
    key: fs.readFileSync('/home/user/certificat/server.key'),
    cert: fs.readFileSync('/home/user/certificat/server.crt')
};

// Création du serveur HTTPS
const server = https.createServer(app);

// Connexion à la base de données SQLite
const db = new sqlite3.Database('/var/www/html/BDD_meteo.db', (err) => {
    if (err) {
        console.error('Erreur de connexion à la base de données:', err.message);
    } else {
        console.log('Connexion à la base de données réussie.');
    }
});
// Certificats TLS pour WebSocket sécurisé
const privateKey = fs.readFileSync('ssl/key.pem');
const certificate = fs.readFileSync('ssl/cert.pem');
const credentials = { key: privateKey, cert: certificate };

// Serveur HTTPS
const express = require('express');
const app = express();
const server = https.createServer(credentials, app);

// WebSocket
const wss = new WebSocket.Server({ server });

// Serveur web Express
app.use(express.static('public')); // dossier avec tes fichiers HTML

// MQTT sécurisé
const mqttClient = mqtt.connect('mqtts://localhost:8883', {
    username: 'user',
    password: 'Azerty.1',
    ca: fs.readFileSync('/etc/mosquitto/certs/server.crt'),
    rejectUnauthorized: false
});

mqttClient.on('connect', () => {
    console.log('Connecté à MQTT sécurisé');
    mqttClient.subscribe('capteur_present');
});

mqttClient.on('message', (topic, message) => {
    const orientationMatch = payload.match(/orientation\s+([\d.]+)°\s+\(([^ )]+)/i);
const vitesseMatch = payload.match(/Vitesse du vent\s*:\s*([\d.]+)/i);

if (orientationMatch && vitesseMatch) {
    const orientation_deg = parseFloat(orientationMatch[1]);
    const orientation_card = orientationMatch[2];
    const vitesse_vent = parseFloat(vitesseMatch[1]);

    const data = {
        DirectionVentDegres: orientation_deg,
        DirectionVentCardinal: orientation_card,
        VitesseVent: vitesse_vent,
        Temperature: null // Si disponible plus tard
    };

    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(data));
        }
    });

    console.log('Données MQTT envoyées :', data);
}

// Middleware pour analyser les requêtes POST et les cookies
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());

// Configuration des sessions
app.use(session({
    secret: '13729501', // Clé secrète pour signer le cookie
    resave: false,                   // Évite de sauvegarder la session si elle n'a pas changé
    saveUninitialized: false,        // Ne sauvegarde pas les sessions vides
    cookie: {
        httpOnly: true,             // Empêche l'accès via JavaScript (sécurité)
        secure: true,               // HTTPS obligatoire (à désactiver en développement)
        maxAge: 5 * 60 * 1000      // Expiration après 5 minutes d'inactivité
    }
}));

// Désactiver la mise en cache pour les pages protégées
app.use((req, res, next) => {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    next();
});

// Servir les fichiers statiques
app.use(express.static(path.join(__dirname, 'public')));

// Traitement du formulaire de login
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    db.get('SELECT * FROM utilisateurs WHERE username = ?', [username], (err, row) => {
        if (err) {
            return res.status(500).send('Erreur de connexion à la base de données');
        }
        if (row && row.password === password) {
            // Créer la session utilisateur avec le nom d'utilisateur
            req.session.user = { username: row.username };
            console.log('Session créée pour :', req.session.user.username);
            res.send('accueil.html');
            
        } else {
            res.send('Identifiants incorrects');
        }
    });
});

// Middleware pour vérifier si l'utilisateur est authentifié
function isAuthenticated(req, res, next) {
    if (req.session && req.session.user) {
        return next();
    }
    console.log("Session inexistante ou expirée. Redirection vers la page de login.");
    res.redirect('/');
}

// Routes protégées
app.get('/accueil', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'accueil.html'));
});

app.get('/BaseDeDonnees', isAuthenticated, (req, res) => {
    if (req.session.user.username !== 'admin') {
        console.log(`Accès refusé à /BaseDeDonnees pour : ${req.session.user.username}`);
        return res.redirect('/accueil');
    }
    res.sendFile(path.join(__dirname, 'public', 'BaseDeDonnees.html'));
});

// Route de déconnexion
app.get('/logout', (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            console.error('Erreur lors de la destruction de la session:', err);
            return res.status(500).send('Erreur lors de la déconnexion');
        }

        // Supprimer le cookie côté client
        res.clearCookie('connect.sid');

        // Forcer suppression côté serveur
        req.session = null;

        console.log('Utilisateur déconnecté, session détruite');
        res.redirect('/');
    });
});

// Analyser les données envoyées par le formulaire de login (doublon, à supprimer si déjà plus haut)
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Page de login
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// API pour récupérer les données météo
app.get('/api/meteo', (req, res) => {
    db.all('SELECT DateHeure, Temperature, VitesseVent, DirectionVentDegres, DirectionVentCardinal FROM meteo ORDER BY DateHeure DESC', [], (err, rows) => {
        if (err) {
            console.error('Erreur SQL:', err.message);
            return res.status(500).json({ error: 'Erreur interne' });
        }
        res.json(rows); // Renvoie les données au format JSON
    });
});

// Endpoint pour récupérer l'utilisateur connecté
app.get('/api/user', (req, res) => {
    if (req.session && req.session.user) {
        res.json({ username: req.session.user.username });
    } else {
        res.status(401).json({ error: 'Utilisateur non connecté' });
    }
});

// Catch-all : redirige toute route inconnue vers la page de login
app.use((req, res) => {
    res.redirect('/');
});

// Démarrage du serveur
server.listen(443, () => {
    console.log('Serveur HTTPS + WebSocket en écoute sur le port 443');
});