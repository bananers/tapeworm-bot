import flask
import injector

from google.cloud import datastore

import tapeworm.ext.telegram as telegram
import tapeworm.incoming as incoming
import tapeworm.services as services
import tapeworm.model_link as model_link


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


class LinksClientModule(injector.Module):
    def configure(self, binder):
        binder.bind(model_link.Links, to=self.create, scope=injector.singleton)

    @injector.inject
    def create(self, ds: datastore.Client) -> model_link.Links:
        return model_link.Links(ds)


class TitleExtractorClientModule(injector.Module):
    def configure(self, binder):
        binder.bind(services.TitleExtractor, to=self.create, scope=injector.singleton)

    def create(self) -> services.TitleExtractor:
        return services.TitleExtractor()


class IncomingModule(injector.Module):
    def configure(self, binder):
        binder.bind(incoming.Incoming, to=self.create, scope=injector.singleton)

    @injector.inject
    def create(
        self,
        telegram_service: telegram.TelegramService,
        links: model_link.Links,
        extractor: services.TitleExtractor,
        config: flask.Config,
    ) -> incoming.Incoming:
        return incoming.Incoming(
            telegram_service, links, extractor, config.get("PROJECT_ID")
        )
