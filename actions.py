import json
import os
from typing import Any, Text, Dict, List, Union
# import ast
from demjson import encode
import requests
from dotenv import load_dotenv
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

load_dotenv()

airtable_api_key = os.getenv("AIRTABLE_API_KEY")
base_id = os.getenv("BASE_ID")
table_name = os.getenv("TABLE_NAME")


from pprint import pprint
from airtable import Airtable

base_key = 'appzuL8U7K6TMDutQ'  # Insert the Base ID of your working base
table_name = 'Table_bot'  # Insert the name of the table in your working base
api_key = 'keyaWserXTjMqcwzl'  # Insert your API Key
# airtable = Airtable(base_key, table_name, api_key)
airtable = Airtable(base_id, table_name, airtable_api_key)


def create_health_log(confirm_exercise, exercise, sleep, diet, stress, goal):
    request_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    # request_url = f"https://api.airtable.com/v0/{base_id}/{table_name}?api_key={airtable_api_key}"
    responses = []
    headers = {
        "Authorization": f"Bearer {airtable_api_key}",
        "Content-Type": "application/json"
        # f"Authorization: Bearer {airtable_api_key}",
        # f"Content-Type: application/json"
        # "Accept": "application/json",
    }
    data = {"records": []}

    data_fields = {
        "fields": {
            "Exercised?": confirm_exercise,
            "Type of exercise": exercise,
            "Amount of sleep": sleep,
            "Stress": stress,
            "Diet": diet,
            "Goal": goal,
        }
    }

    data_fields = {
            "Exercised?": confirm_exercise,
            "Type of exercise": exercise,
            "Amount of sleep": sleep,
            "Stress": stress,
            "Diet": diet,
            "Goal": goal,
    }

    # data = {
    #     "fields": {
    #         "Exercised?": confirm_exercise,
    #         "Type of exercise": exercise,
    #         "Amount of sleep": sleep,
    #         "Stress": stress,
    #         "Diet": diet,
    #         "Goal": goal,
    #     }
    #
    data["records"].append(data_fields)
    # data = ast.literal_eval(data)
    data_json = encode(data)
    # headers = encode(headers)
    # data_json = json.dumps(data)
    print("header " + f'{headers}')


    try:
        response = requests.post(
            # request_url, headers=headers, data=json.dumps(data)
            request_url, headers=headers, json=data_json
        )

        # response.raise_for_status()

    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    responses.append(response)
    print("data: " + f'{data_json}')
    print("response status : " + f'{response.status_code}')
    print("response : " + f'{response}')
    return responses


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

        # response = create_health_log(
        #     confirm_exercise=confirm_exercise,
        #     exercise=exercise,
        #     sleep=sleep,
        #     stress=stress,
        #     diet=diet,
        #     goal=goal
        # )

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
