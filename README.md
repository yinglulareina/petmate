# 🐾 PetMate - AI-Powered Pet Health Assistant

## Project Description

PetMate is an AI-powered web application that interprets natural-language descriptions of pet symptoms, provides potential health insights, and recommends nearby veterinary hospitals based on the user's location.

**Supported Pets:** Dogs 🐕 and Cats 🐈

## Motivation

As a pet owner, I know how stressful it feels when pets act sick and you don't know what's wrong. Many people search online but get unreliable results and waste a lot of time trying to find trustworthy answers. This tool helps pet owners get useful information faster and find real help nearby.

## Features

- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT to understand natural language symptom descriptions
- 💡 AI-generated health insights with confidence scores (general guidance only)
- 📍 Location-based veterinary hospital recommendations
- 🎯 Interactive and user-friendly interface
- 🔄 Fallback to rule-based analysis if API unavailable

## Tech Stack

- **Backend**: Python 3.9+
- **Frontend**: Streamlit
- **AI Engine**: OpenAI API (GPT-3.5/4) for natural language understanding
- **Data Storage**: JSON files
- **APIs**: Geolocation services
- **NLP**: OpenAI-powered symptom analysis

## Project Structure

```
petmate/
├── src/
│   ├── ai_symptom_analyzer.py    # AI-powered symptom analysis (OpenAI)
│   ├── symptom_analyzer.py       # Rule-based fallback analysis
│   ├── vet_locator.py             # Hospital location and recommendation
│   ├── data_manager.py            # Data handling utilities
│   └── utils.py                   # Helper functions
├── data/
│   ├── symptoms_database.json     # Symptom-to-condition mappings (fallback)
│   └── vet_hospitals.json         # Hospital database
├── app/
│   └── main.py                    # Main Streamlit application
├── tests/
│   ├── test_ai_symptom_analyzer.py
│   ├── test_symptom_analyzer.py
│   └── test_vet_locator.py
├── scripts/
│   └── check_gitignore.py         # GitIgnore validation tool
├── .env                           # API keys (DO NOT COMMIT)
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/petmate.git
cd petmate

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API Keys
# Create a .env file in the root directory:
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_api_key_here
```

## Getting OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file
6. **Important**: New accounts get $5 free credit

**Note**: Keep your API key secure and never commit it to Git!

## Usage

```bash
# Ensure your .env file is configured with OPENAI_API_KEY

# Run the application
streamlit run app/main.py

# The app will open in your browser at http://localhost:8501
```

### Example Interaction

```
User: "My dog has been vomiting for two days and won't eat anything"

AI Analysis:
✓ Condition: Digestive Upset / Possible Gastritis
✓ Confidence: 78%
✓ Severity: Moderate
✓ Recommended Action: Visit vet within 24 hours for examination
✓ Nearby Hospitals: [3 hospitals listed with ratings and distances]
```

## Development Tools

### Check GitIgnore Configuration
To verify that your .gitignore is working correctly:

```bash
# Run the validation script
python scripts/check_gitignore.py
```

This will check:
- Files that should be ignored are not tracked
- Important files are properly tracked
- .gitignore syntax is correct

### API Cost Estimation

**OpenAI API Pricing** (GPT-3.5-turbo):
- Input: $0.0005 per 1K tokens
- Output: $0.0015 per 1K tokens
- Average query: ~500 tokens total
- **Cost per analysis**: ~$0.001 (0.1 cents)
- **$5 free credit**: ~5,000 analyses

**Note**: The app includes rate limiting and fallback to rule-based analysis if API quota is exceeded.

## Troubleshooting

### API Key Issues

```bash
# If you see "OpenAI API key not found":
# 1. Check .env file exists in project root
# 2. Verify OPENAI_API_KEY is set correctly
# 3. Restart the Streamlit app

# Test your API key:
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('✅ API key is valid')"
```

### Common Errors

- **Rate Limit Error**: Wait a few seconds and try again, or app will use fallback analysis
- **Invalid API Key**: Regenerate key on OpenAI platform
- **Module Not Found**: Run `pip install -r requirements.txt`

## Development Phases

- [x] **Phase 0**: Project setup and configuration
- [ ] **Phase 1**: Rule-based symptom analysis (fallback system)
- [ ] **Phase 2**: OpenAI API integration for AI-powered analysis
- [ ] **Phase 3**: Vet hospital data management
- [ ] **Phase 4**: Location-based recommendations
- [ ] **Phase 5**: Streamlit user interface
- [ ] **Phase 6**: Integration, testing, and optimization

### Development Timeline

**Week 1-2**: Core functionality with rule-based analysis  
**Week 2-3**: OpenAI API integration and testing  
**Week 3-4**: UI development and location features  
**Week 4**: Final testing, optimization, and documentation

## Collaboration Workflow

### Git Workflow
1. Create feature branches for new features: `git checkout -b feature/feature-name`
2. Commit changes with clear messages: `git commit -m "Add symptom analysis logic"`
3. Push to remote: `git push origin feature/feature-name`
4. Create Pull Request to `dev` branch
5. After testing, merge `dev` to `main`

### Branch Strategy
- `main`: Stable production-ready code
- `dev`: Integration and testing
- `feature/*`: Individual feature development

## Important Disclaimers

⚠️ **Medical Disclaimer**: PetMate provides general information only and is NOT a substitute for professional veterinary care. Always consult a licensed veterinarian for medical advice.

## Team

- Developer 1: Yongxuan Li
- Developer 2: Ying Lu

## License

This project is developed as part of CS5001 coursework at Northeastern University.

## Contact

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Last Updated**: November 2025