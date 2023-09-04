import requests as re
import json
import aiohttp


#* Base URL for ElevenLabs calls
ELEVEN_BASE_URL = 'https://api.elevenlabs.io'


#* Object for all API calls
class ElevenLabs:
    def __init__(self, _voice_name, _api_key):
        self.api_key = _api_key
        request = re.get(url=ELEVEN_BASE_URL + '/v1/voices', headers={'XI-API-KEY':self.api_key})
        name_check = [d for d in request.json()['voices'] if d['name'] == _voice_name]
        if name_check:
            self.voice = name_check[0]

    # Obtain user data from ElevenLabs
    async def get_user(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(ELEVEN_BASE_URL + '/v1/user/subscription', headers={'XI-API-KEY': self.api_key}) as r:
                request = await r.json()
        return request
    
    # Generate audio file from text
    async def generate(self, text, model='eleven_monolingual_v1', stability=0.5, similarity_boost=0.75, style=0, use_speaker_boost=False):
        body = {'text': text,
                'model_id': model,
                'voice_settings': {'stability': stability,
                                   'similarity_boost': similarity_boost,
                                   'style': style,
                                   'use_speaker_boost': use_speaker_boost
                                   }
                }
        print(body)
        async with aiohttp.ClientSession() as session:
            async with session.post(url=ELEVEN_BASE_URL + '/v1/text-to-speech/' + self.voice['voice_id'] + '?optimize_streaming_latency=0',
                                    headers={'XI-API-KEY': self.api_key},
                                    json=body) as r:
                print(await r.read())
                request = await r.read()
        return request