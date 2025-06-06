const session = require('express-session');// Pour la gestion des sessions
const cookieParser = require('cookie-parser');// Pour la gestion des sessions et des cookies
const path = require('path');// Pour la gestion des sessions et des cookies
const sqlite3 = require('sqlite3').verbose();// Pour la base de données SQLite
const https = require('https');// Pour le chiffrement SSL/TLS
const fs = require('fs');// Pour le chiffrement SSL/TLS
const mqtt = require('mqtt');//
const WebSocket = require('ws'); // WebSocket pour la communication en temps réel
const bcrypt = require('bcrypt'); //hachage des mots de passe



// Charger les certificats SSL
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
// Certificats TLS pour WebSocket sécurisé
const privateKey = fs.readFileSync('/home/user/certificat/server.key');
const certificate = fs.readFileSync('/home/user/certificat/server.crt');
const credentials = { key: privateKey, cert: certificate };

// Serveur HTTPS
const express = require('express');
const app = express();
const server = https.createServer(credentials, app);

// WebSocket
const wss = new WebSocket.Server({ server });

// Serveur web Express
app.use(express.static('public')); // dossier avec tes fichiers HTML

// Bootstrap en local 
app.use('/bootstrap', express.static(path.join(__dirname, 'node_modules/bootstrap/dist')));
// Bootstrap en local pour les fichiers CSS et JS
<script src="/bootstrap/js/bootstrap.bundle.min.js"></script>
// Chart.js en local
app.use('/chartjs', express.static(path.join(__dirname, 'node_modules/chart.js/dist')));


// Pour envoyer les données depuis ton MQTT :
function broadcastToClients(data) {
    wss.clients.forEach(function each(client) {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(data));
        }
    });
}

// Exemple d’intégration avec MQTT 
const client = mqtt.connect('mqtts://172.90.93.66:8883', {
    username: "user",
    password: "Azerty.1",
    ca: fs.readFileSync("/home/user/certificat/server.crt"),
    rejectUnauthorized: false
});

client.on('connect', () => {
    console.log("Connecté à MQTT");
    client.subscribe("capteur_present");
});

client.on('message', (topic, message) => {
    const payload = message.toString();
    console.log("MQTT reçu :", payload);

    const orientationMatch = payload.match(/orientation\s+([\d.]+)°\s+\(([^ ]+)/i);
    const vitesseMatch = payload.match(/Vitesse du vent\s*:\s*([\d.]+)/i);

    if (orientationMatch && vitesseMatch) {
        const data = {
            direction_deg: parseFloat(orientationMatch[1]),
            direction_card: orientationMatch[2],
            vitesse: parseFloat(vitesseMatch[1]),
            temperature: 20 // Valeur fictive ou récupérée ailleurs
        };
        broadcastToClients(data);
    } else {
        console.log("Format de message MQTT incorrect");
    }
});

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


// Traitement du formulaire de login
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    console.log("Tentative de connexion :", username, password);
    db.get('SELECT * FROM utilisateurs WHERE username = ?', [username], (err, row) => {
        if (err) {
            return res.status(500).send('Erreur de connexion à la base de données');
        }
        if (!row) {
            return res.send('Identifiants incorrects');
        }

        // Vérification du mot de passe hashé avec bcrypt
        bcrypt.compare(password, row.password, (err, result) => {
            if (err) 
                return res.status(500).send('Erreur serveur');
            

            if (result) {
                req.session.user = { username: row.username, role: row.role };
                console.log('Session créée pour :', row.username);
res.json({ redirect: '/accueil' });
            } else {
                res.send('Identifiants incorrects');
            }
        });
    });
});

// // Formulaire registrer 
// app.post('/register', (req, res) => {
//     const { username, password, role } = req.body;

//     if (!username || !password || !role) {
//         return res.status(400).send("Champs manquants");
//     }

//     // Hachage du mot de passe
//     bcrypt.hash(password, 10, (err, hashedPassword) => {
//         if (err) return res.status(500).send("Erreur de hachage");

//         const sql = `INSERT INTO utilisateurs (username, password, role) VALUES (?, ?, ?)`;
//         db.run(sql, [username, hashedPassword, role], function(err) {
//             if (err) {
//                 console.error(err.message);
//                 return res.status(500).send("Erreur lors de l’ajout de l’utilisateur");
//             }
//             console.log(`Utilisateur ${username} ajouté avec le rôle ${role}`);
//             res.send("Utilisateur enregistré avec succès");
//         });
//     });
// });


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
    if (req.session.user.role !== 'responsable') {
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