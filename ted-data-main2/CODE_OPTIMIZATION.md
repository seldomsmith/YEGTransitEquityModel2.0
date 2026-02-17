# Code Optimization Notes

## Files Requiring Refactoring (>500 lines)

The following files exceed 500 lines and should be refactored into smaller modules to optimize token usage when working with AI assistants:

1. **ted/fare.py** (1043 lines)
   - Suggested split: Separate fare calculation logic, fare product definitions, and fare analysis into distinct modules

2. **ted/gtfs.py** (790 lines)
   - Suggested split: Separate GTFS parsing, validation, and analysis functions

3. **ted/run.py** (754 lines)
   - Suggested split: Separate region setup, matrix computation, and metric calculation into distinct modules

## Token Optimization Strategy

**Why this matters**: AI assistants are charged for the entire file every time any part of it is discussed. Dividing a 1000-line file into two 500-line files makes prompts twice as cheap.

**When to refactor**: Before making significant changes to any of the files listed above, consider splitting them first.

## Current Status

- ✅ Configuration files are appropriately sized
- ✅ Helper scripts are small and focused
- ⏳ Core modules (fare, gtfs, run) need refactoring before major edits
