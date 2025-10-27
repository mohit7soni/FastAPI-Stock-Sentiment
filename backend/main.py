from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
from textblob import TextBlob

app = FastAPI()

# Enable CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# IMPORTANT: Replace with your own API key
NEWS_API_KEY = "29af81ae84d84591b8ea79df68d27688" 
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"

@app.get("/sentiment/")
async def get_sentiment(symbol: str):
    params = {
        "q": symbol,
        "apiKey": NEWS_API_KEY,
        "pageSize": 10,
        "language": "en",
        "sortBy": "relevancy"
    }
    
    try:
        response = requests.get(NEWS_API_ENDPOINT, params=params)
        response.raise_for_status() # Raises an error for bad responses (4xx or 5xx)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return {"symbol": symbol, "sentiment": "Error", "score": 0, "message": f"Error fetching news: {e}"}

    articles = data.get("articles", [])
    if not articles:
        return {"symbol": symbol, "sentiment": "Neutral", "score": 0, "message": "No recent news articles found."}

    scores = []
    for article in articles:
        text = (article.get("title") or "") + " " + (article.get("description") or "")
        if not text.strip():
            continue
            
        blob = TextBlob(text)
        scores.append(blob.sentiment.polarity)

    if not scores:
        return {"symbol": symbol, "sentiment": "Neutral", "score": 0, "message": "No text content found in articles to analyze."}

    avg_score = sum(scores) / len(scores)
    
    if avg_score > 0.1:
        sentiment = "Positive"
    elif avg_score < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {"symbol": symbol, "sentiment": sentiment, "score": round(avg_score, 3)}

# This route is no longer used by the new JavaScript, but it doesn't hurt to keep it.
@app.post("/predict")
async def predict(symbol: str = Form(...)):
    # Call the existing get_sentiment function
    return await get_sentiment(symbol)