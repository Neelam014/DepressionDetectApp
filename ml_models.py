import numpy as np
import pickle
from tensorflow.keras.models import load_model
import os
from textblob import TextBlob

class DepressionPredictor:
    def __init__(self):
        self.models_path = os.path.join(os.path.dirname(__file__), 'models')
        self.svm_model = None
        self.lstm_model = None
        self.encoder = None
        self.scaler = None
        print(f"\n{'='*50}\nInitializing ML Models\n{'='*50}")
        print(f"Models directory: {self.models_path}")
        print(f"Directory exists: {os.path.exists(self.models_path)}")
        if os.path.exists(self.models_path):
            print("Contents of models directory:")
            for file in os.listdir(self.models_path):
                print(f"- {file}")
        self.load_models()

    def load_models(self):
        """Load the trained models and preprocessors"""
        try:
            print("\nAttempting to load models...")
            
            # Load encoder
            encoder_path = os.path.join(self.models_path, 'encoder.pkl')
            print(f"Loading encoder from: {encoder_path}")
            if os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as f:
                    self.encoder = pickle.load(f)
                print("✓ Encoder loaded successfully")
            else:
                print("✗ Encoder file not found")
            
            # Load scaler
            scaler_path = os.path.join(self.models_path, 'scaler.pkl')
            print(f"Loading scaler from: {scaler_path}")
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print("✓ Scaler loaded successfully")
            else:
                print("✗ Scaler file not found")
            
            # Load SVM model
            svm_path = os.path.join(self.models_path, 'svm_model.pkl')
            print(f"Loading SVM model from: {svm_path}")
            if os.path.exists(svm_path):
                with open(svm_path, 'rb') as f:
                    self.svm_model = pickle.load(f)
                print("✓ SVM model loaded successfully")
            else:
                print("✗ SVM model file not found")
            
            # Load LSTM model
            lstm_path = os.path.join(self.models_path, 'lstm_model.h5')
            print(f"Loading LSTM model from: {lstm_path}")
            if os.path.exists(lstm_path):
                self.lstm_model = load_model(lstm_path)
                print("✓ LSTM model loaded successfully")
            else:
                print("✗ LSTM model file not found")
            
        except Exception as e:
            print(f"Warning: ML models not loaded: {str(e)}")
            self.svm_model = None
            self.lstm_model = None
            self.encoder = None
            self.scaler = None

    def predict_depression_svm(self, features):
        """Make prediction using SVM model"""
        try:
            if not self.svm_model or not self.scaler:
                # If models aren't loaded, use a rule-based approach
                phq_score = features.get('phq_score', 0)
                work_interference = features.get('work_interference', 'never')
                family_history = features.get('family_history', False)
                
                # Calculate base probability
                base_prob = min(phq_score / 27.0, 1.0)  # Normalize PHQ-9 score
                
                # Adjust based on other factors
                if work_interference in ['often', 'always']:
                    base_prob += 0.1
                if family_history:
                    base_prob += 0.1
                
                return {
                    'probability': min(base_prob, 1.0),
                    'confidence': 0.7
                }
            
            # Convert features to array format
            feature_array = np.array([
                features['phq_score'],
                1 if features['work_interference'] in ['often', 'always'] else 0,
                1 if features['family_history'] else 0,
                1 if features['self_employed'] else 0,
                features['age']
            ]).reshape(1, -1)
            
            # Scale features
            scaled_features = self.scaler.transform(feature_array)
            
            # Get prediction
            probability = self.svm_model.predict_proba(scaled_features)[0][1]
            
            return {
                'probability': float(probability),
                'confidence': 0.85
            }
            
        except Exception as e:
            print(f"Error in SVM prediction: {str(e)}")
            return None

    def predict_depression_lstm(self, text_data):
        """Make prediction using LSTM model or fallback to sentiment analysis"""
        try:
            if not self.lstm_model or not self.encoder:
                # Fallback to TextBlob sentiment analysis
                blob = TextBlob(text_data)
                sentiment_score = blob.sentiment.polarity
                
                # Convert sentiment to depression probability
                # Negative sentiment -> higher depression probability
                probability = (1 - (sentiment_score + 1) / 2)
                
                # Determine sentiment category
                if sentiment_score < -0.1:
                    sentiment = 'NEGATIVE'
                elif sentiment_score > 0.1:
                    sentiment = 'POSITIVE'
                else:
                    sentiment = 'NEUTRAL'
                
                return {
                    'probability': float(probability),
                    'confidence': 0.6,
                    'sentiment': sentiment
                }
            
            # Process text with encoder
            encoded_text = self.encoder.transform([text_data])
            
            # Get LSTM prediction
            probability = float(self.lstm_model.predict(encoded_text)[0][0])
            
            # Determine sentiment based on probability
            if probability > 0.6:
                sentiment = 'NEGATIVE'
            elif probability < 0.4:
                sentiment = 'POSITIVE'
            else:
                sentiment = 'NEUTRAL'
            
            return {
                'probability': probability,
                'confidence': 0.78,
                'sentiment': sentiment
            }
            
        except Exception as e:
            print(f"Error in LSTM prediction: {str(e)}")
            return None

    def get_ensemble_prediction(self, features, text_data):
        """Combine predictions from both models"""
        svm_result = self.predict_depression_svm(features)
        lstm_result = self.predict_depression_lstm(text_data)
        
        if svm_result and lstm_result:
            # Weighted average of probabilities (adjust weights based on your models' performance)
            ensemble_prob = (0.6 * svm_result['probability'] + 
                           0.4 * lstm_result['probability'])
            
            return {
                'prediction': int(ensemble_prob > 0.5),
                'probability': float(ensemble_prob),
                'svm_prediction': svm_result,
                'lstm_prediction': lstm_result
            }
        return None

def extract_features_from_form(form_data):
    """Extract relevant features from form data for ML models"""
    features = {
        'phq_score': sum(int(form_data.get(f'q{i}', 0)) for i in range(1, 10)),
        'age': int(form_data.get('age', 25)),
        'work_interference': form_data.get('work_interference', 'never'),
        'family_history': form_data.get('family_history') == 'true',
        'self_employed': form_data.get('self_employed') == 'true'
    }
    return features

def extract_text_from_form(form_data):
    """Extract text data for LSTM model"""
    try:
        print("\nExtracting text from form...")
        text_parts = []
        
        # Combine all text fields
        for field in ['mood_description', 'daily_activities', 'thoughts_feelings']:
            if form_data.get(field):
                text_parts.append(form_data.get(field))
        
        combined_text = ' '.join(text_parts)
        print(f"✓ Extracted text: {combined_text[:100]}...")
        return combined_text
        
    except Exception as e:
        print(f"❌ Error extracting text: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
