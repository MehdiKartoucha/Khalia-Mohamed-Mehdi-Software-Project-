"""
Example usage of the BitPacking compression library.

This script demonstrates various use cases and features.
"""

from src.factory import CompressionFactory
import random


def example_basic_usage():
    """Basic compression and decompression."""
    print("="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)
    
    # Create sample data
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"Original data: {data}")
    
    # Create compressor
    compressor = CompressionFactory.create("with_overflow")
    
    # Compress
    compressed = compressor.compress(data)
    print(f"Compressed: {compressed}")
    print(f"Original length: {len(data)} integers")
    print(f"Compressed length: {len(compressed)} integers")
    
    # Decompress
    decompressed = compressor.decompress(compressed)
    print(f"Decompressed: {decompressed}")
    print(f"Match: {data == decompressed}")
    print()


def example_random_access():
    """Demonstrate direct element access without full decompression."""
    print("="*60)
    print("EXAMPLE 2: Random Access (get method)")
    print("="*60)
    
    data = list(range(0, 100, 2))  # [0, 2, 4, 6, ..., 98]
    print(f"Data: [0, 2, 4, ..., 98] ({len(data)} elements)")
    
    compressor = CompressionFactory.create("with_overflow")
    compressor.compress(data)
    
    # Access individual elements
    print(f"Element at index 0: {compressor.get(0)}")
    print(f"Element at index 10: {compressor.get(10)}")
    print(f"Element at index 25: {compressor.get(25)}")
    print(f"Element at index 49: {compressor.get(49)}")
    print()


def example_negative_numbers():
    """Handle negative numbers with ZigZag encoding."""
    print("="*60)
    print("EXAMPLE 3: Negative Numbers")
    print("="*60)
    
    data = [-10, -5, 0, 5, 10, -3, 7, -20]
    print(f"Original data: {data}")
    
    compressor = CompressionFactory.create("with_overflow")
    compressed = compressor.compress(data)
    decompressed = compressor.decompress(compressed)
    
    print(f"Compressed length: {len(compressed)} integers")
    print(f"Decompressed: {decompressed}")
    print(f"Match: {data == decompressed}")
    print()


def example_compare_methods():
    """Compare all three compression methods."""
    print("="*60)
    print("EXAMPLE 4: Comparing Compression Methods")
    print("="*60)
    
    # Generate test data
    random.seed(42)
    data = [random.randint(0, 100) for element in range(100)]
    
    print(f"Data: 100 random integers (0-100)")
    print(f"Original size: 100 integers = 3200 bits\n")
    
    methods = ["with_overflow", "no_overflow", "overflow_area"]
    
    for method_name in methods:
        compressor = CompressionFactory.create(method_name)
        compressed = compressor.compress(data)
        info = compressor.get_info()
        
        print(f"--- {method_name.upper()} ---")
        print(f"  Compressed size: {info['compressed_length']} integers")
        print(f"  Bits per value: {info['bits_per_value']}")
        print(f"  Compression ratio: {info['compression_ratio']:.2f}x")
        print(f"  Total compressed bits: {info['compressed_bits']}")
        print()


def example_with_outliers():
    """Demonstrate overflow area efficiency with outliers."""
    print("="*60)
    print("EXAMPLE 5: Handling Outliers")
    print("="*60)
    
    # Create data with outliers
    data = [random.randint(0, 10) for element in range(100)]
    data[25] = 100000
    data[50] = 200000
    data[75] = 150000
    
    print("Data: 100 values")
    print("  - 97 values in range [0, 10]")
    print("  - 3 outliers: 100000, 200000, 150000\n")
    
    # Compare regular vs overflow area
    methods = ["with_overflow", "overflow_area"]
    
    for method_name in methods:
        compressor = CompressionFactory.create(method_name)
        compressed = compressor.compress(data)
        info = compressor.get_info()
        
        print(f"--- {method_name.upper()} ---")
        print(f"  Bits per value: {info['bits_per_value']}")
        print(f"  Compressed size: {info['compressed_length']} integers")
        print(f"  Compression ratio: {info['compression_ratio']:.2f}x")
        
        if 'has_overflow_area' in info and info['has_overflow_area']:
            print(f"  Overflow area used: YES")
            print(f"  Overflow area size: {info['overflow_area_size']} integers")
        else:
            print(f"  Overflow area used: NO")
        print()


def example_large_dataset():
    """Work with larger datasets."""
    print("="*60)
    print("EXAMPLE 6: Large Dataset")
    print("="*60)
    
    # Generate large dataset
    data = [random.randint(0, 1000) for element in range(10000)]
    print(f"Data: 10,000 random integers (0-1000)")
    print(f"Original size: 10,000 integers = 320,000 bits\n")
    
    compressor = CompressionFactory.create("with_overflow")
    compressed = compressor.compress(data)
    
    info = compressor.get_info()
    print(f"Compressed size: {info['compressed_length']} integers")
    print(f"Compressed bits: {info['compressed_bits']}")
    print(f"Bits per value: {info['bits_per_value']}")
    print(f"Compression ratio: {info['compression_ratio']:.2f}x")
    
    # Verify random access
    test_indices = [0, 100, 1000, 5000, 9999]
    print(f"\nRandom access test:")
    all_match = True
    for test_index in test_indices:
        retrieved = compressor.get(test_index)
        if retrieved != data[test_index]:
            all_match = False
            print(f"  Index {test_index}: MISMATCH")
        else:
            print(f"  Index {test_index}: ✓")
    
    print(f"\nAll accesses correct: {all_match}")
    print()


def example_custom_overflow_threshold():
    """Use custom overflow threshold."""
    print("="*60)
    print("EXAMPLE 7: Custom Overflow Threshold")
    print("="*60)
    
    data = [random.randint(0, 100) for element in range(100)]
    # Add some outliers
    for outlier_index in range(0, 100, 10):
        data[outlier_index] = random.randint(1000, 10000)
    
    print("Data: 100 values with 10 outliers\n")
    
    # Try different thresholds
    thresholds = [0.85, 0.90, 0.95]
    
    for threshold_value in thresholds:
        compressor = CompressionFactory.create("overflow_area", percentile_threshold=threshold_value)
        compressed = compressor.compress(data)
        info = compressor.get_info()
        
        print(f"Threshold: {threshold_value*100}%")
        print(f"  Compressed size: {info['compressed_length']} integers")
        print(f"  Compression ratio: {info['compression_ratio']:.2f}x")
        if info.get('has_overflow_area'):
            print(f"  Overflow items: {info['overflow_area_size']}")
        print()


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("BIT PACKING COMPRESSION - EXAMPLES")
    print("="*60 + "\n")
    
    example_basic_usage()
    example_random_access()
    example_negative_numbers()
    example_compare_methods()
    example_with_outliers()
    example_large_dataset()
    example_custom_overflow_threshold()
    
    print("="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
