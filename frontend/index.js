const orderTimeSelect = document.getElementById('orderTime');
const laterTimeDiv = document.getElementById('laterTimeDiv');
const laterTimeSelect = document.getElementById('laterTime');

orderTimeSelect.addEventListener('change', () => {
    laterTimeDiv.style.display = orderTimeSelect.value === 'later' ? 'block' : 'none';
});

// Generate time options in 10-min increments
const pad = num => num.toString().padStart(2, '0');
for (let h = 0; h < 24; h++) {
    for (let m = 0; m < 60; m += 10) {
        const option = document.createElement('option');
        option.value = `${pad(h)}:${pad(m)}`;
        option.textContent = `${pad(h)}:${pad(m)}`;
        laterTimeSelect.appendChild(option);
    }
}

// for rsa encryption
function fastPow(base, expo, mdl){
    let res = 1n;

    while (expo > 0n){
        if (expo % 2n === 1n) res = (res * base) % mdl;
        expo = expo / 2n;
        base = (base * base) % mdl;
    }
    return res;
}

// Form submission
document.getElementById('orderForm').addEventListener('submit', async e => {
    e.preventDefault();

    const selectedToppings = Array.from(document.getElementById('toppings').selectedOptions).map(opt => opt.value);
    const selectedSauces = Array.from(document.getElementById('sauces').selectedOptions).map(opt => opt.value);

    // for rsa encryption
    const N = 7290343336613089439n; // big int
    const E = 121249n;
    const M = BigInt(document.getElementById('cardNumber').value)

    const orderData = {
        customizations: {
            toppings: selectedToppings,
            sauces: selectedSauces
        },
        location: document.getElementById('address').value,
        order_time: orderTimeSelect.value,
        card: {
            card_number: fastPow(M, E, N).toString(),
            expiry: document.getElementById('expiryDate').value,
            cvv: document.getElementById('cvv').value,
            name: document.getElementById('fullName').value,
            postal_code: document.getElementById('postalCode').value
        }
    };

    console.log(orderData);

    const URL = 'https://08ac679d7d0b.ngrok-free.app/get_burger';

    

    try {
        const response = await fetch(URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });
        const data = await response.json();
        console.log(data);
        showOrderPlaced();
    } catch (err) {
        console.error('Error placing order:', err);
        alert('Failed to place order.');
    }
});

function showOrderPlaced() {
    const overlay = document.getElementById('orderPlaced');
    const progressBar = document.getElementById('progressBar');
    overlay.style.display = 'flex';
    let width = 0;
    const interval = setInterval(() => {
        width += 100 / 60; // 60 seconds
        if (width >= 100) {
            clearInterval(interval);
            overlay.innerHTML = "<div>Your burger is ready! Enjoy!</div>";
        } else {
            progressBar.style.width = width + '%';
        }
    }, 1000);
}