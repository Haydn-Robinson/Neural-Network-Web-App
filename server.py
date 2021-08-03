from neuralnetworkwebapp.persistence import init_manager

if __name__ == '__main__':

    MANAGER_HOST = '127.0.0.1'
    MANAGER_PORT= 22109
    MANAGER_AUTHKEY = b'aaabacadaa'

    init_manager(MANAGER_HOST, MANAGER_PORT, MANAGER_AUTHKEY)
