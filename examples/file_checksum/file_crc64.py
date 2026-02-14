"""File CRC64 checksum calculation - synchronous and asynchronous variants."""

import sys
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from .crc64 import crc64
except ImportError:
    from examples.file_checksum.crc64 import crc64

try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False

MAX_BUF_LEN = 65536


def file_crc64(filepath: str) -> int:
    """Calculate CRC64 checksum for a file (synchronous).
    
    This version uses f.read() which allocates a new bytes object on each iteration.
    
    Args:
        filepath: Path to the file
        
    Returns:
        CRC64 checksum value
    """
    try:
        crc = 0
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(MAX_BUF_LEN)
                if not data:
                    break
                crc = crc64(crc, data)
        return crc
    except (OSError, IOError) as e:
        print(f"Error calculating CRC64 for {filepath}: {e}")
        sys.exit(1)


def file_crc64_readinto(filepath: str) -> int:
    """Calculate CRC64 checksum for a file using readinto (optimized).
    
    This version uses f.readinto() to read into a pre-allocated bytearray buffer,
    avoiding repeated memory allocations and deallocations.
    
    Args:
        filepath: Path to the file
        
    Returns:
        CRC64 checksum value
    """
    try:
        crc = 0
        buffer = bytearray(MAX_BUF_LEN)
        with open(filepath, 'rb') as f:
            while True:
                nbytes = f.readinto(buffer)
                if nbytes == 0:
                    break
                # Create a view of the buffer containing only the bytes read
                data = memoryview(buffer)[:nbytes]
                crc = crc64(crc, data)
        return crc
    except (OSError, IOError) as e:
        print(f"Error calculating CRC64 for {filepath}: {e}")
        sys.exit(1)


async def file_crc64_async_aiofiles(filepath: str) -> int:
    """Calculate CRC64 checksum for a file (asynchronous with aiofiles).
    
    Args:
        filepath: Path to the file
        
    Returns:
        CRC64 checksum value
    """
    if not HAS_AIOFILES:
        raise ImportError("aiofiles is required for async file operations")
    
    try:
        crc = 0
        async with aiofiles.open(filepath, 'rb') as f:
            while True:
                data = await f.read(MAX_BUF_LEN)
                if not data:
                    break
                crc = crc64(crc, data)
        return crc
    except (OSError, IOError) as e:
        print(f"Error calculating CRC64 for {filepath}: {e}")
        sys.exit(1)


async def file_crc64_async_threading(filepath: str) -> int:
    """Calculate CRC64 checksum for a file (asynchronous with thread pool).
    
    Args:
        filepath: Path to the file
        
    Returns:
        CRC64 checksum value
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        crc = await loop.run_in_executor(executor, file_crc64, filepath)
    return crc


def benchmark(filepath: str, warmup: int = 1, iterations: int = 3):
    """Benchmark different CRC64 calculation methods.
    
    Args:
        filepath: Path to the file to checksum
        warmup: Number of warmup iterations (default: 1)
        iterations: Number of benchmark iterations (default: 3)
    """
    import os
    
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    
    file_size = os.path.getsize(filepath)
    print(f"Benchmarking CRC64 calculation for: {filepath}")
    print(f"File size: {file_size:,} bytes ({file_size / (1024**2):.2f} MB)")
    print(f"Warmup iterations: {warmup}, Benchmark iterations: {iterations}")
    print()
    
    methods = [
        ("Synchronous (read)", file_crc64),
        ("Synchronous (readinto)", file_crc64_readinto),
    ]
    
    # Add async methods if available
    if HAS_AIOFILES:
        methods.append(("Async (aiofiles)", lambda fp: asyncio.run(file_crc64_async_aiofiles(fp))))
    
    methods.append(("Async (threading)", lambda fp: asyncio.run(file_crc64_async_threading(fp))))
    
    results = {}
    
    for name, func in methods:
        print(f"Testing {name}...")
        
        # Warmup
        for _ in range(warmup):
            func(filepath)
        
        # Benchmark
        times = []
        crc_value = None
        for i in range(iterations):
            start = time.perf_counter()
            crc_value = func(filepath)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            print(f"  Iteration {i+1}: {elapsed:.4f}s")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        throughput = file_size / avg_time / (1024**2)  # MB/s
        
        results[name] = {
            'avg': avg_time,
            'min': min_time,
            'max': max_time,
            'throughput': throughput,
            'crc': crc_value
        }
        
        print(f"  Average: {avg_time:.4f}s, Min: {min_time:.4f}s, Max: {max_time:.4f}s")
        print(f"  Throughput: {throughput:.2f} MB/s")
        print(f"  CRC64: {crc_value:016x}")
        print()
    
    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Method':<30} {'Avg Time (s)':<15} {'Throughput (MB/s)':<20} {'CRC64':<20}")
    print("-" * 70)
    
    for name, data in results.items():
        print(f"{name:<30} {data['avg']:<15.4f} {data['throughput']:<20.2f} {data['crc']:016x}")
    
    # Verify all methods produce the same CRC
    crc_values = [data['crc'] for data in results.values()]
    if len(set(crc_values)) == 1:
        print("\n✓ All methods produced identical CRC64 values")
    else:
        print("\n✗ WARNING: Methods produced different CRC64 values!")


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate CRC64 checksum of a file')
    parser.add_argument('filepath', help='Path to the file')
    parser.add_argument('--bench', action='store_true', help='Run benchmark comparison')
    parser.add_argument('-n', '--iterations', type=int, default=3, 
                       help='Number of benchmark iterations (default: 3)')
    parser.add_argument('--warmup', type=int, default=1,
                       help='Number of warmup iterations (default: 1)')
    parser.add_argument('--readinto', action='store_true',
                       help='Use optimized readinto variant')
    
    args = parser.parse_args()
    
    if args.bench:
        benchmark(args.filepath, warmup=args.warmup, iterations=args.iterations)
    else:
        if args.readinto:
            crc = file_crc64_readinto(args.filepath)
            print(f"CRC64 (readinto): {crc:016x}")
        else:
            crc = file_crc64(args.filepath)
            print(f"CRC64: {crc:016x}")


if __name__ == '__main__':
    main()
