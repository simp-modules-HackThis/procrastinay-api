class TokenBackend:
    def authenticate(self, request, token=None, username=None, password=None):
        print(token, username, password)
        return None
