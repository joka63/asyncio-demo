"""Command-line interface for examples."""

import sys
import importlib


EXAMPLES = {
    'asyncq_periodic_tasks': 'examples.asyncq_periodic_tasks',
    'crawl': 'examples.crawl',
    'file_crc64': 'examples.file_checksum.file_crc64',
}


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m examples <example_name> [args...]")
        print("\nAvailable examples:")
        for name in EXAMPLES:
            print(f"  - {name}")
        sys.exit(1)
    
    example_name = sys.argv[1]
    
    if example_name not in EXAMPLES:
        print(f"Error: Unknown example '{example_name}'")
        print("\nAvailable examples:")
        for name in EXAMPLES:
            print(f"  - {name}")
        sys.exit(1)
    
    module_name = EXAMPLES[example_name]
    
    # Remove the example name from sys.argv so the module gets clean args
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'main'):
            module.main()
        else:
            print(f"Error: Module '{module_name}' has no main() function")
            sys.exit(1)
    except ImportError as e:
        print(f"Error importing module '{module_name}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running example '{example_name}': {e}")
        raise


if __name__ == '__main__':
    main()
