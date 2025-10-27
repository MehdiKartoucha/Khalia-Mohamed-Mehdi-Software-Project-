"""
BitPacking without Overflow - Version 2

This implementation ensures compressed integers stay within single integer
boundaries (no spanning across consecutive integers).
"""

from typing import List
from src.base_bitpacking import BaseBitPacking


class BitPackingNoOverflow(BaseBitPacking):
    """
    Bit packing implementation where compressed values cannot span across
    consecutive integers (words) in the compressed array.
    
    Example with 12 bits per value:
    - Value 0: bits 0-11 of word 0
    - Value 1: bits 12-23 of word 0
    - Value 2: bits 0-11 of word 1 (starts fresh, doesn't use remaining 8 bits of word 0)
    - Value 3: bits 12-23 of word 1
    - Value 4: bits 0-11 of word 2
    - ...
    
    This provides faster random access at the cost of slightly lower compression.
    """
    
    def compress(self, data: List[int]) -> List[int]:
        """
        Compress an array of integers without overflow.
        
        Args:
            data: List of integers to compress
            
        Returns:
            List of compressed integers
        """
        if not data:
            return []
        
        # Store original data for get() method
        self.original_data = data.copy()
        self.original_length = len(data)
        
        # Encode data to handle negative numbers
        encoded_data = self._encode_data(data)
        
        # Calculate bits needed
        self.bits_per_value = self._calculate_bits_needed(encoded_data)
        
        # Calculate how many values fit in one 32-bit integer
        self.values_per_int = 32 // self.bits_per_value
        
        if self.values_per_int == 0:
            # Values are too large (> 32 bits), need one int per value minimum
            self.values_per_int = 1
            self.bits_per_value = 32
        
        # Calculate number of compressed integers needed
        num_compressed_ints = (self.original_length + self.values_per_int - 1) // self.values_per_int
        
        # Initialize compressed array
        self.compressed_data = [0] * num_compressed_ints
        
        # Pack the data
        for element_index, encoded_value in enumerate(encoded_data):
            int_index = element_index // self.values_per_int
            value_position = element_index % self.values_per_int
            bit_offset = value_position * self.bits_per_value
            
            # Place value in the appropriate position
            self.compressed_data[int_index] |= (encoded_value << bit_offset)
        
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
        
        decompressed = []
        mask = (1 << self.bits_per_value) - 1
        
        for element_index in range(self.original_length):
            int_index = element_index // self.values_per_int
            value_position = element_index % self.values_per_int
            bit_offset = value_position * self.bits_per_value
            
            # Extract the value
            encoded_value = (compressed[int_index] >> bit_offset) & mask
            decompressed.append(encoded_value)
        
        # Decode ZigZag encoding
        return self._decode_data(decompressed)
    
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
        
        # Calculate which compressed integer contains this value
        int_index = index // self.values_per_int
        value_position = index % self.values_per_int
        bit_offset = value_position * self.bits_per_value
        
        # Extract the value
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
        info["values_per_int"] = getattr(self, 'values_per_int', 0)
        info["wasted_bits_per_int"] = 32 - (self.values_per_int * self.bits_per_value) if hasattr(self, 'values_per_int') else 0
        return info
