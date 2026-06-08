# AI-FURNIQ

An intelligent furniture design and manufacturing planning system powered by AI. This project uses GPT-4o and Google Generative AI to generate technical furniture designs, create CAD blueprints, and facilitate 3D visualization for manufacturing.

## Features

- 🤖 **AI-Powered Design Generation** - Generates detailed furniture designs using OpenAI GPT-4o
- 🎨 **Blueprint Generation** - Creates DALL-E generated furniture blueprints
- 📐 **CAD Output** - Produces DXF (CAD) files with technical drawings
- 📊 **Design Validation** - Validates designs against manufacturing rules
- 📋 **BOM Generation** - Creates Bill of Materials (BOM) for furniture components
- 🌐 **Web Interface** - Flask-based web application for easy interaction
- 📄 **PDF Export** - Generates professional PDF reports with designs and specifications

## Project Structure

```
ai-furniq/
├── app.py                    # Flask main application
├── generator.py              # AI design generation module (GPT-4o & DALL-E)
├── validator.py              # Design validation module
├── cek_model.py              # Google Generative AI model checker
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── bom_template.csv          # Bill of Materials template
├── rules.json                # Manufacturing rules and constraints
├── templates/
│   └── index.html            # Web interface
├── static/                   # CSS and JavaScript assets
└── flask_session/            # Session storage (not tracked)
```

## Requirements

- Python 3.8+
- OpenAI API key
- Google Generative AI API key
- Virtual environment (recommended)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Afifamsyar2211/AI-FURNIQ-.git
cd ai-furniq
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

**How to get API keys:**

- **OpenAI API Key**: Get it from https://platform.openai.com/api-keys
- **Google Generative AI Key**: Get it from https://ai.google.dev/tutorials/setup

## Usage

### Running the Flask Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Features Available:

1. **Generate Design** - Input furniture description, receive AI-generated technical specifications
2. **View Blueprint** - See DALL-E generated furniture blueprint
3. **Download CAD** - Export DXF file for CAD software (AutoCAD, FreeCAD, etc.)
4. **View Assembly Steps** - Get detailed step-by-step assembly instructions
5. **Download PDF Report** - Generate professional PDF with all design information

## API Keys Security

⚠️ **Important Security Notes:**

- **Never commit `.env` file** to version control
- `.env` is added to `.gitignore` automatically
- Use `.env.example` as a template for setup
- Regenerate API keys immediately if they're exposed
- Use environment variables for all sensitive data

The application uses `python-dotenv` to securely load API keys from environment variables instead of hardcoding them.

## Main Modules

### `app.py`
Flask web application handling:
- Route management
- Session handling
- PDF generation
- File downloads

### `generator.py`
AI design generation using:
- OpenAI GPT-4o for technical specifications
- DALL-E for blueprint images
- Environment variables for secure API key management

### `validator.py`
Design validation against:
- Manufacturing rules (from `rules.json`)
- BOM constraints
- Feasibility checks

### `cek_model.py`
Google Generative AI integration for:
- Model availability checking
- Alternative design generation

## Technologies Used

- **Backend**: Flask (Python web framework)
- **AI/ML**: OpenAI GPT-4o, DALL-E, Google Generative AI
- **CAD**: ezdxf (DXF file generation)
- **PDF**: fpdf2 (PDF report generation)
- **Frontend**: HTML, CSS, JavaScript
- **Data**: pandas, numpy
- **Visualization**: matplotlib, Pillow

## Configuration Files

- **`rules.json`** - Manufacturing rules and constraints
- **`bom_template.csv`** - Bill of Materials template
- **`.env.example`** - Template for environment variables
- **`requirements.txt`** - Python package dependencies

## Development

### Installing Development Dependencies

```bash
pip install -r requirements.txt
```

### Running Tests

```bash
python -m pytest
```

## Troubleshooting

### "OPENAI_API_KEY not found"
- Check that `.env` file exists in project root
- Verify API key is correctly set in `.env`
- Ensure `.venv` is activated

### "GOOGLE_API_KEY not found"
- Similar to above, check `.env` configuration
- Ensure you have the correct Google API key with Generative AI enabled

### Import Errors
- Verify virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version (3.8+)

## License

This project is created and maintained by Afifamsyar2211.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Contact

For questions or support, please open an issue on GitHub or contact the project maintainer.

## Changelog

### Version 1.0.0
- Initial release
- AI-powered furniture design generation
- CAD and PDF export functionality
- Web-based interface
- Secure API key management using environment variables
