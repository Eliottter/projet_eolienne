const express = require('express');
const session = require('express-session');
const path = require('path');

const app = express();

app.use(session({
    secret: 'secret-key',
    resave: false,
    saveUninitialized: true
}));

app.use(express.static(path.join(__dirname, 'public')));

// Page de login (page d'accueil)
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

app.listen(3000, '0.0.0.0', () => {
    console.log('Serveur demarre sur http://10.160.120.89:3000');
});