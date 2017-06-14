#script qui copie les fichiers utiles dans init.d afin de lancer le programme principal automatiquement au démarrage du raspberry

if [ "$#" -le 2 ] ; then
    echo "Usage : " $0
    exit
fi

sudo cp $1 /etc/init.d/robot_auto

exec 6< $2

read program <&6
read command1 <&6
read command2 <&6

if [ "$#" -ge 5 ] ; then
    sudo echo $3 > /etc/init.d/auto_launch.config
    sudo echo $4 >> /etc/init.d/auto_launch.config
    sudo echo /etc/init.d/robot_auto >> /etc/init.d/auto_launch.config

    mkdir -p $(dirname($3))
    mkdir -p $(dirname($4))

    echo $program > $3
    echo $command1 > $4
    echo $command2 >> $4
else
    sudo echo /var/robot_config/program > /etc/init.d/auto_launch.config
    sudo echo /var/robot_config/commands >> /etc/init.d/auto_launch.config
    sudo echo /etc/init.d/robot_auto >> /etc/init.d/auto_launch.config

    mkdir -p /var/robot_config/program
    mkdir -p /var/robot_config/commands

    echo $program > /var/robot_config/program
    echo $command1 > /var/robot_config/commands
    echo $command2 >> /var/robot_config/commands
fi

sudo chmod 755 /etc/init.d/robot_auto
sudo update-rc.d robot_auto defaults
