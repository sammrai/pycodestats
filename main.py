import os
import argparse
import ast
from collections import defaultdict

COLUMN_WIDTH = 7

def count_lines_of_code(file_path):
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
        for subdir in list(results.keys()):
            parent = os.path.dirname(subdir)
            while parent and parent != '.':
                results[parent]['Lines'] += results[subdir]['Lines']
                results[parent]['LOC'] += results[subdir]['LOC']
                results[parent]['Classes'] += results[subdir]['Classes']
                results[parent]['Methods'] += results[subdir]['Methods']
                parent = os.path.dirname(parent)

    return results

def print_results(results, by_file):
    headers = ['File' if by_file else 'Directory', 'Lines', 'LOC', 'Classes', 'Methods', 'M/C', 'LOC/M']
    name_width = max(len(name) for name in results.keys()) + 2
    header_line = f"{headers[0]:<{name_width}} " + " ".join(f"{header:>{COLUMN_WIDTH}}" for header in headers[1:])
    print(header_line)
    print("-" * len(header_line))

    for path, result in results.items():
        row = f"{path:<{name_width}} {result['Lines']:>{COLUMN_WIDTH}} {result['LOC']:>{COLUMN_WIDTH}} {result['Classes']:>{COLUMN_WIDTH}} {result['Methods']:>{COLUMN_WIDTH}} {result['Methods'] // result['Classes'] if result['Classes'] else 0:>{COLUMN_WIDTH}} {result['LOC'] // result['Methods'] if result['Methods'] else 0:>{COLUMN_WIDTH}}"
        print(row)

    print("-" * len(header_line))
    total_lines = sum(result['Lines'] for result in results.values())
    total_loc = sum(result['LOC'] for result in results.values())
    total_classes = sum(result['Classes'] for result in results.values())
    total_methods = sum(result['Methods'] for result in results.values())
    summary = {
        'Name': 'SUM:',
        'Lines': total_lines,
        'LOC': total_loc,
        'Classes': total_classes,
        'Methods': total_methods,
        'M/C': total_methods // total_classes if total_classes else 0,
        'LOC/M': total_loc // total_methods if total_methods else 0
    }
    summary_row = f"{summary['Name']:<{name_width}} {summary['Lines']:>{COLUMN_WIDTH}} {summary['LOC']:>{COLUMN_WIDTH}} {summary['Classes']:>{COLUMN_WIDTH}} {summary['Methods']:>{COLUMN_WIDTH}} {summary['M/C']:>{COLUMN_WIDTH}} {summary['LOC/M']:>{COLUMN_WIDTH}}"
    print(summary_row)

def main():
    parser = argparse.ArgumentParser(
        description="Count lines of code in a directory, excluding comments and docstrings.",
        epilog="This script scans a directory (recursively) for Python files and summarizes their code statistics."
    )
    parser.add_argument("directory", help="Directory to scan for Python files.")
    parser.add_argument(
        "--by-file", 
        action="store_true", 
        help="Show results for each file instead of aggregating by directory."
    )
    args = parser.parse_args()

    results = scan_directory(args.directory, args.by_file)
    print_results(results, args.by_file)

if __name__ == "__main__":
    main()
