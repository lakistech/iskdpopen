import json
from os.path import exists
import os


class IsKDPOpenState:
    def _get_initial_state(self):
        return {
            "status": "Nieznany",
            "message": "Z jakiegoś powodu nie możemy określić statusu otwarcia KDP",
            "latest_online_status": False,
            "latest_check_time": "Nigdy",
            "latest_update_time": "jakiegoś czasu",
            "visitors_today": {"day": 0, "visitors": {}},
            "latest_api_response": {},
            "admin_sessions": [], 
            "crew_information": {}
        }

    # Read state from storage and return
    def _read_state(self):
        if not hasattr(self, "state"):
            self.state = self._get_initial_state()
        return self.state
    
    # Write to storage and that's it
    def _write_state(self, state):
        for s in state.keys():
            self.state[s] = state[s]

    def get_state(self):
        return self._read_state() # Sync fromm storage

    def set_state(self, state):
        return self._write_state(state)

class IsKDPOpenStateJSONFile(IsKDPOpenState):

    def _write_to_file(self, filepath, state):
        with open(filepath, "w+") as outfile:
            outfile.write(json.dumps(state, indent=4))

    def _read_from_file(self, filepath):
        with open(filepath) as json_file:
            return json.load(json_file)

    def __init__(self, filepath):
        if not exists(filepath):
            self._write_to_file(filepath, self._get_initial_state())
        
        if os.stat(filepath).st_size == 0:
            self._write_to_file(filepath, self._get_initial_state())

        self.filepath = filepath

    def _read_state(self):
        return self._read_from_file(self.filepath)
    
    def _write_state(self, new_state):
        state = self._read_state()

        for s in new_state.keys():
            state[s] = new_state[s]
        
        self._write_to_file(self.filepath, state)
        return True


#state = IsKDPOpenState()
state = IsKDPOpenStateJSONFile("./status.json")
