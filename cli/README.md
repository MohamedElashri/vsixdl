# VSIXDL CLI

This is the command-line interface (CLI) version of VSIXDL. If you prefer a graphical interface, check out our [main web interface](../README.md).

## Installation

To install the CLI version of VSIXDL:

```bash
git clone https://github.com/MohamedElashri/vsixdl
cd vsixdl/cli
```

### Dependencies

The CLI tool has minimal dependencies:
- Python 3
- requests
- colorama

Install them using:
```bash
pip install requests colorama
```

### Optional: Add to PATH

For convenience, you can make the script executable and add it to your PATH:

```bash
chmod +x vsixdl.py
sudo ln -s $(pwd)/vsixdl.py /usr/local/bin/vsixdl
```

## Usage

### 1. List Available Versions

To see all available versions of an extension:

```bash
python vsixdl.py list --id ms-toolsai.jupyter
```

Example output:
```
Fetching available versions...

Available Versions:
1. 2025.1.2025012301
2. 2025.1.2025012301
3. 2025.1.2025012301
...
```

### 2. Download Latest Version

To download the most recent version:

```bash
python vsixdl.py download --id ms-toolsai.jupyter
```

### 3. Download Specific Version

To download a particular version:

```bash
python vsixdl.py download --id ms-toolsai.jupyter --version 2023.8.1002501831
```

## Input Formats

The CLI accepts two formats for extension identification:

1. **Extension ID** (recommended):
   ```
   ms-toolsai.jupyter
   ```

2. **Marketplace URL**:
   ```
   https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter
   ```

## Error Messages

The CLI provides clear error messages for common issues:

- Invalid input format:
  ```
  Invalid extension ID or URL format. Use 'publisher.extension' or full URL.
  ```

- Connection issues:
  ```
  Error: Unable to connect to the VSCode Marketplace API.
  ```

- Version not found:
  ```
  Error: Specified version not found.
  ```

## Note

While the CLI tool is fully functional, consider using the [web interface](../README.md) for a more user-friendly experience.

## License

VSIXDL is released under the **MIT License**. See the [LICENSE](../LICENSE) file for details.

## Disclaimer

This tool is not affiliated with or endorsed by Microsoft. Use it responsibly and ensure compliance with the VS Code Marketplace terms of service.
