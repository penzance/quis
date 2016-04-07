# quis
A django-watchman dashboard

The problem we're trying to solve here is verifying that a number of different
django servers are up and running in a number of different environments (eg.
dev, qa, stage, prod).

## Screenshots

For a quick health check, quis defaults to having all environments show as
collapsed.  If all services in all django servers in that environment check
out, the environment shows green.  If any service on any server has an
error, the environment shows red.

![Defaults to collapsed](img/collapsed.png?raw=true "Defaults to collapsed")

Expanding an environment shows all servers within that environment, again
colored green/red for ok/error.  The servers show the checks for the services
backing them, but here, for readability's sake, we only show red on error.

![Everything ok in this environment](img/everything_ok.png?raw=true "Everything ok in this environment")

In case of error, or in some cases also on success, there are extra details that
may prove helpful.

![Failures and details](img/failures_and_details.png?raw=true "Failures and details")

## Configuration

In your `secure.py`, you'll need to put a `watchmen` key with the set of
environments and servers to pull from.

```python
SECURE_SETTINGS = {
    'watchmen': {
        'dev': {
            'rest-api': 'https://restapi.dev/watchman',
            'some-webapp': 'https://somewebapp.dev/watchman',
        },
        'qa': {
            'rest-api': 'https://restapi.qa/watchman',
            'some-webapp': 'https://somewebapp.qa/watchman',
            'another-webapp': 'https://another.webapp.qa/watchman',
        },
    },
}
```
