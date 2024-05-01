# Testing

Gantry uses `pytest` to manage its testing suite. Make sure you have installed `pytest`, `pytest-aiohttp`, and `pytest-mock` in your environment.

The tests cover the collection and prediction functionalities, as well as core functionalities like helper functions and database actions.

Running all tests:

```
python -m pytest -s gantry
```

If you would like to see details about test coverage, install `coverage` and run:

```
coverage run -m pytest -s gantry && coverage html
```

This will create a folder in the top-level directory containing an `index.html` file which you can open in a browser.
