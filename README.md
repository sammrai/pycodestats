# pycodestats

pycodestats is a tool to count lines of code, classes, and methods in a Python project. It can scan directories recursively and provides summary statistics for each file or directory.

## Features

- Counts lines of code (excluding comments and docstrings)
- Counts number of classes and methods
- Outputs results in table, JSON, or XML format

## Installation

You can install pycodestats using pip:

```bash
pip install pycodestats
```

## Usage

To scan a directory and output results in table format:

```bash
pycodestats path/to/your/project
```

To output results in JSON format:

```bash
pycodestats path/to/your/project --json
```

To output results in XML format:

```bash
pycodestats path/to/your/project --xml
```

## Example

```bash
pycodestats src --by-file
```

This will output the statistics for each Python file in the `src` directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
