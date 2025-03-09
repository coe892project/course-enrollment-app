# course-enrollment-app Backend

## Running the Backend Locally

1. Create a virtual environment (venv).
    ```shell
    py -3 -m venv .venv
    .venv/Scripts/activate
    ```
2. Install all required packages.
    ```shell
    pip install -r requirements.txt
    ```
3. Run `fastapi` in `dev` mode.
    ```shell
    fastapi dev main.py
    ```