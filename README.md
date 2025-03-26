# FIDO 2FA Authentication Demo

![startpage](docs/startpage.png)

![login](docs/login.png)

This project demonstrates secure two-factor authentication (2FA) with FIDO for websites. It was built using Python and the Flask framework.

Users can create new accounts and log in to existing ones using a username and password. If users have set up a FIDO security key (optional), it will also be required during login, protecting the account against identity theft.

All data is stored in a lightweight database. Passwords are never stored in plain text but are hashed and salted.

During development, great emphasis was placed on security. The application is protected against XSS, CORS, CSRF, clickjacking, and SQL injections.

## Features

- Create an account with a username and password
- Log in with a username and password
- Add a FIDO security key to an account (either during account creation or later)
- Log in using a username and password (first factor) and FIDO (second factor)

## Hosting the Application

For security reasons, browsers only allow the use of FIDO on websites served over HTTPS. The browser ensures that the certificate is valid (e.g., not expired, matches the website domain, etc.) and blocks the use of FIDO otherwise.

To host the application yourself, you must use a valid certificate. The application currently generates a self-signed certificate at runtime.

Because of the self-signed certificate, FIDO cannot be used when accessing the application via a domain or IP address. However, most browsers treat `localhost` as a special case and allow the use of FIDO when the site is accessed via `localhost`.

## Running Locally

To run this project locally, you need to install all dependencies. Execute the following commands:

```bash
pip3 install -r requirements.txt
python3 server.py

The application will then be available at https://localhost:5000. Note that browsers will block FIDO for any host other than localhost (e.g., 127.0.0.1) due to the security restrictions mentioned earlier.

The server stores its database in the database folder.

Running with Docker
It is also possible to run this project in a Docker container. To do so, you need to install Docker. Then execute the following commands:

bash
Copy code
docker build -t fido:1.0 .
docker run -ti -p 8000:8000 fido:1.0
The application will be accessible at https://localhost:8000. Note that using HTTPS is mandatory; the server will not respond to HTTP requests.

The previous example stores the database inside the container. To store the database on your local disk, execute the following commands on a UNIX-like system (macOS or Linux):

bash
Copy code
mkdir database
chmod -R a+rwx database
docker run -ti -p 8000:8000 --mount type=bind,source="$(pwd)/database",target=/app/database fido:1.0
