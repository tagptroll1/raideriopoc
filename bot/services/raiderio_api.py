from aiohttp import ClientSession
from bot.services.api_base import Api


class RaiderIOApi(Api):
    def __init__(self, http_session: ClientSession):
        super().__init__(http_session)
        self.base: str = "https://raider.io"

    async def get_character(self, region: str, realm: str, name: str):
        """Retrieve a raider.io profile through their API"""
        return await self.GET(
            f"{self.base}/api/v1/characters/profile"
            f"?region={region}"
            f"&realm={realm}"
            f"&name={name}"
            "&fields=mythic_plus_scores_by_season:current")

    def get_character_score(self, character, tag="all") -> int:
        if character.get("mythic_plus_scores_by_season"):
            season1 = character["mythic_plus_scores_by_season"][0]
            # only 1 season atm, find correct season here.

            scores = season1["scores"]

            # Return given tag
            return scores.get(tag)
