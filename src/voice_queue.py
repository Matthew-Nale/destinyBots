class VoiceQueue:
    # Constructor  for the class
    def __init__(self):
        self.queue = []
        self.max_queue = 10
    
    # Add voice clip to queue
    async def add_request(self, request):
        if len(self.queue) == self.max_queue:
            return
        if request not in self.queue:
            self.queue.append(request)
    
    # Get oldest voice clip from queue and remove it
    async def pop_queue(self):
        if len(self.queue) == 0:
            return {'Error': 'No staged voice clips in Queue'}
        return self.queue.pop(0)
    