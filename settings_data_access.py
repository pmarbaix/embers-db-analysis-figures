source = "local"

if source == "local":
    API_URL = "http://localhost:8000"
    TOKEN = "d4ec10cb9d197550b246bcc48760f8cd6b6d25e6"
    print("WARNING: getting data from the LOCAL database")
elif source == "remote":
    API_URL = "https://climrisk.org/edb1B"
    TOKEN = "d4ec10cb9d197550b246bcc48760f8cd6b6d25e6"
elif source == "file":
    pass
else:
    raise Exception("Source must be 'local', 'remote' or 'file")
