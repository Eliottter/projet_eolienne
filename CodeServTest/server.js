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
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Page de login
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// Gestion de l'authentification avec base de données
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    console.log("Tentative de connexion :", username, password);

    db.get('SELECT * FROM users WHERE username = ? AND password = ?', [username.trim(), password.trim()], (err, row) => {
        if (err) {
            console.error('Erreur SQL:', err.message);
            return res.status(500).json({ error: 'Erreur interne' });
        }
        return res.json({ redirect: '/BaseDeDonnees.html' });
        console.log("Résultat SQL :", row);
        console.log("row id :", row.id);
        if (row.id) {
            console.log("boubobuboubobuboubbuo");
            req.session.user = { username: row.username, role: row.role };
            console.log("Utilisateur connecté :", req.session.user);

            if (row.role == 'operateur') {
                return res.json({ redirect: '/accueil.html' });
            }
            else if (row.role == 'admin') {
            }
        } 
            else {
            console.log("Aucun utilisateur trouvé avec ces identifiants.");
            return res.status(401).json({ error: 'Identifiants incorrects' });
        }
    });
});

// Middleware de protection des routes
function authMiddleware(role) {
    return (req, res, next) => {
        if (!req.session.user) {
            return res.status(401).send("Non autorisé");
        }
        if (role && req.session.user.role !== role) {
            return res.status(403).send("Accès interdit");
        }
        next();
    };
}

// Routes protégées
app.get('/accueil.html', authMiddleware("operateur"), (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'accueil.html'));
});

app.get('/BaseDeDonnees.html', authMiddleware("admin"), (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'BaseDeDonnees.html'));
});

// Déconnexion
app.get('/logout', (req, res) => {
    req.session.destroy(() => {
        res.redirect('/');
    });
});

server.listen(3000, '0.0.0.0', () => {
    console.log('Serveur démarré sur http://10.160.120.89:3000');
});
