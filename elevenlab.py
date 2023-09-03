import requests as re
import json

ELEVEN_BASE_URL = 'https://api.elevenlabs.io'

class ElevenLabs:
    def __init__(self, _voice_name, _api_key):
        self.api_key = _api_key
        request = re.get(url=ELEVEN_BASE_URL + '/v1/voices', headers={'XI-API-KEY':self.api_key})
        name_check = [d for d in request.json()['voices'] if d['name'] == _voice_name]
        if name_check:
            self.voice = name_check[0]

    def get_credits(self):
        request = re.get(ELEVEN_BASE_URL + '/v1/user/subscription', headers={'XI-API-KEY': self.api_key})
        return request.json()
    
    def generate(self, text, model='eleven_monolingual_v1', stability=0.5, similarity_boost=0.75, style=0, use_speaker_boost=False):
        body = {'text': text,
                'model_id': model,
                'voice_settings': {'stability': stability,
                                   'similarity_boost': similarity_boost,
                                   'style': style,
                                   'use_speaker_boost': use_speaker_boost
                                   }
                }
        request = re.post(url=ELEVEN_BASE_URL + '/v1/text-to-speech/' + self.voice['voice_id'] + '?optimize_streaming_latency=0',
                          headers={'XI-API-KEY': self.api_key},
                          data=json.dumps(body))
        return request.content