#script qui annule le lancement du programme principal au démarrage du raspberry

sudo update-rc.d -f robot_loop_launch remove
