#!/usr/bin/env python3
"""
Test runner for Rick and Morty Tactical RTS game.
Runs all unit tests and reports results.
"""

import os
import sys
import unittest
import pygame
import traceback

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_all_tests():
    """Run all test cases and report results"""
    # Initialize pygame so it doesn't complain during tests
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    
    # Get all test modules in the tests directory
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern="test_*.py")
    
    # Run all tests and collect results
    test_runner = unittest.TextTestRunner(verbosity=2)
    results = test_runner.run(test_suite)
    
    # Quit pygame
    pygame.quit()
    
    # Print summary
    print("\n===== Test Summary =====")
    print(f"Tests run: {results.testsRun}")
    print(f"Errors: {len(results.errors)}")
    print(f"Failures: {len(results.failures)}")
    print(f"Skipped: {len(results.skipped)}")
    
    # Print errors
    if results.errors:
        print("\n===== Errors =====")
        for test, error in results.errors:
            print(f"\nERROR: {test}")
            print(error)
    
    # Print failures
    if results.failures:
        print("\n===== Failures =====")
        for test, failure in results.failures:
            print(f"\nFAILURE: {test}")
            print(failure)
    
    # Return success or failure
    return len(results.errors) == 0 and len(results.failures) == 0

if __name__ == "__main__":
    # If running directly, run all tests
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error running tests: {e}")
        traceback.print_exc()
        sys.exit(1)
