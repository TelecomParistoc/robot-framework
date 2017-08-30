# Callback python

Ce dossier écrêmé présente uniquement un test (en plus du code important) qui montre comment interfacer des callbacks python appelés dans des contexte d'exécution (threads C) différents.

Pour tester : *make test*

Pour installer : *sudo make install*

**Important !**
On notera la présence du package encapsulate_callback dont l'utilisation est nécessaire pour encapsuler des callback python dans un objet permettant de les utiliser en C.
