async function loadDeals() {

    try {

        const response = await fetch(
            "deals.json?t=" + Date.now()
        );

        const deals = await response.json();

        renderDeals(deals);

    } catch (error) {

        console.error(error);

        document.getElementById(
            "deals-container"
        ).innerHTML = `
            <div class="text-center py-20 col-span-full">

                <h2 class="text-red-500 text-3xl font-bold">
                    Failed To Load Deals
                </h2>

            </div>
        `;
    }
}

function renderDeals(deals) {

    const container =
        document.getElementById(
            "deals-container"
        );

    container.innerHTML = "";

    deals.forEach(deal => {

        let badge = "bg-gray-700";

        if (deal.store === "Amazon")
            badge = "bg-amber-500";

        if (deal.store === "Flipkart")
            badge = "bg-blue-600";

        if (deal.store === "Myntra")
            badge = "bg-pink-600";

        const card = `

        <div class="bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-2xl transition duration-300">

            <div class="relative">

                <img
                    src="${deal.image}"
                    class="w-full h-72 object-cover"
                >

                <span class="absolute top-3 left-3 bg-red-500 text-white px-3 py-1 rounded-xl text-sm font-black">

                    ${deal.discount}

                </span>

                <span class="absolute top-3 right-3 ${badge} text-white px-3 py-1 rounded-xl text-sm font-bold">

                    ${deal.store}

                </span>

            </div>

            <div class="p-5">

                <h2 class="text-xl font-black text-gray-900 leading-tight">

                    ${deal.title}

                </h2>

                <div class="flex items-center gap-3 mt-4">

                    <span class="text-3xl font-black text-gray-900">

                        ₹${deal.new_price}

                    </span>

                    <span class="text-lg text-gray-400 line-through">

                        ₹${deal.old_price}

                    </span>

                </div>

                <div class="mt-4 text-gray-700 text-sm leading-7 whitespace-pre-line">

                    ${deal.caption}

                </div>

                <a
                    href="${deal.main_link}"
                    target="_blank"
                    class="block text-center mt-6 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-black py-4 rounded-2xl transition"
                >

                    Grab Deal ➜

                </a>

            </div>

        </div>
        `;

        container.innerHTML += card;
    });
}

loadDeals();

setInterval(loadDeals, 30000);
