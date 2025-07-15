"""
ML Prediction Module for Symptom Checker Bot
Handles loading and inference of trained ML models
"""

import joblib
import pandas as pd
import numpy as np
import os
from typing import List, Tuple, Dict, Optional

class SymptomMLPredictor:
    """ML-based symptom to condition predictor"""
    
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        self.model = None
        self.vectorizer = None
        self.metadata = None
        self.is_loaded = False
        
    def load_models(self) -> bool:
        """Load the trained ML models"""
        try:
            model_path = os.path.join(self.model_dir, 'symptom_model.pkl')
            vectorizer_path = os.path.join(self.model_dir, 'symptom_vectorizer.pkl')
            metadata_path = os.path.join(self.model_dir, 'model_metadata.pkl')
            
            # Check if files exist
            if not all(os.path.exists(path) for path in [model_path, vectorizer_path, metadata_path]):
                return False
            
            # Load models
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.metadata = joblib.load(metadata_path)
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            print(f"Error loading ML models: {str(e)}")
            self.is_loaded = False
            return False
    
    def predict_single_symptom(self, symptom_text: str) -> Tuple[str, float]:
        """Predict condition for a single symptom text"""
        if not self.is_loaded:
            return "Model not loaded", 0.0
        
        try:
            # Preprocess and vectorize
            symptom_clean = symptom_text.lower().strip()
            X = self.vectorizer.transform([symptom_clean])
            
            # Get prediction
            prediction = self.model.predict(X)[0]
            
            # Get confidence if available
            confidence = 0.0
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(X)[0]
                confidence = max(probabilities)
            
            return prediction, confidence
            
        except Exception as e:
            print(f"Error in ML prediction: {str(e)}")
            return "Prediction error", 0.0
    
    def predict_multiple_symptoms(self, symptoms: List[str]) -> List[Dict]:
        """Predict conditions for multiple symptoms"""
        results = []
        
        if not self.is_loaded:
            return [{"symptom": s, "condition": "Model not loaded", "confidence": 0.0} for s in symptoms]
        
        # Process each symptom individually
        for symptom in symptoms:
            condition, confidence = self.predict_single_symptom(symptom)
            results.append({
                "symptom": symptom,
                "condition": condition,
                "confidence": confidence
            })
        
        # Also try combined symptoms
        if len(symptoms) > 1:
            combined_text = " ".join(symptoms)
            combined_condition, combined_confidence = self.predict_single_symptom(combined_text)
            results.append({
                "symptom": "Combined symptoms",
                "condition": combined_condition,
                "confidence": combined_confidence
            })
        
        return results
    
    def get_top_predictions(self, symptom_text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Get top K predictions with probabilities"""
        if not self.is_loaded:
            return [("Model not loaded", 0.0)]
        
        try:
            # Preprocess and vectorize
            symptom_clean = symptom_text.lower().strip()
            X = self.vectorizer.transform([symptom_clean])
            
            # Get probabilities if available
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(X)[0]
                class_labels = self.model.classes_
                
                # Get top predictions
                top_indices = np.argsort(probabilities)[-top_k:][::-1]
                top_predictions = [(class_labels[i], probabilities[i]) for i in top_indices]
                
                return top_predictions
            else:
                # Fallback: just return single prediction
                prediction = self.model.predict(X)[0]
                return [(prediction, 1.0)]
                
        except Exception as e:
            print(f"Error getting top predictions: {str(e)}")
            return [("Prediction error", 0.0)]
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if not self.is_loaded:
            return {"status": "Model not loaded"}
        
        info = {
            "status": "Loaded",
            "model_type": self.metadata.get('model_type', 'Unknown'),
            "created_at": self.metadata.get('created_at', 'Unknown'),
            "description": self.metadata.get('description', 'No description'),
            "features_count": self.vectorizer.get_feature_names_out().shape[0] if hasattr(self.vectorizer, 'get_feature_names_out') else 'Unknown',
            "classes_count": len(self.model.classes_) if hasattr(self.model, 'classes_') else 'Unknown'
        }
        
        return info
    
    def is_available(self) -> bool:
        """Check if ML prediction is available"""
        return self.is_loaded

# Global ML predictor instance (singleton pattern for Streamlit)
_ml_predictor = None

def get_ml_predictor() -> SymptomMLPredictor:
    """Get or create the global ML predictor instance"""
    global _ml_predictor
    if _ml_predictor is None:
        _ml_predictor = SymptomMLPredictor()
        _ml_predictor.load_models()
    return _ml_predictor

def predict_symptoms_ml(symptoms: List[str]) -> List[Dict]:
    """Convenience function for ML prediction"""
    predictor = get_ml_predictor()
    return predictor.predict_multiple_symptoms(symptoms)

def get_top_predictions_ml(symptom_text: str, top_k: int = 5) -> List[Tuple[str, float]]:
    """Convenience function for top predictions"""
    predictor = get_ml_predictor()
    return predictor.get_top_predictions(symptom_text, top_k)

def is_ml_available() -> bool:
    """Check if ML prediction is available"""
    predictor = get_ml_predictor()
    return predictor.is_available()

def get_ml_model_info() -> Dict:
    """Get ML model information"""
    predictor = get_ml_predictor()
    return predictor.get_model_info() 