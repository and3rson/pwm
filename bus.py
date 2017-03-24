class Bus(object):
    def __init__(self):
        self.listeners = {}

    def on(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    def off(self, event, callback):
        self.listeners[event].remove(callback)

    def fire(self, event, *args, **kwargs):
        for callback in self.listeners.get(event, []):
            callback(*args, **kwargs)


bus = Bus()
