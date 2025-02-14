# VSIXDL - VSCode Extension Downloader

VSIXDL is a powerful tool that helps you download VSCode extensions (`.vsix` files) directly from the Visual Studio Marketplace. It provides both a modern web interface and a CLI tool, making it flexible for different use cases.

## Why VSIXDL?

Microsoft recently removed direct download links for VS Code extensions from the Marketplace, making it harder to download `.vsix` files for offline installation. This tool is particularly useful if you:
- Work on restricted machines without direct access to the VS Code Marketplace
- Need to download specific versions of extensions for offline installation
- Want to manage multiple versions of extensions

## Hosted Version

A demo version of VSIXDL is available at [Demo](https://vsixdl.melashri.net). Please note:
- This is a demonstration instance with restricted usage limits
- Users must adhere to Visual Studio Marketplace Terms of Service
- No guarantees of availability or support are provided
- For production use, please host your own instance

## Getting Started

### Web Interface

#### Docker Installation (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/MohamedElashri/vsixdl
cd vsixdl/web
```

2. Copy the example environment file:
```bash
cp example.env .env
```

3. Edit `.env` file with your settings

4. Build and run with Docker Compose:
```bash
docker compose up -d
```

The application will be available at `http://localhost:5000`

#### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/MohamedElashri/vsixdl
cd vsixdl/web
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy and configure environment:
```bash
cp example.env .env
# Edit .env with your settings
```

4. Start the server:
```bash
python server.py
```

### Usage

1. Enter the extension ID (e.g., `ms-python.python`) or the full marketplace URL
2. Select how many versions you want to fetch (5, 10, 20, or all)
3. Click the download button next to the version you want to download

The application will fetch the list of available versions from the official VS Code marketplace and allow you to download any specific version.

### Command Line Interface

If you prefer working from the terminal, VSIXDL also provides a CLI tool. Check out the [CLI documentation](cli/README.md) for installation and usage instructions.

## License

VSIXDL is released under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is provided as-is, without any warranty. Users are responsible for ensuring compliance with Visual Studio Marketplace Terms of Service and any applicable licenses. The hosted demo version is provided for demonstration purposes only and may be subject to rate limiting or other restrictions.
