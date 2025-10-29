"""
SYSTÈME DE COMPRESSION PAR BIT-PACKING - Interface Interactive

Programme principal offrant une interface conviviale pour :
- Entrer vos propres données
- Choisir la méthode de compression adaptée
- Compresser et décompresser des données
- Tester l'accès aléatoire aux données compressées
- Exécuter des benchmarks de performance
- Visualiser la compression en direct avec l'interface graphique

Ce projet a été développé dans le cadre du cours de Génie Logiciel - Master 1 IA (2025)
"""

import sys
from typing import List
from src.factory import CompressionFactory


def afficher_entete():
    """Affiche l'en-tête du programme avec style."""
    print("\n" + "="*70)
    print(" "*15 + "SYSTÈME DE COMPRESSION PAR BIT-PACKING")
    print("="*70)


def afficher_menu():
    """Affiche le menu principal avec toutes les options disponibles."""
    print("\n" + "-"*70)
    print("MENU PRINCIPAL")
    print("-"*70)
    print("1. Compresser vos données")
    print("2. Démonstration rapide avec des exemples")
    print("3. Exécuter les benchmarks de performance")
    print("4. Lancer les tests complets")
    print("5. Voir des exemples détaillés")
    print("6. Lancer l'interface graphique (GUI)")
    print("7. Quitter")
    print("-"*70)


def obtenir_methode_compression() -> str:
    """Demande à l'utilisateur de choisir une méthode de compression.
    
    Trois méthodes sont disponibles :
    - Avec débordement (maximum de compression)
    - Sans débordement (accès plus rapide)
    - Zone de débordement (optimale pour données mixtes)
    
    Retourne le nom de la méthode choisie.
    """
    print("\nMéthodes de compression disponibles :")
    print("1. Avec débordement - Les valeurs peuvent chevaucher plusieurs entiers (compression max)")
    print("2. Sans débordement - Les valeurs restent dans une seule limite d'entier (accès rapide)")
    print("3. Zone de débordement - Les valeurs aberrantes stockées séparément (optimal pour données mixtes)")
    
    while True:
        choix = input("\nChoisissez une méthode (1-3) : ").strip()
        if choix == "1":
            return "with_overflow"
        elif choix == "2":
            return "no_overflow"
        elif choix == "3":
            return "overflow_area"
        else:
            print("❌ Choix invalide. Veuillez entrer 1, 2, ou 3.")


def obtenir_donnees_utilisateur() -> List[int]:
    """Demande à l'utilisateur d'entrer des données à compresser.
    
    Accepte les entrées séparées par des espaces ou des virgules.
    Valide que les données entrées sont bien des nombres entiers.
    
    Retourne une liste d'entiers ou demande une nouvelle entrée en cas d'erreur.
    """
    print("\n" + "-"*70)
    print("ENTRÉE DES DONNÉES")
    print("-"*70)
    print("Entrez vos données (nombres entiers séparés par des espaces ou des virgules)")
    print("Exemples :")
    print("  1 2 3 4 5")
    print("  1, 2, 3, 4, 5")
    print("  -10 -5 0 5 10")
    print("-"*70)
    
    while True:
        try:
            entree_utilisateur = input("\nVos données : ").strip()
            
            # Gère les séparations par virgule ou espace
            if ',' in entree_utilisateur:
                donnees = [int(nb.strip()) for nb in entree_utilisateur.split(',') if nb.strip()]
            else:
                donnees = [int(nb) for nb in entree_utilisateur.split() if nb]
            
            if not donnees:
                print("❌ Erreur : Aucune donnée entrée. Veuillez entrer au moins un nombre.")
                continue
            
            return donnees
        
        except ValueError as erreur:
            print(f"❌ Erreur : Entrée invalide. Veuillez entrer uniquement des nombres entiers.")
            print(f"   Détails : {erreur}")


def compresser_donnees_personnalisees():
    """Interface interactive pour compresser les données de l'utilisateur.
    
    Processus :
    1. Demande les données à l'utilisateur
    2. Demande la méthode de compression préférée
    3. Compresse les données
    4. Décompresse pour vérifier l'intégrité
    5. Teste l'accès aléatoire aux éléments compressés
    """
    print("\n" + "="*70)
    print(" "*20 + "COMPRESSION DE DONNÉES PERSONNALISÉES")
    print("="*70)
    
    # Récupération des données
    donnees = obtenir_donnees_utilisateur()
    print(f"\n✓ Données reçues : {len(donnees)} éléments")
    if len(donnees) <= 20:
        print(f"  Données : {donnees}")
    else:
        print(f"  Premiers 10 : {donnees[:10]}")
        print(f"  Derniers 10 : {donnees[-10:]}")
    
    # Récupération de la méthode
    methode = obtenir_methode_compression()
    print(f"\n✓ Méthode sélectionnée : {methode}")
    
    # Création du compresseur
    compresseur = CompressionFactory.create(methode)
    
    # Phase de compression
    print("\n" + "-"*70)
    print("COMPRESSION EN COURS...")
    print("-"*70)
    donnees_compressees = compresseur.compress(donnees)
    infos = compresseur.get_info()
    
    print(f"\n✓ Compression terminée!")
    print(f"\n  Taille originale : {infos['original_length']} entiers ({infos['original_bits']} bits)")
    print(f"  Taille compressée : {infos['compressed_length']} entiers ({infos['compressed_bits']} bits)")
    print(f"  Bits par valeur : {infos['bits_per_value']}")
    print(f"  Ratio de compression : {infos['compression_ratio']:.2f}x")
    
    if len(donnees_compressees) <= 20:
        print(f"\n  Données compressées : {donnees_compressees}")
    
    # Phase de décompression
    print("\n" + "-"*70)
    print("DÉCOMPRESSION EN COURS...")
    print("-"*70)
    donnees_decompressees = compresseur.decompress(donnees_compressees)
    
    # Vérification de l'intégrité
    if donnees_decompressees == donnees:
        print("\n✓ Décompression réussie! Les données correspondent à l'original.")
    else:
        print("\n❌ ERREUR : Les données décompressées ne correspondent pas à l'original!")
        return
    
    # Test d'accès aléatoire
    if len(donnees) > 0:
        print("\n" + "-"*70)
        print("TEST D'ACCÈS ALÉATOIRE")
        print("-"*70)
        
        indices_test = []
        if len(donnees) > 0:
            indices_test.append(0)
        if len(donnees) > 1:
            indices_test.append(len(donnees) - 1)
        if len(donnees) > 5:
            indices_test.append(len(donnees) // 2)
        
        tous_corrects = True
        for indice_test in indices_test:
            valeur = compresseur.get(indice_test)
            valeur_attendue = donnees[indice_test]
            statut = "✓" if valeur == valeur_attendue else "❌"
            print(f"  {statut} Index {indice_test} : {valeur} (attendu : {valeur_attendue})")
            if valeur != valeur_attendue:
                tous_corrects = False
        
        if tous_corrects:
            print("\n✓ Tous les tests d'accès aléatoire sont passés!")
    
    # Possibilité de tester d'autres indices
    while True:
        reponse = input("\nTester un index spécifique? (o/n) : ").strip().lower()
        if reponse in ['o', 'oui', 'yes', 'y']:
            try:
                indice_demande = int(input(f"Entrez l'index (0-{len(donnees)-1}) : ").strip())
                if 0 <= indice_demande < len(donnees):
                    valeur = compresseur.get(indice_demande)
                    print(f"  Valeur à l'index {indice_demande} : {valeur}")
                else:
                    print(f"  ❌ Erreur : Index hors limites (0-{len(donnees)-1})")
            except ValueError:
                print("  ❌ Erreur : Index invalide")
        else:
            break


def demonstration_rapide():
    """Effectue une démonstration rapide avec plusieurs exemples de données.
    
    Compare les trois méthodes de compression sur :
    - Des petits entiers positifs
    - Des nombres négatifs
    - Des données avec des valeurs aberrantes (outliers)
    """
    print("\n" + "="*70)
    print(" "*25 + "DÉMONSTRATION RAPIDE")
    print("="*70)
    
    exemples = [
        ("Petits entiers positifs", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ("Avec nombres négatifs", [-10, -5, 0, 5, 10, -3, 7, -20]),
        ("Avec valeurs aberrantes", [1, 2, 3, 4, 5, 10000, 6, 7, 8, 20000]),
    ]
    
    for nom_exemple, donnees_exemple in exemples:
        print(f"\n{'─'*70}")
        print(f"Exemple : {nom_exemple}")
        print(f"Données : {donnees_exemple}")
        print('─'*70)
        
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            donnees_compressees = compresseur.compress(donnees_exemple)
            infos = compresseur.get_info()
            
            print(f"\n  {nom_methode}:")
            print(f"    Taille compressée : {infos['compressed_length']} entiers (ratio : {infos['compression_ratio']:.2f}x)")
            print(f"    Bits/valeur : {infos['bits_per_value']}")


def lancer_benchmarks():
    """Lance les benchmarks de performance du système de compression.
    
    Les benchmarks mesurent :
    - Le temps de compression
    - Le temps de décompression
    - Le temps d'accès aléatoire
    - Les ratios de compression
    - Les seuils de transmission
    """
    print("\n" + "="*70)
    print(" "*25 + "LANCEMENT DES BENCHMARKS")
    print("="*70)
    print("\nCela peut prendre quelques minutes...")
    
    try:
        from src.benchmark import main as benchmark_main
        benchmark_main()
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution des benchmarks : {e}")
        print("Assurez-vous que numpy est installé : pip install numpy")


def lancer_tests():
    """Exécute la suite complète de tests unitaires.
    
    Les tests valident :
    - Les compressions/décompressions
    - L'accès aléatoire aux éléments
    - Les cas limites
    - Les nombres négatifs
    - Différentes distributions de données
    """
    print("\n" + "="*70)
    print(" "*25 + "LANCEMENT DES TESTS")
    print("="*70)
    
    try:
        import pytest
        resultat = pytest.main(["tests/", "-v"])
        if resultat == 0:
            print("\n✓ Tous les tests sont passés!")
        else:
            print(f"\n❌ Certains tests ont échoué (code de sortie : {resultat})")
    except ImportError:
        print("\n❌ Erreur : pytest n'est pas installé.")
        print("Installez-le avec : pip install pytest")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution des tests : {e}")


def afficher_exemples():
    """Affiche des exemples détaillés d'utilisation du système de compression."""
    print("\n" + "="*70)
    print(" "*25 + "EXÉCUTION DES EXEMPLES")
    print("="*70)
    
    try:
        from examples import main as examples_main
        examples_main()
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution des exemples : {e}")


def lancer_interface_graphique():
    """Lance l'interface graphique pour une expérience utilisateur complète.
    
    L'interface graphique offre :
    - Une saisie visuelle des données
    - La compression en temps réel
    - Des graphiques et visualisations
    - La comparaison côte à côte des méthodes
    - Un accès aléatoire interactif
    """
    print("\n" + "="*70)
    print(" "*20 + "LANCEMENT DE L'INTERFACE GRAPHIQUE")
    print("="*70)
    print("\nDémarrage de l'interface graphique...")
    
    try:
        from src.gui import launch_gui as demarrer_gui
        demarrer_gui()
    except ImportError as e:
        print(f"\n❌ Erreur : Les dépendances pour l'interface graphique ne sont pas disponibles.")
        print(f"   {e}")
        print("\nPour utiliser l'interface graphique, assurez-vous que matplotlib est installé :")
        print("   pip install matplotlib")
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement de l'interface graphique : {e}")


def principale():
    """Boucle principale du programme.
    
    Affiche le menu et traite les choix de l'utilisateur jusqu'à la sortie.
    """
    afficher_entete()
    print("\nBienvenue dans le Système de Compression par Bit-Packing!")
    print("Cet outil compresse les tableaux d'entiers pour une transmission efficace.")
    
    while True:
        afficher_menu()
        
        choix = input("\nChoisissez une option (1-7) : ").strip()
        
        if choix == "1":
            compresser_donnees_personnalisees()
        elif choix == "2":
            demonstration_rapide()
        elif choix == "3":
            lancer_benchmarks()
        elif choix == "4":
            lancer_tests()
        elif choix == "5":
            afficher_exemples()
        elif choix == "6":
            lancer_interface_graphique()
        elif choix == "7":
            print("\n" + "="*70)
            print(" "*20 + "Merci d'avoir utilisé notre outil!")
            print("="*70 + "\n")
            sys.exit(0)
        else:
            print("\n❌ Choix invalide. Veuillez entrer un nombre entre 1 et 7.")
        
        input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    """Point d'entrée du programme.
    
    Lance la boucle principale et gère les interruptions de l'utilisateur
    (Ctrl+C) de manière gracieuse.
    """
    try:
        principale()
    except KeyboardInterrupt:
        print("\n\nProgramme interrompu par l'utilisateur.")
        print("À bientôt!\n")
        sys.exit(0)
