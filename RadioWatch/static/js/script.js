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
