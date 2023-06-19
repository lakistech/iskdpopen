class BulbState:
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def __init__(self):
        self.state = {
            "status": "Nieznany",
            "message": "Z jakiegoś powodu nie możemy określić statusu otwarcia KDP",
            "latest_online_status": False,
            "latest_check_time": "Nigdy",
            "latest_update_time": "jakiegoś czasu",
            "latest_api_response": {},
            "admin_sessions": []
        }
    
    def set_state(self, state):
        for s in state.keys():
            self.state[s] = state[s]

    def insert_visitor(self, date, visitor_ip):
        return 0

    def get_todays_visitors(self):
        return len(self.visitors_today['visitors'])


class VisitCounter:
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def __init__(self):
        self.current_day = 0
        self.todays_visitors = []

    def insert_visitor(self, now_epoch_days, visitor_ip):
        if now_epoch_days == self.current_day:
            self.todays_visitors.add(visitor_ip)
        else:
            self.current_day = now_epoch_days
            self.todays_visitors = {visitor_ip}
        return 0
    
    def get_todays_visitors_count(self):
        return len(self.todays_visitors)
