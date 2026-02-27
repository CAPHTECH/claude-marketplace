// Package example provides template code for technical book examples.
//
// This template demonstrates best practices for Go code examples including:
// - Clear documentation
// - Proper error handling
// - Testable design
// - Idiomatic Go patterns
package example

import (
	"errors"
	"fmt"
	"log"
	"time"
)

// Constants and configuration
const (
	DefaultTimeout = 30 * time.Second
	MaxRetries     = 3
)

// Common errors
var (
	ErrEmptyName = errors.New("name cannot be empty")
	ErrEmptyData = errors.New("data cannot be empty")
)

// Config represents configuration options.
type Config struct {
	Setting string
	Timeout time.Duration
	// Add other configuration fields as needed
}

// ExampleStruct demonstrates best practices for struct design.
//
// This struct shows how to structure code examples with:
// - Clear field documentation
// - Proper encapsulation
// - Testable methods
type ExampleStruct struct {
	name   string
	config Config
}

// NewExampleStruct creates a new instance of ExampleStruct.
//
// This constructor demonstrates:
// - Validation of inputs
// - Proper error handling
// - Initialization with defaults
func NewExampleStruct(name string, config *Config) (*ExampleStruct, error) {
	if name == "" {
		return nil, ErrEmptyName
	}

	// Use default config if not provided
	cfg := Config{
		Timeout: DefaultTimeout,
	}
	if config != nil {
		cfg = *config
	}

	log.Printf("Initialized ExampleStruct with name: %s", name)

	return &ExampleStruct{
		name:   name,
		config: cfg,
	}, nil
}

// Name returns the name of the instance.
func (e *ExampleStruct) Name() string {
	return e.name
}

// ProcessData processes input data according to configuration.
//
// This method demonstrates:
// - Generic type handling with interface{}
// - Error handling and logging
// - Processing with recovery from panics
func (e *ExampleStruct) ProcessData(data []interface{}) ([]string, error) {
	if len(data) == 0 {
		return nil, ErrEmptyData
	}

	log.Printf("Processing %d items", len(data))

	processed := make([]string, 0, len(data))

	for i, item := range data {
		// Recover from panics in processing
		func() {
			defer func() {
				if r := recover(); r != nil {
					log.Printf("Recovered from panic processing item %d: %v", i, r)
				}
			}()

			result := e.processSingleItem(item)
			processed = append(processed, result)
		}()
	}

	log.Printf("Successfully processed %d/%d items", len(processed), len(data))
	return processed, nil
}

// processSingleItem processes a single item (private helper method).
func (e *ExampleStruct) processSingleItem(item interface{}) string {
	// Example transformation
	return fmt.Sprintf("%v", item)
}

// ExampleResult represents the result of an example operation.
type ExampleResult struct {
	Status     string
	Input      string
	Multiplier int
	Output     string
}

// ExampleFunction demonstrates a standalone function with clear signature.
//
// This function shows:
// - Clear parameter naming
// - Return type specification
// - Error handling
func ExampleFunction(param1 string, param2 int) (*ExampleResult, error) {
	if param1 == "" {
		return nil, errors.New("param1 cannot be empty")
	}

	log.Printf("Called ExampleFunction with param1=%s, param2=%d", param1, param2)

	// Build output string
	output := ""
	for i := 0; i < param2; i++ {
		output += param1
	}

	result := &ExampleResult{
		Status:     "success",
		Input:      param1,
		Multiplier: param2,
		Output:     output,
	}

	return result, nil
}

// FetchData demonstrates async operations with proper error handling.
//
// This function shows:
// - HTTP request handling
// - Timeout management
// - Context usage
func FetchData(url string) ([]byte, error) {
	// Example: In real code, use context for timeout
	// and proper HTTP client setup

	// Simulate fetch operation
	log.Printf("Fetching data from: %s", url)

	// In a real implementation:
	// - Create HTTP client with timeout
	// - Make request with context
	// - Handle response and errors
	// - Parse and return data

	return []byte("example data"), nil
}

// Helper function demonstrating error wrapping (Go 1.13+)
func processWithErrorWrapping(data string) error {
	if data == "" {
		return fmt.Errorf("processing failed: %w", ErrEmptyData)
	}

	// Processing logic...
	return nil
}

// Example of method with options pattern
type ProcessOptions struct {
	MaxItems  int
	Timeout   time.Duration
	FailFast  bool
}

// ProcessWithOptions demonstrates the options pattern for flexible APIs.
func (e *ExampleStruct) ProcessWithOptions(data []interface{}, opts ProcessOptions) ([]string, error) {
	// Set defaults
	if opts.MaxItems == 0 {
		opts.MaxItems = len(data)
	}
	if opts.Timeout == 0 {
		opts.Timeout = e.config.Timeout
	}

	// Process with options
	maxItems := opts.MaxItems
	if maxItems > len(data) {
		maxItems = len(data)
	}

	return e.ProcessData(data[:maxItems])
}

// Example of a worker function using channels
func Worker(jobs <-chan string, results chan<- string) {
	for job := range jobs {
		// Process job
		result := fmt.Sprintf("processed: %s", job)
		results <- result
	}
}

// Example main function showing typical usage
func ExampleMain() {
	log.Println("Starting example program")

	// Create instance
	example, err := NewExampleStruct("demo", &Config{
		Setting: "value",
	})
	if err != nil {
		log.Fatalf("Failed to create ExampleStruct: %v", err)
	}

	// Process some data
	data := []interface{}{"item1", "item2", "item3"}
	results, err := example.ProcessData(data)
	if err != nil {
		log.Fatalf("Failed to process data: %v", err)
	}
	log.Printf("Results: %v", results)

	// Call standalone function
	funcResult, err := ExampleFunction("test", 5)
	if err != nil {
		log.Fatalf("ExampleFunction failed: %v", err)
	}
	log.Printf("Function result: %+v", funcResult)

	log.Println("Example program completed")
}

// Example test file content (go in example_test.go):
/*
package example

import (
	"testing"
)

func TestNewExampleStruct(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		wantErr bool
	}{
		{"valid name", "test", false},
		{"empty name", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := NewExampleStruct(tt.input, nil)
			if (err != nil) != tt.wantErr {
				t.Errorf("NewExampleStruct() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr && got.Name() != tt.input {
				t.Errorf("NewExampleStruct() name = %v, want %v", got.Name(), tt.input)
			}
		})
	}
}

func TestExampleFunction(t *testing.T) {
	result, err := ExampleFunction("hello", 2)
	if err != nil {
		t.Fatalf("ExampleFunction() error = %v", err)
	}
	if result.Status != "success" {
		t.Errorf("Status = %v, want success", result.Status)
	}
	if result.Output != "hellohello" {
		t.Errorf("Output = %v, want hellohello", result.Output)
	}
}
*/
