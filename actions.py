import os
from typing import Any, Text, Dict, List, Union
from dotenv import load_dotenv
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from airtable import Airtable

load_dotenv()

airtable_api_key = os.getenv("AIRTABLE_API_KEY")
base_id = os.getenv("BASE_ID")
table_name = os.getenv("TABLE_NAME")

airtable = Airtable(base_id, table_name, airtable_api_key)


class HealthForm(FormAction):

    def name(self):
        return "health_form"

    @staticmethod
    def required_slots(tracker):

        if tracker.get_slot('confirm_exercise') == True:
            return ["confirm_exercise", "exercise", "sleep",
                    "diet", "stress", "goal"]
        else:
            return ["confirm_exercise", "sleep",
                    "diet", "stress", "goal"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "confirm_exercise": [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
                self.from_intent(intent="inform", value=True),
            ],
            "sleep": [
                self.from_entity(entity="sleep"),
                self.from_intent(intent="deny", value="None"),
            ],
            "diet": [
                self.from_text(intent="inform"),
                self.from_text(intent="affirm"),
                self.from_text(intent="deny"),
            ],
            "goal": [
                self.from_text(intent="inform"),
            ],
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:

        confirm_exercise = tracker.get_slot("confirm_exercise")
        exercise = tracker.get_slot("exercise")
        sleep = tracker.get_slot("sleep")
        stress = tracker.get_slot("stress")
        diet = tracker.get_slot("diet")
        goal = tracker.get_slot("goal")

        data_fields = {
            "Exercised?": confirm_exercise,
            "Type of exercise": exercise,
            "Amount of sleep": sleep,
            "Stress": stress,
            "Diet": diet,
            "Goal": goal,
        }

        airtable.insert(data_fields)

        dispatcher.utter_message("Thanks, your answers have been recorded!")
        return []
