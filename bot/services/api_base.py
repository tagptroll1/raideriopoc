from aiohttp import ClientSession


class Api:
    def __init__(self, http_session: ClientSession):
        self.http_session: ClientSession = http_session

    async def GET(self, route, **headers):
        async with self.http_session.get(route, headers=headers) as resp:
            return await resp.json()
