## Outils pour démarrage automatique du robot

Ce dossier contient :
- loop_launch_check_button_state.cpp : Un fichier c++ contenant la boucle de lancement permanent
- setup.sh : Un script permettant de mettre en place automatiquement le lancement du programme c++ au démarrage du raspberry
- remove_autolaunch.sh : Un script permettant de supprimer le lancement du programme c++ au démarrage du raspberry
- launch.py : Un script contenant le nécessaire pour lancer le programme c++ avec les arguments spécifiés dans la configuration du script
- program_and_commands.config : Un fichier de configuration contenant le chemin vers le programme à exécuter et les commandes shell nécessaires pour l'état du bouton
- Makefile : Un super makefile pour installer automatiquement tout ce qui est nécessaire juste en modifiant "program_and_commands.config"
- README.md : Un README (ce même fichier) qui contient tout ce qui est nécessaire pour comprendre le fonctionnement de cette sous partie du robot


**Procédure d'installation très facile**

Changer le chemin du fichier de script utilisé par le robot dans program_and_commands.config
Exécuter make install


**Procédure d'installation facile**

Exécuter make install
Pour changer le chemin utilisé dans la boucle, modifier le contenu du fichier /var/robot_config/program_path
Pour changer les commandes utilisées pour initialiser les gpio ou lire une valeur de gpio, modifier le contenu du fichier /var/robot_config/commands


**Procédure d'installation un peu moins facile**

Exécuter un make pour construire robot_loop_starter
Créer un fichier de configuration contenant 3 lignes : le nom du programme, la commande shell d'initialisation (pull-up/down par exemple), et la commande shell pour obtenir l'état du bouton
Exécuter ./setup.sh robot_loop_starter [chemin vers votre fichier de configuration] [chemin vers l'emplacement utilisé pour savoir quel programme lancer] [chemin vers l'emplacement utilisé pour savoir quelles commandes exécuter]
