# Callback python

Ce dossier contient du code permettant d'encapsuler des fonctions python pour pouvoir utiliser des fonctions python comme callbacks de fonctions C.
Ce genre d'encapsulation est nécessaire pour s'assurer que le garbage collector de python ne libère pas la mémoire allouée pour une fonction qui va ensuite être appelée par du code C. Ce code garde en fait juste une référence "au chaud" de chaque fonction encapsulée, pour que le garbage collector ne les désalloue pas.

Le code effectif est contenu dans encapsulate_callback.py, timer_callbacks_test.cpp et timer_callbacks_test.py sont un test.

Il est nécessaire d'installer cette bibliothèque ; l'installation consiste simplement à copier le fichier encapsulate_callback.py au bon endroit.


## Pour tester
```
$ make test
```

## Pour installer
```
$ sudo make install
```
