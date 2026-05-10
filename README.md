# Лабораторна робота: Regex FSM

## Звіт до роботи

**Мета:** Реалізувати скінченний автомат (Finite State Machine) для перевірки рядків за допомогою простих регулярних виразів.

**Що було зроблено:**
- Реалізовано ієрархію класів станів на основі абстрактного класу `State`
- Кожен тип символу регулярного виразу представлено окремим класом стану
- Реалізовано побудову графу станів з регулярного виразу
- Реалізовано перевірку рядка через рекурсивний обхід графу

---

## Пояснення імплементації

### Класи станів

| Клас | Призначення |
|------|-------------|
| `StartState` | Початковий стан автомату |
| `TerminationState` | Фінальний стан — рядок прийнято |
| `AsciiState` | Збігається з конкретним символом (літера або цифра) |
| `DotState` | Збігається з будь-яким символом (`.`) |
| `StarState` | Нуль або більше повторень попереднього символу (`*`) |
| `PlusState` | Одне або більше повторень попереднього символу (`+`) |

### Побудова графу (`RegexFSM.__init__`)

Регулярний вираз читається посимвольно. Кожен символ створює новий стан і додається до графу:

- Звичайний символ → новий `AsciiState`, прив'язується до попереднього стану
- `.` → новий `DotState`
- `*` → замінює попередній стан на `StarState` із self-петлею (повернення до себе)
- `+` → залишає попередній стан обов'язковим, додає `PlusState` із self-петлею після нього

### Перевірка рядка (`check_string`)

Використовується рекурсивний обхід графу (DFS) із мемоізацією через множину відвіданих пар `(стан, позиція)` — щоб уникнути нескінченних циклів.

Ключові правила переходів:
- `StarState` і `PlusState` можна пропустити без споживання символу (epsilon-перехід), якщо попередній обов'язковий символ вже був спожитий
- Self-петля дозволяє залишатись у `StarState`/`PlusState` і споживати наступний символ
- Рядок прийнято, якщо після споживання всіх символів досягнуто `TerminationState`

---

## Інструкції до запуску

**Вимоги:** Python 3.10 або новіший. Сторонніх бібліотек не потрібно.

**Запуск:**

```bash
python назва_файлу.py
```

**Використання у власному коді:**

```python
fsm = RegexFSM("a*4.+hi")
print(fsm.check_string("aaaaaa4uhi"))  # True
print(fsm.check_string("meow"))        # False
```

---

## Приклади запусків

### Вміст `__main__` блоку

```python
regex_pattern = "a*4.+hi"
regex_compiled = RegexFSM(regex_pattern)
print(regex_compiled.check_string("aaaaaa4uhi"))  # True
print(regex_compiled.check_string("4uhi"))        # True
print(regex_compiled.check_string("meow"))        # False

fsm = RegexFSM("a*b")
print(fsm.check_string("b"))      # True
print(fsm.check_string("aaab"))   # True
print(fsm.check_string("c"))      # False

fsm = RegexFSM("a+b")
print(fsm.check_string("ab"))     # True
print(fsm.check_string("aaab"))   # True
print(fsm.check_string("b"))      # False

fsm = RegexFSM("a.c")
print(fsm.check_string("abc"))    # True
print(fsm.check_string("a1c"))    # True
print(fsm.check_string("ac"))     # False

fsm = RegexFSM("ab*c")
print(fsm.check_string("ac"))     # True
print(fsm.check_string("abbc"))   # True
print(fsm.check_string("aXc"))    # False

fsm = RegexFSM("hello")
print(fsm.check_string("hello"))  # True
print(fsm.check_string("hell"))   # False
print(fsm.check_string("helloo")) # False
```

### Результат у терміналі

```
PS C:\Users\Адміністратор\Desktop\python> python tree.py
True
True
False
True
True
False
True
True
False
True
True
False
True
True
False
True
False
False
```

### Таблиця результатів

| Патерн    | Рядок        | Результат | Пояснення                            |
|-----------|--------------|-----------|--------------------------------------|
| `a*4.+hi` | `aaaaaa4uhi` | `True`    | Кілька `a`, потім `4`, символ, `hi` |
| `a*4.+hi` | `4uhi`       | `True`    | Нуль `a` — зірочка дозволяє         |
| `a*4.+hi` | `meow`       | `False`   | Немає `4` у рядку                   |
| `a*b`     | `b`          | `True`    | Нуль `a`, одразу `b`                |
| `a*b`     | `aaab`       | `True`    | Три `a`, потім `b`                  |
| `a*b`     | `c`          | `False`   | Немає `b` в кінці                   |
| `a+b`     | `ab`         | `True`    | Одне `a` — мінімум для `+`          |
| `a+b`     | `aaab`       | `True`    | Три `a`, потім `b`                  |
| `a+b`     | `b`          | `False`   | `+` вимагає хоча б одне `a`         |
| `a.c`     | `abc`        | `True`    | `b` збігається з `.`                |
| `a.c`     | `a1c`        | `True`    | `1` збігається з `.`                |
| `a.c`     | `ac`         | `False`   | `.` вимагає рівно один символ       |
| `ab*c`    | `ac`         | `True`    | Нуль `b` між `a` і `c`             |
| `ab*c`    | `abbc`       | `True`    | Два `b`                             |
| `ab*c`    | `aXc`        | `False`   | `X` не є `b`                        |
| `hello`   | `hello`      | `True`    | Точний збіг                         |
| `hello`   | `hell`       | `False`   | Рядок коротший за патерн            |
| `hello`   | `helloo`     | `False`   | Зайвий символ в кінці              |
