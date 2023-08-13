Hotel Booking
---

## Table of Contents

- [Hotel Booking Platform with Amadeus](#hotel-booking-platform-with-amadeus) 
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Install Django](#install-django)
  - [Install Oscar](#install-oscar)
  - [Set Up the Project](#set-up-the-project)
- [Integration Setup](#integration-setup)
  - [Amadeus API Integration](#amadeus-api-integration)
    - [Obtaining Amadeus API Key and Secret](#obtaining-amadeus-api-key-and-secret)
    - [Test (Self) Mode vs. Production Mode](#test-self-mode-vs-production-mode)
  - [Google API](#google-api)
  - [Geoapify](#geoapify)
  - [OpenCageData API](#opencagedata-api)
  - [credit-card-key-generation](#credit-card-key-generation)
- [`.env` Setup](#env-setup)
- [Running the Project](#running-the-project)
- [License](#license)

---

## Hotel Booking Platform with Amadeus

Welcome to the Hotel Booking Platform built on Django and integrated with Oscar for e-commerce capabilities. This platform leverages the power of Amadeus APIs for hotel searching and booking.

---
## About the Hotel Booking Platform

Welcome to our **Amadeus Hotel Booking Platform**, a state-of-the-art application built on the robust Django framework and integrated with Oscar for seamless e-commerce capabilities.

### How It Works

1. **Destination Input**:
   Begin your hotel hunting journey by simply inputting your destination. Whether you're searching for an urban escape in New York or a coastal retreat in Bali, just type in where you want to go, and our platform will handle the rest.

   2. **Exploring Hotel Results**:
      Within moments, you'll be presented with a curated list of available hotels in your chosen destination. But we don’t just stop at names and prices. Dive deeper into each listing to discover what truly matters.

   3. **Find the Best Rate**:
      Budget constraints? Looking for a luxurious experience? Or perhaps something in between? Scroll through various hotel rates to find the one that aligns perfectly with your needs and wallet.

   4. **Detailed Insights**:
      When you're spending your hard-earned money, surprises aren’t always welcome. That’s why, for each hotel, we provide intricate details on the amenities they offer, both for the establishment as a whole and for individual rooms. Know what you're getting into, down to the very last detail.

   5. **Proceed to Booking**:
      Once you've made your choice, proceed to the details page. Here, you'll provide necessary information about yourself and any additional requirements or preferences you might have.

   6. **Confirmation & Email Notification**:
      After inputting your details, click through to the confirmation page. Almost immediately, you'll receive an email, sealing the deal. This email will serve as a tangible testament to your upcoming journey, holding all necessary details about your booking.

### A Note on Production Mode

:warning: **Important**: We are currently operating in **Production Mode**. This means that every hotel booking you make through our platform is a legitimate transaction, directly informing the hotel of your reservation. Please proceed with genuine intent and caution. Should you wish to test functionalities or explore without making actual bookings, consider switching to the environment mode. Instructions on how to do so can be found in the [Amadeus Integration Setup](#amadeus-api-integration) section.

---

This explanation is designed to be clear, engaging, and user-friendly. Adjust any specifics as necessary to match your platform's functionalities and design.

---



## Prerequisites

Before proceeding with the installation, make sure you have:

- Python (3.7 or higher recommended)
- pip (Python package installer)
- virtualenv (recommended for creating isolated environments)

## Installation

### Install Django

1. If you haven't already installed `pip`, you can do so by following [this guide](https://pip.pypa.io/en/stable/installation/).
2. (Recommended) Create a new virtual environment for your project:
    ```bash
    pip install virtualenv
    virtualenv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```
3. Install Django:
    ```bash
    pip install Django
    ```

### Install Oscar

Oscar is an open-source e-commerce framework for Django. 

1. Install Oscar using pip:
    ```bash
    pip install django-oscar
    ```

2. Add `'oscar'` and related apps to your `INSTALLED_APPS` in Django settings.

### Set Up the Project

1. Clone the repository:
    ```bash
    git clone [YOUR_REPOSITORY_LINK]
    ```

2. Navigate to the project directory:
    ```bash
    cd frobshop
    ```

3. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Run migrations to set up the database:
    ```bash
    python manage.py migrate
    ```

## Amadeus

---

## Amadeus API Integration

This project integrates with the Amadeus API to fetch and manage hotel bookings. To interact with Amadeus's services, you need an API key and secret.

### Obtaining Amadeus API Key and Secret

1. **Create an Amadeus Developer Account**:
Navigate to [Amadeus for Developers](https://developers.amadeus.com/) and sign up for a developer account.

   2. **Create a New Application**:
     Once your account is active, log in and go to the 'My Applications' section. Click on 'Create a new application'.

   3. **Fill out the Application Details**:
   - Name your application.
   - Choose the APIs you want access to (for this project, select Hotel Search and Booking related APIs).

   4. **Retrieve Your Credentials**:
     After creating the application, you will be provided with an `API Key` and `API Secret`. These are essential for making authenticated requests to the Amadeus API.

### Test (Self) Mode vs. Production Mode

- **Test (Self) Mode**:
  - This is a sandbox environment provided by Amadeus for developers to test their integrations.
  - It doesn't involve real transactions or data. The data returned by the API in this mode is mock data.
  - It's free to use and is mainly for development and testing purposes. 
  - Rate limits might be different compared to production mode. Ensure to check the rate limits for your application in the Amadeus developer dashboard.

  - **Production Mode**:
  - This is the live environment where real transactions occur.
  - To access the production environment, your application needs to be reviewed and approved by Amadeus.
  - There are costs associated with API calls in the production mode, depending on the number and type of calls you make.
  - Rate limits, data accuracy, and availability are optimized for live, commercial use.

**Important:** Always ensure that sensitive credentials like the API Key and Secret are not hardcoded in your application or stored in public repositories. Use environment variables or secret management tools to handle them securely.

---

## Switching Between Test and Production Modes in Amadeus

Amadeus API provides both a production environment and a test (or sandbox) environment. The latter is designed for development and testing, ensuring you can fine-tune your integrations without affecting real-world data or incurring costs. 

Here's how to switch between the two:

### 1. Understanding the URL Structure

The primary difference between the production and test environments in Amadeus is the base URL you use to make API calls.

- **Production URL**:
  ```
  https://api.amadeus.com/
  ```

- **Test (Sandbox) URL**:
  ```
  https://self.api.amadeus.com/
  ```

### 2. Making the Switch

To switch between modes, you need to adjust the base URL in your API calls. Here's an example using the endpoint for fetching hotels by geocode:
for example:
- **Production Mode**:
  ```python
  url = "https://api.amadeus.com/v1/reference-data/locations/hotels/by-geocode"
  ```

- **Test (Sandbox) Mode**:
  ```python
  url = "https://self.api.amadeus.com/v1/reference-data/locations/hotels/by-geocode"
  ```

### 3. Implementation in Your Code

check in views.py booking_platform.py all the amadeus url and change between modes.
notice! when moving to test_mode the get_hotel_offer will not work. 
to make this work add hotels_id (PILONBAK, ACPAR419) of amadeus that working with test mode that will run the code and make the product.
and shutdown the hotel search list call.

change get_hotel_offer_list function that is in booking_platform.py to:


### 4. Other Considerations

- **API Keys & Secrets**: Ensure you're using the appropriate API key and secret. While in some cases the same credentials might work for both environments, it's recommended to double-check them in your Amadeus Developer Dashboard.

- **Rate Limits**: Remember, the rate limits for test mode might be different than those for production. Always keep an eye on API limits to avoid disruptions, especially when in production mode.

- **Data Differences**: The test environment uses mock data, whereas the production environment will have real-time, accurate data. Make sure to validate any logic or functionalities that rely on data returned by the API when switching between environments.

---

Switching between environments is a crucial step in the development cycle, ensuring that functionalities are tested properly before being launched into a live setting. Always double-check your configurations and remain aware of the implications of operating in each mode.
---
Alright! I've expanded upon the sections for Amadeus API Integration, `.env` file setup, and added the necessary steps for setting up Google API, Geoapify, and OpenCageData API. Here's the continuation of your README:

---

## Integration Setup

### Google API

To use Google's services in your project, you need to obtain an API key.

1. **Visit the Google Cloud Console**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project, if necessary.
   - Navigate to the 'Credentials' tab in the sidebar.

2. **Generate New Credentials**:
   - Click the 'Create Credentials' button.
   - Choose 'API Key' from the dropdown.
   - Copy the generated API key.

3. **Restrict the API Key** (recommended):
   - Click on the API key you just created.
   - Under 'API restrictions', select the APIs this key will access (e.g., Maps API, Places API, etc.).
   - Add IP restrictions if necessary.

### Geoapify

1. **Visit Geoapify's website**:
   - Register at [Geoapify](https://www.geoapify.com/).

2. **Generate an API Key**:
   - Once logged in, navigate to 'My API Keys'.
   - Create a new API key.
   - Copy the generated key.

### OpenCageData API

1. **Sign Up**:
   - Register for an account at [OpenCageData](https://opencagedata.com/).

2. **Obtain the API Key**:
   - Once logged in, navigate to the dashboard.
   - Your API key should be visible there. If not, follow the prompts to generate one.
   - Copy the API key.

---

### Credit Card Key Generation

In some projects, especially e-commerce platforms like this one, it might be essential to have encryption keys, for instance, a `CREDIT_CARD_KEY` for securing sensitive data like credit card information.

1. **Navigate to Your Project Directory**:
   Open your terminal or command prompt and navigate to your Django project's root directory.

2. **Inserting the Project**:
   If you haven't added your project yet, insert it now. (This would usually mean either cloning a repository, initializing a new project, or navigating to an existing project's directory.)

   3. **Generate the Key in `coding.py`**:
      Within your Django project, you might have a utility script or module where such tasks are handled. For the purpose of this guide, we'll use a hypothetical file named `coding.py`. 
   
   - Open `coding.py` and run the following Python function to generate a secure random key:
     ```python
        def generate_key():
            return Fernet.generate_key()
     ```

   This will generate a 64-character hexadecimal key.

4. **Add the Key to `.env`**:
   Open your `.env` file (located at the root of your project directory) and append the following line:
   ```
   CREDIT_CARD_KEY=generated_key_here
   ```
   Replace `generated_key_here` with the key that was generated by the `coding.py` script.
---
## env
Of course! The `.env` file is a simple way to manage environment variables, especially for local development. Here's a step-by-step guide on how to create and use a `.env` file, and how to add the `AMADEUS_API_KEY` and `AMADEUS_API_SECRET` to it:

## Setting up a `.env` file

1. **Navigate to Your Project Directory**:
   Open your terminal or command prompt and navigate to your Django project's root directory.

2. **Create the `.env` file**:
   You can use a text editor or simply run the following command to create the file:
   ```bash
   touch .env
   ```

3. **Open the `.env` file and Add the Variables**:
   Using any text editor, open the `.env` file and add the following lines:
   ```
   AMADEUS_API_KEY=your_api_key_here
   AMADEUS_API_SECRET=your_api_secret_here
    CREDIT_CARD_KEY=your_api_key_here
    SEARCH_LOCATION_KEY=your_api_key_here
    GOOGLE_API_KEY=your_api_key_here
    GEO_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` and `your_api_secret_here` with your actual Amadeus API key and secret, respectively.

4. **Prevent the `.env` File from Being Committed**:
   It's crucial that you do not commit the `.env` file to version control, as it can contain sensitive data. If you're using Git, add the `.env` file to your `.gitignore` file:
   ```
   echo ".env" >> .gitignore
   ```

**Note**: Always be cautious with `.env` files. They should never be exposed or shared, as they might contain sensitive information. If you're collaborating with others or pushing code to public repositories, always ensure the `.env` file remains private.


## Running the Project

1. Activate your virtual environment if it's not active:
    ```bash
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

2. Run the Django development server:
    ```bash
    python manage.py runserver
    ```

Open your browser and navigate to `http://127.0.0.1:8000/` to see the project in action.


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---
