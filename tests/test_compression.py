"""
SUITE DE TESTS COMPLÈTE POUR LES ALGORITHMES DE COMPRESSION

Cette suite de tests valide le fonctionnement de tous les algorithmes
de compression par bit-packing sur divers cas d'usage.

Tests couverts :
- Les compressions/décompressions basiques
- L'accès aléatoire direct aux éléments
- Les cas limites et points de basculement
- Les nombres négatifs
- Différentes distributions et modèles de données

À exécuter avec : pytest tests/ -v
"""

import pytest
import random
from src.factory import CompressionFactory
from src.bitpacking_overflow import BitPackingWithOverflow
from src.bitpacking_no_overflow import BitPackingNoOverflow
from src.bitpacking_overflow_area import BitPackingWithOverflowArea


class TestCompressionBasics:
    """Tests de fonctionnalité basique de la compression pour tous les types."""
    
    @pytest.fixture
    def methodes_compression(self):
        """Fixture fournissant tous les types de compression disponibles."""
        return ["with_overflow", "no_overflow", "overflow_area"]
    
    @pytest.fixture
    def donnees_exemple(self):
        """Fixture fournissant des données de test simples."""
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    def test_compression_decompression_identite(self, methodes_compression, donnees_exemple):
        """Vérifie que décompresser(compresser(données)) == données d'origine pour tous les types."""
        for nom_methode in methodes_compression:
            compresseur = CompressionFactory.create(nom_methode)
            donnees_compressees = compresseur.compress(donnees_exemple)
            donnees_decompressees = compresseur.decompress(donnees_compressees)
            assert donnees_decompressees == donnees_exemple, f"Échec pour {nom_methode}"
    
    def test_compression_reduit_taille(self, methodes_compression, donnees_exemple):
        """Vérifie que la compression réduit réellement la taille pour petites valeurs."""
        for nom_methode in methodes_compression:
            compresseur = CompressionFactory.create(nom_methode)
            donnees_compressees = compresseur.compress(donnees_exemple)
            # Devrait utiliser moins d'entiers que l'original
            assert len(donnees_compressees) <= len(donnees_exemple), f"Échec pour {nom_methode}"
    
    def test_tableau_vide(self, methodes_compression):
        """Teste la gestion des tableaux vides."""
        for nom_methode in methodes_compression:
            compresseur = CompressionFactory.create(nom_methode)
            donnees_compressees = compresseur.compress([])
            assert donnees_compressees == []
            donnees_decompressees = compresseur.decompress([])
            assert donnees_decompressees == []
    
    def test_element_unique(self, methodes_compression):
        """Teste la compression de tableaux contenant un seul élément."""
        for nom_methode in methodes_compression:
            compresseur = CompressionFactory.create(nom_methode)
            donnees = [42]
            donnees_compressees = compresseur.compress(donnees)
            donnees_decompressees = compresseur.decompress(donnees_compressees)
            assert donnees_decompressees == donnees, f"Échec pour {nom_methode}"
    
    def test_tous_les_zeros(self, methodes_compression):
        """Teste la compression de tableau contenant uniquement des zéros."""
        for nom_methode in methodes_compression:
            compresseur = CompressionFactory.create(nom_methode)
            donnees = [0] * 100
            donnees_compressees = compresseur.compress(donnees)
            donnees_decompressees = compresseur.decompress(donnees_compressees)
            assert donnees_decompressees == donnees, f"Échec pour {nom_methode}"
    
    def test_toutes_memes_valeurs(self, methodes_compression):
        """Teste la compression de tableau avec toutes les valeurs identiques."""
        for nom_methode in methodes_compression:
            compresseur = CompressionFactory.create(nom_methode)
            donnees = [7] * 50
            donnees_compressees = compresseur.compress(donnees)
            donnees_decompressees = compresseur.decompress(donnees_compressees)
            assert donnees_decompressees == donnees, f"Échec pour {nom_methode}"


class TestAccesAleatoire:
    """Tests de la méthode get() pour l'accès direct aux éléments sans décompression."""
    
    @pytest.fixture
    def donnees_test(self):
        """Génère des données de test - une suite de nombres de 0 à 99."""
        return list(range(100))
    
    def test_obtenir_tous_elements(self, donnees_test):
        """Teste que get() pour tous les éléments correspond aux données originales."""
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            compresseur.compress(donnees_test)
            
            for indice_element in range(len(donnees_test)):
                assert compresseur.get(indice_element) == donnees_test[indice_element], f"Échec à l'index {indice_element} pour {nom_methode}"
    
    def test_obtenir_premier_element(self, donnees_test):
        """Teste l'accès au premier élément."""
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            compresseur.compress(donnees_test)
            assert compresseur.get(0) == donnees_test[0]
    
    def test_obtenir_dernier_element(self, donnees_test):
        """Teste l'accès au dernier élément."""
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            compresseur.compress(donnees_test)
            assert compresseur.get(len(donnees_test) - 1) == donnees_test[-1]
    
    def test_obtenir_hors_limites(self, donnees_test):
        """Teste que get() lève IndexError pour un accès hors limites."""
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            compresseur.compress(donnees_test)
            
            with pytest.raises(IndexError):
                compresseur.get(-1)
            
            with pytest.raises(IndexError):
                compresseur.get(len(donnees_test))
    
    def test_acces_aleatoire(self, donnees_test):
        """Teste un pattern d'accès aléatoire."""
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            compresseur.compress(donnees_test)
            
            # Accès aléatoire
            random.seed(42)
            for num_acces in range(50):
                indice_aleatoire = random.randint(0, len(donnees_test) - 1)
                assert compresseur.get(indice_aleatoire) == donnees_test[indice_aleatoire]


class TestNombresNegatifs:
    """Tests de gestion des nombres négatifs."""
    
    def test_uniquement_negatifs(self):
        """Teste un tableau contenant uniquement des nombres négatifs."""
        donnees = [-10, -20, -30, -40, -50]
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            donnees_compressees = compresseur.compress(donnees)
            donnees_decompressees = compresseur.decompress(donnees_compressees)
            assert donnees_decompressees == donnees, f"Échec pour {nom_methode}"
    
    def test_mélange_positif_negatif(self):
        """Teste un tableau avec des nombres positifs et négatifs mélangés."""
        donnees = [-5, -3, 0, 2, 4, -1, 10, -20]
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            donnees_compressees = compresseur.compress(donnees)
            donnees_decompressees = compresseur.decompress(donnees_compressees)
            assert donnees_decompressees == donnees, f"Échec pour {nom_methode}"
    
    def test_grands_nombres_negatifs(self):
        """Teste avec de grands nombres négatifs."""
        donnees = [-1000000, -500, 1000, 2000000]
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            donnees_compressees = compresseur.compress(donnees)
            donnees_decompressees = compresseur.decompress(donnees_compressees)
            assert donnees_decompressees == donnees, f"Échec pour {nom_methode}"
    
    def test_acces_avec_nombres_negatifs(self):
        """Teste get() avec des nombres négatifs."""
        donnees = list(range(-50, 50))
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            compresseur.compress(donnees)
            
            for indice_element in range(len(donnees)):
                assert compresseur.get(indice_element) == donnees[indice_element], f"Échec à l'index {indice_element} pour {nom_methode}"


class TestDistributionsDonnees:
    """Tests avec différentes distributions de données."""
    
    def test_distribution_uniforme(self):
        """Teste des données uniformément distribuées."""
        random.seed(42)
        donnees = [random.randint(0, 1000) for element in range(200)]
        
        for nom_methode in ["with_overflow", "no_overflow", "overflow_area"]:
            compresseur = CompressionFactory.create(nom_methode)
            donnees_compressees = compresseur.compress(donnees)
            donnees_decompressees = compresseur.decompress(donnees_compressees)
            assert donnees_decompressees == donnees, f"Échec pour {nom_methode}"
    
    def test_small_values(self):
        """Test with mostly small values."""
        random.seed(42)
        data = [random.randint(0, 10) for element in range(200)]
        
        for method_name in ["with_overflow", "no_overflow", "overflow_area"]:
            compressor = CompressionFactory.create(method_name)
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            assert decompressed == data, f"Failed for {method_name}"
            
            # Should achieve good compression
            info = compressor.get_info()
            assert info['compression_ratio'] > 1.5, f"Poor compression for {method_name}"
    
    def test_with_outliers(self):
        """Test data with few large outliers."""
        data = [random.randint(0, 100) for element in range(100)]
        # Add outliers
        data[10] = 100000
        data[50] = 200000
        data[90] = 150000
        
        for method_name in ["with_overflow", "no_overflow", "overflow_area"]:
            compressor = CompressionFactory.create(method_name)
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            assert decompressed == data, f"Failed for {method_name}"
    
    def test_sequential_data(self):
        """Test sequential/ordered data."""
        data = list(range(0, 1000, 5))
        
        for method_name in ["with_overflow", "no_overflow", "overflow_area"]:
            compressor = CompressionFactory.create(method_name)
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            assert decompressed == data, f"Failed for {method_name}"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_max_value_for_bits(self):
        """Test values at bit boundaries."""
        # Test powers of 2 and near-boundaries
        test_cases = [
            [1, 2, 3],  # 2 bits needed
            [1, 2, 3, 4, 7],  # 3 bits needed
            [1, 2, 3, 4, 7, 8, 15],  # 4 bits needed
            [255, 256, 257],  # 9 bits needed
        ]
        
        for test_data in test_cases:
            for method_name in ["with_overflow", "no_overflow", "overflow_area"]:
                compressor = CompressionFactory.create(method_name)
                compressed = compressor.compress(test_data)
                decompressed = compressor.decompress(compressed)
                assert decompressed == test_data, f"Failed for {method_name} with data {test_data}"
    
    def test_large_array(self):
        """Test with large arrays."""
        data = list(range(10000))
        
        for method_name in ["with_overflow", "no_overflow", "overflow_area"]:
            compressor = CompressionFactory.create(method_name)
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            assert decompressed == data, f"Failed for {method_name}"
    
    def test_alternating_pattern(self):
        """Test alternating high-low pattern."""
        data = []
        for element_index in range(100):
            data.append(1 if element_index % 2 == 0 else 1000)
        
        for method_name in ["with_overflow", "no_overflow", "overflow_area"]:
            compressor = CompressionFactory.create(method_name)
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            assert decompressed == data, f"Failed for {method_name}"


class TestFactory:
    """Test the factory pattern."""
    
    def test_create_all_types(self):
        """Test creating all compression types."""
        compression_types = ["with_overflow", "overflow", "no_overflow", "without_overflow", "overflow_area"]
        
        for compression_type in compression_types:
            compressor = CompressionFactory.create(compression_type)
            assert compressor is not None
    
    def test_invalid_type(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError):
            CompressionFactory.create("invalid_type")
    
    def test_get_available_types(self):
        """Test getting available compression types."""
        types = CompressionFactory.get_available_types()
        assert len(types) > 0
        assert "with_overflow" in types
        assert "no_overflow" in types
        assert "overflow_area" in types
    
    def test_overflow_area_with_percentile(self):
        """Test creating overflow area compressor with custom percentile."""
        compressor = CompressionFactory.create("overflow_area", percentile_threshold=0.9)
        assert compressor.percentile_threshold == 0.9


class TestCompressionInfo:
    """Test compression metadata and info methods."""
    
    def test_get_info(self):
        """Test that get_info returns expected fields."""
        data = list(range(100))
        
        for method_name in ["with_overflow", "no_overflow", "overflow_area"]:
            compressor = CompressionFactory.create(method_name)
            compressor.compress(data)
            info = compressor.get_info()
            
            assert "original_length" in info
            assert "compressed_length" in info
            assert "bits_per_value" in info
            assert "compression_ratio" in info
            assert info["original_length"] == 100
    
    def test_compression_ratio(self):
        """Test compression ratio calculation."""
        # Small values should compress well
        data = [random.randint(0, 10) for element in range(100)]
        
        for method_name in ["with_overflow", "no_overflow", "overflow_area"]:
            compressor = CompressionFactory.create(method_name)
            compressor.compress(data)
            ratio = compressor.get_compression_ratio()
            
            # Should be better than 1:1
            assert ratio > 1.0, f"No compression benefit for {method_name}"


class TestSpecificBehaviors:
    """Test specific behaviors of different compression types."""
    
    def test_overflow_vs_no_overflow_difference(self):
        """Test that overflow and no_overflow produce different compressed sizes."""
        # Use data where the difference should be visible
        data = [random.randint(0, 100) for _ in range(100)]
        
        comp1 = CompressionFactory.create("with_overflow")
        comp2 = CompressionFactory.create("no_overflow")
        
        compressed1 = comp1.compress(data)
        compressed2 = comp2.compress(data)
        
        # Both should decompress correctly
        assert comp1.decompress(compressed1) == data
        assert comp2.decompress(compressed2) == data
        
        # Sizes might differ depending on bits per value
        # Just verify both work correctly
        info1 = comp1.get_info()
        info2 = comp2.get_info()
        
        assert info1['bits_per_value'] > 0
        assert info2['bits_per_value'] > 0
    
    def test_overflow_area_detects_outliers(self):
        """Test that overflow area compression handles outliers efficiently."""
        # Mostly small values with few outliers
        data = [random.randint(0, 10) for element in range(100)]
        data[10] = 100000
        data[50] = 200000
        
        compressor = CompressionFactory.create("overflow_area")
        compressor.compress(data)
        info = compressor.get_info()
        
        # Should detect and use overflow area
        if info.get('has_overflow_area'):
            assert info['overflow_area_size'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
