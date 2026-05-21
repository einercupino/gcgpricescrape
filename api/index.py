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

            .cards{
                display:flex;
                flex-direction:column;
                gap:12px;
                margin-top:20px;
            }

            .card{
                background:white;
                border-radius:12px;
                padding:14px;
                border:1px solid #ddd;
                box-shadow:0 2px 6px rgba(0,0,0,0.08);
            }

            .top-row{
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:8px;
            }

            .title{
                font-size:14px;
                line-height:1.4;
                margin-bottom:8px;

                word-wrap:break-word;
                overflow-wrap:break-word;
            }

            .price{
                font-size:18px;
                font-weight:bold;
            }

            .qty{
                color:#666;
                font-size:13px;
            }

            .store{
                font-weight:bold;
                font-size:14px;
            }

            .store-401G{
                color:#2563eb;
            }

            .store-BANG{
                color:#16a34a;
            }

            .store-HOBB{
                color:#ea580c;
            }

            .store-TCGP{
                color:#9333ea;
            }

            .quick-buttons{
                display:flex;
                gap:8px;
                flex-wrap:wrap;
                margin-bottom:15px;
            }

            .quick-btn{
                background:#e5e7eb;
                color:#111;
                border:none;
                padding:8px 12px;
                border-radius:8px;
                cursor:pointer;
                font-size:13px;
                font-weight:bold;
            }

            .quick-btn:hover{
                background:#d1d5db;
            }

            .card{
                display:flex;
                gap:12px;
            }

            .card-image{
                width:90px;
                height:120px;
                object-fit:cover;
                border-radius:8px;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <div class="quick-buttons">

                <button class="quick-btn"
                    onclick="setPrefix('GD01-')">
                    GD01
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('GD02-')">
                    GD02
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('GD03-')">
                    GD03
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('GD04-')">
                    GD04
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('GD05-')">
                    GD05
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST01-')">
                    ST01
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST02-')">
                    ST02
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST03-')">
                    ST03
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST04-')">
                    ST04
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST05-')">
                    ST05
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST06-')">
                    ST06
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST07-')">
                    ST07
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST08-')">
                    ST08
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('ST09-')">
                    ST09
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('EB01-')">
                    EB01
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('R-')">
                    R
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('RP-')">
                    RP
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('EXRP-')">
                    EXRP
                </button>

                <button class="quick-btn"
                    onclick="setPrefix('GCG-PR-')">
                    GCG-PR
                </button>

            </div>

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

            function setPrefix(prefix){

                const input =
                    document.getElementById("code");

                input.value = prefix;

                input.focus();

            }        
        
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

                    let html = `<div class="cards">`;

                    data.results.forEach(item => {

                        html += `

                            <div class="card">

                                <img
                                    src="${item.image}"
                                    class="card-image"
                                >

                                <div class="card-content">

                                    <div class="top-row">

                                        <div class="store store-${item.store}">
                                            ${item.store}
                                        </div>

                                        <div class="price">
                                            $${Number(item.price).toFixed(2)}
                                        </div>

                                    </div>

                                    <div class="title">
                                        ${item.title}
                                    </div>

                                    <div class="qty">
                                        Qty: ${item.quantity ?? "-"}
                                    </div>

                                </div>

                            </div>

                        `;

                    });

                    html += "</div>";

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