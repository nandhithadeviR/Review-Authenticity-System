from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from analyzer import calculate_trust_score

app = FastAPI(title="Professional Review Authenticity Engine")

# CRITICAL: Allows your Browser Extension to speak directly to this API securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReviewInput(BaseModel):
    text: str
    domain: str = "General"
    platform: str = "Web"

@app.post("/analyze")
def analyze_review(data: ReviewInput):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be left blank.")
    
    # Execute analytical tracking pipeline
    analysis = calculate_trust_score(data.text, data.platform, data.domain)
    
    return {
        "platform": data.platform,
        "domain": data.domain,
        "trust_score": analysis["trust_score"],
        "status": analysis["status"],
        "reasons": analysis["reasons"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
