# Installation

## 1. Python

The EUDI rQES Wallet-Driven Wallet Tester application was tested with

- Python version 3.10.8

and should only be used with Python 3.10 or higher.

If you don't have it installed, please downlod it from <https://www.python.org/downloads/> and follow the [Python Developer's Guide](https://devguide.python.org/getting-started/).

## 2. Flask

The EUDI rQES Wallet-Driven Wallet Tester application was tested with

- Flask v. 2.3

and should only be used with Flask v. 2.3 or higher.

To install [Flask](https://flask.palletsprojects.com/en/2.3.x/), please follow the [Installation Guide](https://flask.palletsprojects.com/en/2.3.x/installation/).

## 3. Running the EUDI rQES Wallet-Driven Wallet Tester Application

To run the application, follow these simple steps (some of which may have already been completed when installing Flask) for Linux/macOS or Windows.

### Step 1: Clone the Repository

Clone the eudi-app-web-walletdriven-tester-py repository:

```shell
git clone <repository>
```

### Step 2: Create a Virtual Environment

Create a `.venv` folder within the cloned repository:

```shell
cd eudi-app-web-walletdriven-tester-py
python3 -m venv .venv
```

### Step 3: Activate the Virtual Environment

Linux/macOS

```shell
. .venv/bin/activate
```

Windows

```shell
. .venv\Scripts\Activate
```

### Step 4: Upgrade pip

Install or upgrade _pip_

```shell
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies

Install Flask and other dependencies in virtual environment

```shell
pip install -r requirements.txt
```

### Step 6: Configure the Application

> **Note:** By default, this service (Wallet Tester) authenticates in the QTSP Authorization Server using **OID4VP Same-Device flow**.
> It can also be configured to support **cross-device flow** and **form-based login**.

Update the configuration in `config.py` (located in `app/core`) or create a `.env` file based on `.env.sample`.

#### 6.1 `config.py`

- **ENV**: environment type (e.g., development, preproduction)
- **SECRET_KEY**: REQUIRED - a secure, randomly generated key
- **DOCUMENTS_UPLOAD_FOLDER**: REQUIRED - path to the folder where documents to be signed are stored
- **SERVICE_URL**: REQUIRED - base URL of the service
- **RP_URL**: REQUIRED - URL of a Relying Party (RP) supporting rQES document retrieval 
- **AS_URL**: REQUIRED - URL of the QTSP Authorization Server (AS)
- **RS_URL**: REQUIRED - URL of the QTSP Resource Server (RS)
- **SCA_URL**: REQUIRED - URL of the SCA Service
- **OAUTH_CODE_CHALLENGE_METHOD**: REQUIRED - PKCE code challenge method (e.g., S256)
- **OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS**: additional supported authentication methods (e.g., `test-form`, `cross-device`)

- **OAUTH_CLIENT_ID**: REQUIRED - (Same-device flow) client ID registered in the QTSP AS
- **OAUTH_CLIENT_SECRET**: REQUIRED - (Same-device flow) client secret registered in the QTSP AS
- **OAUTH_REDIRECT_URL**: REQUIRED - (Same-device flow) redirect URI registered in the QTSP AS

- **OAUTH_CROSS_DEVICE_FLOW_CLIENT_ID**: OPTIONAL - (Cross-device flow) client ID registered in the QTSP AS
- **OAUTH_CROSS_DEVICE_FLOW_CLIENT_SECRET**: OPTIONAL - (Cross-device flow) client secret registered in the QTSP AS
- **OAUTH_CROSS_DEVICE_FLOW_REDIRECT_URL**: OPTIONAL - (Cross-device flow) redirect URI registered in the QTSP AS

- **OAUTH_TEST_FORM_CLIENT_ID**: OPTIONAL - (Form Login) client ID registered in the QTSP AS
- **OAUTH_TEST_FORM_CLIENT_SECRET**: OPTIONAL - (Form Login) client secret registered in the QTSP AS
- **OAUTH_TEST_FORM_REDIRECT_URL**: OPTIONAL - (Form Login) redirect URI registered in the QTSP AS
- **OAUTH_USERNAME**: username for form login
- **OAUTH_PASSWORD**: password for form login

#### 6.2 `.env` File

```
FLASK_RUN_PORT=5000
ENV=dev
SECRET_KEY=

DOCUMENTS_UPLOAD_FOLDER=app/documents
SERVICE_URL=http://127.0.0.1:5000/tester

RP_URL=
AS_URL=
RS_URL=
SCA_URL=

OAUTH_CODE_CHALLENGE_METHOD=S256
OAUTH_ADDITIONAL_SUPPORTED_OID4VP_FLOWS='[test-form, cross-device]'

OAUTH_CLIENT_ID=
OAUTH_CLIENT_SECRET=
OAUTH_REDIRECT_URL=http://127.0.0.1:5000/tester/oauth/login/code

OAUTH_CROSS_DEVICE_FLOW_CLIENT_ID=
OAUTH_CROSS_DEVICE_FLOW_CLIENT_SECRET=
OAUTH_CROSS_DEVICE_FLOW_REDIRECT_URL=http://127.0.0.1:5000/tester/oauth2/callback

OAUTH_TEST_FORM_CLIENT_ID=
OAUTH_TEST_FORM_CLIENT_SECRET=
OAUTH_TEST_FORM_REDIRECT_URL=http://127.0.0.1:5000/tester/oauth/login/code
OAUTH_USERNAME=
OAUTH_PASSWORD=
```

### Step 7: Run the Application

Run the EUDI rQES Wallet-Driven Wallet Tester application (on <http://127.0.0.1:5000>)

```shell
flask --app app run
```
