"""
CLASSE DE BASE ABSTRAITE POUR LA COMPRESSION PAR BIT-PACKING

Ce module fournit la classe abstraite de base que tous les algorithmes
de compression par bit-packing doivent implémenter.

Il définit l'interface commune et fournit des méthodes utilitaires pour :
- L'encodage/décodage ZigZag (gestion des nombres négatifs)
- Le calcul des bits nécessaires
- L'accès aux métadonnées de compression
"""

from abc import ABC, abstractmethod
from typing import List


class BaseBitPacking(ABC):
    """Classe de base abstraite pour les algorithmes de compression.
    
    Toutes les implémentations doivent fournir :
    - Une méthode compress() : compresse les données
    - Une méthode decompress() : restaure les données d'origine
    - Une méthode get() : accès direct sans décompression complète
    
    Cette architecture permet l'accès aléatoire même aux données compressées.
    """
    
    def __init__(self):
        """Initialise le compresseur par bit-packing."""
        self.donnees_compressees: List[int] = []  # Les données après compression
        self.longueur_originale: int = 0          # Nombre d'éléments d'origine
        self.bits_par_valeur: int = 0             # Bits utilisés par valeur
        self.donnees_originales: List[int] = []   # Les données avant compression
    
    @abstractmethod
    def compress(self, donnees: List[int]) -> List[int]:
        """Compresse un tableau d'entiers par bit-packing.
        
        Args:
            donnees : Liste d'entiers à compresser
            
        Retourne :
            Liste d'entiers compressés
        """
        pass
    
    @abstractmethod
    def decompress(self, compressees: List[int]) -> List[int]:
        """Décompresse un tableau pour restaurer les données d'origine.
        
        Args:
            compressees : Liste d'entiers compressés
            
        Retourne :
            Liste d'entiers restaurés (identiques aux données d'origine)
        """
        pass
    
    @abstractmethod
    def get(self, indice: int) -> int:
        """Récupère la valeur à un indice sans décompression complète.
        
        Cette méthode est optimisée pour l'accès aléatoire rapide
        aux éléments même dans la forme compressée.
        
        Args:
            indice : Position de l'élément à récupérer (0-based)
            
        Retourne :
            La valeur entière à cette position
            
        Lève :
            IndexError : Si l'indice est en dehors des limites
        """
        pass
    
    def _calculer_bits_necessaires(self, donnees: List[int]) -> int:
        """Calcule le nombre minimal de bits nécessaires pour représenter toutes les valeurs.
        
        Exemple :
        - Valeurs [0, 1, 2, 3] : besoin de 2 bits (max = 11 en binaire)
        - Valeurs [0, 255] : besoin de 8 bits (max = 11111111 en binaire)
        
        Args:
            donnees : Liste d'entiers (doivent être positifs après encodage)
            
        Retourne :
            Nombre de bits nécessaire pour le plus grand élément
        """
        if not donnees:
            return 0
        
        valeur_max = max(donnees)
        if valeur_max == 0:
            return 1
        
        # Obtient la longueur en bits du nombre maximal
        bits = valeur_max.bit_length()
        return bits
    
    def _encoder_zigzag(self, valeur: int) -> int:
        """Encode un entier signé en utilisant le codage ZigZag.
        
        Le codage ZigZag mappe les entiers signés vers les entiers non-signés :
        Exemples :
        - 0 -> 0
        - -1 -> 1
        - 1 -> 2
        - -2 -> 3
        - 2 -> 4
        - ... etc
        
        Ceci permet de traiter efficacement les nombres négatifs
        en utilisant moins de bits.
        
        Args:
            valeur : Entier signé à encoder
            
        Retourne :
            Entier non-signé (encodé ZigZag)
        """
        if valeur >= 0:
            return valeur << 1
        else:
            return (-valeur << 1) - 1
    
    def _decoder_zigzag(self, valeur: int) -> int:
        """Décode un entier encodé ZigZag vers un entier signé.
        
        Inverse la transformation _encoder_zigzag().
        
        Args:
            valeur : Entier non-signé (encodé ZigZag)
            
        Retourne :
            Entier signé décodé
        """
        return (valeur >> 1) ^ (-(valeur & 1))
    
    def _encoder_donnees(self, donnees: List[int]) -> List[int]:
        """Encode les données en utilisant le codage ZigZag.
        
        Utile pour gérer les nombres négatifs de manière efficace.
        
        Args:
            donnees : Liste d'entiers signés
            
        Retourne :
            Liste d'entiers non-signés (encodés ZigZag)
        """
        return [self._encoder_zigzag(valeur) for valeur in donnees]
    
    def _decoder_donnees(self, donnees: List[int]) -> List[int]:
        """Décode les données ZigZag vers des entiers signés.
        
        Restaure les entiers signés d'origine.
        
        Args:
            donnees : Liste d'entiers non-signés (encodés ZigZag)
            
        Retourne :
            Liste d'entiers signés décodés
        """
        return [self._decoder_zigzag(valeur) for valeur in donnees]
    
    def obtenir_ratio_compression(self) -> float:
        """Calcule le ratio de compression (original / compressé).
        
        Exemple : ratio de 4.0x signifie que les données d'origine
        occupaient 4 fois plus d'espace que la version compressée.
        
        Retourne :
            Ratio de compression en tant que nombre décimal
        """
        if not self.donnees_compressees:
            return 0.0
        
        bits_originaux = self.longueur_originale * 32
        bits_compresses = len(self.donnees_compressees) * 32
        
        return bits_originaux / bits_compresses if bits_compresses > 0 else 0.0
    
    def obtenir_infos(self) -> dict:
        """Obtient les informations complètes sur l'état de compression.
        
        Retourne :
            Dictionnaire contenant les métadonnées de compression
        """
        return {
            "original_length": self.longueur_originale,
            "compressed_length": len(self.donnees_compressees),
            "bits_per_value": self.bits_par_valeur,
            "compression_ratio": self.obtenir_ratio_compression(),
            "original_bits": self.longueur_originale * 32,
            "compressed_bits": len(self.donnees_compressees) * 32
        }
    
    # ========== ALIASES POUR COMPATIBILITÉ ==========
    # Permet à l'ancien code en anglais de fonctionner avec les nouvelles méthodes
    
    # Attributs
    @property
    def compressed_data(self):
        """Alias pour donnees_compressees (compatibilité)."""
        return self.donnees_compressees
    
    @compressed_data.setter
    def compressed_data(self, valeur):
        """Setter pour compressed_data (compatibilité)."""
        self.donnees_compressees = valeur
    
    @property
    def original_length(self):
        """Alias pour longueur_originale (compatibilité)."""
        return self.longueur_originale
    
    @original_length.setter
    def original_length(self, valeur):
        """Setter pour original_length (compatibilité)."""
        self.longueur_originale = valeur
    
    @property
    def bits_per_value(self):
        """Alias pour bits_par_valeur (compatibilité)."""
        return self.bits_par_valeur
    
    @bits_per_value.setter
    def bits_per_value(self, valeur):
        """Setter pour bits_per_value (compatibilité)."""
        self.bits_par_valeur = valeur
    
    @property
    def original_data(self):
        """Alias pour donnees_originales (compatibilité)."""
        return self.donnees_originales
    
    @original_data.setter
    def original_data(self, valeur):
        """Setter pour original_data (compatibilité)."""
        self.donnees_originales = valeur
    
    # Méthodes (anciennes implémentations en anglais -> noms français)
    def _calculate_bits_needed(self, donnees: List[int]) -> int:
        """Alias pour _calculer_bits_necessaires (compatibilité)."""
        return self._calculer_bits_necessaires(donnees)
    
    def _zigzag_encode(self, valeur: int) -> int:
        """Alias pour _encoder_zigzag (compatibilité)."""
        return self._encoder_zigzag(valeur)
    
    def _zigzag_decode(self, valeur: int) -> int:
        """Alias pour _decoder_zigzag (compatibilité)."""
        return self._decoder_zigzag(valeur)
    
    def _encode_data(self, donnees: List[int]) -> List[int]:
        """Alias pour _encoder_donnees (compatibilité)."""
        return self._encoder_donnees(donnees)
    
    def _decode_data(self, donnees: List[int]) -> List[int]:
        """Alias pour _decoder_donnees (compatibilité)."""
        return self._decoder_donnees(donnees)
    
    # Alias pour compatibilité (français et anglais)
    get_compression_ratio = obtenir_ratio_compression
    get_info = obtenir_infos
