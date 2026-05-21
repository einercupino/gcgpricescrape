from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gundam_prices import search_prices

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>Gundam Card Prices</title>

        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>

            body{
                font-family: Arial;
                background:#f5f5f5;
                padding:20px;
            }

            .container{
                max-width:1100px;
                margin:auto;
                background:white;
                padding:25px;
                border-radius:10px;
                box-shadow:0 0 10px rgba(0,0,0,0.1);
            }

            h1{
                margin-bottom:20px;
            }

            .search-row{
                display:flex;
                gap:10px;
                flex-wrap:wrap;
            }

            input{
                flex:1;
                min-width:250px;
                padding:12px;
                font-size:16px;
                border:1px solid #ccc;
                border-radius:6px;
            }

            button{
                padding:12px 18px;
                font-size:16px;
                cursor:pointer;
                background:#2563eb;
                color:white;
                border:none;
                border-radius:6px;
                font-weight:bold;
            }

            button:hover{
                background:#1d4ed8;
            }

            table{
                width:100%;
                border-collapse:collapse;
                margin-top:20px;
                display:block;
                overflow-x:auto;
            }

            th, td{
                border:1px solid #ddd;
                padding:10px;
                text-align:left;
                white-space:nowrap;
            }

            th{
                background:#f3f4f6;
            }

            .loading{
                margin-top:20px;
                font-weight:bold;
                color:#2563eb;
            }

            .store-401G{
                color:#2563eb;
                font-weight:bold;
            }

            .store-BANG{
                color:#16a34a;
                font-weight:bold;
            }

            .store-HOBB{
                color:#ea580c;
                font-weight:bold;
            }

            .store-TCGP{
                color:#9333ea;
                font-weight:bold;
            }

            .price{
                font-weight:bold;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h1>Gundam Card Game Price Check</h1>

            <div class="search-row">

                <input
                    id="code"
                    placeholder="Search Gundam Card"
                />

                <button onclick="searchCard()">
                    Search
                </button>

            </div>

            <div id="results"></div>

        </div>

        <script>

            document
                .getElementById("code")
                .addEventListener("keypress", function(e){

                    if(e.key === "Enter"){
                        searchCard();
                    }

                });

            async function searchCard(){

                const code = document
                    .getElementById("code")
                    .value
                    .trim();

                const resultsDiv =
                    document.getElementById("results");

                if(!code){

                    resultsDiv.innerHTML =
                        "Please enter a card code.";

                    return;
                }

                resultsDiv.innerHTML = `
                    <div class="loading">
                        Searching prices...
                    </div>
                `;

                try{

                    const response =
                        await fetch(`/data?code=${code}`);

                    const data =
                        await response.json();

                    if(!data.results ||
                        data.results.length === 0){

                        resultsDiv.innerHTML =
                            "No results found.";

                        return;
                    }

                    data.results.sort(
                        (a,b) => a.price - b.price
                    );

                    let html = `
                        <table>

                            <tr>
                                <th>Store</th>
                                <th>Title</th>
                                <th>Price (CAD)</th>
                                <th>Qty</th>
                            </tr>
                    `;

                    data.results.forEach(item => {

                        html += `

                            <tr>

                                <td class="store-${item.store}">
                                    ${item.store}
                                </td>

                                <td>
                                    ${item.title}
                                </td>

                                <td class="price">
                                    $${Number(item.price).toFixed(2)}
                                </td>

                                <td>
                                    ${item.quantity ?? "-"}
                                </td>

                            </tr>

                        `;

                    });

                    html += "</table>";

                    resultsDiv.innerHTML = html;

                }catch(err){

                    console.log(err);

                    resultsDiv.innerHTML =
                        "Error loading data.";

                }

            }

        </script>

    </body>

    </html>
    """


@app.get("/data")
def data(code: str):

    return {
        "results": search_prices(code)
    }