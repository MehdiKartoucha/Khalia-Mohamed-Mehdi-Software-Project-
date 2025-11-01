# 🗜️ Compression par Bit-Packing

**Master 1 - Génie Logiciel 2025**  
**Auteur :** Khalia Mohamed Mehdi

---

## À Propos

Système de compression d'entiers par **bit-packing** optimisé pour la transmission réseau. 

**Défi :** 1000 entiers = 4000 bytes normalement. Mais si vos nombres ne nécessitent que 8 bits, pourquoi ne pas les compresser à 1000 bytes ?

**3 stratégies implémentées :**
- 🔴 **Compression Maximale** (`with_overflow`) - Meilleure réduction de taille
- 🟡 **Accès Ultra-Rapide** (`no_overflow`) - Lecture directe sans décompression
- 🟢 **Approche Hybride** (`overflow_area`) - Équilibre compression/accès

---

## 📦 Installation

**Prérequis :** Python 3.8+

### Créer un Environnement Virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows (CMD)
venv\Scripts\activate

# Sur Windows (Git Bash)
source venv/Scripts/activate

# Sur macOS/Linux
source venv/bin/activate
```

### Installer les Dépendances

```
pip install -r requirements.txt
```

Cela installe : `numpy`, `pytest`, `matplotlib`

---

## 🚀 Démarrage Rapide

| Mode | Commande | Utilité |
|------|----------|---------|
| 🎨 **GUI** | `python -m src.gui` | Débuter, visualiser les résultats |
| 💻 **Menu** | `python main.py` | Compresser vos données, tester |
| 📊 **Exemples** | `c` | Voir 7 cas d'usage |
| ⚡ **Benchmarks** | `python -m src.benchmark` | Analyser les performances |
| ✅ **Tests** | `python -m pytest tests/ -v` | Valider le code (30 tests) |

---

## 📖 Utilisation

### 1️⃣ Interface Graphique (Recommandée pour débuter)

```
python -m src.gui
```

Accédez à :
- Exemples pré-chargés
- Visualisations graphiques
- Comparaisons en temps réel
- Statistiques détaillées

### 2️⃣ Menu Interactif

```
python main.py
```

7 options disponibles :
1. Compresser vos données
2. Démonstration rapide
3. Exécuter les benchmarks
4. Lancer les tests
5. Voir les exemples
6. Interface graphique
7. Quitter

**Formats d'entrée acceptés :**
- Espaces : `1 2 3 4 5`
- Virgules : `1, 2, 3, 4, 5`
- Négatifs : `-10 -5 0 5 10`

### 3️⃣ Utilisation en Python

```python
from src.factory import CompressionFactory

# Vos données
donnees = [1, 2, 3, 4, 5, 10, 20, 30]

# Créer un compresseur
compresseur = CompressionFactory.create("with_overflow")

# Compresser
compressees = compresseur.compress(donnees)

# Statistiques
infos = compresseur.get_info()
print(f"Ratio : {infos['compression_ratio']:.2f}x")

# Accès direct (sans décompression complète)
premier_element = compresseur.get(0)

# Décompresser
restaurees = compresseur.decompress(compressees)
```

---

## 🏗️ Architecture

```
src/
├── base_bitpacking.py          # Interface abstraite commune
├── factory.py                  # Création des compresseurs
├── bitpacking_overflow.py      # Stratégie 1 : Avec débordement
├── bitpacking_no_overflow.py   # Stratégie 2 : Sans débordement
├── bitpacking_overflow_area.py # Stratégie 3 : Zone de débordement
├── benchmark.py                # Suite de benchmarks
└── gui.py                       # Interface graphique (tkinter)

tests/
└── test_compression.py         # 30 tests unitaires
```

**Patterns utilisés :**
- **Factory Pattern** : Création flexible des compresseurs
- **Strategy Pattern** : Interface commune pour différentes implémentations

---

## 🔧 Stratégies de Compression

### 1. Avec Débordement (`with_overflow`)

**Concept :** Les valeurs compressées peuvent chevaucher plusieurs entiers.

| Aspect | Détail |
|--------|--------|
| ✅ Avantages | Compression maximale, excellent pour petites valeurs |
| ❌ Inconvénients | Accès aléatoire plus lent |
| 🎯 Cas d'usage | Connexion très lente, données uniformément petites |
| 📊 Exemple | Ratio ~5.0x pour `[1,2,3,4,5]` |

### 2. Sans Débordement (`no_overflow`)

**Concept :** Chaque valeur reste confinée dans un seul entier.

| Aspect | Détail |
|--------|--------|
| ✅ Avantages | Accès ultra-rapide, calculs simples |
| ❌ Inconvénients | Compression légèrement moins bonne |
| 🎯 Cas d'usage | Accès fréquent aux éléments, latence acceptable |
| 📊 Exemple | Ratio ~2.0x, accès optimal |

### 3. Zone de Débordement (`overflow_area`)

**Concept :** Valeurs normales compressées ensemble, aberrantes stockées séparément.

| Aspect | Détail |
|--------|--------|
| ✅ Avantages | Bon compromis, détecte les outliers |
| ❌ Inconvénients | Configuration (percentile) |
| 🎯 Cas d'usage | Données réelles avec anomalies |
| 📊 Exemple | Ratio ~2.9x, équilibre compression/accès |

---

## 📊 Résultats Benchmarks (1000 éléments)

| Métrique | Avec Débordement | Sans Débordement | Hybride |
|----------|------------------|------------------|---------|
| **Ratio Compression** | 2.91x | 2.00x | 2.91x |
| **Temps Compression** | 394 µs | 453 µs | 665 µs |
| **Temps Décompression** | 473 µs | 283 µs | 514 µs |
| **Accès Aléatoire** | 1.03 µs | 0.91 µs | 1.12 µs |
| **Seuil Transmission** | 127.3 ms | 45.2 ms | 134.7 ms |

**Seuil de transmission** = latence réseau à partir de laquelle la compression gagne du temps

---

## 🧪 Tests

Suite de **30 tests unitaires** couvrant :

✅ **Compressions/Décompressions Basiques (6 tests)**
- Compression/décompression correcte
- Réduction de taille
- Tableaux vides, single, tous zéros

✅ **Accès Aléatoire (5 tests)**
- Accès à tous les indices
- Premiers/derniers éléments
- Vérification des limites

✅ **Nombres Négatifs (4 tests)**
- Uniquement négatifs
- Mélange positif/négatif
- Grands négatifs

✅ **Distributions de Données (4 tests)**
- Distribution uniforme
- Petites valeurs
- Données avec outliers
- Séquences

✅ **Cas Limites (3 tests)**
- Valeurs maximales
- Grands tableaux (100k+ éléments)
- Patterns alternants

✅ **Usine de Création (4 tests)**
- Création tous types
- Types invalides
- Énumération des types

✅ **Métadonnées (2 tests)**
- Information complète
- Ratio de compression correct

✅ **Comportements Spécifiques (2 tests)**
- Différences between méthodes
- Détection automatique outliers

**Lancer les tests :**

```
python -m pytest tests/ -v
```

Résultat attendu : **30 passed** ✅

---

## ⚙️ Concepts Techniques

### Factory Pattern

Création flexible des compresseurs sans exposer les détails :

```python
compresseur = CompressionFactory.create("with_overflow")
```

L'utilisateur ne connaît pas la classe réelle, mais reçoit une instance correcte.

### Strategy Pattern

Tous les compresseurs implémentent `BaseBitPacking` :

```python
class BaseBitPacking(ABC):
    def compress(self, donnees: List[int]) -> List[int]: pass
    def decompress(self, compressees: List[int]) -> List[int]: pass
    def get(self, indice: int) -> int: pass  # Accès aléatoire
    def get_info(self) -> Dict: pass
```

Chaque stratégie offre la même interface, facilitant les changements.

### Encodage ZigZag

Gère automatiquement les nombres négatifs :

```python
donnees = [-100, -50, 0, 50, 100]
compresseur.compress(donnees)  # Fonctionne parfaitement
```

---

## 💡 FAQ

**Q : Quelle méthode choisir ?**

A :
- 🐢 Connexion lente → `with_overflow` (compression max)
- 🚀 Besoin de vitesse → `no_overflow` (accès rapide)
- ⚖️ Vous hésitez → `overflow_area` (bon équilibre)

**Q : Les données négatives sont supportées ?**

A : Oui, complètement ! Encodage ZigZag géré automatiquement.

**Q : C'est pour la production ?**

A : Bon pour apprentissage et démos. Pour production, ajouter gestion d'erreurs et tests additionnels.

**Q : Comment ajouter ma propre stratégie ?**

A : Créez une classe hérité de `BaseBitPacking` et enregistrez-la dans `factory.py`.

---

## 🐛 Dépannage

| Erreur | Cause | Solution |
|--------|-------|----------|
| `ModuleNotFoundError: src` | Mauvais répertoire | `cd "projet software off"` |
| `ModuleNotFoundError: numpy` | Dépendances non installées | `pip install -r requirements.txt` |
| `Python 3.8 required` | Version trop ancienne | Installer Python 3.8+ |
| Tests échouent | Installation incomplète | `pip install -r requirements.txt` + `python -m pytest tests/ -vv` |

---

## 🎓 Ce Que Vous Apprendrez

1. **Design Patterns** - Factory et Strategy patterns en action
2. **Compression de Données** - Bit-packing et encodage ZigZag
3. **Optimisation** - Compromis compression vs vitesse
4. **Tests Unitaires** - Écrire 30 tests pertinents
5. **Benchmarking** - Mesurer la performance réelle
6. **Interfaces Utilisateur** - CLI et GUI
7. **Génie Logiciel** - Architecture professionnelle

---

## 🚀 Améliorations Futures

- [ ] Support nombres décimaux (float)
- [ ] Compression par dictionnaire
- [ ] Interface web (Flask)
- [ ] Parallélisation (multiprocessing)
- [ ] Support fichiers compressés
- [ ] Intégration protobuf
- [ ] Optimisation Cython
- [ ] Support streaming

---

## 📚 Dépendances

- `numpy` - Calculs numériques et benchmarking
- `pytest` - Framework de tests
- `matplotlib` - Visualisations graphiques

---

## 📄 Informations

- **Type :** Projet académique
- **Institution :** Master 1 IA - Génie Logiciel
- **Année :** 2025
- **Auteur :** Khalia Mohamed Mehdi

---

**Bon compression !** 🚀
