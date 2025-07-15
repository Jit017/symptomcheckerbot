#!/usr/bin/env python3
"""
Simplified ML Training for Symptom Checker Bot
Optimized for sparse medical datasets
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os
from collections import defaultdict

def create_training_data():
    """Load and prepare training data"""
    print("📊 Loading and preparing data...")
    
    # Load dataset
    df = pd.read_csv('symptoms.csv')
    df['symptom'] = df['symptom'].str.lower().str.strip()
    df['condition'] = df['condition'].str.strip()
    
    print(f"   Total records: {len(df)}")
    print(f"   Unique symptoms: {df['symptom'].nunique()}")
    print(f"   Unique conditions: {df['condition'].nunique()}")
    
    # Create expanded training data by using each symptom-condition pair
    # and also creating combinations
    expanded_data = []
    
    # Add original data
    for _, row in df.iterrows():
        expanded_data.append({
            'text': row['symptom'],
            'condition': row['condition']
        })
    
    # Create some multi-symptom examples from related conditions
    condition_symptoms = defaultdict(list)
    for _, row in df.iterrows():
        condition_symptoms[row['condition']].append(row['symptom'])
    
    # For conditions with multiple symptoms, create combined examples
    for condition, symptoms in condition_symptoms.items():
        if len(symptoms) > 1:
            # Create combinations of 2 symptoms
            for i in range(len(symptoms)):
                for j in range(i+1, len(symptoms)):
                    combined = f"{symptoms[i]} {symptoms[j]}"
                    expanded_data.append({
                        'text': combined,
                        'condition': condition
                    })
    
    expanded_df = pd.DataFrame(expanded_data)
    print(f"   Expanded to {len(expanded_df)} training examples")
    
    return expanded_df

def train_models(df):
    """Train lightweight models"""
    print("\n🤖 Training models...")
    
    # Prepare features
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=500,  # Reduced for speed
        min_df=1,
        stop_words='english'
    )
    
    X = vectorizer.fit_transform(df['text'])
    y = df['condition']
    
    print(f"   Features created: {X.shape[1]}")
    
    # Train models
    models = {
        'MultinomialNB': MultinomialNB(alpha=0.1),
        'LogisticRegression': LogisticRegression(max_iter=1000, C=0.1, random_state=42)
    }
    
    best_model = None
    best_model_name = ""
    best_score = 0
    
    for name, model in models.items():
        print(f"   Training {name}...")
        
        try:
            # Train on all data since dataset is small
            model.fit(X, y)
            
            # Evaluate on training data (best we can do with sparse data)
            y_pred = model.predict(X)
            accuracy = accuracy_score(y, y_pred)
            
            print(f"   {name} training accuracy: {accuracy:.3f}")
            
            if accuracy > best_score:
                best_score = accuracy
                best_model = model
                best_model_name = name
                
        except Exception as e:
            print(f"   Error training {name}: {str(e)}")
    
    print(f"\n🏆 Best model: {best_model_name} (accuracy: {best_score:.3f})")
    
    return best_model, vectorizer, best_model_name

def save_model(model, vectorizer, model_name):
    """Save the trained model"""
    print("\n💾 Saving model...")
    
    os.makedirs('models', exist_ok=True)
    
    # Save model and vectorizer
    joblib.dump(model, 'models/symptom_model.pkl')
    joblib.dump(vectorizer, 'models/symptom_vectorizer.pkl')
    
    # Save metadata
    metadata = {
        'model_type': model_name,
        'created_at': pd.Timestamp.now().isoformat(),
        'description': 'Lightweight symptom-to-condition predictor'
    }
    joblib.dump(metadata, 'models/model_metadata.pkl')
    
    print("   ✅ Model saved successfully!")
    return True

def test_model():
    """Quick test of saved model"""
    print("\n🧪 Testing saved model...")
    
    try:
        # Load model
        model = joblib.load('models/symptom_model.pkl')
        vectorizer = joblib.load('models/symptom_vectorizer.pkl')
        
        # Test cases
        test_symptoms = [
            'fever headache',
            'cough chest pain', 
            'nausea vomiting',
            'back pain',
            'rash itching'
        ]
        
        for symptom in test_symptoms:
            # Predict
            X_test = vectorizer.transform([symptom])
            prediction = model.predict(X_test)[0]
            
            # Get probability if available
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X_test)[0]
                confidence = max(proba)
                print(f"   '{symptom}' → {prediction} (confidence: {confidence:.2f})")
            else:
                print(f"   '{symptom}' → {prediction}")
        
        print("   ✅ Model test completed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Model test failed: {str(e)}")
        return False

def main():
    """Main training pipeline"""
    print("🩺 Simple ML Training for Symptom Checker")
    print("=" * 50)
    
    try:
        # Load and prepare data
        df = create_training_data()
        
        # Train models
        model, vectorizer, model_name = train_models(df)
        
        if model is not None:
            # Save model
            save_model(model, vectorizer, model_name)
            
            # Test model
            test_model()
            
            print("\n🎉 Training completed successfully!")
            print("   Your ML model is ready to use in the Streamlit app!")
        else:
            print("\n❌ Training failed - no model could be trained")
            
    except Exception as e:
        print(f"\n❌ Training pipeline failed: {str(e)}")

if __name__ == "__main__":
    main() 