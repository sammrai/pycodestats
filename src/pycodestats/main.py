import os
import argparse
import ast
import json
import xml.etree.ElementTree as ET
from collections import defaultdict

COLUMN_WIDTH = 7


def count_lines_of_code(file_path):
    """Count the lines of code, classes, and methods in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        try:
            tree = ast.parse("".join(lines), filename=file_path)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return 0, 0, 0

    total_lines, classes, methods = len(lines), 0, 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes += 1
            methods += sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
        if isinstance(node, ast.FunctionDef):
            methods += 1

    # Exclude lines that are comments or empty
    loc = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
    
    return total_lines, loc, classes, methods


def scan_directory(directory, by_file):
    """Scan the directory and collect code metrics for each file or directory."""
    results = defaultdict(
        lambda: {'Lines': 0, 'LOC': 0, 'Classes': 0, 'Methods': 0})
    for root, _, files in os.walk(directory):
        parent_dir = os.path.relpath(root, directory)
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_lines, loc, classes, methods = count_lines_of_code(file_path)
                key = file_path if by_file else parent_dir
                results[key]['Lines'] += total_lines
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


def print_results(results, by_file, output_format):
    """Print the results in a formatted table or write to a file."""
    if output_format == "table":
        headers = ['File' if by_file else 'Directory', 'Lines',
                   'LOC', 'Classes', 'Methods', 'M/C', 'LOC/M']
        name_width = max(max(len(name) for name in results.keys()), 9)
        header_line = f"{headers[0]:<{name_width}} " + \
            " ".join(f"{header:>{COLUMN_WIDTH}}" for header in headers[1:])
        print(header_line)
        print("-" * len(header_line))

        for path, result in results.items():
            row = format_row(path, result, name_width)
            print(row)

        print("-" * len(header_line))
        if by_file:
            summary_row = format_row(
                'SUM:', calculate_summary(results), name_width)
            print(summary_row)
    elif output_format == "json":
        print(json.dumps(results, indent=4))
    elif output_format == "xml":
        root = ET.Element("results")
        for path, metrics in results.items():
            entry = ET.SubElement(root, "entry", name=path)
            for key, value in metrics.items():
                child = ET.SubElement(entry, key)
                child.text = str(value)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)  # Pretty print the XML
        print(ET.tostring(root, encoding="unicode"))


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


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Count lines of code in a directory, excluding comments and docstrings.",
        epilog="This script scans a directory (recursively) for Python files and summarizes their code statistics."
    )
    parser.add_argument(
        "directory", help="Directory to scan for Python files.")
    parser.add_argument("--by-file", action="store_true",
                        help="Show results for each file instead of aggregating by directory.")

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_const", const="json",
                              dest="output_format", help="Write the results as JSON.")
    output_group.add_argument("--xml", action="store_const", const="xml",
                              dest="output_format", help="Write the results as XML.")

    parser.set_defaults(output_format="table")

    return parser.parse_args()


def main():
    args = parse_arguments()
    results = scan_directory(args.directory, args.by_file)
    print_results(results, args.by_file, args.output_format)


if __name__ == "__main__":
    main()
