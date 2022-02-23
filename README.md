# record-player pour UL
Travail avec des étudiants au bac en Design de Produits sur la rematérialisation du rituel d'écoute de la musique

## Cette `fork`
- Ajout d'un processus `camera`:
    - Réagit à un bouton pressé sur un raspberryPi
    - Prend une photo
    - Redresse la photo
    - Averti le `frontend`
    - Coder en Python
- Modification du code préexistant:
    - Ajout d'un fichier `camera.js`
    - Ce module réagit par websocket au module `camera`
    - Utilise des fonctions déjà en places pour trouver un Id Spotify
    - Éxecute `spt play --uri ID` dans un shell

## Requis
- Setuper des creds GCP et Spotify
- Avoir `spt` d'installer sur la machine hôte
