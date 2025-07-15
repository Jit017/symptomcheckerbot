# 🩺 Symptom Checker Bot

A free, offline-ready health assistant that helps identify possible medical conditions based on user symptoms. Built with Python, Streamlit, and powered by a local CSV dataset.

## ✨ Features

- **100% Free & Local**: No paid APIs or cloud dependencies
- **Offline Ready**: Works without internet connection (except for optional translation)
- **Smart Matching**: Supports both exact and partial symptom matching
- **Multiple Input Methods**: Type symptoms or select from dropdown
- **Confidence Scoring**: Shows likelihood based on symptom overlap
- **Optional Translation**: Hindi translation support (requires internet)
- **Clean UI**: Modern, responsive design with medical disclaimer
- **Comprehensive Dataset**: 100+ symptom-condition mappings

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone or download this project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run main.py
   ```

4. **Open your browser to:**
   ```
   http://localhost:8501
   ```

### Alternative Installation (Individual packages)
```bash
pip install streamlit pandas deep_translator
```

## 📁 Project Structure

```
symptomcheckerbot/
├── main.py              # Main Streamlit application
├── symptoms.csv         # Medical dataset (symptoms & conditions)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🎯 How to Use

1. **Start the app** using `streamlit run main.py`
2. **Enter symptoms** either by:
   - Typing them in the text area (comma-separated)
   - Selecting from the dropdown list
3. **View results** with possible conditions ranked by confidence
4. **Optional**: Enable Hindi translation in the sidebar
5. **Explore**: Check the sidebar for dataset statistics

### Example Usage

**Input:** `fever, headache, cough`

**Output:** 
- Common Cold (High confidence - matches 3 symptoms)
- Influenza (High confidence - matches 3 symptoms)  
- Bronchitis (Medium confidence - matches 1 symptom)

## 🧠 How It Works

1. **Data Loading**: Loads symptoms.csv with pandas (cached for performance)
2. **Symptom Normalization**: Cleans and standardizes user input
3. **Smart Matching**: 
   - Exact matches (highest priority)
   - Partial matches (word overlap)
   - Fuzzy matching for typos
4. **Confidence Scoring**: Based on number of matching symptoms
5. **Result Ranking**: Sorts conditions by match frequency

## 📊 Dataset

The `symptoms.csv` contains 100+ medically accurate symptom-condition pairs including:

- **Common conditions**: Cold, flu, headaches, allergies
- **Chronic diseases**: Diabetes, arthritis, hypertension  
- **Serious conditions**: Pneumonia, appendicitis, heart issues
- **Specialized areas**: Mental health, skin conditions, reproductive health

### Dataset Format
```csv
symptom,condition
fever,Common Cold
headache,Migraine
cough,Bronchitis
...
```

## ⚠️ Medical Disclaimer

**This tool is for educational and informational purposes only.** 

- Not a substitute for professional medical advice
- Always consult qualified healthcare providers
- In medical emergencies, contact emergency services immediately
- Results are based on limited dataset and basic matching algorithms

## 🔧 Customization

### Adding New Symptoms/Conditions
1. Edit `symptoms.csv`
2. Add new rows in format: `symptom,condition`
3. Restart the application

### Modifying the UI
- Edit the CSS in `main.py` (lines 22-50)
- Customize colors, fonts, layout as needed

### Adding New Languages
- Install additional language support for `deep_translator`
- Modify the `translate_text()` function in `main.py`

## 🐛 Troubleshooting

### Common Issues

**"symptoms.csv not found"**
- Ensure the CSV file is in the same directory as main.py

**Translation not working**
- Check internet connection
- Verify `deep_translator` is installed
- Translation is optional - app works without it

**Streamlit won't start**
- Verify Python 3.10+ is installed
- Check all dependencies are installed: `pip list`
- Try: `python -m streamlit run main.py`

### Performance Tips

- App uses caching - first load may be slower
- For large datasets, consider adding search indexing
- Close browser tabs when not in use to free memory

## 🚀 Future Enhancements

- [ ] Machine Learning symptom prediction
- [ ] Symptom severity scoring
- [ ] Medical history integration
- [ ] Export results to PDF
- [ ] Voice input support
- [ ] Drug interaction checker
- [ ] Appointment booking integration

## 🤝 Contributing

This is a learning project! Feel free to:

1. Fork the repository
2. Add new features or improve existing ones
3. Expand the symptom dataset
4. Improve the matching algorithms
5. Add new languages or UI improvements

## 📄 License

This project is free to use for educational and personal purposes. 

**Note**: Medical data should always be handled responsibly and in compliance with local healthcare regulations.

---

**Built with ❤️ using Streamlit • 100% Free & Local • Perfect for Learning AI/ML** 