"""Gathers function that communicate with the api."""


def exec_api_call(api_call):
    """Exec an api call and check for errors and return its data field."""
    resp = None
    try:
        resp = api_call()
    except BaseException as e:
        err = "Error during request transfert: {}".format(str(e))
        return (None, err)
    if resp['code'] != 200 and resp['code'] != 201:
        err = "Invalid response: code: {} -> {}".format(resp['code'], resp['message'])
        return (None, err)
    return (resp['data'], None)
