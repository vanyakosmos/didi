from dataclasses import dataclass

import didi


def test_config_singleton():
    @dataclass
    class Settings:
        db_dsn: str
        api_base_url: str

    class Db:
        def __init__(self, dsn: str):
            self.dsn = dsn

    class Composer(didi.Composer):
        settings: Settings = didi.Config()
        db = didi.Singleton(Db, dsn=settings.db_dsn)

    composer = Composer()
    composer.settings = Settings(db_dsn="http://db", api_base_url="http://api")
    db = composer.db()
    assert composer.settings.db_dsn == "http://db"
    assert composer.settings.api_base_url == "http://api"
    assert db.dsn == "http://db"


def test_singleton_factory():
    class Db:
        def __init__(self, dsn: str):
            self.dsn = dsn

    class Repo:
        def __init__(self, db: Db):
            self.db = db

    class Composer(didi.Composer):
        db = didi.Singleton(Db, dsn="http://db")
        repo = didi.Factory(Repo, db=db)

    composer = Composer()
    db = composer.db()
    repo = composer.repo()
    assert db.dsn == "http://db"
    assert repo.db.dsn == "http://db"


def test_factory_resource():
    class ApiClient:
        def __init__(self, base_url: str):
            self.base_url = base_url

        def close(self):
            pass

    class Service:
        def __init__(self, api: ApiClient):
            self.api = api

    class Composer(didi.Composer):
        @didi.resource
        def api_client(self) -> ApiClient:
            client = ApiClient(base_url="http://api")
            yield client
            client.close()

        service = didi.Factory(Service, api=api_client)

    composer = Composer()
    api_client = composer.api_client()
    service = composer.service()
    assert api_client.base_url == "http://api"
    assert service.api.base_url == "http://api"


def test_combo():
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

        @didi.resource
        def api_client(self) -> ApiClient:
            client = ApiClient(self.settings.api_base_url)
            yield client
            client.close()

        service = didi.Factory(Service, repo=repo, api=api_client)

    composer = Composer()
    composer.settings = Settings(db_dsn="http://db", api_base_url="http://api")
    db = composer.db()
    repo = composer.repo()
    api_client = composer.api_client()
    service = composer.service()
    assert db.dsn == repo.db.dsn == service.repo.db.dsn == "http://db"
    assert api_client.base_url == service.api.base_url == "http://api"
