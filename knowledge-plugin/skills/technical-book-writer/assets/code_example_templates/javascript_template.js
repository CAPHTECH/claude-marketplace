/**
 * Module description: Brief description of what this module does.
 *
 * This template provides a structure for JavaScript code examples in technical books.
 * Adapt this template to your specific example while maintaining clarity and testability.
 */

// Constants and configuration
const DEFAULT_TIMEOUT = 30000;
const MAX_RETRIES = 3;

/**
 * Example class demonstrating best practices.
 *
 * This class shows how to structure code examples with:
 * - Clear JSDoc comments
 * - Proper error handling
 * - Testable design
 * - Modern JavaScript patterns
 */
class ExampleClass {
  /**
   * Create an instance of ExampleClass.
   *
   * @param {string} name - The name for this instance
   * @param {Object} config - Optional configuration object
   * @throws {Error} If name is empty
   */
  constructor(name, config = {}) {
    if (!name) {
      throw new Error('Name cannot be empty');
    }

    this.name = name;
    this.config = config;
    console.log(`Initialized ExampleClass with name: ${name}`);
  }

  /**
   * Process input data according to configuration.
   *
   * This method demonstrates:
   * - Clear input/output specifications
   * - Processing logic with error handling
   * - Logging for debugging
   *
   * @param {Array} data - Array of items to process
   * @returns {Array} Processed array of items
   * @throws {Error} If data is null or empty
   */
  processData(data) {
    if (!data || data.length === 0) {
      throw new Error('Data cannot be empty');
    }

    console.log(`Processing ${data.length} items`);

    // Example processing logic
    const processed = [];
    for (const item of data) {
      try {
        const result = this._processSingleItem(item);
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
   * @param {*} item - Item to process
   * @returns {*} Processed item
   */
  _processSingleItem(item) {
    // Example transformation
    return String(item).toUpperCase();
  }
}

/**
 * Example standalone function.
 *
 * This demonstrates:
 * - Clear function signature
 * - Default parameters
 * - Descriptive JSDoc
 *
 * @param {string} param1 - Description of parameter 1
 * @param {number} param2 - Description of parameter 2
 * @returns {Object} Object containing results
 *
 * @example
 * const result = exampleFunction('test', 5);
 * console.log(result.status); // 'success'
 */
function exampleFunction(param1, param2 = 10) {
  console.log(`Called exampleFunction with param1=${param1}, param2=${param2}`);

  // Implementation
  const result = {
    status: 'success',
    input: param1,
    multiplier: param2,
    output: param1.repeat(param2)
  };

  return result;
}

/**
 * Async example function demonstrating modern async/await patterns.
 *
 * @async
 * @param {string} url - URL to fetch
 * @returns {Promise<Object>} Fetched data
 * @throws {Error} If fetch fails
 *
 * @example
 * const data = await fetchData('https://api.example.com/data');
 */
async function fetchData(url) {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Data fetched successfully');
    return data;

  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

/**
 * Main entry point for the example.
 *
 * Demonstrates typical usage of the classes and functions defined above.
 */
function main() {
  console.log('Starting example program');

  // Create instance
  const example = new ExampleClass('demo', { setting: 'value' });

  // Process some data
  const data = ['item1', 'item2', 'item3'];
  const results = example.processData(data);
  console.log('Results:', results);

  // Call standalone function
  const funcResult = exampleFunction('test', 5);
  console.log('Function result:', funcResult);

  console.log('Example program completed');
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ExampleClass,
    exampleFunction,
    fetchData
  };
}

// Run main if executed directly
if (require.main === module) {
  main();
}

// Testing examples (optional - include if demonstrating testing)

/**
 * Example test for ExampleClass.
 * For use with testing frameworks like Jest or Mocha.
 */
function testExampleClass() {
  const example = new ExampleClass('test');
  console.assert(example.name === 'test', 'Name should be "test"');
  console.assert(Object.keys(example.config).length === 0, 'Config should be empty');
  console.log('✓ testExampleClass passed');
}

/**
 * Example test for exampleFunction.
 */
function testExampleFunction() {
  const result = exampleFunction('hello', 2);
  console.assert(result.status === 'success', 'Status should be "success"');
  console.assert(result.output === 'hellohello', 'Output should be "hellohello"');
  console.log('✓ testExampleFunction passed');
}

// Uncomment to run tests
// testExampleClass();
// testExampleFunction();
