/**
 * Module description: Brief description of what this module does.
 *
 * This template provides a structure for TypeScript code examples in technical books.
 * Adapt this template to your specific example while maintaining clarity and testability.
 */

// Constants and configuration
const DEFAULT_TIMEOUT = 30000;
const MAX_RETRIES = 3;

/**
 * Configuration interface
 */
interface Config {
  setting?: string;
  timeout?: number;
  [key: string]: any;
}

/**
 * Result type for example function
 */
interface ExampleResult {
  status: 'success' | 'error';
  input: string;
  multiplier: number;
  output: string;
}

/**
 * Example class demonstrating best practices.
 *
 * This class shows how to structure code examples with:
 * - Strong typing with TypeScript
 * - Clear JSDoc comments
 * - Proper error handling
 * - Testable design
 */
class ExampleClass {
  private name: string;
  private config: Config;

  /**
   * Create an instance of ExampleClass.
   *
   * @param name - The name for this instance
   * @param config - Optional configuration object
   * @throws {Error} If name is empty
   */
  constructor(name: string, config: Config = {}) {
    if (!name) {
      throw new Error('Name cannot be empty');
    }

    this.name = name;
    this.config = config;
    console.log(`Initialized ExampleClass with name: ${name}`);
  }

  /**
   * Get the instance name.
   *
   * @returns The instance name
   */
  getName(): string {
    return this.name;
  }

  /**
   * Process input data according to configuration.
   *
   * This method demonstrates:
   * - Type-safe array processing
   * - Error handling
   * - Logging for debugging
   *
   * @param data - Array of items to process
   * @returns Processed array of items
   * @throws {Error} If data is empty
   */
  processData<T>(data: T[]): string[] {
    if (!data || data.length === 0) {
      throw new Error('Data cannot be empty');
    }

    console.log(`Processing ${data.length} items`);

    // Example processing logic
    const processed: string[] = [];
    for (const item of data) {
      try {
        const result = this.processSingleItem(item);
        processed.push(result);
      } catch (error) {
        console.error(`Error processing item ${item}:`, error);
        // Decide whether to continue or throw
        continue;
      }
    }

    console.log(`Successfully processed ${processed.length}/${data.length} items`);
    return processed;
  }

  /**
   * Process a single item (private helper method).
   *
   * @private
   * @param item - Item to process
   * @returns Processed item as string
   */
  private processSingleItem<T>(item: T): string {
    // Example transformation
    return String(item).toUpperCase();
  }
}

/**
 * Example standalone function with type safety.
 *
 * This demonstrates:
 * - Clear function signature with types
 * - Default parameters
 * - Return type specification
 *
 * @param param1 - Description of parameter 1
 * @param param2 - Description of parameter 2
 * @returns Object containing results
 *
 * @example
 * ```typescript
 * const result = exampleFunction('test', 5);
 * console.log(result.status); // 'success'
 * ```
 */
function exampleFunction(param1: string, param2: number = 10): ExampleResult {
  console.log(`Called exampleFunction with param1=${param1}, param2=${param2}`);

  // Implementation
  const result: ExampleResult = {
    status: 'success',
    input: param1,
    multiplier: param2,
    output: param1.repeat(param2)
  };

  return result;
}

/**
 * Async example function with proper typing.
 *
 * @async
 * @param url - URL to fetch
 * @returns Promise resolving to fetched data
 * @throws {Error} If fetch fails
 *
 * @example
 * ```typescript
 * const data = await fetchData<User>('https://api.example.com/user/1');
 * ```
 */
async function fetchData<T>(url: string): Promise<T> {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Data fetched successfully');
    return data as T;

  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

/**
 * Generic utility function example.
 *
 * @param items - Array of items
 * @param predicate - Function to test each item
 * @returns Filtered array
 *
 * @example
 * ```typescript
 * const numbers = [1, 2, 3, 4, 5];
 * const evens = filterArray(numbers, n => n % 2 === 0);
 * console.log(evens); // [2, 4]
 * ```
 */
function filterArray<T>(items: T[], predicate: (item: T) => boolean): T[] {
  return items.filter(predicate);
}

/**
 * Main entry point for the example.
 *
 * Demonstrates typical usage of the classes and functions defined above.
 */
function main(): void {
  console.log('Starting example program');

  // Create instance
  const example = new ExampleClass('demo', { setting: 'value' });

  // Process some data
  const data: string[] = ['item1', 'item2', 'item3'];
  const results = example.processData(data);
  console.log('Results:', results);

  // Call standalone function
  const funcResult = exampleFunction('test', 5);
  console.log('Function result:', funcResult);

  // Use generic function
  const numbers = [1, 2, 3, 4, 5];
  const evens = filterArray(numbers, n => n % 2 === 0);
  console.log('Even numbers:', evens);

  console.log('Example program completed');
}

// Export for module usage
export {
  ExampleClass,
  exampleFunction,
  fetchData,
  filterArray,
  Config,
  ExampleResult
};

// Run main if this is the entry point
if (require.main === module) {
  main();
}

// Testing examples (optional - include if demonstrating testing)

/**
 * Example test for ExampleClass.
 * For use with testing frameworks like Jest.
 */
function testExampleClass(): void {
  const example = new ExampleClass('test');
  console.assert(example.getName() === 'test', 'Name should be "test"');
  console.log('✓ testExampleClass passed');
}

/**
 * Example test for exampleFunction.
 */
function testExampleFunction(): void {
  const result = exampleFunction('hello', 2);
  console.assert(result.status === 'success', 'Status should be "success"');
  console.assert(result.output === 'hellohello', 'Output should be "hellohello"');
  console.log('✓ testExampleFunction passed');
}

// Uncomment to run tests
// testExampleClass();
// testExampleFunction();
