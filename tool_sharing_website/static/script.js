var stripe = Stripe(stripe_public_key);

const button = document.getElementById('verify-card-button');

button.addEventListener('click', event => {
    stripe.redirectToCheckout({
        sessionId: checkout_session_id
    }).then(function (result) {
        // If `redirectToCheckout` fails due to a browser or network
        // error, display the localized error message to your customer
        // using `result.error.message`.
    });
});