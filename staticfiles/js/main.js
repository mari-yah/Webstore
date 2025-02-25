document.addEventListener("DOMContentLoaded", function () {
    updateCartCount();

    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function () {
            let productItem = this.closest(".product-item");

            if (!productItem) {
                console.error("Product item not found.");
                return;
            }

            let id = productItem.dataset.id;
            let name = productItem.dataset.name;
            let price = parseFloat(productItem.dataset.price);
            let image = productItem.dataset.image;

            if (!id || !name || isNaN(price) || !image) {
                console.error("Invalid product data:", { id, name, price, image });
                return;
            }

            addToCart(id, name, price, image);
        });
    });
});

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

function updateCartCount() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let count = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById("cart-count").textContent = count;
}

function loadCart() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartContainer = document.getElementById("cart-items");
    let totalPrice = 0;
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
                    <p>₹${item.price}</p>
                    <p>Qty: ${item.quantity}</p>
                    <button onclick="removeFromCart('${item.id}')">Remove</button>
                </div>
            `;
        });
    }

    document.getElementById("cart-total").textContent = `₹${totalPrice.toFixed(2)}`;
}

function removeFromCart(id) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart = cart.filter(item => item.id !== id);
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCart();
    updateCartCount();
}

function clearCart() {
    localStorage.removeItem("cart");
    loadCart();
    updateCartCount();
}

if (document.getElementById("cart-items")) {
    loadCart();
}
function proceedToCheckout() {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    if (cart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    alert("Proceeding to checkout...");
    window.location.href = "/checkout";  // Redirect to checkout page (replace with actual URL)
}
document.addEventListener("DOMContentLoaded", function () {
    // Attach event listeners to wishlist buttons
    document.querySelectorAll(".wishlist").forEach(button => {
        button.addEventListener("click", function () {
            let productItem = this.closest(".product-item");

            let product = {
                id: productItem.getAttribute("data-id"),
                name: productItem.getAttribute("data-name"),
                price: productItem.getAttribute("data-price"),
                image: productItem.getAttribute("data-image")
            };

            addToWishlist(product);
        });
    });

    loadWishlist(); // Load wishlist items if user visits the wishlist page
});

// Function to add product to wishlist
function addToWishlist(product) {
    let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];

    if (!wishlist.some(item => item.id === product.id)) {
        wishlist.push(product);
        localStorage.setItem("wishlist", JSON.stringify(wishlist));
        alert(`${product.name} added to Wishlist!`);
    } else {
        alert(`${product.name} is already in your Wishlist!`);
    }
}

// Function to load wishlist on the wishlist page
function loadWishlist() {
    let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];
    let wishlistContainer = document.querySelector(".wishlist-items");

    if (!wishlistContainer) return; // Prevent running on other pages

    if (wishlist.length === 0) {
        document.querySelector(".wishlist-empty").style.display = "block";
        wishlistContainer.innerHTML = "";
        return;
    } else {
        document.querySelector(".wishlist-empty").style.display = "none";
    }

    wishlistContainer.innerHTML = wishlist.map(item => `
        <div class="wishlist-item">
            <div class="wishlist-item-image">
                <img src="${item.image}" alt="${item.name}" class="wishlist-item-img">
            </div>
            <div class="wishlist-item-details">
                <h4 class="wishlist-item-name">${item.name}</h4>
                <p class="wishlist-item-price">₹ ${item.price}</p>
                <div class="wishlist-item-actions">
                    <button class="add-to-cart-btn" onclick="moveToCart('${item.id}')">Add to Cart</button>
                    <button class="remove-wishlist-btn" onclick="removeFromWishlist('${item.id}')">Remove</button>
                </div>
            </div>
        </div>
    `).join("");
}

// Function to move item from wishlist to cart
function moveToCart(productId) {
    let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];
    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    let product = wishlist.find(item => item.id === productId);
    if (product) {
        product.quantity = 1; // Ensure quantity is set
        cart.push(product);
        localStorage.setItem("cart", JSON.stringify(cart));

        removeFromWishlist(productId); // Remove from wishlist after adding to cart
        alert(`${product.name} moved to Cart!`);
    }
}

// Function to remove item from wishlist
function removeFromWishlist(productId) {
    let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];
    wishlist = wishlist.filter(item => item.id !== productId);
    localStorage.setItem("wishlist", JSON.stringify(wishlist));

    loadWishlist(); // Refresh wishlist UI
}
