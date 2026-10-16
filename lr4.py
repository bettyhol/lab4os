import threading
import time


TOTAL_MODULES = 6
MAX_REPAIR_TEAMS = 2

# Semaphore:
# одночасно ремонтувати модулі можуть лише 2 інженери
repair_semaphore = threading.Semaphore(MAX_REPAIR_TEAMS)

# Mutex:
# захищає спільну змінну energy
energy_mutex = threading.Lock()

# Condition:
# використовується для повідомлення контролеру
# про завершення ремонту модулів
condition = threading.Condition()

repaired_modules = []
energy = 100


def repair_module(module_id):
    global energy

    thread_name = threading.current_thread().name

    print(
        f"[{thread_name}] Модуль {module_id}: "
        "очікує вільне ремонтне місце..."
    )

    # SEMAPHORE
    with repair_semaphore:
        print(
            f"[{thread_name}] Модуль {module_id}: "
            "початок ремонту."
        )

        # Імітація ремонту
        time.sleep(0.4 + (module_id % 3) * 0.2)

        # MUTEX
        # Тільки один потік може змінювати energy
        with energy_mutex:
            old_energy = energy
            energy -= 10

            print(
                f"[{thread_name}] Mutex: "
                f"енергія {old_energy}% -> {energy}%."
            )

        # CONDITION
        with condition:
            repaired_modules.append(module_id)

            print(
                f"[{thread_name}] Модуль {module_id}: "
                f"відремонтовано "
                f"({len(repaired_modules)}/{TOTAL_MODULES})."
            )

            # Повідомляємо контролеру,
            # що стан системи змінився
            condition.notify_all()

        print(
            f"[{thread_name}] Semaphore: "
            "ремонтне місце звільнено."
        )


def launch_controller():
    print(
        "[CONTROL] Condition: "
        "очікування завершення всіх ремонтів..."
    )

    with condition:

        # while потрібен, оскільки після notify
        # необхідно повторно перевірити умову
        while len(repaired_modules) < TOTAL_MODULES:

            # Потік контролера засинає
            condition.wait()

            print(
                "[CONTROL] Condition: отримано сигнал. "
                f"Готово "
                f"{len(repaired_modules)}/{TOTAL_MODULES}."
            )

    print(
        "[CONTROL] Усі модулі справні. "
        "Корабель готовий до запуску!"
    )


# Окремий потік-контролер
controller = threading.Thread(
    target=launch_controller,
    name="Контролер"
)

controller.start()


# Створення потоків-інженерів
threads = []

for module_id in range(1, TOTAL_MODULES + 1):

    thread = threading.Thread(
        target=repair_module,
        args=(module_id,),
        name=f"Інженер-{module_id}"
    )

    threads.append(thread)
    thread.start()


# Очікуємо завершення всіх потоків
for thread in threads:
    thread.join()

controller.join()


print("\n=== РЕЗУЛЬТАТ ===")
print("Відремонтовані модулі:", repaired_modules)
print("Залишок енергії:", energy, "%")