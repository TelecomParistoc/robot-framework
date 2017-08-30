# Outils pour démarrage automatique du robot
## Description
Pendant la coupe de robotique, on ne peut pas venir avec son ordinateur
et lancer le programme au lancement du match. Il faut donc que celui-ci démarre
automatiquement. Cependant, pendant les phases de test, on ne veut pas que le
lancement du programme soit automatique, il faut donc un moyen pour distinguer les
deux situations. L'outil *startup_autolaunch* a été développé
pour répondre à ces différentes problématiques.  
Afin de déterminer si le programme de match du robot doit être lancé automatiquement
ou non, nous utilisons un bouton qui permet de choisir l'une des deux configurations suivantes:
 - match
 - test

Ce bouton est connecté à l'une des pins du Raspberry-Pi, il suffit donc de lire
l'état (haut/bas) de cette pin pour déterminer la configuration sélectionnée. La pin
à utiliser est configurable, de même que le programme à lancer.

## Contenu
Ce dossier contient :
- **loop_launch_check_button_state.cpp** : Un fichier c++ contenant la boucle de lancement permanent
- **setup.sh** : Un script permettant de mettre en place automatiquement le lancement du programme c++ au démarrage du raspberry
- **remove_autolaunch.sh** : Un script permettant de supprimer le lancement du programme c++ au démarrage du raspberry
- **launch.py** : Un script contenant le nécessaire pour lancer le programme c++ avec les arguments spécifiés dans la configuration du script
- **program_and_commands.config** : Un fichier de configuration contenant le chemin vers le programme à exécuter et les commandes shell nécessaires pour l'état du bouton
- **Makefile** : Un super makefile pour installer automatiquement tout ce qui est nécessaire juste en modifiant "program_and_commands.config"
- **README.md** : Un README (ce même fichier) qui contient tout ce qui est nécessaire pour comprendre le fonctionnement de cette sous partie du robot

## Installation

Les trois procédures d'installation suivantes sont de plus en plus "complexes" mais permettent à chaque fois une plus grand maîtrise des fichiers utilisés pour la configuration.

### Procédure d'installation très facile

 1. Changer le chemin du fichier de script utilisé par le robot et les commandes d'inialisation/vérification de l'état situés dans **program_and_commands.config**.
 2. Exécuter ```$ make install```

### Procédure d'installation facile

 1. Exécuter ```$ make install```
 2. Pour changer le chemin utilisé dans la boucle, modifier le contenu du fichier **/var/robot_config/program_path**.
 3. Pour changer les commandes utilisées pour initialiser les gpio ou lire une valeur de gpio, modifier le contenu du fichier **/var/robot_config/commands**.

### Procédure d'installation un peu moins facile

 1. Exécuter un ```$ make``` pour construire **robot_loop_starter**
 2. Créer un fichier de configuration contenant 3 lignes :
  - le nom du programme
  - la commande shell d'initialisation (pull-up/down par exemple)
  - la commande shell pour obtenir l'état du bouton
 3. Exécuter ```./setup.sh robot_loop_starter launch.py [chemin vers votre fichier de configuration] [chemin vers l'emplacement utilisé pour savoir quel programme lancer] [chemin vers l'emplacement utilisé pour savoir quelles commandes exécuter]```
