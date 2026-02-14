# File Checksum Module

This module provides CRC64 checksum calculation functionality with optimized variants for file I/O.

## Features

- **Pure Python CRC64 implementation** using ECMA-182 polynomial
- **Standard file checksum** using `read()` method
- **Optimized variant** using `readinto()` method to avoid memory allocations
- **Async variants** with aiofiles and threading support
- **Benchmark tool** to compare performance of different methods

## Usage

### Command Line Interface

Calculate CRC64 checksum of a file:

```bash
# Using standard read() method
python -m examples file_crc64 /path/to/file

# Using optimized readinto() method
python -m examples file_crc64 /path/to/file --readinto

# Run benchmark comparison
python -m examples file_crc64 /path/to/file --bench -n 5 --warmup 2
```

### Python API

```python
from examples.file_checksum import file_crc64, file_crc64_readinto

# Standard method
crc = file_crc64('/path/to/file')
print(f"CRC64: {crc:016x}")

# Optimized method with readinto
crc = file_crc64_readinto('/path/to/file')
print(f"CRC64: {crc:016x}")
```

### Low-level CRC64 API

```python
from examples.file_checksum import crc64

# Calculate CRC64 for data
data = b'Hello, World!'
checksum = crc64(0, data)

# Incremental calculation
crc = 0
crc = crc64(crc, b'Hello, ')
crc = crc64(crc, b'World!')
```

## Optimization: read() vs readinto()

The module provides two variants for file I/O:

### `file_crc64()` - Standard Method

Uses `f.read(buffer_size)` which allocates a new bytes object on each iteration:

```python
def file_crc64(filepath: str) -> int:
    crc = 0
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(MAX_BUF_LEN)  # Allocates new bytes each iteration
            if not data:
                break
            crc = crc64(crc, data)
    return crc
```

### `file_crc64_readinto()` - Optimized Method

Uses `f.readinto(buffer)` with a pre-allocated bytearray to avoid repeated allocations:

```python
def file_crc64_readinto(filepath: str) -> int:
    crc = 0
    buffer = bytearray(MAX_BUF_LEN)  # Pre-allocated buffer
    with open(filepath, 'rb') as f:
        while True:
            nbytes = f.readinto(buffer)  # Reuses same buffer
            if nbytes == 0:
                break
            data = memoryview(buffer)[:nbytes]  # View of actual data
            crc = crc64(crc, data)
    return crc
```

### Benefits of readinto()

1. **No repeated allocations**: The same buffer is reused for each read
2. **Reduced GC pressure**: Less work for the garbage collector
3. **Better for large files**: More predictable memory usage
4. **C extension friendly**: Can benefit more when using Cython extensions

### Performance Comparison

Use the built-in benchmark to compare methods:

```bash
python -m examples file_crc64 /path/to/large/file --bench -n 3
```

Example output:

```
Benchmarking CRC64 calculation for: /tmp/large_test.bin
File size: 10,485,760 bytes (10.00 MB)
Warmup iterations: 1, Benchmark iterations: 3

Testing Synchronous (read)...
  Iteration 1: 1.5086s
  Iteration 2: 1.5230s
  Iteration 3: 1.5121s
  Average: 1.5146s
  Throughput: 6.60 MB/s

Testing Synchronous (readinto)...
  Iteration 1: 1.5516s
  Iteration 2: 1.5311s
  Iteration 3: 1.5417s
  Average: 1.5415s
  Throughput: 6.49 MB/s

✓ All methods produced identical CRC64 values
```

## Testing

Run the test suite:

```bash
python -m unittest tests.test_file_checksum -v
```

## Implementation Details

- **Buffer size**: 65,536 bytes (64 KB)
- **CRC64 polynomial**: ECMA-182 standard
- **Supported Python**: 3.6+
- **Dependencies**: None (aiofiles optional for async variant)

## Async Support

The module also provides async variants:

```python
import asyncio
from examples.file_checksum import file_crc64_async_aiofiles, file_crc64_async_threading

# Using aiofiles (requires: pip install aiofiles)
async def example_aiofiles():
    crc = await file_crc64_async_aiofiles('/path/to/file')
    return crc

# Using threading (no additional dependencies)
async def example_threading():
    crc = await file_crc64_async_threading('/path/to/file')
    return crc

# Run
asyncio.run(example_aiofiles())
asyncio.run(example_threading())
```
