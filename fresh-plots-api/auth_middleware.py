import falcon
import falcon.asgi
import httpx

class AuthMiddleware:
    async def process_request(self, req, resp):
        token = req.get_header('Authorization')

        challenges = ['Token type="Fernet"']
        return
        if token is None:
            if 'login' not in req.uri:
                description = ('Please provide an auth token '
                           'as part of the request.')

                raise falcon.HTTPUnauthorized(title='Auth token required',
                                          description=description,
                                          challenges=challenges,
                                          href='http://docs.example.com/auth')

        if not self._token_is_valid(token):
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized(title='Authentication required',
                                          description=description,
                                          challenges=challenges,
                                          href='http://docs.example.com/auth')

    def _token_is_valid(self, token):
        # we will integrate this with firebase/google sign in if time permits.
        return True  # Suuuuuure it's valid...
