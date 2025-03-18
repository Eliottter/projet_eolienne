const express = require('express');
const session = require('express-session');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Connexion à la base de données SQLite
const db = new sqlite3.Database('/var/www/html/BDD_meteo.db', (err) => {
    if (err) {
        console.error('Erreur de connexion à la base de données:', err.message);
    } else {
        console.log('Connexion à la base de données réussie.');
    }
});

app.use(session({
    secret: 'secret-key',
    resave: false,
    saveUninitialized: true
}));

app.use(express.static(path.join(__dirname, 'public')));

// Page de login
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// Gestion de l'authentification
app.post('/login', express.urlencoded({ extended: true }), (req, res) => {
    const { username, password } = req.body;
    if (username === 'admin' && password === 'adminpass') {
        req.session.user = { role: 'admin' };
        res.redirect('/monitoring.html');
    } else if (username === 'operateur' && password === 'operateurpass') {
        req.session.user = { role: 'operateur' };
        res.redirect('/monitoring.html');
    } else {
        res.send('Identifiants incorrects');
    }
});

// Middleware de protection des routes
function authMiddleware(role) {
    return (req, res, next) => {
        if (!req.session.user || (role && req.session.user.role !== role)) {
            return res.status(403).send('Accès interdit');
        }
        next();
    };
}

// Routes protégées
app.get('/monitoring.html', authMiddleware(), (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'monitoring.html'));
});

app.get('/bdd.html', authMiddleware('admin'), (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'bdd.html'));
});

// Déconnexion
app.get('/logout', (req, res) => {
    req.session.destroy(() => {
        res.redirect('/');
    });
});

// Route API pour récupérer les dernières données météo
app.get('/api/meteodata', (req, res) => {
    db.get("SELECT * FROM meteo ORDER BY timestamp DESC LIMIT 1", (err, row) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(row);
    });
});

// WebSockets pour mise à jour en temps réel
io.on('connection', (socket) => {
    console.log('Client connecté');
    setInterval(() => {
        db.get("SELECT * FROM meteo ORDER BY timestamp DESC LIMIT 1", (err, row) => {
            if (!err && row) {
                socket.emit('updateData', row);
            }
        });
    }, 5000);
});

server.listen(3000, '0.0.0.0', () => {
    console.log('Serveur démarré sur http://10.160.120.88:3000');
});
