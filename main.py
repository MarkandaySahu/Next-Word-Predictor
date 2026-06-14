import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = FastAPI(title="LSTM Next Word Predictor API")

# --- THE FIX: Custom Wrappers to bypass the quantization_config bug ---
class SafeEmbedding(keras.layers.Embedding):
    def __init__(self, **kwargs):
        kwargs.pop('quantization_config', None)
        super().__init__(**kwargs)

class SafeDense(keras.layers.Dense):
    def __init__(self, **kwargs):
        kwargs.pop('quantization_config', None)
        super().__init__(**kwargs)

class SafeLSTM(keras.layers.LSTM):
    def __init__(self, **kwargs):
        kwargs.pop('quantization_config', None)
        super().__init__(**kwargs)
# --------------------------------------------------------------------

# 1. Load Tokenizer
try:
    with open("tokenizer.pickle", "rb") as handle:
        tokenizer = pickle.load(handle)
except FileNotFoundError:
    print("CRITICAL ERROR: tokenizer.pickle not found in the directory!")
    tokenizer = None

# 2. Load Model using the Safe Wrappers
try:
    model = keras.models.load_model(
        "next_word_lstm.h5", 
        custom_objects={
            'Embedding': SafeEmbedding,
            'Dense': SafeDense,
            'LSTM': SafeLSTM
        }
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Model Load Error: {e}")
    model = None

MAX_SEQUENCE_LEN = 20 

class TextRequest(BaseModel):
    text: str

def predict_next_words(text: str, top_k: int = 3) -> list[str]:
    if not text.strip() or tokenizer is None or model is None:
        return ["The", "I", "This"]
    
    try:
        token_list = tokenizer.texts_to_sequences([text])[0]
        token_list = pad_sequences([token_list], maxlen=MAX_SEQUENCE_LEN-1, padding='pre')
        
        predictions = model.predict(token_list, verbose=0)[0]
        top_indices = np.argsort(predictions)[-top_k:][::-1]
        
        predicted_words = []
        for index in top_indices:
            for word, idx in tokenizer.word_index.items():
                if idx == index:
                    predicted_words.append(word)
                    break
                    
        return predicted_words if predicted_words else ["next"]
        
    except Exception as e:
        print(f"Prediction Error: {e}")
        return ["Error", "processing", "prediction"]

@app.post("/predict")
async def predict(request: TextRequest):
    predictions = predict_next_words(request.text)
    return {"predictions": predictions}

if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")