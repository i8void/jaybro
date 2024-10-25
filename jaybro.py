#!/usr/bin/env python3

import os
import json
import readline
import argparse
import sys
from termcolor import colored
from datetime import datetime

class PathCompleter:
    def __init__(self, json_data):
        self.json_data = json_data
        self.paths = list(extract_paths(json_data).keys())
        self.current_completions = []
        self.commands = {
            '/f ': 'Case-insensitive filter paths by word',
            '/F ': 'Case-sensitive filter paths by word',
            '/k ': 'Search for term in JSON values, print paths with content, and pretty print the containing JSON node',
            '/ks': 'Save the results of the previous /k search to a session-specific JSON file',
            '/kl': 'List the content of the session-specific JSON file in a pretty format',
            '/p ': 'Print JSON at path',
            '/h ': 'Display help message'
        }
        
    def complete(self, text, state):
        if state == 0:
            # Special commands completion
            if text.startswith('/'):
                self.current_completions = []
                for cmd, help_text in self.commands.items():
                    if cmd.startswith(text):
                        # Add help text in a different color
                        self.current_completions.append(f"{cmd}\t{colored(help_text, 'yellow')}")
            else:
                # Path completion
                self.current_completions = [p for p in self.paths if p.startswith(text)]
                
        return self.current_completions[state] if state < len(self.current_completions) else None

def load_json(filename):
    """Load a JSON file into a Python dictionary."""
    with open(filename, 'r') as file:
        return json.load(file)

def extract_paths(data, current_path='', results=None):
    """Recursively extract all paths in the JSON data."""
    if results is None:
        results = {}
    if isinstance(data, dict):
        for key, value in data.items():
            path = f'{current_path}.{key}' if current_path else key
            results[path] = value
            extract_paths(value, path, results)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            path = f'{current_path}[{i}]'
            results[path] = item
            extract_paths(item, path, results)
    return results

def get_value_at_path(data, path):
    """Get value at the specified path in the JSON data."""
    elements = path.strip().split('.')
    try:
        current_data = data
        for elem in elements:
            if '[' in elem and ']' in elem:
                index = int(elem[elem.find('[') + 1:elem.find(']')])
                elem = elem.split('[')[0]
                current_data = current_data[elem][index]
            else:
                current_data = current_data[elem]
        return current_data
    except (KeyError, IndexError, TypeError):
        return None

def display_paths_at_depth(data, depth):
    """Display paths at a specific depth."""
    paths = extract_paths(data)
    for path, value in paths.items():
        path_parts = path.split('.')
        if len(path_parts) <= depth:
            print(colored(f"{path}", "blue"))

def print_structure(data, path):
    """Print the content of the JSON structure at the specified path."""
    value = get_value_at_path(data, path)
    if value is not None:
        print(colored(json.dumps(value, indent=4), "cyan"))
    else:
        print(colored("Invalid path.", "red"))

def search_values_in_json(data, term, file_name, session_ts):
    """Search for a term in the JSON values and print matching paths and content."""
    paths = extract_paths(data)
    json_output = []
    
    for path, value in paths.items():
        if term.lower() in str(value).lower():
            current_tag = path.split('.')[-1]
            value_str = str(value)
            highlighted_value = value_str.replace(term.lower(), colored(term.lower(), 'red'))
            result = f"Path: {path}\nTag: {current_tag}\nValue: {highlighted_value}\n"
            print(colored(result, "blue"))
            print(colored(json.dumps(get_value_at_path(data, path), indent=4), "cyan"))
            
            # For JSON output
            json_output.append({
                "path": path,
                "tag": current_tag,
                "value": get_value_at_path(data, path)
            })
    
    if json_output:
        session_file = f"{file_name}_{session_ts}.json"
        
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        existing_data.extend(json_output)
        
        with open(session_file, "w") as f:
            json.dump(existing_data, f, indent=2)

def list_saved_json(file_name, session_ts):
    session_file = f"{file_name}_{session_ts}.json"
    try:
        with open(session_file, "r") as f:
            saved_data = json.load(f)
            for entry in saved_data:
                print(colored(f"Path: {entry['path']}", "blue"))
                print(colored(f"Tag: {entry['tag']}", "green"))
                print(colored(f"Value: {json.dumps(entry['value'], indent=2)}", "yellow"))
                print()
    except FileNotFoundError:
        print(colored("No saved JSON data found for the current session.", "red"))

def print_help():
    """Print the available commands."""
    help_message = """
Available commands:
?          : List all top-level nodes.
prefix?    : List nodes starting with the specified prefix.
?.?        : Expand two levels.
??         : Recursively expand all paths.
/f WORD    : Case-insensitive filter paths by WORD and list them.
/F WORD    : Case-sensitive filter paths by WORD and list them.
/k TERM    : Search for TERM in JSON values, print paths with content, and pretty print the containing JSON node.
/ks        : Save the results of the previous /k search to a session-specific JSON file.
/kl        : List the content of the session-specific JSON file in a pretty format.
/p PATH    : Print JSON at the specified path.
/h         : Display this help message.
%          : Exit the program.

Use TAB for autocompletion of paths and commands (with help text).
"""
    print(colored(help_message, "yellow"))

def setup_readline():
    """Set up readline with proper configuration for the current platform."""
    if sys.platform == 'darwin':  # macOS
        if os.path.exists(os.path.expanduser('~/.inputrc')):
            readline.read_init_file()
        readline.parse_and_bind('bind ^I rl_complete')
    else:  # Linux and others
        readline.parse_and_bind('tab: complete')

def interactive_browse(json_data, file_name):
    """Main function to handle user interaction."""
    session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Set up readline with custom completer
    completer = PathCompleter(json_data)
    readline.set_completer(completer.complete)
    readline.set_completer_delims(' \t\n')
    setup_readline()
    
    print_help()  # Display help on first run

    while True:
        try:
            user_input = input(colored("\nEnter command or path: ", "green")).strip()
            
            # Strip off the help text if present (from autocompletion)
            if '\t' in user_input:
                user_input = user_input.split('\t')[0]

            if user_input == "%":
                print(colored("Exiting.", "yellow"))
                break
            elif user_input == "/h":
                print_help()
            elif user_input == "?":
                display_paths_at_depth(json_data, 1)
            elif user_input == "??":
                display_paths_at_depth(json_data, float('inf'))
            elif user_input.count("?.") > 0:
                depth = user_input.count("?.") + 1
                display_paths_at_depth(json_data, depth)
            elif user_input.endswith("?"):
                prefix = user_input[:-1]
                paths = extract_paths(json_data)
                matching_paths = {path for path in paths.keys() if path.startswith(prefix)}
                if not matching_paths:
                    print(colored("No matching results.", "red"))
                else:
                    for path in matching_paths:
                        print(colored(f"{path}", "blue"))
            elif user_input.startswith("/f "):
                word = user_input[3:].strip().lower()
                paths = extract_paths(json_data)
                matching_paths = {path for path in paths.keys() if word in path.lower()}
                for path in matching_paths:
                    highlighted_path = path.replace(word.lower(), colored(word.lower(), 'red'))
                    print(colored(f"{highlighted_path}", "blue"))
            elif user_input.startswith("/F "):
                word = user_input[3:].strip()
                paths = extract_paths(json_data)
                matching_paths = {path for path in paths.keys() if word in path}
                for path in matching_paths:
                    highlighted_path = path.replace(word, colored(word, 'red'))
                    print(colored(f"{highlighted_path}", "blue"))
            elif user_input.startswith("/k "):
                term = user_input[3:].strip()
                search_values_in_json(json_data, term, file_name, session_ts)
            elif user_input == "/ks":
                # Save the results of the previous /k search
                pass
            elif user_input == "/kl":
                list_saved_json(file_name, session_ts)
            elif user_input.startswith("/p "):
                try:
                    path_to_print = user_input[3:].strip()
                    print_structure(json_data, path_to_print)
                except ValueError:
                    print(colored("Invalid input. Please enter a valid path.", "red"))
            else:
                print_structure(json_data, user_input)

        except EOFError:
            print(colored("\nEOF detected. Exiting.", "yellow"))
            break

    print(colored("JSON browser session ended.", "green"))


def main():
    parser = argparse.ArgumentParser(description="Interactive JSON browser.")
    parser.add_argument("json_file", nargs="?", help="Path to the JSON file to browse")
    args = parser.parse_args()

    try:
        # Check if there's input from pipe
        if not sys.stdin.isatty():
            # Read from stdin for piped input
            json_data = json.load(sys.stdin)
            file_name = "stdin"
        elif args.json_file and os.path.exists(args.json_file):
            json_data = load_json(args.json_file)
            file_name = os.path.splitext(args.json_file)[0]
        else:
            print(colored("Error: No JSON file provided or piped input detected.", "red"))
            return

        interactive_browse(json_data, file_name)
    except json.JSONDecodeError:
        print(colored("Error: Invalid JSON data provided.", "red"))
    except Exception as e:
        print(colored(f"An unexpected error occurred: {e}", "red"))

if __name__ == "__main__":
    main()
