import json
import os
import datetime
import random

from typing import Dict, Any, Tuple, List

class DataManager:
    
    def __init__(self):
        with open('log.txt', 'w') as f:
            f.write(f'Started bots at {datetime.now()}\n\n')
            
    
    def write_to_log(self, message: str):
        """Write a formatted message to the log file.

        Args:
            message (str): Formatted message to be logged.
        """
        with open('log.txt', 'a') as f:
            f.write(message)
    
    
    def reset_topics(self) -> (Dict[str, Dict[str, Any]]):
        """Resets all topics in the text_conversations JSON.
        
        Returns:
            topics (dict): Dictionary of all available conversation topics.
        """
        
        with open('data/text_conversations.json', "r") as f:
            topics = json.load(f)
            
        for k, v in topics["conversations"].items():
            for topic in v["topics"].keys():
                v["topics"][topic]["chosen"] = False
            topics["topics"][k] = v
            
        with open('data/text_conversations.json', 'w') as f:
            f.write(json.dumps(topics, indent=4))
        
        return topics["conversations"]
    
    
    def choose_topic(self, first_speaker: str) -> (Tuple(str, List[str])):
        """Chooses an available topic from the topic list randomly.
    
        Args:
            first_speaker (str): The first speaker in the conversation.
        
        Returns:
            topics (str): The chosen topic from the list
            other_speakers (List[str]): The other characters present in the conversation
        """
        
        with open('data/text_conversations.json', 'r') as f:
            topics = json.load(f)
        available_topics = {}
        
        for category, info in topics["conversations"].items():
            all_topics = [k for k, v in info["topics"].items() if v["chosen"] is False]
            if len(all_topics) != 0:
                available_topics[category] = {"weight": info["weight"],
                                                "topics": {}}
                for t in all_topics:
                    available_topics[category]["topics"][t] = info["topics"][t]
        
        if len(available_topics) == 0:
            available_topics = self.reset_topics()
        
        weights = {}
        
        for _, (k, v) in enumerate(available_topics.items()):
            weights[k] = v["weight"]
        
        chosen_key = random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]
        chosen_topic = random.choice(list(available_topics[chosen_key]["topics"].keys()))
        
        other_speakers = available_topics[chosen_key]["topics"][chosen_topic]["req_membs"]

        if first_speaker in other_speakers:
            other_speakers.remove(first_speaker)
        
        topics["conversations"][chosen_key]["topics"][chosen_topic]["chosen"] = True
        
        with open('data/text_conversations.json', 'w') as f:
            f.write(json.dumps(topics, indent=4))
        
        return chosen_topic, other_speakers
        