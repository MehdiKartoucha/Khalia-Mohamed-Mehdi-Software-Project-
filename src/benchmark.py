"""
Comprehensive benchmarking system for compression algorithms.

This module provides tools to measure performance and calculate transmission
time thresholds for different compression methods.
"""

import time
import random
import numpy as np
from typing import List, Dict, Tuple, Callable
from src.factory import CompressionFactory
from src.base_bitpacking import BaseBitPacking


class BenchmarkTimer:
    """Context manager for precise timing measurements."""
    
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.elapsed = 0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time


class CompressionBenchmark:
    """
    Benchmark suite for compression algorithms.
    
    Measures:
    - Compression time
    - Decompression time
    - Random access time (get method)
    - Compression ratio
    - Transmission time analysis
    """
    
    def __init__(self, num_iterations: int = 100):
        """
        Initialize the benchmark.
        
        Args:
            num_iterations: Number of iterations for timing measurements
        """
        self.num_iterations = num_iterations
        self.results = {}
    
    def generate_test_data(self, size: int, data_type: str = "uniform") -> List[int]:
        """
        Generate test data with different distributions.
        
        Args:
            size: Number of elements
            data_type: Type of data distribution:
                - "uniform": Uniformly distributed values
                - "small": Mostly small values
                - "mixed": Mix of small and large values
                - "outliers": Mostly small with few large outliers
                - "negative": Mix of positive and negative values
        
        Returns:
            List of test integers
        """
        if data_type == "uniform":
            return [random.randint(0, 1000) for element in range(size)]
        
        elif data_type == "small":
            return [random.randint(0, 100) for element in range(size)]
        
        elif data_type == "mixed":
            data = []
            for element in range(size):
                if random.random() < 0.5:
                    data.append(random.randint(0, 100))
                else:
                    data.append(random.randint(1000, 10000))
            return data
        
        elif data_type == "outliers":
            data = [random.randint(0, 100) for element in range(size)]
            # Add a few outliers
            num_outliers = max(1, size // 20)
            for outlier_num in range(num_outliers):
                random_index = random.randint(0, size - 1)
                data[random_index] = random.randint(10000, 100000)
            return data
        
        elif data_type == "negative":
            return [random.randint(-1000, 1000) for element in range(size)]
        
        else:
            raise ValueError(f"Unknown data type: {data_type}")
    
    def benchmark_compression(self, compressor: BaseBitPacking, data: List[int]) -> Dict:
        """
        Benchmark compression operation.
        
        Args:
            compressor: Compression instance
            data: Data to compress
        
        Returns:
            Dictionary with timing results
        """
        times = []
        
        for iteration in range(self.num_iterations):
            # Create fresh compressor instance
            compressor_type = type(compressor).__name__
            fresh_compressor = CompressionFactory.create(
                "with_overflow" if "Overflow" in compressor_type and "Area" not in compressor_type
                else "no_overflow" if "NoOverflow" in compressor_type
                else "overflow_area"
            )
            
            with BenchmarkTimer() as timer:
                fresh_compressor.compress(data)
            times.append(timer.elapsed)
        
        return {
            "mean": np.mean(times),
            "std": np.std(times),
            "min": np.min(times),
            "max": np.max(times),
            "median": np.median(times)
        }
    
    def benchmark_decompression(self, compressor: BaseBitPacking, compressed: List[int]) -> Dict:
        """
        Benchmark decompression operation.
        
        Args:
            compressor: Compression instance (already compressed)
            compressed: Compressed data
        
        Returns:
            Dictionary with timing results
        """
        times = []
        
        for iteration in range(self.num_iterations):
            with BenchmarkTimer() as timer:
                compressor.decompress(compressed)
            times.append(timer.elapsed)
        
        return {
            "mean": np.mean(times),
            "std": np.std(times),
            "min": np.min(times),
            "max": np.max(times),
            "median": np.median(times)
        }
    
    def benchmark_random_access(self, compressor: BaseBitPacking, data: List[int], num_accesses: int = 100) -> Dict:
        """
        Benchmark random access (get method).
        
        Args:
            compressor: Compression instance (already compressed)
            data: Original data
            num_accesses: Number of random accesses to perform
        
        Returns:
            Dictionary with timing results
        """
        times = []
        indices = [random.randint(0, len(data) - 1) for access_num in range(num_accesses)]
        
        for index in indices:
            with BenchmarkTimer() as timer:
                compressor.get(index)
            times.append(timer.elapsed)
        
        return {
            "mean": np.mean(times),
            "std": np.std(times),
            "min": np.min(times),
            "max": np.max(times),
            "median": np.median(times)
        }
    
    def calculate_transmission_threshold(
        self,
        compress_time: float,
        decompress_time: float,
        compression_ratio: float,
        data_size_bits: int
    ) -> float:
        """
        Calculate the latency threshold at which compression becomes worthwhile.
        
        Transmission time without compression: T1 = data_size_bits / bandwidth
        Transmission time with compression: T2 = (data_size_bits / compression_ratio) / bandwidth
        Total time with compression: T_total = compress_time + T2 + decompress_time
        
        Compression is worthwhile when:
        T_total < T1
        compress_time + T2 + decompress_time < T1
        compress_time + decompress_time < T1 - T2
        compress_time + decompress_time < data_size_bits / bandwidth * (1 - 1/compression_ratio)
        
        bandwidth = data_size_bits * (1 - 1/compression_ratio) / (compress_time + decompress_time)
        
        For latency t (seconds), bandwidth = data_size_bits / t
        
        Solving for t:
        t > (compress_time + decompress_time) / (1 - 1/compression_ratio)
        
        Args:
            compress_time: Time to compress (seconds)
            decompress_time: Time to decompress (seconds)
            compression_ratio: Compression ratio (original_size / compressed_size)
            data_size_bits: Size of original data in bits
        
        Returns:
            Minimum latency (seconds) for compression to be worthwhile
        """
        if compression_ratio <= 1.0:
            return float('inf')  # No compression benefit
        
        # Time saved by compression
        compression_benefit = 1 - (1 / compression_ratio)
        
        if compression_benefit <= 0:
            return float('inf')
        
        # Threshold latency
        threshold = (compress_time + decompress_time) / compression_benefit
        
        return threshold
    
    def run_full_benchmark(self, data: List[int], compression_type: str) -> Dict:
        """
        Run complete benchmark for a compression type.
        
        Args:
            data: Test data
            compression_type: Type of compression to benchmark
        
        Returns:
            Dictionary with all benchmark results
        """
        print(f"\nBenchmarking {compression_type}...")
        
        # Create compressor
        compressor = CompressionFactory.create(compression_type)
        
        # Compress
        compressed = compressor.compress(data)
        info = compressor.get_info()
        
        # Benchmark compression
        compress_results = self.benchmark_compression(compressor, data)
        
        # Benchmark decompression
        decompress_results = self.benchmark_decompression(compressor, compressed)
        
        # Benchmark random access
        access_results = self.benchmark_random_access(compressor, data)
        
        # Calculate transmission threshold
        data_size_bits = len(data) * 32
        threshold = self.calculate_transmission_threshold(
            compress_results['mean'],
            decompress_results['mean'],
            info['compression_ratio'],
            data_size_bits
        )
        
        return {
            "compression_type": compression_type,
            "data_size": len(data),
            "compressed_size": len(compressed),
            "compression_ratio": info['compression_ratio'],
            "bits_per_value": info['bits_per_value'],
            "compression_time": compress_results,
            "decompression_time": decompress_results,
            "random_access_time": access_results,
            "transmission_threshold_seconds": threshold,
            "transmission_threshold_ms": threshold * 1000
        }
    
    def compare_all_methods(self, data: List[int]) -> Dict:
        """
        Compare all compression methods on the same data.
        
        Args:
            data: Test data
        
        Returns:
            Dictionary with comparison results
        """
        compression_methods = ["with_overflow", "no_overflow", "overflow_area"]
        results = {}
        
        for method_name in compression_methods:
            results[method_name] = self.run_full_benchmark(data, method_name)
        
        return results
    
    def print_results(self, results: Dict):
        """
        Pretty print benchmark results.
        
        Args:
            results: Results dictionary from run_full_benchmark or compare_all_methods
        """
        print("\n" + "="*80)
        print("BENCHMARK RESULTS")
        print("="*80)
        
        if "compression_type" in results:
            # Single result
            self._print_single_result(results)
        else:
            # Multiple results
            for method_name, method_result in results.items():
                print(f"\n{'─'*80}")
                print(f"Method: {method_name.upper()}")
                print('─'*80)
                self._print_single_result(method_result)
    
    def _print_single_result(self, result: Dict):
        """Print a single benchmark result."""
        print(f"\nData size: {result['data_size']} elements")
        print(f"Compressed size: {result['compressed_size']} elements")
        print(f"Compression ratio: {result['compression_ratio']:.2f}x")
        print(f"Bits per value: {result['bits_per_value']}")
        
        print(f"\nCompression time:")
        print(f"  Mean: {result['compression_time']['mean']*1e6:.2f} µs")
        print(f"  Std:  {result['compression_time']['std']*1e6:.2f} µs")
        
        print(f"\nDecompression time:")
        print(f"  Mean: {result['decompression_time']['mean']*1e6:.2f} µs")
        print(f"  Std:  {result['decompression_time']['std']*1e6:.2f} µs")
        
        print(f"\nRandom access time:")
        print(f"  Mean: {result['random_access_time']['mean']*1e6:.2f} µs")
        print(f"  Std:  {result['random_access_time']['std']*1e6:.2f} µs")
        
        if result['transmission_threshold_ms'] != float('inf'):
            print(f"\nTransmission threshold: {result['transmission_threshold_ms']:.2f} ms")
            print(f"  (Compression worthwhile when latency > {result['transmission_threshold_ms']:.2f} ms)")
        else:
            print(f"\nTransmission threshold: ∞ (no compression benefit)")


def main():
    """Main benchmark execution."""
    print("="*80)
    print("BIT PACKING COMPRESSION BENCHMARK")
    print("="*80)
    
    benchmark = CompressionBenchmark(num_iterations=100)
    
    # Test different data types
    data_types = ["uniform", "small", "outliers", "negative"]
    data_size = 1000
    
    for data_type in data_types:
        print(f"\n{'#'*80}")
        print(f"# Data Type: {data_type.upper()}")
        print(f"{'#'*80}")
        
        data = benchmark.generate_test_data(data_size, data_type)
        results = benchmark.compare_all_methods(data)
        benchmark.print_results(results)


if __name__ == "__main__":
    main()
