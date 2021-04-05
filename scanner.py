import socket
from threading import Thread
import queue
import time

class Scanner:
    def __init__(self, ip : str, max_port : int) -> None:
        
        self.ip = ip
        self.max_port = max_port
        self.ports_for_thread = 1000
        self.ranges_queue = queue.Queue()
        self.range_generator()
        for i in range(100):
            t = Thread(target=self.worker, args=(i,))
            t.start()
        
        #while True:
        #    e = self.ranges_queue.unfinished_tasks
        #    print("Задания, которые надо выбрать:", e)
    
    def range_generator(self):
        """Определяет диапазоны портов для каждого потока"""

        ports_ranges_list = []
        print(self.max_port)
        for offset in range(1,self.max_port // self.ports_for_thread+1):
            buffer = [(offset-1) * self.ports_for_thread, offset * self.ports_for_thread]
            ports_ranges_list.append(buffer)
        
        #Патчим первый диапазон
        ports_ranges_list[0][0] = 1
        #Патчим последний диапазон
        ports_ranges_list[-1][1] = self.max_port

        #Закидываем все элементы в очередь
        for item in ports_ranges_list:
            self.ranges_queue.put(item)
    
    def worker(self, number : int):
        while True:
            try:
                port_range = self.ranges_queue.get_nowait()
                print(f"Поток {number} взял диапазон {port_range}..")
                for port in range(*port_range):
                    sock = socket.socket()
                    try:
                        sock.connect((self.ip, port))
                        print(f"[Поток {number}] Порт {port} открыт")
                    except:
                        print(f"[Поток {number}] Порт {port} закрыт")
                        continue
                    finally:
                        sock.close()
                self.ranges_queue.task_done()
                print(f"Поток {number} завершил выполнение задания")
            except queue.Empty:
                print(f"Для потока {number} больше нет диапазонов")
                break

def main():
    n = 2**16 - 1
    ip_input = "127.0.0.1"
    scanner = Scanner(ip_input, n)

if __name__ == "__main__":
    main()