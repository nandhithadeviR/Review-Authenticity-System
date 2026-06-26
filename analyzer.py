import re
import sqlite3
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize Database
DB_FILE = "authenticity_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Table to store unique reviews across platforms to find duplicates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT UNIQUE,
            domain TEXT,
            platform TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Initialize Database on load
init_db()

# Load lightweight NLP model


# Load a dedicated AI detector from Hugging Face
print("Loading Deep Learning AI Detection Model... (This might take a minute on first run)")
try:
    # Using a robust, fast sequence classifier optimized for synthetic text boundaries
    ai_classifier = pipeline("text-classification", model="PirateXX/AI-Content-Detector")
except Exception as e:
    print(f"Deep learning fallback activated. Error loading model: {e}")
    ai_classifier = None

def calculate_trust_score(review_text: str, current_platform: str, current_domain: str) -> dict:
    """
    Professional Scoring Matrix evaluating Deep Learning AI signatures,
    Linguistic Stylometry, and Cross-Platform Database duplication checks.
    """
    score = 100
    reasons = []
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # --- 1. Database Cross-Platform Duplicate / Bot-Farm Analysis ---
    cursor.execute("SELECT text FROM reviews")
    all_historical = [row[0] for row in cursor.fetchall()]
    
    if all_historical:
        all_texts = [review_text] + all_historical
        vectorizer = TfidfVectorizer().fit_transform(all_texts)
        vectors = vectorizer.toarray()
        
        # Calculate similarity against all old database entries
        cosine_matrix = cosine_similarity([vectors[0]], vectors[1:])
        similarities = cosine_matrix.flatten()
        
        # Find matches with greater than 70% structural similarity
        duplicate_matches = sum(1 for sim in similarities if sim > 0.70)
        if duplicate_matches > 0:
            deduction = min(duplicate_matches * 20, 50)
            score -= deduction
            reasons.append(f"Plagiarism Alert: Text matches {duplicate_matches} other historical reviews in database (-{deduction} pts).")

    # Save current review into the database if it's completely new
    try:
        cursor.execute("INSERT INTO reviews (text, domain, platform) VALUES (?, ?, ?)", 
                       (review_text, current_domain, current_platform))
        conn.commit()
    except sqlite3.IntegrityError:
        # File already exists in DB
        pass
    finally:
        conn.close()

    # --- 2. Transformer Deep Learning AI Text Analysis ---
    if ai_classifier:
        try:
            # Run model prediction (Trimming length to match model safety requirements)
            prediction = ai_classifier(review_text[:512])[0]
            if prediction['label'] == 'LABEL_1' or 'ai' in prediction['label'].lower():
                ai_probability = prediction['score'] * 100
                if ai_probability > 60:
                    deduction = int(ai_probability * 0.4)
                    score -= deduction
                    reasons.append(f"AI Signature Detected: Deep Learning model indicates a {ai_probability:.1f}% probability of synthetic origin (-{deduction} pts).")
        except Exception:
            pass

    # --- 3. Advanced Stylometric Checks (Sentence Consistency) ---
# Clean up text and split into sentences using standard punctuation rules (. ! ?)
import re
import math

# This splits text by periods, exclamation marks, or question marks cleanly
sentences = [s.strip() for s in re.split(r'[.!?]+', review_text) if s.strip()]

# Count total words to calculate average length
words = [w for w in review_text.split() if w]
total_words = len(words)
total_sentences = len(sentences)

avg_sentence_len = total_words / total_sentences if total_sentences else 0

if total_sentences > 2:
    # Calculate word count for each sentence
    lengths = [len(s.split()) for s in sentences]
    
    # Calculate variance manually without any external libraries
    variance = sum((l - avg_sentence_len) ** 2 for l in lengths) / total_sentences
    
    # Low variance means robotic, identical sentence structures
    if variance < 3.0:
        score -= 15
        reasons.append("Linguistic Pattern: Unusually low sentence structure variance")
    # --- 4. Marketing/Promotional Density Analysis ---
    promo_keywords = r'\b(buy now|click here|best ever|mega discount|guaranteed results|use code|absolute best)\b'
    matches = len(re.findall(promo_keywords, review_text.lower()))
    if matches >= 2:
        deduction = min(matches * 12, 36)
        score -= deduction
        reasons.append(f"Linguistic Alert: High promotional keyword density (-{deduction} pts).")

    # Final Boundary Normalization
    score = max(0, min(score, 100))
    
    status = "Authentic" if score >= 75 else "Suspicious" if score >= 45 else "Flagged/Fake"
    
    return {
        "trust_score": score,
        "status": status,
        "reasons": reasons if reasons else ["Review demonstrates natural, high-integrity human patterns."]
    }
