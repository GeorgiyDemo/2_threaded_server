import socket
import threading
import queue
import time

socket.setdefaulttimeout(0.25)
que = queue.Queue()
results = []

class Worker(threading.Thread):

    def __init__(self, number : int, ip : str) -> None:
        threading.Thread.__init__(self, name=f"t{number}")
        self.number = number
        self.ip = ip

    def run(self):
        global results
        while True:
            try:
                current_port = que.get_nowait()
                #print(f"Поток {self.number} взял порт {current_port}..")
                sock = socket.socket()
                try:
                    sock.connect((self.ip, current_port))
                    print(f"Порт {current_port} открыт")
                    with threading.Lock():
                        results.append(str(current_port))
                except Exception as e:
                    continue
                finally:
                    sock.close()
                    que.task_done()

            #Елси больше нет заданий - гасим поток
            except queue.Empty:
                #print(f"Для потока {self.number} больше нет портов")
                break

class Scanner:
    def __init__(self, ip : str, max_port : int) -> None:
        
        self.ip = ip
        self.max_port = max_port
        self.result = []
        self.range_generator()
        for i in range(300):
            t = Worker(i, self.ip)
            t.start()
        
        while True:
            counter = que.unfinished_tasks
            if counter == 0:
                break
            print(f"Осталось {counter} заданий..")
            time.sleep(5)

            

        self.result_output()
    
    def range_generator(self):
        """Определяет диапазоны портов для каждого потока"""
        for port in range(1,self.max_port+1):
            que.put(port)
    
    def result_output(self):
        print(results)

def main():
    n = 2**16 - 1
    ip_input = "127.0.0.1"
    scanner = Scanner(ip_input, n)

if __name__ == "__main__":
    main()