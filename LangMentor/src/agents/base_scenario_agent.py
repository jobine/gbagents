class BaseSenarioAgent:
    def __init__(self):
        self.name = 'Scenario Agent'
    
    def respond(self, input_text):
        raise NotImplementedError("This method should be overridden by subclasses.")