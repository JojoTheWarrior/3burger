// importing the bouquet map
import { bouquetMap } from './bouquetMap.js';

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
    showOrderPlaced();

    // const selectedToppings = Array.from(document.getElementById('toppings').selectedOptions).map(opt => opt.value);
    // const selectedSauces = Array.from(document.getElementById('sauces').selectedOptions).map(opt => opt.value);

    const getCheckedValues = (containerId) => {
        return Array.from(document.querySelectorAll(`#${containerId} input[type="checkbox"]:checked`))
                .map(input => input.value);
    }
    const selectedToppings = getCheckedValues('toppings');
    const selectedSauces = getCheckedValues('sauces');
    console.log(selectedToppings, selectedSauces);

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
        pickup_name: document.getElementById('pickup-name').value,
        card: {
            card_number: fastPow(M, E, N).toString(),
            expiry: document.getElementById('expiryDate').value,
            cvv: document.getElementById('cvv').value,
            name: document.getElementById('fullName').value,
            postal_code: document.getElementById('postalCode').value,
        }
    };

    console.log(orderData);

    // for local testing
    // const URL 
    const URL = 'https://9d53a5b072a0.ngrok-free.app/get_burger';

    try {
        const response = await fetch(URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });
        const data = await response.json();
        console.log(data);
    } catch (err) {
        console.error('Error placing order:', err);
        alert('Failed to place order.');
    }
});

function showOrderPlaced() {
    /*
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
    */
}

// bouquet layer logic
document.addEventListener("DOMContentLoaded", () => {
    const main = document.querySelector("main");
    let bouquetLayer = document.getElementById("bouquet-layer");
    
    if (!bouquetLayer) {
        bouquetLayer = document.createElement("div");
        bouquetLayer.id = "bouquet-layer";
        main.appendChild(bouquetLayer);
    }

    // Handle filenames (special cases)
    function getFilename(item, index = 0) {
        if (item === "Jalapeños") return "jalapenos_bouquet.png";
        if (item === "Salt & Pepper") {
            return index % 2 === 0
                ? "salt_shaker_bouquet.png"
                : "pepper_shaker_bouquet.png";
        }
        return (
            item
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/ /g, "_")
                .replace(/&/g, "and") + "_bouquet.png"
        );
    }

    // Seeded random function for reproducible positions
    function nextRandom() {
        return Math.random();
    }

    function generateCoords(item, count) {
        const coords = [];
        for (let i = 0; i < count; i++) {
            const r = nextRandom();
            let top, left;

            if (r < 0.125) {
                // top
                top = "-5%";
                left = `${nextRandom() * 110 - 5}%`;
            } else if (r < 0.25) {
                // bottom
                top = "100%";
                left = `${nextRandom() * 110 - 5}%`;
            } else if (r < 0.625) {
                // left
                top = `${nextRandom() * 110 - 5}%`;
                left = "-10%";
            } else {
                // right
                top = `${nextRandom() * 110 - 5}%`;
                left = "95%";
            }

            const rot = `${nextRandom() * 180 - 90}deg`; // -90 to 90 degrees
            coords.push({ top, left, rot });
        }
        return coords;
    }

    // Pre-create bouquet image elements with generated coords
    Object.keys(bouquetMap).forEach((item) => {
        const coords = generateCoords(item, 15); // 10 images per item
        bouquetMap[item] = coords; // update bouquetMap with generated positions
        coords.forEach((c, i) => {
            const img = document.createElement("img");
            const filename = getFilename(item, i);
            img.src = `./assets/${filename}`;
            img.classList.add("bouquet-img");
            img.style.top = c.top;
            img.style.left = c.left;
            img.style.setProperty("--rot", c.rot);
            img.dataset.item = item;
            img.dataset.index = i;

            // Give each image a unique float phase via animation-delay
            const delay = nextRandom() * 2; // 0 to 2s for 2s loop
            img.style.animationDelay = `${delay}s`;

            bouquetLayer.appendChild(img);
        });
    });

    // Hook up toggles
    function updateBouquet(selectId) {
        const select = document.getElementById(selectId);
        select.addEventListener("change", () => {
            const selected = Array.from(document.querySelectorAll(`input[type="checkbox"]:checked`))
                    .map(input => input.value);
            
            bouquetLayer.querySelectorAll(".bouquet-img").forEach((img) => {
                if (img.dataset.item in bouquetMap) {
                    if (selected.includes(img.dataset.item)) {
                        img.classList.add("active");
                    } else {
                        img.classList.remove("active");
                    }
                }
            });
        });
    }

    updateBouquet("toppings");
    updateBouquet("sauces");

});
