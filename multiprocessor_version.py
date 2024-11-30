import multiprocessing
from collections import defaultdict
from time import time
from colorama import Fore, Style, init

file_paths = [
    "./file1.txt",
    "./file2.txt",
    "./file3.txt",
    "./file4.txt"
]


# Ініціалізуємо colorama
init(autoreset=True)


def search_keywords_in_file(filename, keywords):
    """Шукає ключові слова в конкретному файлі."""
    result = defaultdict(list)
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
            print(f"{Fore.CYAN}Читання файлу {filename}:\n{Fore.YELLOW}{text}\n")
            for word in keywords:
                if word.lower() in text.lower():
                    result[word].append(filename)
    except Exception as e:
        print(f"{Fore.RED}Помилка при читанні файлу {filename}: {e}")
    return result


def process_task(files, keywords, queue):
    """Завдання для окремого процесу."""
    local_result = defaultdict(list)
    for file in files:
        result = search_keywords_in_file(file, keywords)
        for k, v in result.items():
            local_result[k].extend(v)
    queue.put(local_result)


def multiprocessing_search(files, keywords):
    """Запускає багатопроцесорний пошук по файлах."""
    processes = []
    queue = multiprocessing.Queue()
    results = defaultdict(list)

    # Розділяємо файли між процесами
    num_processes = min(4, len(files))
    chunk_size = len(files) // num_processes if num_processes > 0 else 1

    for i in range(num_processes):
        start = i * chunk_size
        end = len(files) if i == num_processes - 1 else (i + 1) * chunk_size
        process = multiprocessing.Process(target=process_task, args=(files[start:end], keywords, queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    while not queue.empty():
        result = queue.get()
        for k, v in result.items():
            results[k].extend(v)

    return results


if __name__ == "__main__":
    keywords = ["error", "warning", "critical"]
    files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]

    print(f"{Fore.GREEN}Запускаємо багатопроцесорний пошук...\n")
    start_time = time()
    results = multiprocessing_search(files, keywords)
    end_time = time()

    print(f"{Fore.MAGENTA}Багатопроцесорний пошук завершено за {end_time - start_time:.2f} секунд.\n")
    print(f"{Style.BRIGHT}Результати пошуку:")
    for keyword, found_files in results.items():
        print(f"{Fore.BLUE}Ключове слово '{keyword}' знайдено у файлах: {Fore.YELLOW}{found_files}")
