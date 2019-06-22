import flask
import injector

import tapeworm.ext.telegram as telegram
import tapeworm.incoming as incoming


class TelegramClientModule(injector.Module):
    def configure(self, binder):
        binder.bind(telegram.TelegramService, to=self.create, scope=injector.singleton)

    @injector.inject
    def create(self, config: flask.Config) -> telegram.TelegramService:
        return telegram.TelegramService(config.get("TG_URL"))


class IncomingModule(injector.Module):
    def configure(self, binder):
        binder.bind(incoming.Incoming, to=self.create, scope=injector.singleton)

    @injector.inject
    def create(self, telegram_service: telegram.TelegramService) -> incoming.Incoming:
        return incoming.Incoming(telegram_service)
