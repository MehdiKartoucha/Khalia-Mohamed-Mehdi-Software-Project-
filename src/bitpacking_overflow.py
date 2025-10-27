"""
BitPacking with Overflow - Version 1

This implementation allows compressed integers to span across two consecutive
integers in the output array for maximum compression efficiency.
"""

from typing import List
from src.base_bitpacking import BaseBitPacking


class BitPackingWithOverflow(BaseBitPacking):
    """
    Bit packing implementation where compressed values can span across
    consecutive integers (words) in the compressed array.
    
    Example with 12 bits per value:
    - Value 0: bits 0-11 of word 0
    - Value 1: bits 12-23 of word 0
    - Value 2: bits 24-31 of word 0 + bits 0-3 of word 1
    - Value 3: bits 4-15 of word 1
    - ...
    
    This provides maximum compression at the cost of slightly more complex
    random access.
    """
    
    def compress(self, data: List[int]) -> List[int]:
        """
        Compress an array of integers with overflow allowed.
        
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
        
        # Calculate total bits needed
        total_bits = self.original_length * self.bits_per_value
        
        # Calculate number of 32-bit integers needed
        num_compressed_ints = (total_bits + 31) // 32
        
        # Initialize compressed array
        self.compressed_data = [0] * num_compressed_ints
        
        # Pack the data
        bit_position = 0
        for encoded_value in encoded_data:
            # Determine which integer(s) this value will occupy
            int_index = bit_position // 32
            bit_offset = bit_position % 32
            
            # How many bits can fit in the current integer
            bits_in_current = min(32 - bit_offset, self.bits_per_value)
            bits_in_next = self.bits_per_value - bits_in_current
            
            # Extract the parts of the value
            if bits_in_next > 0:
                # Value spans two integers
                lower_mask = (1 << bits_in_current) - 1
                lower_part = encoded_value & lower_mask
                upper_part = encoded_value >> bits_in_current
                
                # Place lower part in current integer
                self.compressed_data[int_index] |= (lower_part << bit_offset)
                
                # Place upper part in next integer
                if int_index + 1 < num_compressed_ints:
                    self.compressed_data[int_index + 1] |= upper_part
            else:
                # Value fits in current integer
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
        
        decompressed = []
        bit_position = 0
        mask = (1 << self.bits_per_value) - 1
        
        for element_index in range(self.original_length):
            int_index = bit_position // 32
            bit_offset = bit_position % 32
            
            # How many bits are in the current and next integers
            bits_in_current = min(32 - bit_offset, self.bits_per_value)
            bits_in_next = self.bits_per_value - bits_in_current
            
            if bits_in_next > 0:
                # Value spans two integers
                lower_mask = (1 << bits_in_current) - 1
                lower_part = (compressed[int_index] >> bit_offset) & lower_mask
                
                upper_mask = (1 << bits_in_next) - 1
                upper_part = compressed[int_index + 1] & upper_mask
                
                value = lower_part | (upper_part << bits_in_current)
            else:
                # Value in current integer only
                value = (compressed[int_index] >> bit_offset) & mask
            
            decompressed.append(value)
            bit_position += self.bits_per_value
        
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
        
        # Calculate bit position for this index
        bit_position = index * self.bits_per_value
        int_index = bit_position // 32
        bit_offset = bit_position % 32
        
        # How many bits are in the current and next integers
        bits_in_current = min(32 - bit_offset, self.bits_per_value)
        bits_in_next = self.bits_per_value - bits_in_current
        
        if bits_in_next > 0:
            # Value spans two integers
            lower_mask = (1 << bits_in_current) - 1
            lower_part = (self.compressed_data[int_index] >> bit_offset) & lower_mask
            
            upper_mask = (1 << bits_in_next) - 1
            upper_part = self.compressed_data[int_index + 1] & upper_mask
            
            encoded_value = lower_part | (upper_part << bits_in_current)
        else:
            # Value in current integer only
            mask = (1 << self.bits_per_value) - 1
            encoded_value = (self.compressed_data[int_index] >> bit_offset) & mask
        
        # Decode ZigZag encoding
        return self._zigzag_decode(encoded_value)
