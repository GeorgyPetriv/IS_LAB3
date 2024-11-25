import math
import random

from formatter import export_fortnight_to_csv, export_schedule_to_csv
from uni import Lesson

from const import SUBJECTS, ROOMS, TIMESLOTS, GROUPS, LECTURERS, PROGRAM, DAYS

POP_SIZE = 100
MUT_RATE = 0.25
GENERATIONS = 50


def generate_random_lesson():
    subject = random.choice(SUBJECTS)
    subject_name = subject.name
    lecturer = subject.get_random_teacher()
    group = random.choice(GROUPS)
    room = random.choice(ROOMS)
    day = random.choice(DAYS)
    timeslot = random.choice(TIMESLOTS)
    return Lesson(subject_name, lecturer, group, room, timeslot, day)


def generate_random_week():
    week = []

    for _ in range(28):
        lesson = generate_random_lesson()
        week.append(lesson)
    return week


def loss(gene, week_loss=False):
    penalty = 0

    # Жорсткі обмеження
    lecturer_times = {}
    group_times = {}
    room_times = {}
    lecturer_slots = {lecturer: [] for lecturer in LECTURERS}
    group_slots = {group: [] for group in GROUPS}

    for lesson in gene:
        # Викладач не може викладати в двох місцях одночасно
        if (lesson.lecturer, lesson.timeslot, lesson.day) in lecturer_times:
            return math.inf
        lecturer_times[(lesson.lecturer, lesson.timeslot, lesson.day)] = lesson.room

        # Група не може мати кілька занять одночасно
        if (lesson.group, lesson.timeslot, lesson.day) in group_times:
            return math.inf
        group_times[(lesson.group, lesson.timeslot, lesson.day)] = lesson.room

        # Аудиторія не може бути зайнята більше одного разу в один час
        if (lesson.room, lesson.timeslot, lesson.day) in room_times:
            return math.inf
        room_times[(lesson.room, lesson.timeslot, lesson.day)] = lesson.group

        lecturer_slots[lesson.lecturer].append(lesson.timeslot)
        group_slots[lesson.group].append(lesson.timeslot)

    # М'які обмеження
    # Зменшення "вікон" (чим менше вікон, тим краще)
    for slots in lecturer_slots.values():
        if len(slots) > 1:
            slots.sort()
            for i in range(len(slots) - 1):
                index1 = TIMESLOTS.index(slots[i])
                index2 = TIMESLOTS.index(slots[i + 1])
                window = index2 - index1
                penalty += window * 100

    for slots in group_slots.values():
        if len(slots) > 1:
            slots.sort()
            for i in range(len(slots) - 1):
                index1 = TIMESLOTS.index(slots[i])
                index2 = TIMESLOTS.index(slots[i + 1])
                window = index2 - index1
                penalty += window * 100

    # Заняття не може проводитися, якщо група більша за кількість місць в аудиторії.
    for lesson in gene:
        students_num = lesson.group.students_num
        room_capacity = lesson.room.capacity

        if students_num > room_capacity:
            penalty += (students_num - room_capacity) * 50

    # Кількість занятть має наближатися до кількості, що вказана у програмі
    schedule_programm = dict()
    for lesson in gene:
       if lesson.lecturer in schedule_programm.keys():
           schedule_programm[lesson.lecturer] += 1
       else:
           schedule_programm[lesson.lecturer] = 1

    for lecturer in schedule_programm.keys():
        if schedule_programm[lecturer] != PROGRAM[lecturer]:
            penalty += abs(schedule_programm[lecturer] - PROGRAM[lecturer])

    # Тижневі обмеження
    # Зменшення ассиметричності
    if week_loss:
        for _ in range(len(gene) // 2):
            if gene[_] != gene[_ + 50]:
                penalty += 2

    return penalty


def crossover(parent1, parent2):
    child1, child2 = parent1, parent2
    if random.random() < MUT_RATE:
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]

    return child1, child2


def mutate(gene):
    for i in range(len(gene)):
        if random.random() < MUT_RATE:
            gene[i] = generate_random_lesson()
    return gene


def genetic_algorithm(logging=False, week_loss=False):
    penalty = math.inf
    population = []
    #if week_loss:
    #    population = generate_schedule_population()
    #else:
    while penalty == math.inf:
        population = [generate_random_week() for _ in range(POP_SIZE)]
        penalty = min([loss(p, week_loss) for p in population])

    for generation in range(GENERATIONS):
        population.sort(key=lambda x: loss(x))
        parents = population[:2]

        penalty = math.inf
        new_population = []

        while penalty == math.inf:
            for _ in range(POP_SIZE // 2):
                child1, child2 = crossover(parents[0], parents[1])
                new_population.extend([mutate(child1), mutate(child2)])
            penalty = min([loss(p) for p in new_population])

        population = new_population
        population.sort(key=lambda x: loss(x))
        best_penalty = loss(population[0])
        if logging:
            print(f"Generation {generation + 1}, Best fitness: {best_penalty}")
        # if best_penalty == 0:
    population[0].sort(key=lambda x: x.timeslot)
    return population[0]



def generate_schedule(logging=True):
    best_schedule = genetic_algorithm(logging, week_loss=False)
    return best_schedule


print("Generating week 1")
best_schedule = generate_schedule()
export_schedule_to_csv(best_schedule)
