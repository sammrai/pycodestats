import os
import argparse
import ast
from collections import defaultdict

def count_lines_of_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read(), filename=file_path)
    total_lines = 0
    classes = 0
    methods = 0
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
    for root, dirs, files in os.walk(directory):
        parent_dir = os.path.relpath(root, directory)
        total_lines = 0
        total_classes = 0
        total_methods = 0
        python_files = [file for file in files if file.endswith('.py')]
        for file in python_files:
            file_path = os.path.join(root, file)
            loc, classes, methods = count_lines_of_code(file_path)
            lines = sum(1 for _ in open(file_path))
            if by_file:
                results[file_path] = {
                    'Lines': lines,
                    'LOC': loc,
                    'Classes': classes,
                    'Methods': methods,
                    'M/C': methods // classes if classes else 0,
                    'LOC/M': loc // methods if methods else 0
                }
            else:
                results[parent_dir]['Lines'] += lines
                results[parent_dir]['LOC'] += loc
                results[parent_dir]['Classes'] += classes
                results[parent_dir]['Methods'] += methods

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
    if by_file:
        headers = ['File', 'Lines', 'LOC', 'Classes', 'Methods', 'M/C', 'LOC/M']
        header_line = "| {:<35} | {:>6} | {:>6} | {:>7} | {:>8} | {:>4} | {:>5} |".format(*headers)
        print(header_line)
        print("-" * len(header_line))
        for path, result in results.items():
            row = "| {:<35} | {:>6} | {:>6} | {:>7} | {:>8} | {:>4} | {:>5} |".format(
                path, result['Lines'], result['LOC'], result['Classes'], result['Methods'], result['M/C'], result['LOC/M']
            )
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
        summary_row = "| {Name:<35} | {Lines:>6} | {LOC:>6} | {Classes:>7} | {Methods:>8} | {M/C:>4} | {LOC/M:>5} |".format(**summary)
        print(summary_row)
    else:
        headers = ['Directory', 'Lines', 'LOC', 'Classes', 'Methods', 'M/C', 'LOC/M']
        header_line = "| {:<20} | {:>6} | {:>6} | {:>7} | {:>8} | {:>4} | {:>5} |".format(*headers)
        print(header_line)
        print("-" * len(header_line))
        for dir_name, result in results.items():
            row = "| {:<20} | {:>6} | {:>6} | {:>7} | {:>8} | {:>4} | {:>5} |".format(
                dir_name, result['Lines'], result['LOC'], result['Classes'], result['Methods'],
                result['Methods'] // result['Classes'] if result['Classes'] else 0,
                result['LOC'] // result['Methods'] if result['Methods'] else 0
            )
            print(row)

def main():
    parser = argparse.ArgumentParser(description="Count lines of code in a directory, excluding comments and docstrings.")
    parser.add_argument("directory", help="Directory to scan for Python files.")
    parser.add_argument("--by-file", action="store_true", help="Show results for each file.")
    args = parser.parse_args()

    results = scan_directory(args.directory, args.by_file)
    print_results(results, args.by_file)

if __name__ == "__main__":
    main()
