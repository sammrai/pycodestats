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

## Output Format

When using the default table format, the output includes the following columns:

- **Directory/File**: The name of the directory or file. If `--by-file` is used, this column lists each individual file. Otherwise, it lists each directory.
- **Lines**: The total number of lines in the file or directory. This includes all lines, regardless of content.
- **LOC**: The number of lines of code (LOC), excluding comments and docstrings.
- **Classes**: The number of classes defined in the file or directory.
- **Methods**: The number of methods defined in the file or directory.
- **M/C**: The average number of methods per class. This is calculated as the number of methods divided by the number of classes. If there are no classes, this value is 0.
- **LOC/M**: The average number of lines of code per method. This is calculated as the number of lines of code divided by the number of methods. If there are no methods, this value is 0.

### Example Output

```plaintext
File                        Lines    LOC  Classes  Methods   M/C   LOC/M
-------------------------------------------------------------------------
src/main.py                  120     130       2        10     5      13
src/utils.py                  80      90       1         5     5      18
src/models.py                100     120       3        15     5       8
-------------------------------------------------------------------------
SUM:                         300     340       6        30     5      11
```

In this example:

- **Directory**: Lists directories or files.
- **Lines**: Shows the total number of lines.
- **LOC**: Shows the lines of code.
- **Classes**: Shows the number of classes.
- **Methods**: Shows the number of methods.
- **M/C**: Shows the average number of methods per class.
- **LOC/M**: Shows the average number of lines of code per method.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
