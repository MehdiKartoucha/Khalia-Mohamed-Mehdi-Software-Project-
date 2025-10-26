"""
USINE DE CRÉATION DES COMPRESSEURS (Factory Pattern)

Ce module fournit une usine de création pour instancier facilement
les différentes méthodes de compression par bit-packing.

Pattern utilisé : Factory Pattern - crée les objets sans exposer
la logique de création au client.
"""

from src.base_bitpacking import BaseBitPacking
from src.bitpacking_overflow import BitPackingWithOverflow
from src.bitpacking_no_overflow import BitPackingNoOverflow
from src.bitpacking_overflow_area import BitPackingWithOverflowArea


class CompressionFactory:
    """Usine de création des instances de compression.
    
    Cette classe utilise le pattern Factory pour créer les compresseurs
    appropriés selon le type demandé.
    
    Types de compression supportés :
    - "with_overflow" ou "overflow" : Compression maximale avec débordement
    - "no_overflow" ou "without_overflow" : Accès rapide sans débordement
    - "overflow_area" ou "with_overflow_area" : Optimisé pour données mixtes
    """
    
    # Mapping des types de compression vers leurs classes respectives
    COMPRESSION_TYPES = {
        "with_overflow": BitPackingWithOverflow,
        "overflow": BitPackingWithOverflow,
        "no_overflow": BitPackingNoOverflow,
        "without_overflow": BitPackingNoOverflow,
        "overflow_area": BitPackingWithOverflowArea,
        "with_overflow_area": BitPackingWithOverflowArea,
    }
    
    @staticmethod
    def create(compression_type: str, **kwargs) -> BaseBitPacking:
        """Crée une instance de compression du type spécifié.
        
        Args:
            compression_type (str) : Type de compression demandé. Accepte :
                - "with_overflow" / "overflow" : BitPackingWithOverflow
                - "no_overflow" / "without_overflow" : BitPackingNoOverflow
                - "overflow_area" / "with_overflow_area" : BitPackingWithOverflowArea
                
            **kwargs : Arguments additionnels passés au constructeur
                     (ex: percentile_threshold pour overflow_area)
        
        Retourne :
            BaseBitPacking : Instance du compresseur demandé
            
        Lève :
            ValueError : Si le type de compression n'existe pas
            
        Exemples :
            >>> compressor = CompressionFactory.create("with_overflow")
            >>> compressor = CompressionFactory.create("overflow_area", percentile_threshold=0.9)
        """
        # Normalisation du type (minuscules et sans espaces)
        compression_type = compression_type.lower().strip()
        
        # Vérification que le type existe
        if compression_type not in CompressionFactory.COMPRESSION_TYPES:
            types_disponibles = ", ".join(sorted(set(CompressionFactory.COMPRESSION_TYPES.keys())))
            raise ValueError(
                f"Type de compression inconnu : '{compression_type}'. "
                f"Types disponibles : {types_disponibles}"
            )
        
        # Récupération de la classe et création d'une instance
        classe_compression = CompressionFactory.COMPRESSION_TYPES[compression_type]
        return classe_compression(**kwargs)
    
    @staticmethod
    def obtenir_types_disponibles() -> list:
        """Retourne la liste des types de compression disponibles.
        
        Retourne :
            list : Liste des identifiants de type de compression
        """
        return sorted(set(CompressionFactory.COMPRESSION_TYPES.keys()))
    
    # Alias pour compatibilité
    @staticmethod
    def get_available_types() -> list:
        """Alias pour obtenir_types_disponibles (compatibilité anglais)."""
        return CompressionFactory.obtenir_types_disponibles()
    
    @staticmethod
    def obtenir_description_type(type_compression: str) -> str:
        """Retourne une description lisible du type de compression.
        
        Args:
            type_compression (str) : Identifiant du type
            
        Retourne :
            str : Description explicative du type de compression
        """
        descriptions = {
            "with_overflow": "Permet aux valeurs compressées de chevaucher plusieurs entiers consécutifs pour une compression maximale",
            "no_overflow": "Garde les valeurs compressées dans les limites d'un entier unique pour un accès aléatoire rapide",
            "overflow_area": "Stocke les valeurs aberrantes séparément pour une compression optimale avec des plages de valeurs mixtes",
        }
        
        # Normalisation
        type_compression = type_compression.lower().strip()
        
        # Mappage des alias vers les noms canoniques
        canonical = {
            "overflow": "with_overflow",
            "without_overflow": "no_overflow",
            "with_overflow_area": "overflow_area",
        }
        
        type_compression = canonical.get(type_compression, type_compression)
        
        return descriptions.get(type_compression, "Pas de description disponible")


def demonstration():
    """Démonstration d'utilisation de l'usine de création.
    
    Crée des compresseurs de chaque type et affiche leurs performances
    sur un ensemble de données échantillon.
    """
    import random
    
    print("=" * 50)
    print("  DÉMONSTRATION DE L'USINE DE CRÉATION (Factory)")
    print("=" * 50)
    print()
    
    # Génération de données d'exemple
    donnees = [random.randint(0, 100) for element in range(20)]
    print(f"Données originales : {donnees}\n")
    
    # Test de chaque type de compression
    for type_compression in ["with_overflow", "no_overflow", "overflow_area"]:
        print(f"--- {type_compression.upper()} ---")
        
        # Création du compresseur via l'usine
        compresseur = CompressionFactory.create(type_compression)
        
        # Compression et décompression
        donnees_compressees = compresseur.compress(donnees)
        donnees_decompressees = compresseur.decompress(donnees_compressees)
        
        # Affichage des informations
        infos = compresseur.get_info()
        print(f"Taille compressée : {infos['compressed_length']} entiers")
        print(f"Bits par valeur : {infos['bits_per_value']}")
        print(f"Ratio de compression : {infos['compression_ratio']:.2f}x")
        print(f"Décompression correcte : {donnees == donnees_decompressees}")
        print()


if __name__ == "__main__":
    demonstration()
