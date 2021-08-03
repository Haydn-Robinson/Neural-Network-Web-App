from multiprocessing.managers import BaseManager, BaseProxy, DictProxy, NamespaceProxy
import types
from .api import TrainNetwork

class StateManager(BaseManager):
    pass

class TrainNetworkProxy(NamespaceProxy):

    _exposed_ = tuple(dir(TrainNetwork))

    def __getattr__(self, key):
        result = super().__getattr__(key)
        if isinstance(result, types.MethodType):
            def wrapper(*args, **kwargs):
                return self._callmethod(name, args, kwargs)
            return wrapper
        return result


shared_dict = {}
train_network_task = TrainNetwork()

def get_dict():
    return shared_dict

def get_train_network_task():
    return train_network_task

StateManager.register('TrainNetwork', get_train_network_task)


def init_manager(host, port, key):
    manager = StateManager(address=(host, port), authkey=key)
    server = manager.get_server()
    print(f'HOST: {host}\nPORT: {port}')
    server.serve_forever()


def get_manager(app):
    manager = StateManager(address=(app.config['MANAGER_HOST'], app.config['MANAGER_PORT']), authkey=app.config['MANAGER_AUTHKEY'])
    manager.register('TrainNetwork')
    manager.connect()
    return manager

