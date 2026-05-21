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

                font-family:Arial;

                background:#f5f5f5;

                padding:8px;

                margin:0;
            }

            .container{

                width:100%;

                max-width:1600px;

                margin:auto;

                background:white;

                padding:16px;

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

            <!-- Cart link -->
            <div style="text-align:right; margin-bottom:10px;">
                <a href="/cart" style="text-decoration:none; font-weight:bold; font-size:14px; color:#2563eb;">
                    🛒 Cart (<span id="cart-count">0</span>)
                </a>
            </div>

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
                    onclick="setPrefix('T-')">
                    T
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
        
            // cart state persisted in localStorage
            function getCart(){
                try{
                    const c = localStorage.getItem('cart');
                    return c ? JSON.parse(c) : [];
                }catch(e){
                    return [];
                }
            }

            function saveCart(cart){
                localStorage.setItem('cart', JSON.stringify(cart));
            }

            function updateCartCount(){
                const cart = getCart();
                const span = document.getElementById('cart-count');
                if(span){
                    span.textContent = cart.length;
                }
            }

            function addToCartByIndex(index){
                // Add an item from the current results array into the cart without redirecting.
                if(!window.currentResults || !Array.isArray(window.currentResults)) return;
                const item = window.currentResults[index];
                if(!item) return;
                const cart = getCart();
                cart.push({
                    store: item.store,
                    title: item.title,
                    price: item.price,
                    quantity: item.quantity,
                    image: item.image,
                    cart_qty: 1
                });
                saveCart(cart);
                updateCartCount();
                // show a brief confirmation toast instead of alert
                const toast = document.createElement('div');
                toast.innerText = 'Added to cart';
                toast.style.position = 'fixed';
                toast.style.bottom = '20px';
                toast.style.left = '50%';
                toast.style.transform = 'translateX(-50%)';
                toast.style.background = '#111';
                toast.style.color = 'white';
                toast.style.padding = '10px 16px';
                toast.style.borderRadius = '8px';
                toast.style.zIndex = '9999';
                toast.style.fontSize = '14px';
                document.body.appendChild(toast);
                setTimeout(() => {
                    toast.remove();
                }, 1200);
            }

            // initialize cart count on page load
            updateCartCount();

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

                    // sort by price ascending
                    data.results.sort(
                        (a,b) => a.price - b.price
                    );

                    // store results globally so click events can reference them
                    window.currentResults = data.results;

                    let html = `<div class="cards">`;

                    data.results.forEach((item, idx) => {

                        html += `

                            <div class="card" onclick="addToCartByIndex(${idx})">

                                <img
                                    src="${item.image || 'https://via.placeholder.com/90x120?text=No+Image'}"
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

                    updateCartCount();

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


# Cart page displaying selected items stored in localStorage.
@app.get("/cart", response_class=HTMLResponse)
def cart():
    """
    Render the shopping cart page.  This version uses card-style containers
    instead of a table to improve mobile usability.  Each item in the cart
    is displayed as a card with the product image, store abbreviation,
    title, editable price and quantity, and subtotal.  The grand total
    updates automatically when the price or quantity is changed.
    """
    return """
    <!DOCTYPE html>
    <html>

    <head>
        <title>Gundam Cart</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body{

                font-family:Arial;

                background:#f5f5f5;

                padding:8px;

                margin:0;
            }
.container{

    width:100%;

    max-width:1600px;

    margin:auto;

    background:white;

    padding:16px;

    border-radius:10px;

    box-shadow:0 0 10px rgba(0,0,0,0.1);
}
            h1{
                margin-bottom:20px;
            }

            /* Card layout for cart items */
            .cart-cards{
                display:flex;
                flex-direction:column;
                gap:14px;
                margin-top:20px;
            }
.cart-card{

    display:flex;

    gap:12px;

    background:white;

    border-radius:14px;

    padding:10px 12px;

    border:1px solid #ddd;

    box-shadow:0 2px 6px rgba(0,0,0,0.08);

    align-items:center;

    width:100%;

    box-sizing:border-box;
}

            .cart-image{

                width:70px;
                height:95px;

                object-fit:cover;

                border-radius:8px;

                flex-shrink:0;
            }

            .cart-content{

                flex:1;

                min-width:0;

                width:100%;
            }

            .cart-title{
                /* smaller font size for card names to save space */
                font-size:13px;
                line-height:1.4;
                margin-bottom:8px;
                word-break:break-word;
            }

            .cart-controls{
                /* Use a grid layout so price, quantity and subtotal align horizontally on the same plane.  Each group gets equal space. */
                display:grid;
                grid-template-columns:
                    1fr
                    1fr
                    auto;
                gap:10px;
                margin-bottom:10px;
                align-items:center;
            }

            .control-group{
                display:flex;
                flex-direction:column;
                justify-content:flex-start;
                /* Allow groups to stretch to fill available grid columns */
                width:100%;
            }

            .control-group label{

                font-size:11px;

                color:#666;

                margin-bottom:4px;
            }

            .control-group input{
                /* Full width input to align with other groups */
                width:100%;
                padding:6px;
                border:1px solid #ccc;
                border-radius:6px;
                font-size:14px;
            }

            /* Quantity controls */
            .qty-controls{
                display:flex;
                align-items:center;
                justify-content:center;
                gap:6px;
                width:100%;
            }
            .qty-btn{
                width:26px;
                height:26px;
                border:none;
                border-radius:6px;
                font-size:16px;
                font-weight:bold;
                cursor:pointer;
                display:flex;
                align-items:center;
                justify-content:center;
            }
            .qty-btn.minus{
                background:#ef4444;
                color:white;
            }
            .qty-btn.plus{
                background:#2563eb;
                color:white;
            }
            .qty-btn.minus:hover{
                background:#dc2626;
            }
            .qty-btn.plus:hover{
                background:#1d4ed8;
            }
            .qty-value{
                min-width:24px;
                text-align:center;
                font-size:14px;
            }

            /* Subtotal group styled similarly to other control groups */
            .subtotal-value{
                display:flex;
                align-items:center;
                font-size:14px;
                font-weight:bold;
                /* Ensure consistent height with input fields */
                min-height:34px;
            }

            .remove-btn{

                background:#ef4444;

                color:white;

                border:none;

                padding:7px 12px;

                border-radius:6px;

                cursor:pointer;

                font-size:13px;
            }
            .remove-btn:hover{
                background:#dc2626;
            }
            /* Colour coding for store labels within the cart */
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
            .total{
                font-size:18px;
                font-weight:bold;
                margin-top:20px;
            }
            .actions{
                margin-top:15px;
            }
            .actions button{
                margin-right:10px;
                padding:8px 14px;
                font-size:14px;
                cursor:pointer;
                border:none;
                border-radius:6px;
                font-weight:bold;
            }
            .clear-btn{
                background:#f97316;
                color:white;
            }
            .back-btn{
                background:#2563eb;
                color:white;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h1>Shopping Cart</h1>
            <div id="cart-items" class="cart-cards"></div>
            <div class="total" id="grand-total"></div>
            <div class="actions">
                <button class="back-btn" onclick="goBack()">&larr; Back to Search</button>
                <button class="clear-btn" onclick="clearCart()">Clear Cart</button>
            </div>
        </div>
        <script>
            function getCart(){
                try{
                    const c = localStorage.getItem('cart');
                    return c ? JSON.parse(c) : [];
                }catch(e){
                    return [];
                }
            }
            function saveCart(cart){
                localStorage.setItem('cart', JSON.stringify(cart));
            }
            function removeItem(index){
                const cart = getCart();
                cart.splice(index, 1);
                saveCart(cart);
                renderCart();
            }
            function clearCart(){
                localStorage.removeItem('cart');
                renderCart();
            }
            function goBack(){
                window.location.href = '/';
            }
            function updatePrice(idx, val){
                const cart = getCart();
                let price = Number(val);
                if(isNaN(price) || price < 0){ price = 0; }
                cart[idx].price = price;
                saveCart(cart);
                renderCart();
            }
            function updateQty(idx, val){
                const cart = getCart();
                let qty = parseInt(val, 10);
                if(isNaN(qty) || qty < 1){ qty = 1; }
                cart[idx].cart_qty = qty;
                saveCart(cart);
                renderCart();
            }

            // Increase the quantity of an item by one
            function increaseQty(idx){
                const cart = getCart();
                if(!cart[idx]) return;
                let qty = parseInt(cart[idx].cart_qty || 0, 10);
                if(isNaN(qty) || qty < 0){ qty = 0; }
                cart[idx].cart_qty = qty + 1;
                saveCart(cart);
                renderCart();
            }

            // Decrease the quantity of an item by one.  If quantity drops below 1, remove the item.
            function decreaseQty(idx){
                const cart = getCart();
                if(!cart[idx]) return;
                let qty = parseInt(cart[idx].cart_qty || 0, 10);
                if(isNaN(qty) || qty < 1){ qty = 1; }
                qty = qty - 1;
                if(qty < 1){
                    cart.splice(idx, 1);
                } else {
                    cart[idx].cart_qty = qty;
                }
                saveCart(cart);
                renderCart();
            }
            function renderCart(){
                const cart = getCart();
                const itemsDiv = document.getElementById('cart-items');
                const totalDiv = document.getElementById('grand-total');
                if(!cart || cart.length === 0){
                    itemsDiv.innerHTML = '<p>Your cart is empty.</p>';
                    totalDiv.textContent = '';
                    return;
                }
                let html = '';
                let grandTotal = 0;
                cart.forEach((item, idx) => {
                    if(!item.cart_qty){ item.cart_qty = 1; }
                    let price = Number(item.price || 0);
                    const subtotal = Number(price) * Number(item.cart_qty);
                    grandTotal += subtotal;
                    
                    html += `
                        <div class="cart-card">
                            <img
                                src="${item.image || 'https://via.placeholder.com/60x84?text=No+Image'}"
                                class="cart-image"
                            />
                            <div class="cart-content">
                                <div class="cart-title">
                                    ${item.title}
                                </div>
                                <!-- Updated controls layout: price, quantity and subtotal aligned horizontally -->
                                <div class="cart-controls">
                                    <div class="control-group">
                                        <label>Price</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            min="0"
                                            value="${price.toFixed(2)}"
                                            onchange="updatePrice(${idx}, this.value)"
                                        />
                                    </div>
                                    
                                    <div class="control-group">
                                        <label>Subtotal</label>
                                        <div class="subtotal-value">
                                            $${subtotal.toFixed(2)}
                                        </div>
                                    </div>

                                    <div class="control-group">
                                        <label>Qty</label>
                                        <div class="qty-controls">
                                            <button class="qty-btn minus" onclick="decreaseQty(${idx})">-</button>
                                            <span class="qty-value">${item.cart_qty}</span>
                                            <button class="qty-btn plus" onclick="increaseQty(${idx})">+</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;

                });
                itemsDiv.innerHTML = html;
                totalDiv.textContent = 'Grand Total: $' + grandTotal.toFixed(2);
            }
            renderCart();
        </script>
    </body>
    </html>
    """