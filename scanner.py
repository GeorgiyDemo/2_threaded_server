import socket
from threading import Thread

N = 2**16 - 1

class Scanner:
    def __init__(self, ip) -> None:
        self.ip = ip
        self.processing()
    
    def processing(self):

        for port in range(1,N):
            sock = socket.socket()
            try:
                sock.connect((self.ip, port))
                print(f"Порт {port} открыт")
            except:
                print(f"Порт {port} закрыт")
                continue
            finally:
                sock.close()


def main():
    ip_input = "127.0.0.1"
    scanner = Scanner(ip_input)


if __name__ == "__main__":
    main()