# Projet Théorie des Graphes - Grille Hexagonale

**CIR3 Brest - 2026**

## 📋 Description

Ce projet implémente différents algorithmes de théorie des graphes appliqués à une grille hexagonale représentant une carte géographique. Chaque case hexagonale est un sommet du graphe, avec des propriétés (terrain, altitude) et des arêtes vers ses 6 voisins.

## 🗂️ Structure du projet

```
projet_graphes/
├── main.py                 # Code principal avec menu interactif
├── hexa.py                 # Module fourni pour l'affichage (HexGridViewer)
├── README.md               # Ce fichier
└── rapport.pdf             # Rapport du projet
```

## 🚀 Installation et exécution

### Prérequis

- Python 3.8+
- Bibliothèques : 
  - `matplotlib` (pour les graphiques de benchmark)
  - Modules standard Python : `random`, `heapq`, `itertools`, `time`

### Installation

```bash
# Installer la seule dépendance externe
pip install matplotlib
```

**Note** : Tous les autres modules (`random`, `heapq`, `itertools`, `time`) sont inclus dans Python par défaut, aucune installation supplémentaire nécessaire.

### Lancement

```bash
python main.py
```

Un menu interactif s'affichera pour choisir la question à exécuter.

## 📊 Fonctionnalités implémentées

### Q3 - Génération de carte
- **Algorithme** : Diamond-Square pour générer des altitudes réalistes
- **Terrains** : Eau, Plage, Plaine, Forêt, Montagne
- **Visualisation** : Couleurs pour les terrains

### Q5 - Rivières
- Trouve le point le plus haut de la carte
- Trace une rivière descendante vers le point le plus bas (pas forcément la mer)
- **Algorithme** : Greedy (choix du voisin avec altitude minimale)

### Q6 - Génération cohérente
- Combine Diamond-Square, rivières et terrains logiques
- Génère des cartes réalistes avec cohérence géographique

### Q7 - Routes entre villes (sans contraintes)
- Place des villes aléatoirement sur la carte
- Calcule le réseau de routes minimal entre toutes les villes
- **Algorithmes** :
  - Dijkstra : O((V + E) log V) pour les plus courts chemins
  - Prim : O(N² log N) pour l'arbre couvrant minimum (MST)
- **Benchmark** : Analyse des temps de calcul selon taille de grille et nombre de villes

### Q8 - Routes avec contraintes
- Prend en compte le type de terrain (coûts différents)
- Prend en compte l'altitude (pénalité pour montée/descente)
- **Impossible** de traverser l'eau
- **Algorithme** : Dijkstra avec coûts pondérés

### Q9 - Réseau minimal (MST)
- Crée un réseau de routes le moins coûteux possible
- Toutes les villes sont accessibles les unes par rapport aux autres
- **Algorithme** : Prim (déjà utilisé en Q7/Q8)

### Q10 - Voyageur de commerce (TSP)
- Trouve le circuit optimal pour visiter toutes les villes et revenir au départ
- **Algorithme** : Brute force (test de toutes les permutations)
- **Complexité** : O(N!) - ⚠️ Limité à N ≤ 10 villes
- Option avec/sans contraintes de terrain

## 🎮 Guide d'utilisation du menu

```
PROJET THÉORIE DES GRAPHES - GRILLE HEXAGONALE

Questions disponibles:
  [3]  Q3 - Génération de carte avec terrains aléatoires
  [5]  Q5 - Génération de rivières
  [7]  Q7 - Villes et routes (sans contraintes)
  [8]  Q8 - Routes avec contraintes (terrain + altitude)
  [9]  Q9 - Réseau de routes minimal (MST)
  [10] Q10 - Voyageur de commerce (TSP exact)
  [B7] Benchmark Q7 (temps de calcul)

Autres:
  [C78] Comparaison Q7 vs Q8
  [0]   Quitter
```

### Exemples d'utilisation

#### Q3 - Carte simple
```
Votre choix: 3
Largeur (défaut 30): 40
Hauteur (défaut 30): 40
```
→ Génère une carte 40×40 avec terrains aléatoires

#### Q7 - Routes sans contraintes
```
Votre choix: 7
Largeur (défaut 30): 30
Hauteur (défaut 30): 30
Nombre de villes (défaut 6): 8
```
→ Place 8 villes et calcule les routes optimales (coût uniforme)

#### Q10 - TSP
```
Votre choix: 10
Largeur (défaut 25): 25
Hauteur (défaut 25): 25
Nombre de villes (défaut 6): 6
Seed aléatoire (Entrée = aléatoire): 42
Avec contraintes terrain? (o/N): o
```
→ Résout le TSP avec seed fixe et contraintes terrain

## 📈 Complexités algorithmiques

| Question | Algorithme | Complexité | Note |
|----------|-----------|------------|------|
| Q3 | Diamond-Square | O(n²) | n = taille heightmap |
| Q5 | Greedy descent | O(V) | Chemin unique |
| Q6 | Diamond-Square + Rivières | O(n² + V) | Utilisé automatiquement |
| Q7 | Dijkstra + Prim | O(N·V log V + N² log N) | N = villes |
| Q8 | Dijkstra pondéré + Prim | O(N·V log V + N² log N) | Idem Q7 |
| Q9 | Prim (MST) | O(N² log N) | N = villes |
| Q10 | Brute force | O(N!) | ⚠️ N ≤ 10 |

## 🎨 Légende des couleurs

- 🔵 **Bleu** : Eau (infranchissable en Q8)
- 🟡 **Jaune** : Plage/Sable (coût moyen)
- 🟢 **Vert foncé** : Plaine/Herbe (coût faible)
- 🟢 **Vert clair** : Forêt (coût élevé)
- ⚫ **Gris** : Montagne (coût très élevé)
- 🔵 **Cyan** : Rivière
- 🔴 **Rouge** : Villes
- 🟠 **Orange** : Routes du réseau
- 🟣 **Magenta** : Circuit du voyageur de commerce (Q10)

## 🔧 Paramètres ajustables

Dans le code (`main.py`), vous pouvez modifier :

```python
# Diamond-Square
roughness = 0.6        # Rugosité du terrain (0.0 à 1.0)

# Placement des villes
min_distance = 2       # Distance min entre villes (en cases)
quadrants = 4          # Répartition spatiale (4 ou 9)

# Coûts de terrain (Q8)
terrain_costs = {
    "yellow": 1.5,     # Plage
    "darkgreen": 1.0,  # Plaine (référence)
    "green": 2.0,      # Forêt
    "grey": 3.0,       # Montagne
    "orange": 0.5      # Route
}

# Pénalité d'altitude (Q8)
altitude_penalty = altitude_diff * 2.0
```

## 🐛 Limitations connues

1. **Q10 (TSP)** : Temps de calcul exponentiel
   - 6 villes : ~0.01s
   - 8 villes : ~0.5s
   - 10 villes : ~30s
   - 12 villes : ~10 min ⚠️

2. **Placement des villes** : Peut échouer si contraintes trop strictes (min_distance élevé, beaucoup de villes, petite carte)

3. **Eau** : En Q8, certaines villes peuvent devenir inaccessibles si entourées d'eau

## 👥 Auteurs

- Antoine Corvaisier
- Coraline Savary

CIR3 - ISEN Brest - 2026
