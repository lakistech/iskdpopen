import json
from os.path import exists


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

    # Read state from storage and override self.state
    def _read_state(self):
        if not hasattr(self, "state"):
            self.state = self._get_initial_state()
        return True
    
    # Write state entirely self.state ---> File / Storage
    def _write_state(self, state):
        for s in state.keys():
            self.state[s] = state[s]

    def get_state(self):
        return self.state

    def set_state(self, state):
        self._read_state()
        return self._write_state(state)

    def __init__(self):
        self._read_state() # Initial read from driver
        return

class IsKDPOpenStateJSONFile(IsKDPOpenState):

    def _write_to_file(self, state):
        with open(self.filepath, "w+") as outfile:
            outfile.write(json.dumps(state, indent=4))

    def _read_from_file(self):
        with open(self.filepath) as json_file:
            return json.load(json_file)

    def __init__(self, filepath):
        self.filepath = filepath
        self.changed = True

        if not exists(filepath):
            self._write_to_file({})

        super().__init__()

    def _read_state(self):        
        if self.changed:
            with open(self.filepath) as json_file:
                self.state = json.load(json_file)
            self.changed = False

        return self.state
    
    def _write_state(self, state):
        for s in state.keys():
            self.state[s] = state[s]
        
        self._write_to_file(self.state)
        with open(self.filepath, "w") as outfile:
            outfile.write(json.dumps(self.state, indent=4))
        
        self.changed = True
        return True


state = IsKDPOpenState()
#state = IsKDPOpenStateJSONFile("./status.json")
