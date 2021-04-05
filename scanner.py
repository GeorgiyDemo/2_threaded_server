import socket
import threading
import queue
import time
import sys

socket.setdefaulttimeout(0.25)
que = queue.Queue()
results = []


class ProgressBar:
    """Класс визуализации прогресса сканирования"""

    def __init__(self, iterable: iter, size: int) -> None:
        self.iterable = iterable
        self.iter_len = len(self.iterable)
        self.output = sys.stdout
        self.size = size

    def display(self, j):
        x = int(self.size * j / self.iter_len)
        current_percent = round(j / self.iter_len * 100, 1)
        items_ready_str = "=" * x
        items_waiting_str = " " * (self.size - x)
        self.output.write(
            f"[{items_ready_str}{items_waiting_str}] {current_percent}/100%\r"
        )
        self.output.flush()

    def processing(self):
        self.display(0)
        for i, item in enumerate(self.iterable):
            yield item
            self.display(i + 1)
        self.output.write("\n")
        self.output.flush()


class Worker(threading.Thread):
    def __init__(self, number: int, ip: str) -> None:
        threading.Thread.__init__(self, name=f"t{number}")
        self.number = number
        self.ip = ip

    def run(self):
        global results
        while True:
            try:
                current_port = que.get_nowait()
                # print(f"Поток {self.number} взял порт {current_port}..")
                sock = socket.socket()
                try:
                    sock.connect((self.ip, current_port))
                    # print(f"Порт {current_port} открыт")
                    with threading.Lock():
                        results.append(current_port)
                except ConnectionRefusedError:
                    continue
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Какая-то новая ошибка: {e}")
                    continue

                finally:
                    sock.close()
                    que.task_done()

            # Елси больше нет заданий - гасим поток
            except queue.Empty:
                # print(f"Для потока {self.number} больше нет портов")
                break


class Scanner:
    def __init__(self, ip: str, max_port: int) -> None:

        self.time_begin = time.monotonic()
        self.ip = ip
        self.max_port = max_port
        self.result = []
        self.adder()

        for i in range(300):
            t = Worker(i, self.ip)
            t.start()

        progress_bar = ProgressBar(range(self.max_port + 1), 35)
        for i in progress_bar.processing():
            while (self.max_port - que.unfinished_tasks) < i:
                continue
        self.result_output()

    def adder(self):
        """Добавляет порты в очередь"""
        for port in range(1, self.max_port + 1):
            que.put(port)

    def result_output(self):
        time_result = round(time.monotonic() - self.time_begin, 2)
        results_str = "\n -> ".join(map(str, results))
        print(f"Заняло времени: {time_result} сек.")
        print(f"**Открытые порты**\n -> {results_str}")


def main():
    n = 2 ** 16 - 1
    ip_input = "127.0.0.1"
    scanner = Scanner(ip_input, n)


if __name__ == "__main__":
    main()
