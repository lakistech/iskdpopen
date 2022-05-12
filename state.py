
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
            "admin_sessions": [] # {"created_at": ..., "pic": }
        }

    def _read_state(self):        
        return self.state
    
    def _write_state(self, state):
        if not hasattr(self, "state"):
            self.state = {}
        
        for s in state.keys():
            self.state[s] = state[s]

    def get_state(self):
        state = self._read_state()

        if not state:
            state = self._get_initial_state()
            self._write_state(state)

        return state

    def set_state(self, state):
        return self._write_state(state)

    def __init__(self):
        self.set_state({})

class IsKDPOpenStateJSONFile(IsKDPOpenState):
    def __init__(self, filepath):
        super(IsKDPOpenStateJSONFile).__init__()
        self.filepath = filepath

    def _read_state(self):
        return self.state
    
    def _write_state(self, state):
        for s in state.keys():
            self.state[s] = state[s]


state = IsKDPOpenState()
