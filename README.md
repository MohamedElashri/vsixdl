# VSIXDL - VSCode Extension Downloader

VSIXDL is a powerful tool that helps you download VSCode extensions (`.vsix` files) directly from the Visual Studio Marketplace. It provides both a modern web interface and a CLI tool, making it flexible for different use cases.

## Why VSIXDL?

Microsoft recently removed direct download links for VS Code extensions from the Marketplace, making it harder to download `.vsix` files for offline installation. This tool is particularly useful if you:
- Work on restricted machines without direct access to the VS Code Marketplace
- Use VS Code forks like VSCodium, Cursor, or other alternatives
- Need to manage multiple versions of extensions

## Getting Started

### Web Interface (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/MohamedElashri/vsixdl
cd vsixdl
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python server.py
```

4. Open your browser and navigate to `http://localhost:5000`

### Usage

1. Enter the extension ID (e.g., `ms-python.python`) or the full marketplace URL
2. Select how many versions you want to fetch (5, 10, 20, or all)
3. Click the download button next to the version you want to download

The application will fetch the list of available versions from the official VS Code marketplace and allow you to download any specific version.

## Alternative: Command Line Interface

If you prefer working from the terminal, VSIXDL also provides a CLI tool. Check out the [CLI documentation](cli/README.md) for installation and usage instructions.

## License

VSIXDL is released under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is not affiliated with or endorsed by Microsoft. Use it responsibly and ensure compliance with the VS Code Marketplace terms of service.
