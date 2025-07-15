import streamlit as st
import pandas as pd
import re
from collections import Counter
from typing import List, Dict, Tuple
from datetime import datetime
import base64
import json

# Optional imports
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

try:
    import pdfkit
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Configure Streamlit page
st.set_page_config(
    page_title="🩺 Symptom Checker Bot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'show_back_to_top' not in st.session_state:
    st.session_state.show_back_to_top = False

def get_css_styles(dark_mode=False):
    """Get CSS styles based on theme mode"""
    if dark_mode:
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Dark Mode Styles */
            .main {
                font-family: 'Inter', sans-serif;
                background-color: #0f172a;
                color: #e2e8f0;
            }
            
            .main-header {
                font-size: 3rem;
                color: #60a5fa;
                text-align: center;
                margin-bottom: 2rem;
                font-weight: 700;
                background: linear-gradient(135deg, #60a5fa, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .card {
                background: #1e293b;
                border-radius: 16px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                border: 1px solid #334155;
                transition: all 0.3s ease;
                min-height: 48px;
            }
            
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
                border-color: #475569;
            }
            
            .symptom-card {
                background: linear-gradient(135deg, #1e3a8a, #1e40af);
                border-left: 4px solid #60a5fa;
                padding: 1.2rem;
                border-radius: 12px;
                margin: 0.5rem 0;
                transition: transform 0.2s ease;
                min-height: 48px;
                cursor: pointer;
            }
            
            .symptom-card:hover {
                transform: translateX(4px);
                background: linear-gradient(135deg, #1e40af, #2563eb);
            }
            
            .condition-card {
                background: #1e293b;
                border-radius: 20px;
                padding: 2rem;
                margin: 1.5rem 0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                border: 1px solid #334155;
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
                min-height: 48px;
            }
            
            .condition-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
            }
            
            .condition-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
                border-color: #475569;
            }
            
            .condition-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: #f1f5f9;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .confidence-high {
                background: #7f1d1d;
                color: #fca5a5;
                border: 1px solid #991b1b;
            }
            
            .confidence-medium {
                background: #78350f;
                color: #fed7aa;
                border: 1px solid #92400e;
            }
            
            .confidence-low {
                background: #1e3a8a;
                color: #93c5fd;
                border: 1px solid #1e40af;
            }
            
            .info-section {
                background: #0f172a;
                color: #e2e8f0;
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
                border-left: 4px solid #10b981;
            }
            
            .translation-section {
                background: linear-gradient(135deg, #1e40af, #7c3aed);
                color: white;
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
                font-style: italic;
            }
            
            .alert-warning {
                background: #78350f;
                border-color: #f59e0b;
                color: #fed7aa;
            }
            
            .alert-info {
                background: #1e3a8a;
                border-color: #3b82f6;
                color: #93c5fd;
            }
            
            .stat-card {
                background: #1e293b;
                color: #e2e8f0;
                padding: 1.5rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                border-top: 4px solid #60a5fa;
                margin: 1rem 0;
                transition: transform 0.2s ease;
                min-height: 48px;
            }
            
            .welcome-section {
                background: linear-gradient(135deg, #1e40af, #7c3aed);
                color: white;
                padding: 3rem 2rem;
                border-radius: 20px;
                text-align: center;
                margin: 2rem 0;
            }
            
            .no-results {
                text-align: center;
                padding: 3rem 2rem;
                background: linear-gradient(135deg, #78350f, #92400e);
                border-radius: 20px;
                margin: 2rem 0;
                color: #fed7aa;
            }
            
            .suggestion-card {
                background: #1e3a8a;
                color: #e2e8f0;
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 12px;
                border-left: 4px solid #60a5fa;
                transition: transform 0.2s ease;
                min-height: 48px;
                cursor: pointer;
            }
            
            .suggestion-card:hover {
                transform: translateX(4px);
                background: #1e40af;
            }
            
            .footer {
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: #e2e8f0;
                padding: 2rem;
                border-radius: 20px;
                text-align: center;
                margin-top: 3rem;
                border: 1px solid #334155;
            }
            
            .back-to-top {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 1.2rem;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
                transition: all 0.3s ease;
                z-index: 1000;
            }
            
            .back-to-top:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.6);
            }
            
            .severity-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.25rem;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 0.5rem;
            }
            
            .severity-critical {
                background: #7f1d1d;
                color: #fca5a5;
            }
            
            .severity-high {
                background: #78350f;
                color: #fed7aa;
            }
            
            .severity-medium {
                background: #365314;
                color: #bef264;
            }
            
            .severity-low {
                background: #1e3a8a;
                color: #93c5fd;
            }
            
            /* Custom scrollbar for dark mode */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #0f172a;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #475569;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #64748b;
            }
        </style>
        """
    else:
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Light Mode Styles */
            .main {
                font-family: 'Inter', sans-serif;
            }
            
            .main-header {
                font-size: 3rem;
                color: #1e40af;
                text-align: center;
                margin-bottom: 2rem;
                font-weight: 700;
                background: linear-gradient(135deg, #1e40af, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .card {
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                border: 1px solid #e5e7eb;
                transition: all 0.3s ease;
                min-height: 48px;
            }
            
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }
            
            .symptom-card {
                background: linear-gradient(135deg, #eff6ff, #dbeafe);
                border-left: 4px solid #3b82f6;
                padding: 1.2rem;
                border-radius: 12px;
                margin: 0.5rem 0;
                transition: transform 0.2s ease;
                min-height: 48px;
                cursor: pointer;
            }
            
            .symptom-card:hover {
                transform: translateX(4px);
                background: linear-gradient(135deg, #dbeafe, #bfdbfe);
            }
            
            .condition-card {
                background: white;
                border-radius: 20px;
                padding: 2rem;
                margin: 1.5rem 0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                border: 1px solid #e5e7eb;
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
                min-height: 48px;
            }
            
            .condition-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
            }
            
            .condition-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            }
            
            .condition-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .confidence-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                border-radius: 50px;
                font-size: 0.875rem;
                font-weight: 600;
                margin: 0.5rem 0;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .confidence-high {
                background: #fee2e2;
                color: #dc2626;
                border: 1px solid #fecaca;
            }
            
            .confidence-medium {
                background: #fef3c7;
                color: #d97706;
                border: 1px solid #fed7aa;
            }
            
            .confidence-low {
                background: #dbeafe;
                color: #2563eb;
                border: 1px solid #bfdbfe;
            }
            
            .info-section {
                background: #f8fafc;
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
                border-left: 4px solid #10b981;
            }
            
            .translation-section {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
                font-style: italic;
            }
            
            .alert {
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
                border-left: 4px solid;
            }
            
            .alert-warning {
                background: #fef3c7;
                border-color: #f59e0b;
                color: #92400e;
            }
            
            .alert-info {
                background: #dbeafe;
                border-color: #3b82f6;
                color: #1e40af;
            }
            
            .stat-card {
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                border-top: 4px solid #3b82f6;
                margin: 1rem 0;
                transition: transform 0.2s ease;
                min-height: 48px;
            }
            
            .stat-card:hover {
                transform: translateY(-2px);
            }
            
            .stat-number {
                font-size: 2rem;
                font-weight: 700;
                color: #1f2937;
                margin: 0.5rem 0;
            }
            
            .stat-label {
                color: #6b7280;
                font-size: 0.875rem;
                font-weight: 500;
            }
            
            .welcome-section {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                padding: 3rem 2rem;
                border-radius: 20px;
                text-align: center;
                margin: 2rem 0;
            }
            
            .welcome-title {
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }
            
            .welcome-text {
                font-size: 1.1rem;
                opacity: 0.9;
            }
            
            .no-results {
                text-align: center;
                padding: 3rem 2rem;
                background: linear-gradient(135deg, #fef3c7, #fed7aa);
                border-radius: 20px;
                margin: 2rem 0;
                color: #92400e;
            }
            
            .no-results-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            
            .no-results-title {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }
            
            .suggestion-card {
                background: #eff6ff;
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 12px;
                border-left: 4px solid #3b82f6;
                transition: transform 0.2s ease;
                min-height: 48px;
                cursor: pointer;
            }
            
            .suggestion-card:hover {
                transform: translateX(4px);
                background: #dbeafe;
            }
            
            .footer {
                background: linear-gradient(135deg, #f8fafc, #e2e8f0);
                padding: 2rem;
                border-radius: 20px;
                text-align: center;
                margin-top: 3rem;
            }
            
            .footer-title {
                font-size: 1.25rem;
                color: #374151;
                margin-bottom: 1rem;
                font-weight: 600;
            }
            
            .footer-features {
                display: flex;
                justify-content: center;
                gap: 2rem;
                margin: 1.5rem 0;
                flex-wrap: wrap;
            }
            
            .footer-feature {
                color: #3b82f6;
                text-align: center;
            }
            
            .footer-feature-icon {
                font-size: 1.5rem;
                margin-bottom: 0.25rem;
            }
            
            .footer-feature-text {
                font-size: 0.875rem;
                font-weight: 500;
            }
            
            .back-to-top {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 1.2rem;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
                transition: all 0.3s ease;
                z-index: 1000;
            }
            
            .back-to-top:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.6);
            }
            
            .severity-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.25rem;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 0.5rem;
            }
            
            .severity-critical {
                background: #fee2e2;
                color: #dc2626;
            }
            
            .severity-high {
                background: #fef3c7;
                color: #d97706;
            }
            
            .severity-medium {
                background: #dcfce7;
                color: #16a34a;
            }
            
            .severity-low {
                background: #dbeafe;
                color: #2563eb;
            }
            
            .pill-button {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                border: none;
                border-radius: 50px;
                padding: 0.5rem 1rem;
                margin: 0.25rem;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 0.875rem;
                font-weight: 500;
            }
            
            .pill-button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            
            .body-part-map {
                background: #f8fafc;
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
                border: 1px solid #e5e7eb;
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .main-header {
                    font-size: 2rem;
                }
                
                .condition-card {
                    padding: 1.5rem;
                    margin: 1rem 0;
                }
                
                .condition-title {
                    font-size: 1.25rem;
                }
                
                .welcome-section {
                    padding: 2rem 1rem;
                }
                
                .welcome-title {
                    font-size: 1.5rem;
                }
                
                .footer-features {
                    gap: 1rem;
                }
                
                .stat-card {
                    padding: 1rem;
                }
                
                .stat-number {
                    font-size: 1.5rem;
                }
                
                .symptom-card, .suggestion-card {
                    padding: 1rem;
                    min-height: 48px;
                }
            }
            
            @media (max-width: 480px) {
                .main-header {
                    font-size: 1.75rem;
                }
                
                .condition-card {
                    padding: 1rem;
                }
                
                .condition-title {
                    font-size: 1.1rem;
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 0.25rem;
                }
                
                .confidence-badge {
                    font-size: 0.75rem;
                    padding: 0.375rem 0.75rem;
                }
                
                .back-to-top {
                    width: 45px;
                    height: 45px;
                    font-size: 1rem;
                }
            }
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #f1f5f9;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #94a3b8;
            }
        </style>
        """

@st.cache_data
def load_symptoms_data() -> pd.DataFrame:
    """Load the symptoms dataset with caching for better performance."""
    try:
        df = pd.read_csv('symptoms.csv')
        # Clean and normalize the data
        df['symptom'] = df['symptom'].str.lower().str.strip()
        df['condition'] = df['condition'].str.strip()
        
        # Add severity levels if not present
        if 'severity' not in df.columns:
            # Add mock severity data for demonstration
            severity_map = {
                'Heart Attack': 'Critical',
                'Pneumonia': 'High',
                'COVID-19': 'High',
                'Appendicitis': 'High',
                'Malaria': 'High',
                'Migraine': 'Medium',
                'Flu': 'Medium',
                'Asthma': 'Medium',
                'Common Cold': 'Low',
                'Allergies': 'Low',
                'Tension Headache': 'Low'
            }
            df['severity'] = df['condition'].map(severity_map).fillna('Medium')
        
        return df
    except FileNotFoundError:
        st.error("❌ symptoms.csv file not found! Please ensure the file exists in the same directory.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

def normalize_symptom(symptom: str) -> str:
    """Normalize symptom text for better matching."""
    symptom = symptom.lower().strip()
    symptom = re.sub(r'[^\w\s-]', '', symptom)
    symptom = re.sub(r'\s+', ' ', symptom)
    return symptom

def find_symptom_matches(user_symptoms: List[str], df: pd.DataFrame) -> Dict[str, List[Tuple[str, str]]]:
    """Find matching conditions for given symptoms with severity."""
    matches = {}
    
    for user_symptom in user_symptoms:
        user_symptom_normalized = normalize_symptom(user_symptom)
        matched_conditions = []
        
        # Exact match
        exact_matches = df[df['symptom'] == user_symptom_normalized][['condition', 'severity']].values.tolist()
        matched_conditions.extend([(condition, severity) for condition, severity in exact_matches])
        
        # Partial match
        for _, row in df.iterrows():
            db_symptom = row['symptom']
            condition = row['condition']
            severity = row['severity']
            
            if any(condition == existing_condition for existing_condition, _ in matched_conditions):
                continue
                
            if (user_symptom_normalized in db_symptom or 
                db_symptom in user_symptom_normalized or
                any(word in db_symptom.split() for word in user_symptom_normalized.split() if len(word) > 2)):
                matched_conditions.append((condition, severity))
        
        matches[user_symptom] = matched_conditions
    
    return matches

def get_combined_conditions(matches: Dict[str, List[Tuple[str, str]]]) -> List[Tuple[str, int, str]]:
    """Get conditions ranked by frequency and severity."""
    condition_data = {}
    
    for conditions in matches.values():
        for condition, severity in conditions:
            if condition not in condition_data:
                condition_data[condition] = {'count': 0, 'severity': severity}
            condition_data[condition]['count'] += 1
    
    # Sort by severity weight and frequency
    severity_weights = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
    
    sorted_conditions = sorted(
        condition_data.items(),
        key=lambda x: (severity_weights.get(x[1]['severity'], 2), x[1]['count']),
        reverse=True
    )
    
    return [(condition, data['count'], data['severity']) for condition, data in sorted_conditions]

def translate_text(text: str, target_language: str = 'hi') -> str:
    """Translate text to target language if translator is available."""
    if not TRANSLATOR_AVAILABLE:
        return text
    
    try:
        translator = GoogleTranslator(source='en', target=target_language)
        return translator.translate(text)
    except Exception:
        return text

def get_body_part_mapping(symptom: str) -> str:
    """Map symptoms to body parts for visual context."""
    body_part_map = {
        'headache': '🧠 Head',
        'fever': '🌡️ Whole Body',
        'cough': '🫁 Respiratory',
        'sore throat': '👄 Throat',
        'chest pain': '💓 Chest',
        'stomach pain': '🤰 Abdomen',
        'nausea': '🤢 Digestive',
        'dizziness': '🧠 Head',
        'fatigue': '😴 Whole Body',
        'muscle aches': '💪 Muscles',
        'joint pain': '🦴 Joints',
        'skin rash': '🤚 Skin'
    }
    
    normalized_symptom = normalize_symptom(symptom)
    for key, value in body_part_map.items():
        if key in normalized_symptom or normalized_symptom in key:
            return value
    return '🏥 General'

def generate_pdf_report(user_symptoms: List[str], combined_conditions: List[Tuple[str, int, str]], matches: Dict) -> str:
    """Generate PDF report of the diagnosis."""
    if not PDF_AVAILABLE:
        return None
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Symptom Checker Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; color: #1e40af; margin-bottom: 30px; }}
            .section {{ margin: 20px 0; }}
            .condition {{ background: #f8fafc; padding: 15px; margin: 10px 0; border-left: 4px solid #3b82f6; }}
            .confidence {{ font-weight: bold; }}
            .timestamp {{ text-align: center; color: #6b7280; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🩺 Symptom Checker Report</h1>
        </div>
        
        <div class="section">
            <h2>📝 Reported Symptoms</h2>
            <ul>
                {''.join([f'<li>{symptom.title()}</li>' for symptom in user_symptoms])}
            </ul>
        </div>
        
        <div class="section">
            <h2>🏥 Possible Conditions</h2>
            {''.join([f'''
            <div class="condition">
                <h3>{condition}</h3>
                <p class="confidence">Confidence: {frequency} symptom match(es)</p>
                <p><strong>Severity:</strong> {severity}</p>
            </div>
            ''' for condition, frequency, severity in combined_conditions[:5]])}
        </div>
        
        <div class="section">
            <p><strong>⚠️ Medical Disclaimer:</strong> This report is for informational purposes only. 
            Always consult with qualified healthcare professionals for proper diagnosis and treatment.</p>
        </div>
        
        <div class="timestamp">
            <p>Report generated on: {timestamp}</p>
        </div>
    </body>
    </html>
    """
    
    try:
        pdf = pdfkit.from_string(html_content, False)
        return base64.b64encode(pdf).decode()
    except:
        return None

def main():
    # Apply CSS styles based on theme
    st.markdown(get_css_styles(st.session_state.dark_mode), unsafe_allow_html=True)
    
    # Header with anchor
    st.markdown('<a name="top"></a>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🩺 Symptom Checker Bot</h1>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="alert alert-warning">
        <strong>⚠️ Medical Disclaimer:</strong> This tool is for informational purposes only and should not replace professional medical advice. 
        Always consult with a qualified healthcare provider for proper diagnosis and treatment.
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_symptoms_data()
    
    # Sidebar with enhanced features
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Dark mode toggle
        if st.button("🌙 Toggle Dark Mode" if not st.session_state.dark_mode else "☀️ Toggle Light Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Dataset Statistics")
        
        # Statistics with enhanced styling
        unique_symptoms = len(df['symptom'].unique())
        unique_conditions = len(df['condition'].unique())
        total_records = len(df)
        
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🩺</div>
            <div class="stat-number">{unique_symptoms}</div>
            <div class="stat-label">Unique Symptoms</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏥</div>
            <div class="stat-number">{unique_conditions}</div>
            <div class="stat-label">Medical Conditions</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
            <div class="stat-number">{total_records}</div>
            <div class="stat-label">Total Records</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("🔧 Options")
        
        # Translation option
        translate_results = False
        if TRANSLATOR_AVAILABLE:
            translate_results = st.checkbox("🌐 Translate to Hindi", help="Requires internet connection")
        else:
            st.info("💡 Install 'deep_translator' for translation features")
        
        # Show available symptoms with search
        if st.checkbox("📋 Show Available Symptoms"):
            st.subheader("Available Symptoms:")
            search_term = st.text_input("🔍 Search symptoms:", placeholder="Type to search...")
            
            unique_symptoms_list = sorted(df['symptom'].unique())
            if search_term:
                filtered_symptoms = [s for s in unique_symptoms_list if search_term.lower() in s.lower()]
            else:
                filtered_symptoms = unique_symptoms_list[:20]
            
            for symptom in filtered_symptoms:
                body_part = get_body_part_mapping(symptom)
                st.markdown(f"• {symptom.title()} - {body_part}")
            
            if not search_term and len(unique_symptoms_list) > 20:
                st.text(f"... and {len(unique_symptoms_list) - 20} more")
    
    # Main interface
    st.header("💬 Enter Your Symptoms")
    
    # Enhanced input methods with pill buttons
    input_method = st.radio(
        "Choose input method:",
        ["✏️ Type symptoms", "📝 Select from list", "🔘 Quick Select"],
        horizontal=True
    )
    
    user_symptoms = []
    
    if input_method == "✏️ Type symptoms":
        symptoms_text = st.text_area(
            "Describe your symptoms (separate multiple symptoms with commas):",
            placeholder="e.g., fever, headache, cough",
            height=100
        )
        if symptoms_text:
            user_symptoms = [s.strip() for s in symptoms_text.split(',') if s.strip()]
    
    elif input_method == "📝 Select from list":
        available_symptoms = sorted(df['symptom'].unique())
        
        # Add search functionality to multiselect
        search_filter = st.text_input("🔍 Search symptoms:", placeholder="Type to filter options...")
        if search_filter:
            filtered_options = [s for s in available_symptoms if search_filter.lower() in s.lower()]
        else:
            filtered_options = available_symptoms
        
        user_symptoms = st.multiselect(
            "Select your symptoms:",
            filtered_options,
            help="You can select multiple symptoms. Use the search box above to filter options."
        )
    
    else:  # Quick Select with pill buttons
        st.markdown("**🔘 Quick Select Common Symptoms:**")
        common_symptoms = ['fever', 'headache', 'cough', 'sore throat', 'fatigue', 'nausea', 'chest pain', 'dizziness']
        
        cols = st.columns(4)
        selected_quick = []
        
        for i, symptom in enumerate(common_symptoms):
            with cols[i % 4]:
                if st.button(f"💊 {symptom.title()}", key=f"quick_{symptom}"):
                    if symptom not in selected_quick:
                        selected_quick.append(symptom)
        
        if selected_quick:
            user_symptoms = selected_quick
            st.success(f"Selected: {', '.join([s.title() for s in selected_quick])}")
    
    # Process symptoms with loading spinner
    if user_symptoms:
        # Auto-scroll to results
        st.markdown('<a name="results"></a>', unsafe_allow_html=True)
        
        with st.spinner("🔍 Analyzing your symptoms..."):
            # Simulate processing time for better UX
            import time
            time.sleep(1)
            
            st.header("🔍 Analysis Results")
            
            # Show entered symptoms with body part mapping
            st.markdown("### 📝 Your Reported Symptoms")
            
            # Create responsive columns
            num_symptoms = len(user_symptoms)
            if num_symptoms <= 2:
                cols = st.columns(num_symptoms)
            elif num_symptoms <= 4:
                cols = st.columns(2)
            else:
                cols = st.columns(3)
            
            for i, symptom in enumerate(user_symptoms):
                body_part = get_body_part_mapping(symptom)
                with cols[i % len(cols)]:
                    st.markdown(f"""
                    <div class="symptom-card">
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🩺</div>
                            <strong style="color: {'#f1f5f9' if st.session_state.dark_mode else '#1f2937'};">{symptom.title()}</strong>
                            <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">{body_part}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Find matches
            matches = find_symptom_matches(user_symptoms, df)
            combined_conditions = get_combined_conditions(matches)
            
            if combined_conditions:
                st.markdown("### 🏥 Possible Medical Conditions")
                st.markdown("*Sorted by severity and symptom match frequency:*")
                
                # Show top conditions with severity
                for i, (condition, frequency, severity) in enumerate(combined_conditions):
                    # Determine confidence level
                    if frequency >= 3:
                        confidence = "High"
                        confidence_class = "confidence-high"
                        confidence_icon = "🔴"
                    elif frequency >= 2:
                        confidence = "Medium"
                        confidence_class = "confidence-medium"
                        confidence_icon = "🟡"
                    else:
                        confidence = "Low"
                        confidence_class = "confidence-low"
                        confidence_icon = "🔵"
                    
                    # Severity styling
                    severity_class = f"severity-{severity.lower()}"
                    severity_icons = {
                        'Critical': '🚨',
                        'High': '⚠️',
                        'Medium': '⚡',
                        'Low': 'ℹ️'
                    }
                    
                    # Get matched symptoms
                    matched_symptoms_list = []
                    for symptom, conditions in matches.items():
                        if any(condition == cond for cond, _ in conditions):
                            matched_symptoms_list.append(symptom.title())
                    
                    matched_symptoms_text = ", ".join(matched_symptoms_list) if matched_symptoms_list else "General symptoms"
                    
                    # Translation if enabled
                    translated_condition = translate_text(condition, 'hi') if translate_results else condition
                    
                    # Create enhanced condition card
                    st.markdown(f"""
                    <div class="condition-card">
                        <div class="condition-title">
                            ✅ {condition}
                            <span class="severity-badge {severity_class}">
                                {severity_icons.get(severity, 'ℹ️')} {severity}
                            </span>
                        </div>
                        <div class="confidence-badge {confidence_class}">
                            {confidence_icon} {confidence} Confidence
                        </div>
                        <div style="color: {'#94a3b8' if st.session_state.dark_mode else '#6b7280'}; margin: 0.5rem 0;">
                            🧪 <strong>Match Score:</strong> {frequency} symptom{'s' if frequency != 1 else ''} matched
                        </div>
                        <div class="info-section">
                            🧾 <strong>Matched Symptoms:</strong> {matched_symptoms_text}
                        </div>
                        {f'<div class="translation-section">🌐 <strong>Hindi Translation:</strong> {translated_condition}</div>' if translate_results and translated_condition != condition else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export to PDF option
                if PDF_AVAILABLE:
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("📄 Download Report as PDF", type="primary"):
                            pdf_data = generate_pdf_report(user_symptoms, combined_conditions, matches)
                            if pdf_data:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                st.download_button(
                                    label="⬇️ Download PDF Report",
                                    data=base64.b64decode(pdf_data),
                                    file_name=f"symptom_report_{timestamp}.pdf",
                                    mime="application/pdf"
                                )
                            else:
                                st.error("Failed to generate PDF report")
                else:
                    st.info("💡 Install 'pdfkit' for PDF export functionality")
                
                # Detailed breakdown
                with st.expander("📊 Detailed Symptom Analysis"):
                    for symptom, conditions in matches.items():
                        if conditions:
                            st.write(f"**{symptom.title()}** → {len(conditions)} possible condition(s)")
                            for condition, severity in conditions[:5]:
                                st.write(f"  • {condition} ({severity} severity)")
                            if len(conditions) > 5:
                                st.write(f"  ... and {len(conditions) - 5} more")
                        else:
                            st.write(f"**{symptom.title()}** → No direct matches found")
            
            else:
                # Enhanced no results section
                st.markdown("""
                <div class="no-results">
                    <div class="no-results-icon">🤔</div>
                    <div class="no-results-title">No Direct Matches Found</div>
                    <p>Don't worry! Try rephrasing your symptoms or check for typos. 
                    Our database might have similar conditions under different terms.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Enhanced suggestions
                st.markdown("### 💡 Did You Mean Any of These?")
                all_symptoms = df['symptom'].unique()
                suggestions = []
                
                for user_symptom in user_symptoms:
                    normalized_input = normalize_symptom(user_symptom)
                    for db_symptom in all_symptoms:
                        if any(word in db_symptom for word in normalized_input.split() if len(word) > 2):
                            suggestions.append(db_symptom)
                
                if suggestions:
                    unique_suggestions = list(set(suggestions))[:6]
                    cols = st.columns(2)
                    for i, suggestion in enumerate(unique_suggestions):
                        body_part = get_body_part_mapping(suggestion)
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class="suggestion-card">
                                <strong>💡 {suggestion.title()}</strong>
                                <div style="font-size: 0.8rem; margin-top: 0.25rem; opacity: 0.8;">{body_part}</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="alert alert-info">
                        Try using more common medical terms or check our available symptoms in the sidebar.
                    </div>
                    """, unsafe_allow_html=True)
        
        # Show back to top button
        st.session_state.show_back_to_top = True
    
    else:
        # Enhanced welcome section
        st.markdown("""
        <div class="welcome-section">
            <div class="welcome-title">👋 Welcome to Your Health Assistant!</div>
            <div class="welcome-text">
                Enter your symptoms above to get personalized health insights based on our medical database.
                Our AI-powered system analyzes symptoms and provides possible conditions with severity levels.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced dataset overview
    st.markdown("### 📈 Dataset Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔝 Most Common Symptoms")
        symptom_counts = df['symptom'].value_counts().head(8)
        for symptom, count in symptom_counts.items():
            body_part = get_body_part_mapping(symptom)
            st.markdown(f"""
            <div class="suggestion-card">
                <strong>{symptom.title()}</strong>
                <div style="font-size: 0.8rem; opacity: 0.8;">{body_part}</div>
                <span style="float: right; color: {'#94a3b8' if st.session_state.dark_mode else '#6b7280'};">{count} condition{'s' if count > 1 else ''}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🏥 Most Common Conditions")
        condition_counts = df['condition'].value_counts().head(8)
        for condition, count in condition_counts.items():
            severity = df[df['condition'] == condition]['severity'].iloc[0]
            severity_class = f"severity-{severity.lower()}"
            severity_icons = {'Critical': '🚨', 'High': '⚠️', 'Medium': '⚡', 'Low': 'ℹ️'}
            
            st.markdown(f"""
            <div class="suggestion-card">
                <strong>{condition}</strong>
                <span class="severity-badge {severity_class}" style="margin-left: 0.5rem;">
                    {severity_icons.get(severity, 'ℹ️')} {severity}
                </span>
                <span style="float: right; color: {'#94a3b8' if st.session_state.dark_mode else '#6b7280'};">{count} symptom{'s' if count > 1 else ''}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Back to top button
    if st.session_state.show_back_to_top:
        st.markdown("""
        <button class="back-to-top" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">
            🔝
        </button>
        <script>
            window.addEventListener('scroll', function() {
                const backToTop = document.querySelector('.back-to-top');
                if (window.pageYOffset > 300) {
                    backToTop.style.display = 'block';
                } else {
                    backToTop.style.display = 'none';
                }
            });
        </script>
        """, unsafe_allow_html=True)
    
    # Enhanced footer with timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="footer">
        <div class="footer-title">🩺 Symptom Checker Bot</div>
        <div class="footer-features">
            <div class="footer-feature">
                <div class="footer-feature-icon">🏗️</div>
                <div class="footer-feature-text">Built with Streamlit</div>
            </div>
            <div class="footer-feature">
                <div class="footer-feature-icon">📊</div>
                <div class="footer-feature-text">Powered by Pandas</div>
            </div>
            <div class="footer-feature">
                <div class="footer-feature-icon">💻</div>
                <div class="footer-feature-text">100% Local & Free</div>
            </div>
            <div class="footer-feature">
                <div class="footer-feature-icon">🔒</div>
                <div class="footer-feature-text">Privacy Protected</div>
            </div>
            <div class="footer-feature">
                <div class="footer-feature-icon">🌙</div>
                <div class="footer-feature-text">Dark Mode Ready</div>
            </div>
        </div>
        <div class="alert alert-warning" style="margin: 1rem 0;">
            <strong>⚠️ Medical Disclaimer:</strong>
            This tool provides educational information only. Always consult qualified healthcare 
            professionals for proper medical diagnosis and treatment.
        </div>
        <div style="color: {'#94a3b8' if st.session_state.dark_mode else '#6b7280'}; font-size: 0.875rem; margin-top: 1rem;">
            Made with ❤️ for educational purposes • Perfect for learning AI/ML development<br>
            ⏱️ Report generated on: {current_time}
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
