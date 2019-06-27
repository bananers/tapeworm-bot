import flask
import injector

from google.cloud import datastore

import tapeworm.ext.telegram as telegram
import tapeworm.incoming as incoming


class TelegramClientModule(injector.Module):
    def configure(self, binder):
        binder.bind(telegram.TelegramService, to=self.create, scope=injector.singleton)

    @injector.inject
    def create(self, config: flask.Config) -> telegram.TelegramService:
        return telegram.TelegramService(config.get("TG_URL"))


class DatastoreClientModule(injector.Module):
    def configure(self, binder):
        binder.bind(datastore.Client, to=self.create, scope=injector.singleton)

    @injector.inject
    def create(self, config: flask.Config) -> datastore.Client:
        return datastore.Client(config.get("PROJECT_ID"))


class IncomingModule(injector.Module):
    def configure(self, binder):
        binder.bind(incoming.Incoming, to=self.create, scope=injector.singleton)

    @injector.inject
    def create(
        self, telegram_service: telegram.TelegramService, database: datastore.Client
    ) -> incoming.Incoming:
        return incoming.Incoming(telegram_service, database)
