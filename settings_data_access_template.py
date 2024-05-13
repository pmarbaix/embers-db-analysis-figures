source = "remote"

if source == "local":
    API_URL = "http://localhost:8000"
    TOKEN = "<personal-install-token>"
    print("WARNING: getting data from the LOCAL database")
elif source == "remote":
    API_URL = "https://climrisk.org/edb"
    TOKEN = "<your-token-on-climrisk-for-edb>"
elif source == "file":
    pass
else:
    raise Exception("Source must be 'local', 'remote' or 'file")
