from .base_scenario_agent import BaseSenarioAgent

class HotelCheckInAgent(BaseSenarioAgent):
    def __init__(self):
        super().__init__()
        self.name = "Hotel Check-In Agent"

    def respond(self, input_text):
        return f'Hotel Check-In Agent Response: {input_text}'