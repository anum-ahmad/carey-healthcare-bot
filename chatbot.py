import spacy
from intents import intents 
from symptom_analysis import analyze_symptoms
from medication_info import get_medication_info
from health_tips import health_tips

class HealthcareChatbot:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def process_input(self, user_input):
        doc = self.nlp(user_input)
        intent = self.get_intent(user_input)
        if intent == 'greeting':
            return "Hello! I am Carey: The Get Well Bot and I am here to ensure you that All is Well!! How may I help you today?"
        elif intent == 'symptom_analysis':
            symptoms = extract_symptoms(doc)
            return analyze_symptoms(symptoms)
        elif intent == 'medication_info':
            return get_medication_info()
        elif intent == 'health_tips':
            return health_tips()
        else:
            return "I'm so sorry, I didn't understand. Can you please rephrase?"

    def get_intent(self, user_input):
        # Process user input using spaCy
        doc = self.nlp(user_input)

        # Check for each intent
        for intent, examples in intents.items():
            for example in examples:
                if example in user_input.lower():
                    return intent

        # Default intent if none of the specific intents are found
        return 'unknown'

# Example usage:
if __name__ == "__main__":
    chatbot = HealthcareChatbot()

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        response = chatbot.process_input(user_input)
        print("Carey:", response)
        
def extract_symptoms(doc):
    # Extract entities related to symptoms
    symptoms = [ent.text.lower() for ent in doc.ents if ent.label_ == 'SYMPTOM']
    return symptoms