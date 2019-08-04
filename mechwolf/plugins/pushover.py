from typing import Callable

from loguru import logger


def generate_sink(token: str, user: str) -> Callable:
    """Programm
    """
    import requests

    def sink(message):
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data=dict(
                token=token,
                user=user,
                message=message.record["level"].icon + ": " + message.record["message"],
                title="MechWolf ⚙️🐺",
            ),
        )

    return sink


def pushover(token: str, user: str, level: str):
    """Bind [Pushover](https://pushover.net) notifications to the MechWolf logger.

    Pushover is an online service that takes care of most of the complexity of sending push notifications to mobile devices.
    This function handles the API calls and logger configuration: all you neded to do is set up your Pushover account and download the app.
    At the time of this writing, the app is a one-time $5 purchase.


    To set up an account, you will require a token and a user key.
    Please see [this guide](https://pushover.net/api) for more information.

    Arguments:
    - `token`: Your Pushover token.
    - `user`: The user key for your account.
    - `level`: The logging level. See `Protocol.execute` for the valid level strings.

    Example:
    ```python
    import mechwolf as mw
    mw.plugins.pushover(YOUR_TOKEN, YOUR_USER_KEY, "info")
    ```
    """

    logger.add(generate_sink(token=token, user=user), level=level.upper(), enqueue=True)
