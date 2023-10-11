import requests as re
import aiohttp

#* Base URL for ElevenLabs calls
ELEVEN_BASE_URL = 'https://api.elevenlabs.io'

#* Object for all API calls
class ElevenLabs:
    def __init__(self, _voice_name: str, _api_key: str) -> (None):
        self.api_key = _api_key
        request = re.get(url=ELEVEN_BASE_URL + '/v1/voices', headers={'XI-API-KEY':self.api_key})
        name_check = [d for d in request.json()['voices'] if d['name'] == _voice_name]
        if name_check:
            self.voice = name_check[0]

    async def get_user(self) -> (dict):
        """
        Obtain information of the user from ElevenLabs
        
        :param self (Self@ElevenLabs): Self reference to ElevenLabs object
        
        :param dict: Dictionary response from ElevenLabs
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(ELEVEN_BASE_URL + '/v1/user/subscription', headers={'XI-API-KEY': self.api_key}) as r:
                request = await r.json()
        return request

    async def generate(self, text: str, model: str='eleven_monolingual_v1', stability: float=0.5, 
                       similarity_boost: float=0.75, style: float=0, use_speaker_boost: bool=False) -> bytes:
        """
        Generates audio from ElevenLabs according to text

        :param text (str): Text to be converted to audio
        :param model (str, optional): ElevenLabs model to be used. Defaults to 'eleven_monolingual_v1'.
        :param stability (float, optional): Stability value for voice. Defaults to 0.5.
        :param similarity_boost (float, optional): Clarity value for voice. Defaults to 0.75.
        :param style (float, optional): Style value for voice. Defaults to 0.
        :param use_speaker_boost (bool, optional): Whether to use speaker boost or not. Defaults to False.

        :return bytes: Generated audio in bytes
        """
        body = {'text': text,
                'model_id': model,
                'voice_settings': {'stability': stability,
                                   'similarity_boost': similarity_boost,
                                   'style': style,
                                   'use_speaker_boost': use_speaker_boost
                                   }
                }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=ELEVEN_BASE_URL + '/v1/text-to-speech/' + self.voice['voice_id'] + '?optimize_streaming_latency=0',
                                    headers={'XI-API-KEY': self.api_key},
                                    json=body) as r:
                request = await r.read()
        return request