# didi

The easies dependency injector framework.

```python
import didi
from dataclasses import dataclass

@dataclass
class Settings:
    db_dsn: str
    api_base_url: str

class Db:
    def __init__(self, dsn: str):
        self.dsn = dsn

class Repo:
    def __init__(self, db: Db):
        self.db = db

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def close(self):
        pass

class Service:
    def __init__(self, repo: Repo, api: ApiClient):
        self.repo = repo
        self.api = api

class Composer(didi.Composer):
    settings: Settings = didi.Config()
    db = didi.Singleton(Db, dsn=settings.db_dsn)
    repo = didi.Factory(Repo, db=db)

    @didi.resource(base_url=settings.api_base_url)
    @staticmethod
    def api_client(base_url: str) -> ApiClient:
        client = ApiClient(base_url)
        yield client
        client.close()

    service = didi.Factory(Service, repo=repo, api=api_client)

composer = Composer()
composer.settings = Settings(db_dsn="http://db", api_base_url="http://api")
service = composer.service()
```
