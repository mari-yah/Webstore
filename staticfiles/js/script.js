function toggleCart(button) {
    if (button.classList.contains('added')) {
        button.classList.remove('added');
        button.querySelector('span').innerText = 'Add to Cart';
    } else {
        button.classList.add('added');
        button.querySelector('span').innerText = 'Added to Cart';
    }
}

function toggleWishlist(button) {
    if (button.classList.contains('wishlisted')) {
        button.classList.remove('wishlisted');
        button.querySelector('span').innerText = 'Wishlist';
    } else {
        button.classList.add('wishlisted');
        button.querySelector('span').innerText = 'Wishlisted';
    }
}
// Function to Add Product to Cart
function addToCart(id, name, price, image) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    let existingItem = cart.find(item => item.id === id);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id, name, price, image, quantity: 1 });
    }

    localStorage.setItem("cart", JSON.stringify(cart));
    updateCartCount();
    alert(`${name} added to cart!`);
}

// Function to Add Product to Cart
function addToCart(id, name, price, image) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    let existingItem = cart.find(item => item.id === id);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id, name, price, image, quantity: 1 });
    }

    localStorage.setItem("cart", JSON.stringify(cart));
    updateCartCount();
    alert(`${name} added to cart!`);
}

// Function to Update Cart Count in Header
function updateCartCount() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let count = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    let cartCountElement = document.getElementById("cart-count");
    if (cartCountElement) {
        cartCountElement.textContent = count;
    }
}

// Function to Load Cart Items on Cart Page
function loadCart() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartContainer = document.getElementById("cart-items");
    let totalPrice = 0;

    if (!cartContainer) return;

    cartContainer.innerHTML = "";

    if (cart.length === 0) {
        cartContainer.innerHTML = "<p>Your cart is empty.</p>";
    } else {
        cart.forEach(item => {
            totalPrice += item.price * item.quantity;
            cartContainer.innerHTML += `
                <div class="cart-item">
                    <img src="${item.image}" alt="${item.name}">
                    <p><strong>${item.name}</strong></p>
                    <p>$${item.price}</p>
                    <p>Qty: ${item.quantity}</p>
                    <button onclick="removeFromCart('${item.id}')">Remove</button>
                </div>
            `;
        });
    }

    document.getElementById("cart-total").textContent = `$${totalPrice.toFixed(2)}`;
}

// Function to Remove Item from Cart
function removeFromCart(id) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart = cart.filter(item => item.id !== id);
    localStorage.setItem("cart", JSON.stringify(cart));

    loadCart();
    updateCartCount();
}

// Ensure cart count updates when the page loads
document.addEventListener("DOMContentLoaded", function() {
    updateCartCount();
    if (document.getElementById("cart-items")) {
        loadCart();
    }
});
