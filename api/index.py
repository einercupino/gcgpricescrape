from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sys
import os

# Extend path to import our price-search module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gundam_prices import search_prices

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """Render a simple web UI for the Gundam price checker."""
    return """
    <html>
    <head>
        <title>Gundam Card Price Checker</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background: #f5f7fa;
                padding: 30px;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            h2 {
                margin-bottom: 20px;
            }
            form {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                width: 100%;
            }
            label {
                font-weight: 600;
                font-size: 14px;
                display: block;
                margin-bottom: 8px;
            }
            input[type="text"] {
                width: 100%;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-family: 'Inter', sans-serif;
            }
            button {
                background: #2563eb;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                margin-top: 10px;
            }
            button:hover {
                background: #1d4ed8;
            }
            #output {
                margin-top: 25px;
                width: 100%;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px 12px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }
            th {
                background-color: #f3f4f6;
                font-weight: 600;
            }
            .error {
                color: #b91c1c;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🃏 Gundam Card Price Checker</h2>
            <form onsubmit="search(event)">
                <label for="code">Enter Card Code (e.g. GD04-041):</label>
                <input type="text" id="code" placeholder="GD04-041" required>
                <button type="submit">Search</button>
            </form>
            <div id="output"></div>
        </div>
        <script>
        async function search(e) {
            e.preventDefault();
            const output = document.getElementById('output');
            const code = document.getElementById('code').value.trim();
            if (!code) {
                output.innerHTML = '<p class="error">Please enter a card code.</p>';
                return;
            }
            output.innerHTML = '<p>Loading...</p>';
            try {
                const res = await fetch('/data?code=' + encodeURIComponent(code));
                const data = await res.json();
                const results = data.results || [];
                if (results.length === 0) {
                    output.innerHTML = '<p>No matching products found.</p>';
                    return;
                }
                let html = '<table><thead><tr><th>Store</th><th>Title</th><th>Price (CAD)</th><th>Qty</th></tr></thead><tbody>';
                results.forEach(r => {
                    html += `<tr><td>${r.store}</td><td>${r.title}</td><td>${r.price.toFixed(2)}</td><td>${r.quantity ?? '-'}</td></tr>`;
                });
                html += '</tbody></table>';
                output.innerHTML = html;
            } catch (err) {
                output.innerHTML = '<p class="error">Error fetching data.</p>';
            }
        }
        </script>
    </body>
    </html>
    """


@app.get("/data")
def data(code: str):
    """API endpoint to return price data for a given card code."""
    results = search_prices(code)
    # For JSON responses, float values are fine; JS will format them
    return {"results": results}
