import os
import argparse
import ast
from collections import defaultdict

COLUMN_WIDTH = 7

def count_lines_of_code(file_path):
    """Count the lines of code, classes, and methods in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read(), filename=file_path)
    
    total_lines, classes, methods = 0, 0, 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes += 1
            methods += sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
        if isinstance(node, ast.FunctionDef):
            methods += 1
        if not isinstance(node, (ast.Expr, ast.If, ast.For, ast.While, ast.Try, ast.FunctionDef, ast.ClassDef)):
            total_lines += 1
    
    return total_lines, classes, methods

def scan_directory(directory, by_file):
    """Scan the directory and collect code metrics for each file or directory."""
    results = defaultdict(lambda: {'Lines': 0, 'LOC': 0, 'Classes': 0, 'Methods': 0})
    for root, _, files in os.walk(directory):
        parent_dir = os.path.relpath(root, directory)
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                loc, classes, methods = count_lines_of_code(file_path)
                lines = sum(1 for _ in open(file_path))
                key = file_path if by_file else parent_dir
                results[key]['Lines'] += lines
                results[key]['LOC'] += loc
                results[key]['Classes'] += classes
                results[key]['Methods'] += methods

    if not by_file:
        aggregate_parent_directory_results(results)

    return results

def aggregate_parent_directory_results(results):
    """Aggregate results for parent directories."""
    for subdir in list(results.keys()):
        parent = os.path.dirname(subdir)
        while parent and parent != '.':
            results[parent]['Lines'] += results[subdir]['Lines']
            results[parent]['LOC'] += results[subdir]['LOC']
            results[parent]['Classes'] += results[subdir]['Classes']
            results[parent]['Methods'] += results[subdir]['Methods']
            parent = os.path.dirname(parent)

def print_results(results, by_file):
    """Print the results in a formatted table."""
    headers = ['File' if by_file else 'Directory', 'Lines', 'LOC', 'Classes', 'Methods', 'M/C', 'LOC/M']
    name_width = max(len(name) for name in results.keys()) + 2
    header_line = f"{headers[0]:<{name_width}} " + " ".join(f"{header:>{COLUMN_WIDTH}}" for header in headers[1:])
    print(header_line)
    print("-" * len(header_line))

    for path, result in results.items():
        row = format_row(path, result, name_width)
        print(row)

    print("-" * len(header_line))
    summary_row = format_row('SUM:', calculate_summary(results), name_width)
    print(summary_row)

def format_row(name, result, name_width):
    """Format a single row for the output table."""
    return (
        f"{name:<{name_width}} "
        f"{result['Lines']:>{COLUMN_WIDTH}} "
        f"{result['LOC']:>{COLUMN_WIDTH}} "
        f"{result['Classes']:>{COLUMN_WIDTH}} "
        f"{result['Methods']:>{COLUMN_WIDTH}} "
        f"{result['Methods'] // result['Classes'] if result['Classes'] else 0:>{COLUMN_WIDTH}} "
        f"{result['LOC'] // result['Methods'] if result['Methods'] else 0:>{COLUMN_WIDTH}}"
    )

def calculate_summary(results):
    """Calculate the summary metrics for all results."""
    total_lines = sum(result['Lines'] for result in results.values())
    total_loc = sum(result['LOC'] for result in results.values())
    total_classes = sum(result['Classes'] for result in results.values())
    total_methods = sum(result['Methods'] for result in results.values())
    return {
        'Lines': total_lines,
        'LOC': total_loc,
        'Classes': total_classes,
        'Methods': total_methods,
        'M/C': total_methods // total_classes if total_classes else 0,
        'LOC/M': total_loc // total_methods if total_methods else 0
    }

def main():
    parser = argparse.ArgumentParser(
        description="Count lines of code in a directory, excluding comments and docstrings.",
        epilog="This script scans a directory (recursively) for Python files and summarizes their code statistics."
    )
    parser.add_argument("directory", help="Directory to scan for Python files.")
    parser.add_argument("--by-file", action="store_true", help="Show results for each file instead of aggregating by directory.")
    args = parser.parse_args()

    results = scan_directory(args.directory, args.by_file)
    print_results(results, args.by_file)

if __name__ == "__main__":
    main()
