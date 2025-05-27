import os
import configparser

class ConfigHandler:
    host: str
    server_password: str
    port: int
    ssl: bool
    nickname: str
    username: str
    realname: str
    user_password: str

    def __init__(self, filename="config.cfg"):
        self.filename = filename
        self.config = configparser.RawConfigParser()  # disables % interpolation

        if not os.path.exists(self.filename):
            self._create_default_config()
        else:
            self._read_config()

        self._load_server_settings()
        self._validate_all()

    def _create_default_config(self):
        self.config['server'] = {
            'host': '',
            'server_password': '',
            'port': '6697',
            'ssl': 'True',
            'nickname': '',
            'username': '',
            'realname': '',
            'user_password': ''
        }
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)

    def _read_config(self):
        self.config.read(self.filename)

    def _load_server_settings(self):
        server = self.config['server']
        self.host = server.get('host', '').strip('"')
        self.server_password = server.get('server_password', '').strip('"')
        try:
            self.port = server.getint('port')
        except ValueError:
            raise ValueError("Port must be an integer")

        try:
            self.ssl = server.getboolean('ssl')
        except ValueError:
            raise ValueError("SSL must be a boolean (True/False)")

        self.nickname = server.get('nickname', '').strip('"')
        self.username = server.get('username', '').strip('"')
        self.realname = server.get('realname', '').strip('"')
        self.user_password = server.get('user_password', '').strip('"')

    def _validate_all(self):
        if not self.host:
            raise ValueError("Host must not be empty")
        if not self.nickname:
            raise ValueError("Nickname must not be empty")
        if not self.username:
            raise ValueError("Username must not be empty")
        if not self.realname:
            raise ValueError("Realname must not be empty")

    def update_setting(self, key, value):
        if key in self.config['server']:
            if key == 'port':
                if not isinstance(value, int):
                    raise ValueError("Port must be an integer")
            elif key == 'ssl':
                if not isinstance(value, bool):
                    raise ValueError("SSL must be a boolean")

            self.config['server'][key] = str(value)
            with open(self.filename, 'w') as configfile:
                self.config.write(configfile)
            self._load_server_settings()
            self._validate_all()
        else:
            raise KeyError(f"Invalid config key: {key}")

    def get_all_settings(self):
        return dict(self.config['server'])

