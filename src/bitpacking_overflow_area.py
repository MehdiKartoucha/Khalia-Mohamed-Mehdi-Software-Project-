"""
BitPacking with Overflow Area - Version 3

This implementation uses an overflow area to store outlier values separately,
allowing the main data to be compressed more efficiently.
"""

from typing import List, Tuple
import math
from src.base_bitpacking import BaseBitPacking


class BitPackingWithOverflowArea(BaseBitPacking):
    """
    Bit packing implementation with an overflow area for outlier values.
    
    When a few values require significantly more bits than the majority,
    those outliers are stored separately in an "overflow area" at the end
    of the compressed array. The main area uses a special marker to indicate
    when a value is actually stored in the overflow area.
    
    Example: [1, 2, 3, 1024, 4, 5, 2048]
    - Main values: 1, 2, 3, 4, 5 (need 3 bits each)
    - Outliers: 1024, 2048 (need 11 bits each)
    - With overflow area: use 1 extra bit to mark overflow
    - Encoding: [0-001, 0-010, 0-011, 1-00, 0-100, 0-101, 1-01] + [1024, 2048]
    
    This provides optimal compression when there are few outliers.
    """
    
    def __init__(self, percentile_threshold: float = 0.95):
        """
        Initialize the overflow area compressor.
        
        Args:
            percentile_threshold: Percentile to use for determining overflow threshold
                                 (0.95 means values above 95th percentile go to overflow)
        """
        super().__init__()
        self.percentile_threshold = percentile_threshold
        self.overflow_area: List[int] = []
        self.main_bits: int = 0
        self.overflow_index_bits: int = 0
        self.has_overflow: bool = False
    
    def _determine_overflow_strategy(self, encoded_data: List[int]) -> Tuple[int, List[int], List[int]]:
        """
        Determine if using overflow area is beneficial and split data accordingly.
        
        Args:
            encoded_data: ZigZag encoded data
            
        Returns:
            Tuple of (main_bits, main_data_indices, overflow_indices)
        """
        if not encoded_data:
            return 0, [], []
        
        # Sort to find percentile
        sorted_data = sorted(encoded_data)
        n = len(sorted_data)
        
        # Find the threshold value at the percentile
        percentile_index = int(n * self.percentile_threshold)
        if percentile_index >= n:
            percentile_index = n - 1
        
        threshold_value = sorted_data[percentile_index]
        
        # Calculate bits needed for main values (up to threshold)
        main_bits = threshold_value.bit_length() if threshold_value > 0 else 1
        
        # Identify overflow values
        overflow_indices = [index for index, value in enumerate(encoded_data) if value > threshold_value]
        
        # Calculate cost with and without overflow area
        all_bits = self._calculate_bits_needed(encoded_data)
        
        # Cost without overflow area
        cost_without = n * all_bits
        
        # Cost with overflow area
        num_overflow = len(overflow_indices)
        if num_overflow > 0:
            overflow_index_bits = math.ceil(math.log2(num_overflow + 1))
            # 1 bit for overflow flag + main_bits for value or overflow_index_bits for index
            cost_with_main = n * (1 + max(main_bits, overflow_index_bits))
            # Plus the overflow values themselves (32 bits each for simplicity)
            cost_with_overflow = num_overflow * 32
            cost_with = cost_with_main + cost_with_overflow
        else:
            cost_with = cost_without
        
        # Use overflow area only if it's beneficial
        if cost_with < cost_without and num_overflow > 0:
            return main_bits, [index for index in range(n) if index not in overflow_indices], overflow_indices
        else:
            return all_bits, list(range(n)), []
    
    def compress(self, data: List[int]) -> List[int]:
        """
        Compress an array of integers with overflow area.
        
        Args:
            data: List of integers to compress
            
        Returns:
            List of compressed integers (main area + overflow area)
        """
        if not data:
            return []
        
        # Store original data for get() method
        self.original_data = data.copy()
        self.original_length = len(data)
        
        # Encode data to handle negative numbers
        encoded_data = self._encode_data(data)
        
        # Determine overflow strategy
        main_bits, main_indices, overflow_indices = self._determine_overflow_strategy(encoded_data)
        
        self.has_overflow = len(overflow_indices) > 0
        self.main_bits = main_bits
        
        if self.has_overflow:
            # Calculate bits for overflow index
            num_overflow = len(overflow_indices)
            self.overflow_index_bits = math.ceil(math.log2(num_overflow)) if num_overflow > 1 else 1
            
            # Build overflow area (store original encoded values)
            self.overflow_area = [encoded_data[index] for index in overflow_indices]
            
            # Build overflow index mapping
            overflow_map = {original_idx: overflow_idx for overflow_idx, original_idx in enumerate(overflow_indices)}
            
            # Total bits per value: 1 (flag) + max(main_bits, overflow_index_bits)
            value_bits = max(self.main_bits, self.overflow_index_bits)
            self.bits_per_value = 1 + value_bits
            
            # Calculate compressed main area size
            total_main_bits = self.original_length * self.bits_per_value
            num_main_ints = (total_main_bits + 31) // 32
            
            # Initialize compressed main area
            compressed_main = [0] * num_main_ints
            
            # Pack the main data
            bit_position = 0
            for element_index in range(self.original_length):
                if element_index in overflow_map:
                    # This is an overflow value
                    flag = 1
                    value = overflow_map[element_index]
                else:
                    # Regular value
                    flag = 0
                    value = encoded_data[element_index]
                
                # Combine flag and value
                packed_value = (flag << value_bits) | (value & ((1 << value_bits) - 1))
                
                # Pack into compressed array (with overflow allowed for simplicity)
                int_index = bit_position // 32
                bit_offset = bit_position % 32
                bits_in_current = min(32 - bit_offset, self.bits_per_value)
                bits_in_next = self.bits_per_value - bits_in_current
                
                if bits_in_next > 0:
                    lower_mask = (1 << bits_in_current) - 1
                    lower_part = packed_value & lower_mask
                    upper_part = packed_value >> bits_in_current
                    
                    compressed_main[int_index] |= (lower_part << bit_offset)
                    if int_index + 1 < num_main_ints:
                        compressed_main[int_index + 1] |= upper_part
                else:
                    compressed_main[int_index] |= (packed_value << bit_offset)
                
                bit_position += self.bits_per_value
            
            # Combine main area and overflow area
            self.compressed_data = compressed_main + self.overflow_area
            
        else:
            # No overflow area needed, use simple compression
            self.bits_per_value = main_bits
            total_bits = self.original_length * self.bits_per_value
            num_compressed_ints = (total_bits + 31) // 32
            
            self.compressed_data = [0] * num_compressed_ints
            
            bit_position = 0
            for encoded_value in encoded_data:
                int_index = bit_position // 32
                bit_offset = bit_position % 32
                bits_in_current = min(32 - bit_offset, self.bits_per_value)
                bits_in_next = self.bits_per_value - bits_in_current
                
                if bits_in_next > 0:
                    lower_mask = (1 << bits_in_current) - 1
                    lower_part = encoded_value & lower_mask
                    upper_part = encoded_value >> bits_in_current
                    
                    self.compressed_data[int_index] |= (lower_part << bit_offset)
                    if int_index + 1 < num_compressed_ints:
                        self.compressed_data[int_index + 1] |= upper_part
                else:
                    self.compressed_data[int_index] |= (encoded_value << bit_offset)
                
                bit_position += self.bits_per_value
        
        return self.compressed_data
    
    def decompress(self, compressed: List[int]) -> List[int]:
        """
        Decompress a compressed array.
        
        Args:
            compressed: List of compressed integers
            
        Returns:
            List of decompressed integers
        """
        if not compressed:
            return []
        
        if not self.original_length or not self.bits_per_value:
            raise ValueError("No compression metadata available. Must compress first.")
        
        decompressed_encoded = []
        
        if self.has_overflow:
            # Calculate main area size
            total_main_bits = self.original_length * self.bits_per_value
            num_main_ints = (total_main_bits + 31) // 32
            
            # Extract main area and overflow area
            compressed_main = compressed[:num_main_ints]
            overflow_area = compressed[num_main_ints:]
            
            value_bits = max(self.main_bits, self.overflow_index_bits)
            mask = (1 << self.bits_per_value) - 1
            value_mask = (1 << value_bits) - 1
            
            bit_position = 0
            for element_index in range(self.original_length):
                int_index = bit_position // 32
                bit_offset = bit_position % 32
                bits_in_current = min(32 - bit_offset, self.bits_per_value)
                bits_in_next = self.bits_per_value - bits_in_current
                
                if bits_in_next > 0:
                    lower_mask = (1 << bits_in_current) - 1
                    lower_part = (compressed_main[int_index] >> bit_offset) & lower_mask
                    upper_mask = (1 << bits_in_next) - 1
                    upper_part = compressed_main[int_index + 1] & upper_mask
                    packed_value = lower_part | (upper_part << bits_in_current)
                else:
                    packed_value = (compressed_main[int_index] >> bit_offset) & mask
                
                # Extract flag and value
                flag = packed_value >> value_bits
                value = packed_value & value_mask
                
                if flag == 1:
                    # Get from overflow area
                    decompressed_encoded.append(overflow_area[value])
                else:
                    # Regular value
                    decompressed_encoded.append(value)
                
                bit_position += self.bits_per_value
        else:
            # Simple decompression without overflow area
            mask = (1 << self.bits_per_value) - 1
            bit_position = 0
            
            for element_index in range(self.original_length):
                int_index = bit_position // 32
                bit_offset = bit_position % 32
                bits_in_current = min(32 - bit_offset, self.bits_per_value)
                bits_in_next = self.bits_per_value - bits_in_current
                
                if bits_in_next > 0:
                    lower_mask = (1 << bits_in_current) - 1
                    lower_part = (compressed[int_index] >> bit_offset) & lower_mask
                    upper_mask = (1 << bits_in_next) - 1
                    upper_part = compressed[int_index + 1] & upper_mask
                    value = lower_part | (upper_part << bits_in_current)
                else:
                    value = (compressed[int_index] >> bit_offset) & mask
                
                decompressed_encoded.append(value)
                bit_position += self.bits_per_value
        
        # Decode ZigZag encoding
        return self._decode_data(decompressed_encoded)
    
    def get(self, index: int) -> int:
        """
        Get the value at the specified index without full decompression.
        
        Args:
            index: Index of the element to retrieve (0-based)
            
        Returns:
            The integer value at the specified index
            
        Raises:
            IndexError: If index is out of bounds
        """
        if index < 0 or index >= self.original_length:
            raise IndexError(f"Index {index} out of bounds for array of length {self.original_length}")
        
        if not self.compressed_data:
            raise ValueError("No compressed data available")
        
        if self.has_overflow:
            # Calculate main area size
            total_main_bits = self.original_length * self.bits_per_value
            num_main_ints = (total_main_bits + 31) // 32
            
            # Get from main area
            bit_position = index * self.bits_per_value
            int_index = bit_position // 32
            bit_offset = bit_position % 32
            bits_in_current = min(32 - bit_offset, self.bits_per_value)
            bits_in_next = self.bits_per_value - bits_in_current
            
            if bits_in_next > 0:
                lower_mask = (1 << bits_in_current) - 1
                lower_part = (self.compressed_data[int_index] >> bit_offset) & lower_mask
                upper_mask = (1 << bits_in_next) - 1
                upper_part = self.compressed_data[int_index + 1] & upper_mask
                packed_value = lower_part | (upper_part << bits_in_current)
            else:
                mask = (1 << self.bits_per_value) - 1
                packed_value = (self.compressed_data[int_index] >> bit_offset) & mask
            
            # Extract flag and value
            value_bits = max(self.main_bits, self.overflow_index_bits)
            flag = packed_value >> value_bits
            value = packed_value & ((1 << value_bits) - 1)
            
            if flag == 1:
                # Get from overflow area
                encoded_value = self.compressed_data[num_main_ints + value]
            else:
                encoded_value = value
        else:
            # Simple get without overflow area
            bit_position = index * self.bits_per_value
            int_index = bit_position // 32
            bit_offset = bit_position % 32
            bits_in_current = min(32 - bit_offset, self.bits_per_value)
            bits_in_next = self.bits_per_value - bits_in_current
            
            if bits_in_next > 0:
                lower_mask = (1 << bits_in_current) - 1
                lower_part = (self.compressed_data[int_index] >> bit_offset) & lower_mask
                upper_mask = (1 << bits_in_next) - 1
                upper_part = self.compressed_data[int_index + 1] & upper_mask
                encoded_value = lower_part | (upper_part << bits_in_current)
            else:
                mask = (1 << self.bits_per_value) - 1
                encoded_value = (self.compressed_data[int_index] >> bit_offset) & mask
        
        # Decode ZigZag encoding
        return self._zigzag_decode(encoded_value)
    
    def get_info(self) -> dict:
        """
        Get information about the current compression state.
        
        Returns:
            Dictionary containing compression metadata
        """
        info = super().get_info()
        info["has_overflow_area"] = self.has_overflow
        info["overflow_area_size"] = len(self.overflow_area)
        info["main_bits"] = self.main_bits
        info["overflow_index_bits"] = self.overflow_index_bits
        return info
