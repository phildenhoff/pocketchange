# pocketchange

You'll need to install the requirements in `requirements.txt` with

```sh
python -m pip install -r requirements.txt
```

Then, fill in your Pocket Consumer token and Access Token. There is a bit of a
process to get both these values, which is not discussed here.

Fill in your Pushover token and user to send messages to (or remove it
altogether).

Customise the RSS feeds to be what you enjoy.

Now you should be able to run the script with `python pocketchange.py` and see
it automatically fetch any new articles (within the last day) and add them to
your Pocket account.
