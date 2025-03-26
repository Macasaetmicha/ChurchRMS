import * as fidoLayout from "/js/fido-layout.js";
import {
    create,
    parseCreationOptionsFromJSON,
} from '/js/webauthn-json.browser-ponyfill.js';


document.addEventListener("DOMContentLoaded", function () {
    // Call the function when the page loads
    fetchUserInfo();

    document.body.addEventListener('click', function(event) {
        if (event.target.matches('button[data-page="updateRecovNum"]')) {
            event.preventDefault(); // Prevent the default form submission
            const form = document.querySelector('#updateRecovNumForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            console.log(data);
            console.log('BUTTON WAS PRESSED');
            updateNumber(data);
        }
    });
});

async function updateNumber(data) {
    try {
        const response = await fetch('/settings/update/recoveryNumber', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const result = await response.json();
        Swal.fire({
            title: 'Success!',
            text: result.message,
            icon: 'success',
            confirmButtonText: 'OK'
        }).then(() => {
            window.location.href = '/settings';
        });
    } catch (error) {
        console.error('Error inserting data:', error);
        Swal.fire({
            title: 'Error!',
            text: 'Failed to insert data.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    }
}

function fetchUserInfo() {
    fetch('/settings/user')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error:", data.error);
            } else {
                // Populate the user information
                document.getElementById("accnt-name").innerHTML = (data.firstname || "N/A")+ " " + (data.middlename || "N/A") + " " + (data.lastname || "N/A");
                document.getElementById("accnt-username").innerHTML = (data.username || "N/A");
                document.getElementById("accnt-email").innerHTML = (data.email || "N/A");
                document.getElementById("accnt-number").innerHTML = (data.contact_number || "N/A");
                document.getElementById("accnt-joined").innerHTML = (formatDateToLong(data.joined) || "N/A");
                document.getElementById("recovery-number").innerHTML = (data.contact_number || "N/A"); // Example number
            }
        })
        .catch(error => console.error("Fetch error:", error));
}

const buttonDiv = document.getElementById("button-div");
const authenticateButton = document.getElementById("update-authenticate-button");

authenticateButton.onclick = onAuthenticateButtonClicked;

function displayFailure() {
    fidoLayout.displayFailure("FIDO setup failed");

    authenticateButton.innerText = "Try Again";
    buttonDiv.style.display = "block";
}

function displayInProgress() {
    fidoLayout.displayInProgress();
    buttonDiv.style.display = "none";
}

async function onAuthenticateButtonClicked() {
    displayInProgress();
    

    let request = await fetch('/settings/update/authentication', {
        method: 'PUT',
    });

    if(request.ok) {
        let request = await fetch('/api/register/begin', {
            method: 'POST',
        });

        let json = await request.json();
        let options = parseCreationOptionsFromJSON(json);

        let response = null;
        try {
            response = await create(options);
        } catch (e) {
            displayFailure();
            throw Error("The browser could not process the cryptographic challenge. The most likely cause is that the " +
                "user didn't allow the request. Raw Error: " + e);
        }

        let result = await fetch('/api/register/complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(response),
        });

        if (!result.ok) {
            displayFailure();
            let errorMessage = "The server rejected the signed challenge. URL: " + request.url +
                " Status: " + request.status + " Response Body: " + await request.text();
            throw new Error(errorMessage);
        }

        window.location = "/settings";
    } else{
        displayFailure();
        let errorMessage = "Failed to retrieve registration data from the server. URL: " + request.url +
            " Status: " + request.status + " Response Body: " + await request.text();
        throw new Error(errorMessage);
    }

    
}
