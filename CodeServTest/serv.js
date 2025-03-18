const express = require('express');
const session = require('express-session');
const path = require('path');

const app = express();//Initialisation de l'application express

// Middleware pour rediriger les utilisateurs non connectés vers la page de login
//Ce middleware s'exécute avant chaque requête.
app.use((req, res, next) => {
    if (!req.session.user && req.path !== '/' && req.path !== '/login') {//Vérifie si l'utilisateur n'est pas connecté (!req.session.user) et si il essaie d'accéder à une page autre que / ou /login.
        return res.redirect('/');//Si c'est le cas, il est redirigé vers la page de login (/)
    }

    next();//Sinon, la requête continue avec next().
});

app.use(session({
    secret: 'secret-key',
    resave: false,
    saveUninitialized: true
}));

// Middleware pour restreindre l'accès à bdd.html uniquement à l'administrateur
app.use((req, res, next) => {
    if (req.path === '/bdd.html' && (!req.session.user || req.session.user.role !== 'admin')) {
        return res.status(403).send('Accès interdit');//Si l'utilisateur n'est pas connecté ou n'est pas administrateur, il reçoit une erreur 403 (Accès interdit) et la requête s'arrête ici.
    }
    next();//Sinon, la requête continue avec next().
});

app.use(express.static(path.join(__dirname, 'public'))); 

// Page de login (page d'accueil)
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));//
});

// Gestion de l'authentification
app.post('/login', express.urlencoded({ extended: true }), (req, res) => { //Middleware pour récupérer les données du formulaire
    const { username, password } = req.body;//Récupération des données du formulaire
    if (username === 'admin' && password === '2btsciel$') {//Vérification des identifiants
        req.session.user = { role: 'admin' };//Création de la session utilisateur
        res.redirect('/accueil.html');//Redirection vers la page d'accueil
    } else if (username === 'operateur' && password === 'Azerty') {
        req.session.user = { role: 'operateur' };// Création de la session
        res.redirect('/accueil.html');//Redirection 
        res.send('Identifiants incorrects');//Message d'erreur
    }
});

// Middleware de protection des routes
function authMiddleware(role) {
    return (req, res, next) => {
        if (!req.session.user || (role && req.session.user.role !== role)) {//Vérifie si l'utilisateur est connecté (req.session.user)
            return res.status(403).send('Acc  s interdit');//Si l'utilisateur n'est pas connecté, il reçoit une erreur 403 (Accès interdit) et la requête s'arrête ici.
        }
        next();//Sinon, la requête continue avec next().
    };
}

// Routes protégés
app.get('/accueil.html', authMiddleware(), (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'accueil.html'));//Si l'utilisateur est connecté, la page d'accueil est renvoyée.
});

app.get('/bdd.html', authMiddleware('admin'), (req, res) => {// restreindre l'accès à bdd.html uniquement à l'administrateur
    res.sendFile(path.join(__dirname, 'public', 'bdd.html'));
});

// Déconnexion
app.get('/logout', (req, res) => {
    req.session.destroy(() => {//Détruit la session utilisateur
        res.redirect('/');//Redirige vers la page de login
    });
});

app.listen(3000, '0.0.0.0', () => {//Démarrage du serveur sur le port 3000
    console.log('Serveur demarre  sur http://10.160.120.89:3000');//Affichage d'un message dans la console
});
