"""Tests for file_checksum package."""

import os
import sys
import tempfile
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.file_checksum.crc64 import crc64
from examples.file_checksum.file_crc64 import file_crc64, file_crc64_readinto


class TestCRC64(unittest.TestCase):
    """Test CRC64 implementation."""
    
    def test_crc64_empty(self):
        """Test CRC64 of empty data."""
        result = crc64(0, b'')
        self.assertEqual(result, 0)
    
    def test_crc64_simple(self):
        """Test CRC64 with simple data."""
        result = crc64(0, b'Hello, World!')
        # This should be a deterministic value
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
    
    def test_crc64_incremental(self):
        """Test that CRC64 can be calculated incrementally."""
        data = b'Hello, World!'
        
        # Calculate in one go
        crc_single = crc64(0, data)
        
        # Calculate incrementally
        crc_multi = crc64(0, data[:7])
        crc_multi = crc64(crc_multi, data[7:])
        
        self.assertEqual(crc_single, crc_multi)
    
    def test_crc64_consistency(self):
        """Test that same data produces same CRC64."""
        data = b'Test data for CRC64'
        result1 = crc64(0, data)
        result2 = crc64(0, data)
        self.assertEqual(result1, result2)


class TestFileCRC64(unittest.TestCase):
    """Test file CRC64 calculation."""
    
    def setUp(self):
        """Create temporary test file."""
        self.test_data = b'This is test data for file CRC64 calculation.\n' * 100
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
        self.temp_file.write(self.test_data)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_file_crc64_basic(self):
        """Test basic file CRC64 calculation."""
        result = file_crc64(self.temp_file.name)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
    
    def test_file_crc64_readinto_basic(self):
        """Test basic file CRC64 calculation with readinto."""
        result = file_crc64_readinto(self.temp_file.name)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
    
    def test_file_crc64_consistency(self):
        """Test that multiple reads produce same CRC64."""
        result1 = file_crc64(self.temp_file.name)
        result2 = file_crc64(self.temp_file.name)
        self.assertEqual(result1, result2)
    
    def test_file_crc64_readinto_consistency(self):
        """Test that multiple reads with readinto produce same CRC64."""
        result1 = file_crc64_readinto(self.temp_file.name)
        result2 = file_crc64_readinto(self.temp_file.name)
        self.assertEqual(result1, result2)
    
    def test_file_crc64_methods_equal(self):
        """Test that read() and readinto() produce identical results."""
        crc_read = file_crc64(self.temp_file.name)
        crc_readinto = file_crc64_readinto(self.temp_file.name)
        self.assertEqual(crc_read, crc_readinto,
                        f"read() produced {crc_read:016x}, readinto() produced {crc_readinto:016x}")
    
    def test_file_crc64_small_file(self):
        """Test with a small file (smaller than buffer)."""
        small_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
        small_file.write(b'Small file content')
        small_file.close()
        
        try:
            crc_read = file_crc64(small_file.name)
            crc_readinto = file_crc64_readinto(small_file.name)
            self.assertEqual(crc_read, crc_readinto)
        finally:
            os.unlink(small_file.name)
    
    def test_file_crc64_large_file(self):
        """Test with a file larger than buffer size."""
        large_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
        # Write 200 KB (larger than 64 KB buffer)
        large_file.write(b'x' * 200000)
        large_file.close()
        
        try:
            crc_read = file_crc64(large_file.name)
            crc_readinto = file_crc64_readinto(large_file.name)
            self.assertEqual(crc_read, crc_readinto)
        finally:
            os.unlink(large_file.name)
    
    def test_file_crc64_empty_file(self):
        """Test with an empty file."""
        empty_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
        empty_file.close()
        
        try:
            crc_read = file_crc64(empty_file.name)
            crc_readinto = file_crc64_readinto(empty_file.name)
            self.assertEqual(crc_read, 0)
            self.assertEqual(crc_readinto, 0)
        finally:
            os.unlink(empty_file.name)


class TestCRC64Values(unittest.TestCase):
    """Test specific CRC64 values for consistency."""
    
    def test_consistent_values(self):
        """Test CRC64 produces consistent values."""
        # Test with various data to ensure consistency
        test_cases = [
            b'123456789',
            b'Hello, World!',
            b'The quick brown fox jumps over the lazy dog',
            b'',
            b'\x00\x01\x02\x03\x04\x05\x06\x07',
        ]
        
        for data in test_cases:
            # Calculate multiple times to ensure consistency
            result1 = crc64(0, data)
            result2 = crc64(0, data)
            self.assertEqual(result1, result2,
                           f"CRC64 of {data!r} should be consistent")


if __name__ == '__main__':
    unittest.main()
