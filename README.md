# jaybro

A lightweight interactive JSON browser for the terminal.

## Description
`jaybro` is an interactive command-line tool for browsing and exploring JSON files. It features:
- Path-based navigation
- Tab completion for paths and commands
- Search functionality
- Color-coded output
- Session-based search history
- Pretty printing of JSON structures

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/jaybro
cd jaybro

# Make the script executable
chmod +x jaybro.py

# Optional: Create a symbolic link to use it from anywhere
ln -s $(pwd)/jaybro.py /usr/local/bin/jaybro
```

## Dependencies
- Python 3.6+
- termcolor

Install dependencies:
```bash
pip install termcolor
```

## Usage
```bash
# Browse a JSON file
jaybro input.json

## Start typing + TAB for autocomplete on paths or commands
## Press return on a path to display json

# Available commands:
?          : List all top-level nodes
prefix?    : List nodes starting with the specified prefix
?.?        : Expand two levels
??         : Recursively expand all paths
/f WORD    : Case-insensitive filter paths by WORD
/F WORD    : Case-sensitive filter paths by WORD
/k TERM    : Search for TERM in values
/ks        : Save search results
/kl        : List saved search results
/p PATH    : Print JSON at path
/h         : Display help message
%          : Exit program
```

## Examples
```bash
# List top level nodes
?
# List all upon 2nd level nodes, etc
?.?

# Show all paths
??

# Filter paths containing "name" (case-insensitive)
/f name

# Search for values containing "error"
/k error

# Print specific path
/p users.0.name
```

## Features
- **Interactive Browsing**: Navigate through JSON structures using intuitive commands
- **Smart Completion**: Tab completion for both commands and JSON paths
- **Search Capabilities**: Search through paths and values with case-sensitive/insensitive options
- **Color Output**: Syntax highlighted output for better readability
- **Session Storage**: Save and retrieve search results within a session
- **Pretty Printing**: Formatted JSON output with proper indentation

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer
This tool is provided as-is without any warranties. Users are responsible for validating its suitability for their use case.
