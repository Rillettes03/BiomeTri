# BiomeTri
Par Aurore Lépine et Paul Terrien

## Fonctionnalités implémentées 
* Application de base fonctionnelle
    * Mise en évidence de la reconnaissance du visage avec l'apparition de 68 points sur le visages. Cela correspond aux points reconnus.
* Hashage (Prénom + Nom -> SHA256)
    * On n'expose pas les noms mais des id. Cela contribue à une meilleure sécurité de données. On pseudo-anonymise.
* Base de données

## A suivre
* Envoi de mails automatiques pour une double authentification (Problème de serveur ftp)
* Hash de toutes les données : on ferait diminuer la taille de la BDD et nous continuerions à pseudo-anonymiser les données. Nous ne l'avons pas imlémenter pour des raisons de démonstration.
