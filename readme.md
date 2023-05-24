## Install Python 3.10 (ideal)

### ✅ Running locally
1. create your vitual-env `python3 -m venv venv`
2. acitvate venv `source venv/bin/activate`
3. Install dependencies: `pip3 install -r requirements-dev.txt`
4. Run the app: `uvicorn app.main:app --reload --port 8000`
5. Open [localhost:8000](http://localhost:8000) in your browser.


<br />

## Setup pre-commit

This project uses [pre-commit](https://pre-commit.com/) to ensure that code standard checks pass locally before pushing to the remote project repo. [Follow](https://pre-commit.com/#installation) the installation instructions, then set up hooks with `pre-commit install`.

Make sure everything is working correctly by running

    pre-commit run --all

### Setup pre-commit as pre-push hook

To use `pre-push` hooks with pre-commit, run:

    pre-commit install --hook-type pre-push
