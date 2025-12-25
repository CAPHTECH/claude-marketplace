#!/usr/bin/env python3
"""
Module description: Brief description of what this module does.

This template provides a structure for Python code examples in technical books.
Adapt this template to your specific example while maintaining clarity and testability.
"""

from typing import List, Dict, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Constants and configuration
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3


class ExampleClass:
    """
    Example class demonstrating best practices.

    This class shows how to structure code examples with:
    - Clear docstrings
    - Type hints
    - Proper error handling
    - Testable design

    Attributes:
        name: A descriptive name for this instance
        config: Configuration dictionary
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the example class.

        Args:
            name: The name for this instance
            config: Optional configuration dictionary

        Raises:
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("Name cannot be empty")

        self.name = name
        self.config = config or {}
        logger.info(f"Initialized {self.__class__.__name__} with name: {name}")

    def process_data(self, data: List[Any]) -> List[Any]:
        """
        Process input data according to configuration.

        This method demonstrates:
        - Clear input/output types
        - Processing logic with error handling
        - Logging for debugging

        Args:
            data: List of items to process

        Returns:
            Processed list of items

        Raises:
            ValueError: If data is None or empty
        """
        if not data:
            raise ValueError("Data cannot be empty")

        logger.debug(f"Processing {len(data)} items")

        # Example processing logic
        processed = []
        for item in data:
            try:
                result = self._process_single_item(item)
                processed.append(result)
            except Exception as e:
                logger.error(f"Error processing item {item}: {e}")
                # Decide whether to continue or raise
                continue

        logger.info(f"Successfully processed {len(processed)}/{len(data)} items")
        return processed

    def _process_single_item(self, item: Any) -> Any:
        """
        Process a single item (private helper method).

        Args:
            item: Item to process

        Returns:
            Processed item
        """
        # Example transformation
        return str(item).upper()


def example_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Example standalone function.

    This demonstrates:
    - Clear function signature with type hints
    - Default parameters
    - Descriptive docstring

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: 10)

    Returns:
        Dictionary containing results

    Example:
        >>> result = example_function("test", 5)
        >>> print(result['status'])
        'success'
    """
    logger.info(f"Called example_function with param1={param1}, param2={param2}")

    # Implementation
    result = {
        'status': 'success',
        'input': param1,
        'multiplier': param2,
        'output': param1 * param2
    }

    return result


def main():
    """
    Main entry point for the example.

    Demonstrates typical usage of the classes and functions defined above.
    """
    # Example usage
    logger.info("Starting example program")

    # Create instance
    example = ExampleClass("demo", {"setting": "value"})

    # Process some data
    data = ["item1", "item2", "item3"]
    results = example.process_data(data)
    logger.info(f"Results: {results}")

    # Call standalone function
    func_result = example_function("test", 5)
    logger.info(f"Function result: {func_result}")

    logger.info("Example program completed")


if __name__ == "__main__":
    main()


# Testing examples (optional - include if demonstrating testing)
def test_example_class():
    """Example test function."""
    example = ExampleClass("test")
    assert example.name == "test"
    assert example.config == {}


def test_example_function():
    """Example test function."""
    result = example_function("hello", 2)
    assert result['status'] == 'success'
    assert result['output'] == 'hellohello'


# To run tests (if pytest is available):
# pytest python_template.py
