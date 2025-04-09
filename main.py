from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import uvicorn
import os

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static HTML from the templates folder
templates = Jinja2Templates(directory="templates")


# Dummy model
def predict_box_office(budget, runtime, popularity, genre):
    genre_bonus = {
        'action': 20,
        'comedy': 10,
        'drama': 5,
        'sci-fi': 25
    }.get(genre.lower(), 0)
    return 2 * budget + 0.5 * runtime + 3 * popularity + genre_bonus


class Movie(BaseModel):
    budget: float
    runtime: float
    popularity: float
    genre: str


@app.get("/", response_class=HTMLResponse)
def get_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/predict")
def predict(movie: Movie):
    prediction = predict_box_office(
        movie.budget, movie.runtime, movie.popularity, movie.genre
    )
    return {"box_office_prediction": round(prediction, 2)}


if __name__ == "__main__":
    # Ensure templates directory exists
    os.makedirs("templates", exist_ok=True)

    # Write the HTML file into templates folder
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Box Office Predictor 🎬</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #f4f6f8;
      padding: 40px 20px;
      max-width: 420px;
      margin: auto;
      color: #333;
    }

    h2 {
      text-align: center;
      color: #222;
      margin-bottom: 20px;
    }

    input, select, button {
      width: 100%;
      padding: 12px;
      margin-top: 12px;
      border: 1px solid #ccc;
      border-radius: 6px;
      box-sizing: border-box;
      font-size: 16px;
    }

    button {
      background-color: #4CAF50;
      color: white;
      font-weight: bold;
      border: none;
      cursor: pointer;
      transition: background-color 0.3s;
    }

    button:hover {
      background-color: #45a049;
    }

    h3#result {
      text-align: center;
      margin-top: 20px;
      font-size: 20px;
      color: #1a73e8;
    }

    select {
      background-color: #fff;
    }
  </style>
</head>
<body>
  <h2>Box Office Predictor 🎬</h2>

  <input type="number" id="budget" placeholder="Budget (in millions)">
  <input type="number" id="runtime" placeholder="Runtime (minutes)">
  <input type="number" id="popularity" placeholder="Popularity Score">

  <select id="genre">
    <option value="action">Action</option>
    <option value="comedy">Comedy</option>
    <option value="drama">Drama</option>
    <option value="sci-fi">Sci-Fi</option>
    <option value="other">Other</option>
  </select>

  <button onclick="predict()">Predict</button>

  <h3 id="result"></h3>

  <script>
    async function predict() {
      const data = {
        budget: parseFloat(document.getElementById('budget').value),
        runtime: parseFloat(document.getElementById('runtime').value),
        popularity: parseFloat(document.getElementById('popularity').value),
        genre: document.getElementById('genre').value
      };

      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      const result = await response.json();
      document.getElementById('result').innerText = 
        "🎯 Predicted Box Office: $" + result.box_office_prediction + "M";
    }
  </script>
</body>
</html>
        """)

    uvicorn.run("main:app", port=8000, reload=True)