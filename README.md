# Simulateur de Feu de Forêts
## Automate Cellulaire


Ce projet a pour but de simuler une situation complexe au travers d'une grille pixelisée. Pour simuler le feu de forêt, on se place dans une grille contenant une forêt. 
La simulation actuelle comprend un système de forêt qui peut grandir et brûler, mais également un système de propagation du feu basé sur la direction du vent donné par l'utilisateur. A chaque nouvelle simulation, un certain nombre de rivières sont générées aléatoirement sur la grille pour essayer de stopper le feu.

## Fonctionnement
Chaque case de la grille représente une portion de la forêt, et a un état en fonction de sa couleur :
* <span style="color:blue"> blanc </span> si la case est vide ;
* vert si la case contient un arbre ;
* rouge si la case contient un arbre en feu ;
* jaune si la case contient un arbre frappé par un éclair ;
* bleu si la case contient de l'eau.

La simulation fonctionne par ticks d'horloge. A chaque tick, la grille se met entièrement à jour :
* Les arbres ont une chance de pousser : la case vide devient verte.
* Le feu peut se répandre aux arbres proches selon la direction du vent.
* Chaque arbre a une très faible probabilité d'être frappé par un éclair et donc de prendre feu.

Les arbres brûlent pendant une durée de 1 tick.
