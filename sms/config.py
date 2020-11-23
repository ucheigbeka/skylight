from kivy.storage.jsonstore import JsonStore

store = JsonStore('config.json')

# Default values
backend_config = {
    'protocol': 'http',
    'host': '127.0.0.1',
    'port': 1807
}


class Config:
    @staticmethod
    def get(section_key, key=None):
        if not store.exists(section_key):
            Config.restore_default(section_key)
        return store.get(section_key) if not key else store.get(section_key)[key]

    @staticmethod
    def put(section_key, values):
        if section_key == 'backend':
            backend_config_cpy = backend_config.copy()
            backend_config_cpy.update(values)
            store.put(section_key, **backend_config_cpy)

    @staticmethod
    def restore_default(section_key):
        if section_key == 'backend':
            store.put(section_key, **backend_config)
