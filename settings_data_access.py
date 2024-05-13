source = "remote"

if source == "local":
    API_URL = "http://localhost:8000"
    TOKEN = "the-token-that-was-here-is-canceled"
    print("WARNING: getting data from the LOCAL database")
elif source == "remote":
    API_URL = "https://climrisk.org/edb1B"
    TOKEN = "the-token-that-was-here-is-canceled"
elif source == "file":
    pass
else:
    raise Exception("Source must be 'local', 'remote' or 'file")
