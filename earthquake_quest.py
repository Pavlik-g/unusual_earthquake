# -*- coding: utf8 -*- 

import os, re
from time import sleep
from sys import exit
'''
Пожалуйста, не меняйте данный код, если не умеете программировать.
Это может повлиять на его работоспособность.
Приложение написано под Windows
'''

program_version = "0.8"
quest_version = "8.0.1"


class Page(): #создается образ будущей страницы
    def __init__(self, number_page, text_page):
        #Номрер ответа и текст страницы. Должны быть уже полностью готовы, изменить их уже нельзя будет
        global all_variants
        self.text_page = text_page
        self.number_page = number_page
        all_variants = []
        #Страницы, имена которых записаны не в формате page_number, а в формате page_string, не сохраняются в историю посещений
        if type(self.number_page) == int:
            self.zapominanie()
    
    def otrisovka(self, new=True): #Отрисовываем страницу
        global nomer
        separation = "-" * barrier #разделительная черта
        if razrab: #если велючен режим разработчика
            separation += f"\n{self.number_page}" #рисуем номер страницы
        print(separation) #рисуем разделительную черту
        print(f"{self.text_page}\n") #выводим текст
        if new:
            nomer = 0 #будет перед ответом стоять

    def zapominanie(self):
        global global_pages, local_pages, back_pages
        global_pages[self.number_page] = "1" #сохранение в файл потом будет
        local_pages[self.number_page] = "1" #список локальных страниц
        back_pages.append(self.number_page) #локальная история посещений
        global number_page
        number_page = self.number_page


class Variant_otveta(): #создается новый вариант ответа
    def __init__(self, text_otveta, stranica,  *actions, normal_variant=True):
        self.text_otveta = text_otveta
        self.stranica = stranica
        self.actions = actions
        self.next_page = "page_" + str(self.stranica) #сохраняем название страницы, на которую нужно перейти при выборе
        if normal_variant:
            self.save_variant()

    def print_variant(self): #всё что нужно
        global nomer
        nomer += 1 #номер, который перед ответом стоит
        self.nomer_otv = nomer #сохраняем порядковый номер ответа внутри класса
        strelka = ""
        if razrab:
            strelka = f"  --> {self.stranica}" #Показывет на какую страницу попадаешь при нажатии этого ответа
        print(f"{self.nomer_otv}. {self.text_otveta}{strelka}") #выводим обработанный ответ
    
    def save_variant(self): #добавляет себя в список
        global all_variants
        all_variants.append(self) #добавление в список всех вариантов

    def choice(self, next_page = None): #Действия при выборе этого ответа
        if not next_page:
            #Можно изменить номер следующей страницы при выборе ответа
            #Требуется для правильной работы перехода на непредусмотренные страницы, например с помощью кода go
            next_page = self.next_page
        for action in self.actions:
            #выполняет все действия
            exec(action, globals())

        if clear_back_page:
            os.system("cls")

        if next_page == "page_back":
            next_page = f"page_{return_back()}"
        elif next_page == "page_1":
            #выход из рекурсии
            return
        globals()[next_page]() #Преобразует строку в вызов функции(не знаю как, но работает). Это по крайней мере лучше, чем exec() или eval()

#функции, которые срабатывают при выборе ответа__▼
def var_set(variable: str, value=0): #установка заначения переменной
    if type(value) == str:
        value = f"'{value}'"
    return f"{variable} = {value}"
def var_add(variable: str, value=1): #прибавление значения к переменной
    if type(value) == str:
        value = f"'{value}'"
    return f"{variable} += {value}"
#________________________________________________▲


class Full_page:
    #Классы до этого только присваивали значения переменных, тут же всё это вылезет наружу
    def __init__(self, now_page):
        global all_variants
        self.now_page = now_page
        self.all_variants = all_variants
        self.all_good = True
        #Отрисовка всего
        now_page.otrisovka()
        self.otrisovka_variantov()


    def otrisovka_variantov(self):
        for var in self.all_variants:
            var.print_variant()
    
    def vybor_otveta(self, user_pag = None):
        end = False
        while not end: #цикл прерывается, когда проверка на сочетаемость пройдена
            if self.all_good:
                self.user_pag = self.vvod_otveta()
            else:
                self.user_pag = int(user_pag)
            global all_variants, nomer
            transition = self.check_code(str(self.user_pag), r"\*") #проверка на звёздочку
            for var in all_variants: #перебираем все варианты в списке
                if var.nomer_otv == self.user_pag or transition: #Если ввод совпадает с еомером ответа илибудет происходить внеплановый переход
                    end = True
                    if transition: #Если переход
                        self.user_pag = self.clear(str(self.user_pag), r"\*") #убираем звёздочку
                        var.choice(f"page_{self.user_pag}") #запускаем выбор ответа с изменением страницы
                    else:
                        var.choice() #запускаем обычный выбор ответа
                    break

    def vvod_otveta(self, osob = False):
        user_pag = input("\n")
        if osob: #особый режим когда необычно изменяется значение переменных или при выюоре какого-нибудь ответа должно происходить что-то необычное
            self.all_good = False #довольно редко ипользуется
        else:
            self.all_good = True #если всё в штатном режиме, то всё хорошо
        user_pag = self.pererabotка_otveta(user_pag)
        if not self.all_good and user_pag != None:
            user_pag = str(user_pag)
        return user_pag

    def pererabotка_otveta(self, user_pag): #обрабатывает ввод пользователя
        try:
            if user_pag[0] == "*":
                user_pag = self.codes(user_pag)
                if self.check_code(user_pag, r"\*"): #При изменении номера следующей страницы
                    return user_pag
            user_pag = int(user_pag)
            if self.check_accord(user_pag): #проверяем сочетаемость ввода
                return user_pag
            raise Exception #создаёт ошибку
        except Warning:
            print("Чит код активирован")
        except Exception as exc:
            if user_pag == "exit":
                finish()
            print("Неправильный ввод. Попробуйте ещё раз")
            if razrab:
                print(exc)
    
    def check_accord(self, user_pag):
        global nomer
        if user_pag > 0 and user_pag <= nomer and user_pag % 1 == 0: #если число больше нуля и не больше количества вариантов ответа и целое
            return True
        return False
    
    def codes(self, user_pag):
        user_pag = user_pag.lstrip("*") #убираем звёздочку
        if self.check_code(user_pag, "print", "get"): #выводит любую переменную по названию
            code = self.clear(user_pag, "print", "get")
            if code == "now": #выводит номер текущей страницы
                #global number_page
                print(number_page)
                self.oshibka()
            elif code == "back":
                print(back_pages)
                self.oshibka()
            else:
                eval("print(" + code + ")")
                self.oshibka()
        elif self.check_code(user_pag, "set"): #изменение значения переменной во время игры.
            code = self.clear(user_pag, "set")
            #exec(f"global {code}")
            variable = eval(code)
            variable = input(f"Текущее значение переменной {code}: {variable}\nИзменить на ")
            if variable.lower() == "no":
                print("Отказ от переназначения переменной")
                self.oshibka()
            if re.match(r"^[\'\"].+[\'\"]$", variable):
                variable = variable.strip("\"", "\'")
                exec(f"{code} = str(\"{variable}\")", globals())
            else:
                try:
                    exec(f"{code} = float(\"{variable}\")", globals())
                except ValueError:
                    print("Ожидается число, но введена строка")
                    raise ValueError
            print(f"Значение переменной {code} после изменения: {eval(code)}")
            self.oshibka()
        elif self.check_code(user_pag, "back"):
            return f"*{return_back()}"
        elif self.check_code(user_pag, "go"): #преходит на любую страницу по номеру
            code = self.clear(user_pag, "go")
            return f"*{code}"
            #globals()[f"page_{code}"]()
        elif self.check_code(user_pag, "rep", "replay"): #replay
            self.now_page.otrisovka()
            self.otrisovka_variantov()
            self.oshibka()
            #globals()[f"page_{number_page}"]()
        elif self.check_code(user_pag, "dead","death"):
            return "*1"
            #globals()["page_1"]()
        elif self.check_code(user_pag, "random", "rand"): #random
            import random
            user_pag = random.randint(1, nomer)
            print(f"Выбран ответ {user_pag}")
        elif self.check_code(user_pag, "exit"):
            finish(save = False)
        elif self.check_code(user_pag, "razrab", "debug"): #режим разработчика
            global razrab
            if razrab == True:
                razrab = False
                print("Режим разработчика отключён")
            else:
                razrab = True
                print("Режим разработчика включён")
            self.oshibka()
        else:
            print("Чит-код не распознан")
        return user_pag

    def check_code(self, string, *codes: str):
        #Проверяет на наличие в начале строки string фразы code
        string = string.strip(" ")
        for code in codes:
            if re.match(r"^\s*" + code, string, flags=re.I):
                return True
        return False

    def clear(self, proposal, *words, whitespace=True):
        #убирает из proposal все words и пробелы
        for word in words:
            proposal = re.sub(word, "", proposal, flags=re.I)
        if whitespace:
            proposal = re.sub(r"\s", "", proposal)
        return proposal

    def oshibka(self, massage=None):
        if massage:
            print(massage)
        raise Warning

class Variable_is_incorrect:
    def er_directory(self):
        #global directory
        print(f"\n\n\nВозникла ошибка с чтением файлов. Возможно вы изменили название папки или файла с данными. Если вы так сделали, то программа должна была создать новые файлы. Если же вы ничего не делали, не удаляли, то очень странно, что такое произошло. В таком случае, скорее всего, Вы каким-то образом повредили файл, и теперь он не пригоден для чтения.\nЕсли вы уверены, что ничего такого не было, тогда напишите о проблеме на почту.\nТакая проблема впринципе не должна была возникнуть, ведь программа создаёт необходимые папки и файлы сама, если их нет вналичии\nСкажите мне, что вы сделали?! Мне действительно интересно!\n\n\n")
    def variable_incorrect(self, variable_name, variable_value, *need_variable):
        print("-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!")
        print("[variable is incorrect]\n[0] Возникла ошибка переменной.\n Возможно вы перешли на эту страницу неправильно или изменили значение переменой вручную. Дальнейшая работа квеста может быть неккоректной.")
        print(f"Необходимое значение переменной: {variable_name} должна быть {need_variable}")
        print(f"Текущее значение переменной: {variable_name} = {variable_value}")
    def do_not_destroy_files(self, file):
        print("\n\nНу вот что ты делаешь? Какой смысл?\nНу написал ты ерунду в файл, что тебе, от этого легче стало? Сомневаюсь.\nХотел проверить код на живучесть? Молодец! Не получилось.\nМожешь пробовать ещё и ещё, мне-то всё равно.\nНет, ты конечно молодец, так держать, но ищи лучше ошибки в квесте, не мучай интерпретатор\n\n")
        sleep(17)


def create_files(values=False): #Создаем недостающие файлы
    if not os.path.isdir(r"eafiles"):
        os.mkdir(r"eafiles")
    if not os.path.isfile(directory_global_pages):
        open(directory_global_pages, 'w', encoding='utf-8').close()
    if not os.path.isfile(directory_vaules) or values:
        if values:
            os.remove(directory_vaules)
            print("Пользовательские настройки были повреждены. Их ждёт перезапись к заводским")
        with open(directory_vaules, "w") as v:
            v.write('120\n') #barrier
            v.write('False\n') #clear_back_page
            v.write('0') #pol
        if values:
            print("\n\nЗапустите программу заново\n\n")
            sleep(10)
            finish(save=False)

def zapusk(quantity_pages):
    create_files() # ◄ создаем все файлы

    try:
        # Считываем список глобальных страниц и убираем пустые варианты_▼
        with open(directory_global_pages, "r") as gp:
            global_pages = [line.strip() for line in gp]
        while "" in global_pages:
            global_pages.remove("")
        #Список готов___________________________________________________▲

        #Считываем переменные_▼
        with open(directory_vaules, "r") as v:
            barrier = v.readline()

            clear_back_page = v.readline()
            clear_back_page = clear_back_page.strip("\n")
            if clear_back_page == "True":
                clear_back_page = True
            else:
                clear_back_page = False
            
            pol = v.readline()
            #Считали_________▲

        try:
            pol = int(float(pol))
            barrier = int(float(barrier))
        except ValueError:
            print("Ошибка")
            create_files(True)
    except Exception as er:
        print(er)
        sleep(5)
        directory_error = Variable_is_incorrect
        directory_error.er_directory(1)
        
    #Проверка на корректность сохранённых числовых данных_▼
    if barrier > 999 or barrier < 0:
        barrier = 120
    if pol > 0: pol = 10
    elif pol < 0: pol = -10
    #Теперь всё корректно_________________________________▲

    local_pages = ["0" for x in range (quantity_pages)]

    #Корректировка спика глобальных страниц_▼
    #Очень удобно, когда список был повреждён или количество страниц в квесте изменилось
    if len(global_pages) != quantity_pages:
        print(f"Количество страниц в файле не соответствует нужному. В файле: {len(global_pages)}, должно быть: {quantity_pages}")
        counter = 0
        while len(global_pages) < quantity_pages:
            global_pages.append("0")
            counter += 1
        while len(global_pages) > quantity_pages:
            global_pages.pop()
            counter += 1
        print(f"В файл было добавлено/удалено {counter} Страниц")
        if len(global_pages) == quantity_pages:
            print("Завершено успешно!")
        else:
            print("Завершено с ОШИБКОЙ!")
        sleep(1)
    #Список готов к работе_________________▲


    return global_pages, local_pages, clear_back_page, barrier, pol

def finish(exiting = True, save = True):
    #Завершение работы
    global global_pages, pol
    print("Подождите...")
    sleep(0.2)
    if save == True:
        with open(directory_global_pages, "w") as gp:
            for index in global_pages:
                gp.write(index + '\n')
        with open(directory_vaules, "w") as v:
            v.write(str(barrier)+'\n')
            v.write(str(clear_back_page)+'\n')
            v.write(str(pol))
        print("Данные сохранены")
    if exiting == True:
        sleep(0.4)
        print("Выход")
        sleep(0.4)
        exit()

def reset(values=False, folder=True):
    if folder:
        print("Процесс удаления данных...")
        os.popen('chcp 1251').read()
        cmd = os.popen(r"rd /s /q eafiles").read()
        print("Сброс произведён. Перезагрузите программу")
        print(cmd)
        finish(save=False)

def return_back():
    #Переход на предыдущую страницу
    global back_pages
    back_pages.pop()
    try:
        need_pag = back_pages.pop()
    except IndexError as exc:
        if razrab:
            print(exc)
        back_pages.append(number_page)
        return "1"
    else:
        return f"{need_pag}"


#пошли страницы, все вручную заполнял (а как ещё?)_▼

def page_settings_0():
    global variant_1, variant_2, variant_3, variant_4, variant_5, variant_6
    now_page = Page("settings_0", "Вы можете настроить некоторые аспекты игры")
    variant_1 = Variant_otveta("Разделительная черта", "settings_barrier")
    variant_2 = Variant_otveta("Отображение предыдущей страницы", "settings_cls")
    if pol != 0:
        variant_3 = Variant_otveta("Сменить пол", "settings_pol")
    variant_4 = Variant_otveta("Сброс", "settings_reset")
    variant_5 = Variant_otveta("Техническая информация", "settings_information")
    variant_6 = Variant_otveta("В главное меню", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_settings_barrier():
    global variant_1, variant_2, barrier
    now_page = Page("barrier", f"Измените длину чёрточки, разделяющей текущую страницу от предыдущей\nТекущая длинна черты: {barrier}")
    now_page.otrisovka()
    try:
        vvod = int(input("Введите целое число в консоль   "))
        if vvod >= 0 and vvod <= 1000:
            barrier = vvod
            print(f"Изменено на {barrier}")
        else:
            print("Некорректное число")
    except ValueError:
        print("Боюсь, что это не число.")
    page_settings_0()
def page_settings_cls():
    global variant_1, variant_2, clear_back_page
    if clear_back_page:
        mode = ""
    else:
        mode = "НЕ "
    now_page = Page("settings_cls", f"Здесь можно включить или отключить отображение предыдущей страницы.\nТеперь она будет стираться, и на её место придет новая, чистая страница\nСейчас предыдущая страница {mode}стирается\nВнимание: функция экспериментальная. Вы можете не увидеть важные сообщения из за очистки консоли.")
    if clear_back_page:
        variant_1 = Variant_otveta("Выключить", "settings_cls", var_set("clear_back_page", False))
    else:
        variant_2 = Variant_otveta("Включить", "settings_cls", var_set("clear_back_page", True))
    variant_2 = Variant_otveta("[Назад]", "settings_0")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_settings_pol():
    global variant_1, variant_2, variant_3, pol
    if pol >= 0:
        mode = "Мужской"
    else:
        mode = "Женский"
    now_page = Page("settings_pol", f"Здесь вы можете изменить пол вашего персонажа\nТекущий пол: {mode}")
    if pol >= 0:
        variant_1 = Variant_otveta("Сменить пол на женский", "settings_pol", var_set("pol", -10))
    else:
        variant_2 = Variant_otveta("Сменить пол на мужской", "settings_pol", var_set("pol", 10))
    variant_3 = Variant_otveta("[Назад]", "settings_0")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_settings_reset():
    global variant_1, variant_2
    now_page = Page("settings_reset", "Вы можете сбросить всю свою историю посещений, достижения и концовки.\nХотите ли вы это сделать? Вот в чём вопрос...")
    variant_1 = Variant_otveta("Хочу", "settings_reset_sure")
    variant_2 = Variant_otveta("Ни за что!", "settings_0")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_settings_reset_sure():
    global variant_1, variant_2
    now_page = Page("settings_reset_sure", "Будут удалены пользовательские настройки и все достижения.\nПосле удаления данных программа будет отключена.\nПри следующем запуске будут заного созданы нужные папки и файлы.\nДанное действие нельзя будет отменить. Вы уверены?\nЕсли да, то введите 'yes'")
    now_page.otrisovka()
    vvod = input()
    if vvod == "yes":
        print("Начинаем сброс")
        reset()
        finish(save=False)
    else:
        print("Отмена")
        page_settings_0()
def page_settings_information():
    global variant_1, variant_2
    now_page = Page("settings_information", f"Здесь находится основная техническая информация\nВерсия квеста: {quest_version}\nВерсия программы: {program_version}\nНазвание квеста: \"Необычное землятресение\"\nКоличество страниц в квесте: {quantity_pages}\nПочта для обратной связи: koelibotonibud@gmail.com \nСсылка на GitHub: None")
    variant_1 = Variant_otveta("[Назад]", "settings_0")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()

def page_0():
    global variant_1, variant_2 #Вынужденная мера. Я ничего лучше не придумал, чем сделать варианты глобальными
    now_page = Page(0, "Здравствуй. Мне кажется, что вы запустили этот код первый раз. Позвольте дать вам несколько инструкций\n\n\t\tОБЯЗАТЕЛЬНО К ПРОЧТЕНИЮ!\nЗакрыть программу можно в любой момент, написав в поле ввода команду \"exit\". Не рекомендую использовать прерывание с клавиатуры.\nДля выбора ответа введите номер этого ответа без пробелов и точек (номер ответа указывается перед самим вариантом ответа).\n\n\t\tНЕОБЯЗАТЕЛЬНО К ПРОЧТЕНИЮ\nДля отделения страниц используется длинная черта. Если она вылазит на вторую строчку, можете изменить её длинну во вкладке настроек.\nВ начале страницы пишется информационный текст.\nПри удалении или повреждении файлов игры, при следующем запуске они либо ваосстановятся, либо вернутся к изначальным настройккам\nЕсли вы закроете программу посреди игры, то продолжить уже не сможете(только с начала).\nПри возникновении ошибок пишите разработчику.\nПри следующем запуске это окно показываться не будет(если будет, то плохо).\n\tПриятной игры!")
    variant_1 = Variant_otveta("Понятно, дальше", 1)
    variant_2 = Variant_otveta("Ничего не понятно", 0)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_1():
    global variant_1, variant_2, variant_3, variant_4, variant_5, variant_6, local_pages, global_pages, clear_back_page, barrier, pol
    global edavoda, z, zz, casha, camen, ray, ooo, live, surok_canyon, dog
    edavoda, z, zz, casha, camen, ray, ooo, live, surok_canyon, dog = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    finish(exiting = False)
    global_pages, local_pages, clear_back_page, barrier, pol = zapusk(361)
    now_page = Page(1, f"\t\t\t\tНЕОБЫЧНОЕ ЗЕМЛЯТРЕСЕНИЕ\n\tПрочитано на {round(global_pages.count(str(1)) / len(global_pages) * 100, 1)}%\n\tАвтор: Кое-кто\n\nВы - совершенно обычный человек, живущий в элитном районе Подмосковья. Но в один прекрасный момент Ваша жизнь переменилась.\nЗдесь может произойти всё что угодно. От волшебного лифта до летающего коня. И не пытайтесь пройти квест обычным образом, потому что весь смысл в том, чтобы открыть как можно больше интересных концовок.")
    if global_pages[280] != "1" or pol == 0:
        variant_1 = Variant_otveta("Начать", 280)
    else:
        variant_2 = Variant_otveta("Начать", 56)
    variant_3 = Variant_otveta("Контрольные точки", 119)
    variant_4 = Variant_otveta("Концовки", 107)
    variant_5 = Variant_otveta("От автора", 225)
    variant_6 = Variant_otveta("Настройки", "settings_0")
    full_now_page = Full_page(now_page)
    print("Для выхода введите exit")
    full_now_page.vybor_otveta()
def page_2():
    global variant_1
    now_page = Page(2, "Вы продолжаете спать. Минут через 15 Вы снова просыпаетесь, но на этот раз от того, что дом ходит ходуном.")
    variant_1 = Variant_otveta("Вскочить с кровати!", 4)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_3():
    global variant_1, variant_2, variant_3
    now_page = Page(3, "Вы встали, умылись и оделись. Что дальше?")
    variant_1 = Variant_otveta("Взять телефон", 7)
    variant_2 = Variant_otveta("Лечь на кровать", 14)
    variant_3 = Variant_otveta("Включить радио", 13)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_4():
    global variant_1, variant_2, variant_3
    now_page = Page(4, "Как только вы встали, на кровать обрушился кусок потолка. Началось землетрясение!")
    variant_1 = Variant_otveta("Выскочить из квартиры", 6)
    variant_2 = Variant_otveta("Взять всё необходимое и выскочить из квартиры", 6)
    variant_3 = Variant_otveta("Выпрыгнуть в окно", 88)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_5():
    global variant_1, variant_2
    now_page = Page(5, "Каким способом будем подниматься?")
    variant_1 = Variant_otveta("На лифте", 9)
    variant_2 = Variant_otveta("По лестнице", 12)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_6():
    global variant_1, variant_2
    now_page = Page(6, "Вы оказываетесь на лестничной площадке")
    variant_1 = Variant_otveta("Подняться наверх", 5)
    variant_2 = Variant_otveta("Спуститься вниз", 8)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_7():
    global variant_1, variant_2, variant_3
    now_page = Page(7, "Ого! ^У вас 84 с половиной пропущенных вызовов^!")
    variant_1 = Variant_otveta("Поиграть в энгри бёрдс", 14)
    variant_2 = Variant_otveta("Включить радио", 13)
    variant_3 = Variant_otveta("Перезвонить", 15)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_8():
    global variant_1, variant_2
    now_page = Page(5, "Каким способом будем спускаться?")
    variant_1 = Variant_otveta("На лифте", 9)
    variant_2 = Variant_otveta("По лестнице", 10)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_9():
    global variant_1, variant_2
    now_page = Page(9, "Похоже это была плохая идея. В лифте отключился свет и Вы полетели вниз со скоростью свободного падения.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    variant_2 = Variant_otveta("Попытаться выжить", 11)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_10():
    global variant_1
    now_page = Page(10, "Вы быстро побежали по лестнице и мигом оказались на первом этаже. Дом еще раз тряхануло, но вы уже были внизу.")
    variant_1 = Variant_otveta("Выйти на улицу", 16)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_11():
    global variant_1, variant_2
    now_page = Page(11, "Ну что ж,  попробуй")
    variant_1 = Variant_otveta("Жизнь", 27)
    variant_2 = Variant_otveta("Смерть", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_12():
    global variant_1
    now_page = Page(12, "Как только вы начали подниматься, дом ещё раз тряхануло и Вы полетели вниз.\nК счастью вы ничего не сломали, а вот лестница обрушилась.")
    variant_1 = Variant_otveta("Спуститься вниз", 8)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_13():
    global variant_1, variant_2
    now_page = Page(13, "Вы включаете радио. Идут новости. В срочном сообщении объявили, что в сторону Москвы и области надвигается землетрясение!")
    variant_1 = Variant_otveta("\"Мало ли что они там выдумали\" [лечь на кровать]", 14)
    variant_2 = Variant_otveta("Выбежать из квартиры", 6)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_14():
    global variant_1, variant_2
    now_page = Page(14, "Вы удобно устроились на кровати. Вдруг весь дом тряхануло, и вам на голову упал кусок потолка. Вы умерли, зато приятно провели время.\n(Слушайте умных людей)\n\nВы открыли концовку \"Беспечный\"")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_15():
    global variant_1, variant_2, pol
    text = "Вы перезвонили. На другом конце взяли трубку.\"Дорог"
    if pol < 0:
        text += "ая"
    elif pol >= 0:
        text += "ой"
    text += ", слава Богу ты жив"
    if pol < 0:
        text += "а"
    text += ". У вас скоро случиться землятресение! Немедленно уходи из дома!\""
    now_page = Page(15, text)
    variant_1 = Variant_otveta("\"Да брось, мама\"", 14)
    variant_2 = Variant_otveta("\"ОК, уже бегу\"", 6)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_16():
    global variant_1, variant_2
    now_page = Page(16, "Вокруг творится нечто ужасное. Земля ходит ходуном, вокруг бегают испуганные люди, туда-сюда ездят кареты \"Скорой помощи\" и \"МЧС\"")
    variant_1 = Variant_otveta("Присоедениться ко всеобщей панике", 17)
    variant_2 = Variant_otveta("Попросить, чтобы вас забрали в больницу", 18)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_17():
    global variant_1, variant_2
    now_page = Page(17, "Вы начали бегать как угорелый. Полиция начала собирать людей в кучки и успокаивать.")
    variant_1 = Variant_otveta("Собраться в кучку и успокоиться", 19)
    variant_2 = Variant_otveta("Не успокаиваться и сбежать", 20)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_18():
    global variant_1, variant_2
    now_page = Page(18, "Вам сказали, что бы вы убирались от сюда, а то заберут в психушку")
    variant_1 = Variant_otveta("Присоединиться ко всеобщей панике", 17)
    variant_2 = Variant_otveta("Дальше донимать врачей", 21)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_19():
    global variant_1, variant_2
    now_page = Page(19, "Полиция куда-то повела всех людей")
    variant_1 = Variant_otveta("Пойти со всеми", 25)
    variant_2 = Variant_otveta("Сбежать", 20)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_20():
    global variant_1, variant_2
    now_page = Page(20, "Вас поймала полиция")
    variant_1 = Variant_otveta("Подраться", 21)
    variant_2 = Variant_otveta("Успокоиться", 22)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_21():
    global variant_1, variant_2, local_pages
    now_page = Page(21, "Вас передали \"Скорой помощи\" и увезли в психушку")
    if local_pages[39] != "1":
        variant_1 = Variant_otveta("Смириться с судьбой", 23)
    variant_2 = Variant_otveta("Попытаться сбежать", 24)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_22():
    global variant_1, variant_2
    now_page = Page(22, "Вы успокоились и пошли вместе со всеми")
    variant_1 = Variant_otveta("Снова всбеситься и сбежать", 21)
    variant_2 = Variant_otveta("Продолжать идти", 25)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_23():
    global variant_1, variant_2
    now_page = Page(23, "Вы смирились с судьбой и сели на койку. Через три минуты психушка затряслась и обрушилась. Вы погибли под завалами.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    variant_2 = Variant_otveta("Попытаться выжить", 35)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_24():
    now_page = Page(24, "К вам навстречу вышел пациент и сказал — \"Хочешь сбежать, ответь мне на вопрос: сколько будет 2 плюс 2?\"")
    now_page.otrisovka()
    for x in range(5):
        try: #да, пришлось написать эту страницу вручную, зато получилось довольно интересно
            chetire = int(input("Введите целое число в консоль   "))
            if chetire == 4:
                page_30()
            elif chetire == 1:
                page_26()
            else:
                page_28()
            break
        except ValueError:
            print("Боюсь, что это не число. Попробуйте ещё раз")
        if x >= 5:
            print("\nПохоже, что вы невменяемый. Я устал от ваших издевательств. Уходите\n")
            finish()
def page_25():
    global variant_1, variant_2, variant_3, edavoda
    now_page = Page(25, "Вас привели в здание оказания первой помощи")
    variant_1 = Variant_otveta("Попросить поесть", 31, var_set("edavoda", 10))
    variant_2 = Variant_otveta("Попросить попить", 31, var_set("edavoda", 5))
    variant_3 = Variant_otveta("\"Что здесь вообще происходит?\"", 33)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_26():
    global variant_1, variant_2, z, zz
    now_page = Page(26, "\"Правильно, пошли за мной\", — сказал психопат.\nПоздравляю, у вас очень хорошая интуиция.")
    z, zz = 0, 0
    variant_1 = Variant_otveta("Погладить интуицию", 29)
    variant_2 = Variant_otveta("Пойти за психопатом", 29)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_27():
    global variant_1, variant_2, variant_3
    now_page = Page(27, "Логика Вас работает, теперь проверим удачу :-)")
    variant_1 = Variant_otveta("СМЕРТЬ", 36)
    variant_2 = Variant_otveta("СМЕРТЬ", 36)
    variant_3 = Variant_otveta("СМЕРТЬ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_28():
    global variant_1
    now_page = Page(28, "\"Неправильный ответ!\" сказал психопат и всадил вам нож в тело.")
    variant_1 = Variant_otveta("УВЫ. МАТЕМАТИКУ НАДО УЧИТЬ.", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_29():
    global variant_1, variant_2, variant_3, zz
    now_page = Page(29, "\"А меня, кстати, зовут Гуамоколатокинт\", — сказал психопат и подвёл Вас к забору.")
    variant_1 = Variant_otveta("Убить психопата", 52, var_add("zz"))
    variant_2 = Variant_otveta("Перепрыгнуть через забор", 53)
    variant_3 = Variant_otveta("А меня Урфин Джус", 32)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_30():
    global variant_1
    now_page = Page(30, "Правильно, но неправильно. У психопата другое мнение. Он всадил вам нож в тело, и душа у вас улетела.")
    variant_1 = Variant_otveta("СМЕРТЬ!", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_31():
    global variant_1
    text = "Вам дали "
    if edavoda == 10:
        text += "еды"
    elif edavoda == 5:
        text += "воды"
    else:
        vara = Variable_is_incorrect()
        vara.variable_incorrect("edavoda", edavoda, 5, 10)
    text += " и попросили собраться в главном зале"
    now_page = Page(31, text)
    variant_1 = Variant_otveta("Пойти в главный зал", 34)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_32():
    global variant_1
    now_page = Page(32, "Услышав это, сумасшедший радостно набросился на вас и начал кричать что то наподобие \"Уху, уху, ты вернулся\". От радости, не расчитав свои силы, Гуамоколатокинт сильно толкнул вас, вы отлетели в забор, котоый был под напряжением. Так получилось, что вы не могли отлипнуть от забора, и конец был уже ясен. Не смирившись с этим, помешанный задушил себя смирительной рубашкой...\nВпредь учись следить за языком.")
    variant_1 = Variant_otveta("Постараюсь", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_33():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(33, "Вам сказали, что происходит нечто ужасное и попросили собраться в главном зале.")
    variant_1 = Variant_otveta("\"Как будто я не догадался\" [пойти в главный зал]", 34)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_34():
    global variant_1, variant_2
    now_page = Page(34, "В главном зале было много людей. ОЧЕНЬ МНОГО людей.\nНа сцену вышел какой-то высокопоставленный человек и сказал — \"Я понимаю, в народе царит паника. Конечно, где это видано, чтобы землятресение случалось в центральной части России. Мы расследуем это дело, ну а пока, нам нужна помощь\".")
    variant_1 = Variant_otveta("Сидеть тихо", 89)
    variant_2 = Variant_otveta("Попроситься в добровольцы", 90)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_35():
    global variant_1, variant_2
    now_page = Page(35, "Ну что ж , попробуй")
    variant_1 = Variant_otveta("СМЕРТЬ", 37)
    variant_2 = Variant_otveta("СМЕРТЬ", 37)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_36():
    global variant_1, variant_2, variant_3, variant_4, variant_5
    now_page = Page(36, "Ну что ж, теперь выбирай, куда ты хочешь")
    variant_1 = Variant_otveta("Хочу домой", 230)
    variant_2 = Variant_otveta("Хочу в Ад", 40)
    variant_3 = Variant_otveta("Хочу в Рай", 41)
    variant_4 = Variant_otveta("Хочу в будущее", 43)
    variant_5 = Variant_otveta("Хочу в прошлое", 83)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_37():
    global variant_1, variant_2, variant_3
    now_page = Page(37, "Везунчик. Но просто так я тебя не отпущу.")
    variant_1 = Variant_otveta("СМЕРТЬ", 39)
    variant_2 = Variant_otveta("СМЕРТЬ", 1)
    variant_3 = Variant_otveta("СМЕРТЬ", 39)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_38():
    global variant_1, variant_2
    now_page = Page(38, "Вам вручили увесистый камень")
    variant_1 = Variant_otveta("Поднять камень на гору", 50)
    variant_2 = Variant_otveta("Кинуть камень в чёрта", 51)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_39():
    global variant_1
    now_page = Page(39, "Молодец. В награду могу тебе сказать, что психам очень нравится число один.")
    variant_1 = Variant_otveta("Эммм... ОК", 21)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_40():
    global variant_1, variant_2, variant_3
    now_page = Page(40, "Welcome to Hell !!!")
    variant_1 = Variant_otveta("Таскать камни", 38)
    variant_2 = Variant_otveta("Вариться в котле", 42)
    variant_3 = Variant_otveta("Покончить жизнь самоубийством", 44)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_41():
    global variant_1, variant_2, variant_3, local_pages, ray
    now_page = Page(41, "Welcome to Рай !!!")
    variant_1 = Variant_otveta("Нежиться на солнышке", 46)
    variant_2 = Variant_otveta("Пить вино", 46)
    ray = 0
    if local_pages[48] != 1:
        variant_3 = Variant_otveta("Покончить жизнь самоубийством", 49)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_42():
    global variant_1, variant_2, variant_3, variant_4, casha
    now_page = Page(42, "Выберите температуру")
    variant_1 = Variant_otveta("10 градусов", 45)
    variant_2 = Variant_otveta("100 градусов", 45)
    variant_3 = Variant_otveta("1000 градусов", 45)
    variant_4 = Variant_otveta("10000 градусов", 48)
    casha = 0
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_43():
    global variant_1, variant_2
    now_page = Page(43, "Вы телепортировались на 100 лет вперёд.\nВы лежите в гробу.")
    variant_1 = Variant_otveta("Лежать дальше", 47)
    variant_2 = Variant_otveta("Задохнуться", 229)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_44():
    global variant_1, variant_2
    now_page = Page(44, "У вас ничего не вышло, Вы ведь и так мертвы. Ха ха ха.")
    variant_1 = Variant_otveta("Таскать камни", 38)
    variant_2 = Variant_otveta("Вариться в котле", 42)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_45():
    global variant_1, variant_2, variant_3, variant_4, casha
    now_page = Page(45, "Вы будете вариться здесь ВЕЧНО ВЕЧНО ВЕЧНО!!!\nОткрыта концовка \"Грешник кашевар\"")
    variant_1 = Variant_otveta("Вариться", 45, var_add("casha", 1))
    variant_2 = Variant_otveta("Конец", 1)
    variant_3 = Variant_otveta("Концовки", 107)
    if casha >= 10:
        variant_4 = Variant_otveta("Внимание!", 228, var_set("casha", -1000))
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_46():
    global variant_1, variant_2, variant_3, variant_4, variant_5, ray
    now_page = Page(46, "Вы хорошо провели время\n\nВы открыли концовку \"Блаженный\"")
    variant_1 = Variant_otveta("Нежиться на солнышке", 46, var_add("ray"))
    variant_2 = Variant_otveta("Пить вино", 46, var_add("ray"))
    variant_3 = Variant_otveta("ВЫХОД", 1)
    variant_4 = Variant_otveta("Концовки", 107)
    if ray >= 10:
        variant_5 = Variant_otveta("Внимание!", 228, var_set("ray", -1000))
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_47():
    global variant_1
    now_page = Page(47, "Увы. Кончился кислород.")
    variant_1 = Variant_otveta("Задохнуться", 228)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_48():
    global variant_1, variant_2, variant_3, variant_4, variant_5, local_pages
    now_page = Page(48, "Черти не знают, как сделать так, чтобы вода достигла такой температуры. Они разрешили загадать им одно желание.")
    variant_1 = Variant_otveta("хочу в Рай", 41)
    if local_pages[141] == "1":
        variant_2 = Variant_otveta("Хочу в прошлое", 141)
    elif local_pages[141] != "1":
        variant_3 = Variant_otveta("Хочу в прошлое", 6)
    variant_4 = Variant_otveta("Хочу в будущее", 43)
    variant_5 = Variant_otveta("Хочу домой", 230)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_49():
    global variant_1
    now_page = Page(49, "Ангелы увидели это и отправили Вас в Ад")
    variant_1 = Variant_otveta("Идти в Ад", 40)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_50():
    global variant_1, variant_2, variant_3, variant_4, camen
    now_page = Page(50, "Вам вручили ещё один увесистый камень. Вы обречены.\n\nОткрыта концовка \"Грешник работяга\"")
    variant_1 = Variant_otveta("Поднять камень на гору", 50, var_add("camen"))
    variant_2 = Variant_otveta("КОНЕЦ", 1)
    variant_3 = Variant_otveta("Концовки", 107)
    if camen >= 10:
        variant_4 = Variant_otveta("Внимание!", 228, var_set("camen", -1000))
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_51():
    global variant_1, variant_2, local_pages
    now_page = Page(51, "Вы нарушили пространственно временной континум")
    if local_pages[141] != "1":
        variant_1 = Variant_otveta("ОК", 6)
    elif local_pages[141] == "1":
        variant_2 = Variant_otveta("ОК", 141)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_52():
    global variant_1, variant_2, zz
    now_page = Page(52, "Вы бросились на психа со словами \"Ты мне не нужен!\". Но у него был нож. Нужно уметь ценить друзей.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    if zz <= 1:
        variant_2 = Variant_otveta("Нееее, так дело не пойдёт", 29)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_53():
    global variant_1, variant_2, z
    now_page = Page(53, "Вы успешно перепрыгнули.")
    variant_1 = Variant_otveta("Помочь другу", 54)
    variant_2 = Variant_otveta("Оставить друга", 55, var_add("z"))
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_54():
    global variant_1
    now_page = Page(54, "Вы оба успешно перелезли через забор. В следующий момент психушка обрушилась.")
    variant_1 = Variant_otveta("Пойти по дороге", 57)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_55():
    global variant_1, variant_2, z
    now_page = Page(55, "Гуамоколатокинт оказался отличным прыгуном. Он догнал Вас и всадил вам нож в тело. Надо учиться ценить друзей.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    if z <= 1:
        variant_2 = Variant_otveta("ВЖУХ!", 53)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_56():
    global variant_1, variant_2
    now_page = Page(56, "Вы просыпаетесь рано утром. Ваша интуиция, словно собачка, крутится у ваших ног и скулит.")
    variant_1 = Variant_otveta("Пнуть интуицию ногой и продолжить спать", 2)
    variant_2 = Variant_otveta("Погладить интуицию и встать", 3)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_57():
    global variant_1, variant_2, variant_3
    now_page = Page(57, "Вы вышли на дорогу. Позади послышался рокот автомобиля.")
    variant_1 = Variant_otveta("Броситься под машину", 58)
    variant_2 = Variant_otveta("Бросить товарища под машину", 59)
    variant_3 = Variant_otveta("Попросить водителя остановиться", 60)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_58():
    global variant_1, variant_2
    now_page = Page(58, "Поздравляем, Вы покончили жизнь самоубийством, а вы ожидали чего-то другого? Не надо так. За такую бессмысленную глупость я вам даже концовки не дам.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_59():
    global variant_1, variant_2
    now_page = Page(59, "Вы бросили Гуамоколатокинта под машину. Водитель резко остановился и вызвал полицию.")
    variant_1 = Variant_otveta("Стоять и ждать", 70)
    variant_2 = Variant_otveta("Убежать", 71)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_60():
    global variant_1, variant_2, variant_3
    now_page = Page(60, "Водитель остановился")
    variant_1 = Variant_otveta("Попросить подвести", 61)
    variant_2 = Variant_otveta("Убить водителя", 62)
    variant_3 = Variant_otveta("Выкинуть водителя из машины и уехать", 63)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_61():
    global variant_1, variant_2, variant_3
    now_page = Page(61, "Куда едем?")
    variant_1 = Variant_otveta("Жить в Лондон", 64)
    variant_2 = Variant_otveta("В Москву", 65)
    variant_3 = Variant_otveta("Куда-нибудь", 66)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_62():
    global variant_1
    now_page = Page(62, "Вы убили водителя и сели за руль, только Гуамоколатокинт не одобрил вашего действия и зарезал Вас.")
    variant_1 = Variant_otveta("Истекать кровью", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_63():
    global variant_1, variant_2
    now_page = Page(63, "Куда поедем?")
    variant_1 = Variant_otveta("Домой", 81)
    variant_2 = Variant_otveta("В Москву", 82)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_64():
    global variant_1, variant_2, local_pages
    now_page = Page(64, "Водитель оценил вашу остроумную шутку")
    if local_pages[65] != "1":
        variant_1 = Variant_otveta("В Москву", 65)
    variant_2 = Variant_otveta("Куда-нибудь", 66)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_65():
    global variant_1, variant_2
    now_page = Page(65, "Увы, проезд перекрыт")
    if local_pages[64] != "1":
        variant_1 = Variant_otveta("В Лондон", 64)
    variant_2 = Variant_otveta("Куда-нибудь", 66)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_66():
    global variant_1, variant_2
    now_page = Page(66, "ОК, поедем на Украину")
    variant_1 = Variant_otveta("Я согласен", 67)
    variant_2 = Variant_otveta("Убить водителя", 62)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_67():
    global variant_1, variant_2
    now_page = Page(67, "Вы поехали на Украину. На полпути земля затряслась и под вами разверзлась бездна.")
    variant_1 = Variant_otveta("Пристегнуться", 68)
    variant_2 = Variant_otveta("Выпрыгнуть из машины", 69)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_68():
    global variant_1
    now_page = Page(68, "После того, как вы пристегнулись, водитель затормозил, вас занесло, перевернуло несколько раз и выбросило в бездну.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_69():
    global variant_1, variant_2
    now_page = Page(69, "Вы выпрыгнули из машины. Автомобиль поехал дальше, переворачиваясь и кувыркаясь. Вы выжили, но повредили руку. Хотите в больницу?")
    variant_1 = Variant_otveta("Хочу в больницу (шанс умереть мал)", 75)
    variant_2 = Variant_otveta("Выжить самостоятельно (шанс умереть высок)", 76)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_70():
    global variant_1, variant_2
    now_page = Page(70, "Ждать пришлось довольно долго. Наконец, когда полиция приехала, у вас уже затекли ноги. Водитель расказал, как вы выбросили человека. Слово передали Вам.")
    variant_1 = Variant_otveta("Он всё врет! [соврать]", 72)
    variant_2 = Variant_otveta("Он говорит правду [сказать правду]", 72)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_71():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(71, "Вы убежали. К сожалению у водителя оказался пистолет. Он им воспользовался.")
    variant_1 = Variant_otveta("Выстрел", 73)
    variant_2 = Variant_otveta("Выстрел", 74)
    variant_3 = Variant_otveta("Выстрел", 73)
    variant_4 = Variant_otveta("Выстрел", 74)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_72():
    global variant_1, variant_2
    now_page = Page(72, "Вас посадили в машину и увезли в тюрьму. На Вас повесили все остальные преступления, к которым вы не имеете никакого отношения.\n\nВы открыли концовку\"В тюряге\"")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_73():
    global variant_1
    now_page = Page(73, "Увы, Вас застрелили")
    variant_1 = Variant_otveta("СМЕРТЬ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_74():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(74, "Вам повезло. водитель промахнулся. Вы успешно убежали.")
    variant_1 = Variant_otveta("Молодец", 259)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_75():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(75, "Удачи")
    variant_1 = Variant_otveta("СМЕРТЬ", 77)
    variant_2 = Variant_otveta("СМЕРТЬ", 1)
    variant_3 = Variant_otveta("СМЕРТЬ", 77)
    variant_4 = Variant_otveta("СМЕРТЬ", 77)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_76():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(76, "Ваш выбор")
    variant_1 = Variant_otveta("СМЕРТЬ", 1)
    variant_2 = Variant_otveta("СМЕРТЬ", 1)
    variant_3 = Variant_otveta("СМЕРТЬ", 1)
    variant_4 = Variant_otveta("СМЕРТЬ ", 79)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_77():
    global variant_1
    now_page = Page(77, "Вы выжили. Поздравляем!")
    variant_1 = Variant_otveta("Открыть глаза", 78)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_78():
    global variant_1
    now_page = Page(78, "Ахахахах, вы серьёзно поверили, что по вашему хотению вы окажетесь в больнице? К сожаленю так не работает, поэтому вы остались лежать на дороге одни.")
    variant_1 = Variant_otveta("Умереть", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_79():
    global variant_1, variant_2
    now_page = Page(79, "Однако, вам повезло. Вы лежите один на дороге. Около Вас огромный каньон.")
    variant_1 = Variant_otveta("Попытаться встать", 80)
    variant_2 = Variant_otveta("Умереть", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_80():
    global variant_1
    now_page = Page(80, "Вы встали. Вокруг ни души.")
    variant_1 = Variant_otveta("Осмотреться", 307)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_81():
    global variant_1
    now_page = Page(81, "Вы разогнались до неимоверной скорости в 6 миллионов мм/ч. Очень странный спидометр в машине стоит, но это неважно. На самом деле это небольшая скорость, но Ваше сознание восприняло эту цифру слишком буквально. Вы подумали, что это скорость в км/ч. Мы летим.")
    variant_1 = Variant_otveta("Земля в иллюминаторе, Земля в иллюминаторе, Земля в иллюминаторе видна...", 255)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_82():
    global variant_1, variant_2, global_pages
    now_page = Page(82, "Вы ехали, ехали, но не доехали. Проезд оказался перекрыт. Остается только один вариант.")
    variant_1 = Variant_otveta("Ехать домой", 81)
    if global_pages[352] != 1:
        variant_2 = Variant_otveta("Серьёзно?", 352)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_83():
    global variant_1, variant_2
    now_page = Page(83, "Вжух! Вы снова отказываетесь на лестничной площадке.")
    variant_1 = Variant_otveta("Спуститься вниз", 84)
    variant_2 = Variant_otveta("Подняться наверх", 85)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_84():
    global variant_1, variant_2
    now_page = Page(84, "Каким способом будем спускаться?")
    variant_1 = Variant_otveta("На лифте", 86)
    variant_2 = Variant_otveta("По лестнице", 10)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_85():
    global variant_1, variant_2
    now_page = Page(85, "Каким способом будем подниматься?")
    variant_1 = Variant_otveta("На лифте", 86)
    variant_2 = Variant_otveta("По лестнице", 87)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_86():
    global variant_1
    now_page = Page(86, "Увы, ещё одного шанса я тебе не дам")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_87():
    global variant_1
    now_page = Page(87, "Нет. Вы не угадали.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_88():
    global variant_1, variant_2
    now_page = Page(88, "Вы полетели вниз. Ветерок приятно обдувал Ваше тело. Каким-то волшебным образом Вы попали в кабину самолета.")
    variant_1 = Variant_otveta("Сесть в кресло и пристегнуться", 93)
    variant_2 = Variant_otveta("Вытолкнуть пилота из самолета", 94)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_89():
    global variant_1, variant_2
    now_page = Page(89, "На сцену вышло 10 добровольцев.\n\"Остальные могут разместиться в нашем центре\"")
    variant_1 = Variant_otveta("Выйти в добровольцы", 90)
    variant_2 = Variant_otveta("Разместиться", 120)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_90():
    global variant_1, variant_2
    now_page = Page(90, "Добровольцев собралось человек двесте.\n\"Дорогие друзья, мы очень признательны Вам за Ваш энтузиазм. Выберите, как вы бы хотели нам помочь\"")
    variant_1 = Variant_otveta("Разгребать завалы", 91)
    variant_2 = Variant_otveta("Оказать медицинскую помощь", 92)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_91():
    global variant_1
    now_page = Page(91, "Вы пошли разгребать завалы. Вам попался самый хлипкий дом. Конечно же Вас завалило.")
    variant_1 = Variant_otveta("Попытаться выжить", 122)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_92():
    global variant_1, variant_2, variant_3, variant_4, local_pages
    now_page = Page(92, "Вы решили помочь другим людям, леча их. С кого начнём?")
    variant_1 = Variant_otveta("Я устал, хочу полежать", 124)
    if local_pages[203] != "1":
        variant_2 = Variant_otveta("Излечить мать троих детей", 203)
    if local_pages[204] != "1":
        variant_3 = Variant_otveta("Излечить сына маминой подруги", 204)
    if local_pages[205] != "1":
        variant_4 = Variant_otveta("Излечить собаку", 205)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_93():
    global variant_1, variant_2
    now_page = Page(93, "Пилот явно незаметил Вас и полетел дальше по своим делам.")
    variant_1 = Variant_otveta("Ждать", 108)
    variant_2 = Variant_otveta("Нет, всё-таки я хочу убить пилота", 94)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_94():
    global variant_1, variant_2
    now_page = Page(94, "Вы вытолкнули пилота. Он пролетел несколько метров в воздухе, взмахнул крылышками и полетел в Рай.")
    variant_1 = Variant_otveta("Сойти с ума", 95)
    variant_2 = Variant_otveta("Еще рано", 96)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_95():
    global variant_1
    now_page = Page(95, "Ввод выпил горького вина")
    variant_1 = Variant_otveta("Усил жилого вред", 110)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_96():
    global variant_1
    now_page = Page(96, "Вы вытолкнули пилота. Он пролетел несколько метров в воздухе, взмахнул крылышками и полетел в Рай.")
    variant_1 = Variant_otveta("Взяться за штурвал", 97)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_97():
    global variant_1, variant_2
    now_page = Page(97, "Куда бы дернуть штурвал?")
    variant_1 = Variant_otveta("На себя", 98)
    variant_2 = Variant_otveta("От себя", 99)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_98():
    global variant_1, variant_2
    now_page = Page(98, "Вы умудрились взлететь, правда самолёту повредил крыло асфальт. Это всё из за асфальта, ты тут ни причём.")
    variant_1 = Variant_otveta("Посадить самолёт", 100)
    variant_2 = Variant_otveta("Взлететь", 101)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_99():
    global variant_1
    now_page = Page(99, "Вы полетели вниз.")
    variant_1 = Variant_otveta("Разбиться", 144)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_100():
    global variant_1
    now_page = Page(100, "Вы успешно посадили самолёт. Каким-то Макаром Вас не заметили.")
    variant_1 = Variant_otveta("Выйти из самолёта", 260)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_101():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(101, "Куда летим?")
    variant_1 = Variant_otveta("Куда-нибудь", 102)
    variant_2 = Variant_otveta("Чёрте куда", 103)
    variant_3 = Variant_otveta("Куда глаза глядят", 105)
    variant_4 = Variant_otveta("Лети уже куда-нибудь", 104)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_102():
    global variant_1
    now_page = Page(102, "Вы прилетели в Лондон. Вокруг царила такая же разруха")
    variant_1 = Variant_otveta("Остаться жить в Лондоне", 106)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_103():
    global variant_1, variant_2
    now_page = Page(103, "Вы прилетели к Вашему старому другу — чёрту. \"Какими судьбами?\", воскликнул он.")
    variant_1 = Variant_otveta("Случайно залетел. Полечу, пожалуй, обратно", 202)
    variant_2 = Variant_otveta("В гости", 214)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_104():
    global variant_1
    now_page = Page(104, "Вы прилетели домой. Совершенно случайно Вы врезались в свой же дом.")
    variant_1 = Variant_otveta("Разбиться", 114)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_105():
    global variant_1, variant_2
    now_page = Page(105, "Вы задумчиво глядели в потолок.")
    variant_1 = Variant_otveta("Лететь в потолок", 222)
    variant_2 = Variant_otveta("Я передумал", 101)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_106():
    global variant_1, variant_2
    now_page = Page(106, "Вы удачно посадили самолёт, купили жилье в Лондоне, завели себе семью и детей и стали жить в полуразрушенном городе. Жаль только, что вы не знаете английского языка.\n\nВы довели историю до концовки \"Иностранец\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_107():
    global global_pages, variant_1, variant_2, variant_3, variant_4, variant_5, variant_6, variant_7, variant_8, variant_9, variant_10, variant_11, variant_12, variant_13, variant_14, variant_15, variant_16, variant_17, variant_18, variant_19, variant_20, variant_21, variant_22, variant_23, variant_24, variant_25, variant_26, variant_27, variant_28, variant_29, variant_30
    ordinary_ends = [106, 121, 72, 14, 46, 45, 180, 50, 215, 236, 266, 268, 263, 281, 282, 293, 353, 357, 360, 198] #Страницы с концовками
    secret_ends = [201, 270, 227, 175, 306, 327, 339]
    ordinary, secret = 0, 0 #количество тех или иных концовок
    for end in ordinary_ends:
        if global_pages[end] == "1":
            ordinary += 1
    if global_pages[253] == "1" or global_pages[251] == "1": #Противная концовка
        ordinary += 1
    for end in secret_ends:
        if global_pages[end] == "1":
            secret += 1

    now_page = Page(107, f"В ходе истории можно открыть различные концовки. Перечень открытых концовок находится здесь.\nНа данный момент количество концовок в квесте: 22 обычных и 7 секретных.\nОтркрыто у вас:\nОбычных: {ordinary}\nСекретных: {secret}")

    if global_pages[106] == "1":
        variant_1 = Variant_otveta("Иностранец", 106)
    if global_pages[121] == "1":
        variant_2 = Variant_otveta("Перетерпел", 121)
    if global_pages[72] == "1":
        variant_3 = Variant_otveta("В тюряге", 72)
    if global_pages[14] == "1":
        variant_4 = Variant_otveta("Беспечный", 14)
    if global_pages[46] == "1":
        variant_5 = Variant_otveta("Блаженный", 46)
    if global_pages[45] == "1":
        variant_6 = Variant_otveta("Грешник кашевар", 45)
    if global_pages[180] == "1":
        variant_7 = Variant_otveta("Хам", 180)
    if global_pages[50] == "1":
        variant_8 = Variant_otveta("Грешник работяга", 50)
    if global_pages[215] == "1":
        variant_9 = Variant_otveta("Чайка", 215)
    if global_pages[236] == "1":
        variant_10 = Variant_otveta("Сёмга", 236)
    if global_pages[253] == "1" or global_pages[251] == "1": #!
        variant_11 = Variant_otveta("Водоросли", 253)
        ordinary += 1
    if global_pages[266] == "1":
        variant_12 = Variant_otveta("Очень вкусно", 266)
    if global_pages[268] == "1":
        variant_13 = Variant_otveta("Удачный тост", 268)
    if global_pages[263] == "1":
        variant_14 = Variant_otveta("Невезунчик", 263)
    if global_pages[281] == "1":
        variant_15 = Variant_otveta("Водитель", 281)
    if global_pages[282] == "1":
        variant_16 = Variant_otveta("Страшный лисёнок", 282)
    if global_pages[285] == "1":
        variant_17 = Variant_otveta("Спаситель", 285)
    if global_pages[293] == "1":
        variant_18 = Variant_otveta("Батут", 293)
    if global_pages[353] == "1":
        variant_19 = Variant_otveta("Одиночество", 353)
    if global_pages[357] == "1":
        variant_20 = Variant_otveta("Интересная болтовня", 357)
    if global_pages[360] == "1":
        variant_21 = Variant_otveta("Изолятор", 360)
    if global_pages[198] == "1":
        variant_22 = Variant_otveta("Спасительная лестница", 198)
    if global_pages[201] == "1":
        variant_23 = Variant_otveta("Другой Илон Маск /секретная/", 201)
    if global_pages[270] == "1":
        variant_24 = Variant_otveta("Капец /секретная/", 270)
    if global_pages[227] == "1":
        variant_25 = Variant_otveta("Можно было и лучше/секретная/", 227)
    if global_pages[175] == "1":
        variant_26 = Variant_otveta("Покоритель планет /секретная/", 175)
    if global_pages[306] == "1":
        variant_27 = Variant_otveta("Смерть без ума /секретная/", 306)
    if global_pages[327] == "1":
        variant_28 = Variant_otveta("Выживший /секретная/", 327)
    if global_pages[339] == "1":
        variant_29 = Variant_otveta("Сурок в каньоне /секретная/", 339)
    variant_30 = Variant_otveta("[Главное меню]", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_108():
    global variant_1, variant_2
    now_page = Page(108, "Самолет летел дальше. Ничего не происходило. Ваше терпение было на исходе.")
    variant_1 = Variant_otveta("Всё равно ждать", 109)
    variant_2 = Variant_otveta("УБИТЬ ПИЛОТА", 94)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_109():
    global variant_1, variant_2
    now_page = Page(109, "Самолет летел дальше. Ничего не происходило. Ваше терпение было на исходе.\nВы решили ждать дальше, но времени уже прошло слишком много. Внутри Вас всё закипело. Вы поняли, что больше не можете себя сдерживать.")
    variant_1 = Variant_otveta("Убить пилота", 94)
    variant_2 = Variant_otveta("Пилота убить", 94)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_110():
    global variant_1, variant_2
    now_page = Page(110, "Уезжал паспорт хопа у")
    variant_1 = Variant_otveta("Вклад дискретизации лопатки", 95)
    variant_2 = Variant_otveta("Частично прийти в сознание", 111)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_111():
    global variant_1
    now_page = Page(111, "\"Я здесь\", сказало Вам сознание")
    variant_1 = Variant_otveta("Где ты было?", 112)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_112():
    global variant_1
    now_page = Page(112, "Я ушло погулять")
    variant_1 = Variant_otveta("Не уходи больше от меня", 113)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_113():
    global variant_1
    now_page = Page(113, "Хорошо\n\n ПЕРЕЗАГРУЗКА\n\n ПЕРЕЗАГРУЗКА\n\n ПЕРЕЗАГРУЗКА")
    variant_1 = Variant_otveta("ПЕРЕЗАГРУЗКА", 114)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_114():
    global variant_1, variant_2
    now_page = Page(114, "Вы лежите на чём-то мягком. Пахнет лекарствами и пылью.")
    variant_1 = Variant_otveta("Причём тут пыль?", 115)
    variant_2 = Variant_otveta("Открыть глаза", 116)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_115():
    global variant_1
    now_page = Page(115, "Это не имеет значения.\nВы лежите на чём-то мягком. Пахнет лекарствами и пылью.")
    variant_1 = Variant_otveta("Открыть глаза", 116)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_116():
    global variant_1, variant_2
    now_page = Page(116, "Вокруг белые стены. Вы опутаны крепкими верёвками. Пошевелиться не имеется возможности.")
    variant_1 = Variant_otveta("Спокойно лежать и ждать", 117)
    variant_2 = Variant_otveta("Позвать кого-нибудь", 117)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_117():
    global variant_1, variant_2, variant_3, variant_4, local_pages, pol
    text = "К вам зашла медсестра.\n— Лежите спокойно, Вам нельзя кричать и шевелиться.\n— Что со мной произошло?\n"
    if local_pages[258] == "1":
        text += "— Мы нашли Вас в машине, которая влетела в стену дома. Причём за рулём был"
        if pol < 0:
            text += "а"
        text += " ты!"
    elif local_pages[88] == "1":
        text += "— Мы нашли Вас в разбившемся самолёте на окраине города."
    elif local_pages[307] == "1" and pol >= 0:
        text += "— Мы нашли Вас, лежащим на дне каньона, образовавшегося из за землятресения."
    elif local_pages[307] == "1" and pol < 0:
        text += "— Мы нашли Вас, лежащей на дне каньона, образовавшегося из за землятресения."
    else:
        text += "\n\nВы перешли на данную страницу неккоректно\n\n"
    text += " Вы сильно повредили ногу. Вам нельзя ходить. Потерпите немного, сейчас к Вам подойдет врач."
    now_page = Page(117, text)
    variant_1 = Variant_otveta("Потерпеть", 118)
    variant_2 = Variant_otveta("Немного потерпеть", 118)
    variant_3 = Variant_otveta("Очень сильно потерпеть", 118)
    variant_4 = Variant_otveta("Потерпеть до потери сознания", 121)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_118():
    global variant_1
    now_page = Page(118, "К вам зашёл врач.\n—Здравствуйте, Как Вас зовут?")
    variant_1 = Variant_otveta("Назвать своё имя", 243)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_119():
    global variant_1, variant_2, variant_3, variant_4, variant_5, global_pages
    now_page = Page(119, "Вы можете продолжить историю с определённых моментов, если Вы дошли туда хотя бы раз.")
    if global_pages[88] == "1":
        variant_1 = Variant_otveta("В самолёт", 88)
    if global_pages[25] == "1":
        variant_2 = Variant_otveta("В Здание Оказаия Первой Помощи", 25)
    if global_pages[21] == "1":
        variant_3 = Variant_otveta("В психушку", 21)
    if global_pages[79] == "1":
        variant_4 = Variant_otveta("В каньон", 79)
    variant_5 = Variant_otveta("Назад", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_120():
    global variant_1, variant_2, variant_3, local_pages
    now_page = Page(120, "Вы подошли на ресепшн. Вам дали номер № 666. Как символично, не правда ли?")
    variant_1 = Variant_otveta("Поспать", 139)
    if local_pages[126] != "1":
        variant_2 = Variant_otveta("Поесть", 126)
    if local_pages[135] != "1":
        variant_3 = Variant_otveta("Позвонить дьяволу", 127)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_121():
    global variant_1, variant_2
    now_page = Page(121, "Вы потеряли сознание. Дальше Вы ничего не помните. Скорее всего Вы умерли.\n*Печалька*\n\nВы довели историю до концовки \"Перетерпел\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_122():
    global variant_1, variant_2, variant_3, variant_4, variant_5, variant_6, variant_7, variant_8, variant_9, variant_10, variant_11
    now_page = Page(122, "Удачи")
    variant_1 = Variant_otveta("Смерть", 123)
    variant_2 = Variant_otveta("Смерть", 124)
    variant_3 = Variant_otveta("Смерть", 123)
    variant_4 = Variant_otveta("Смерть", 124)
    variant_5 = Variant_otveta("Смерть", 124)
    variant_6 = Variant_otveta("Смерть", 123)
    variant_7 = Variant_otveta("Смерть", 124)
    variant_8 = Variant_otveta("Смерть", 124)
    variant_9 = Variant_otveta("Смерть", 124)
    variant_10 = Variant_otveta("Смерть", 123)
    variant_11 = Variant_otveta("Смерть", 124)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_123():
    global variant_1
    now_page = Page(123, "Увы, Вам неповезло.")
    variant_1 = Variant_otveta("СМЕРТЬ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_124():
    global variant_1
    now_page = Page(124, "Вы лежите на чём-то мягком. Пахнет сёмгой.")
    variant_1 = Variant_otveta("Почему сёмгой?", 144)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_125():
    global variant_1
    now_page = Page(125, "Все говорят \"Серьёзно?\", а ты купи слона")
    variant_1 = Variant_otveta("Все говорят \"Все говорят \"Серьёзно?\", а ты купи слона\", а ты купи слона", 140)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_126():
    global variant_1
    now_page = Page(126, "Вы поели, теперь можно и поспать.")
    variant_1 = Variant_otveta("Я сам решу, чего я хочу", 120)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_127():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(127, "Вам ответил дьявол")
    variant_1 = Variant_otveta("Привет", 128)
    variant_2 = Variant_otveta("Вас плохо слышно", 129)
    variant_3 = Variant_otveta("Как дела?", 130)
    variant_4 = Variant_otveta("Купи слона", 131)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_128():
    global variant_1, variant_2, variant_3, local_pages
    now_page = Page(128, "Привет, привет")
    if local_pages[129] != "1":
        variant_1 = Variant_otveta("Вас плохо слышно", 129)
    variant_2 = Variant_otveta("Как дела?", 130)
    variant_3 = Variant_otveta("Купи слона", 131)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_129():
    global variant_1, variant_2, variant_3, local_pages
    now_page = Page(129, "Ты мне врёшь.")
    if local_pages[128] != "1":
        variant_1 = Variant_otveta("Привет", 128)
    variant_2 = Variant_otveta("Как дела?", 130)
    variant_3 = Variant_otveta("Купи слона", 131)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_130():
    global variant_1
    now_page = Page(130, "Да норм. Чего звонишь то?")
    variant_1 = Variant_otveta("Хотел слона тебе предложить", 131)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_131():
    global variant_1, variant_2, variant_3
    now_page = Page(131, "Серьёзно?")
    variant_1 = Variant_otveta("Да", 132)
    variant_2 = Variant_otveta("Нет", 133)
    variant_3 = Variant_otveta("Все говорят \"Серьёзно?\", а ты купи слона", 134)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_132():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(132, "Вот повезло так повезло. Мне как раз нужен был слон. За сколько продашь?")
    variant_1 = Variant_otveta("Честно говоря, у меня нет слона", 138)
    variant_2 = Variant_otveta("1000 $", 136)
    variant_3 = Variant_otveta("10000 $", 136)
    variant_4 = Variant_otveta("100000 $", 136)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_133():
    global variant_1
    now_page = Page(133, "Эмм,  а чего звонишь то?")
    variant_1 = Variant_otveta("Незнаю...", 143)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_134():
    global variant_1, variant_2
    now_page = Page(134, "Хорошо. Сколько стоит?")
    variant_1 = Variant_otveta("Серьёзно?", 125)
    variant_2 = Variant_otveta("Все говорят \"Хоршо. Сколько стоит\", а ты купи слона", 135)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_135():
    global variant_1
    now_page = Page(135, "У вас в руке сгорел телефон.")
    variant_1 = Variant_otveta("Печально", 120)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_136():
    global variant_1, variant_2, variant_3
    now_page = Page(136, "\"Сойдет\", - сказал дьявол и деньги оказались на столе - \"А как доставлять то будешь?\"")
    variant_1 = Variant_otveta("Мой слон в цирке", 137)
    variant_2 = Variant_otveta("Иди на…", 138)
    variant_3 = Variant_otveta("У меня нет слона", 138)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_137():
    global variant_1
    now_page = Page(137, "Да? Хорошо,  спасибо.\n[Гудки]")
    variant_1 = Variant_otveta("Пожалуйста...", 139)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_138():
    global variant_1
    now_page = Page(138, "Ты обманывать меня решил?! Я насылаю на тебя проклятие!!!\n\nСИЛОЙ, ДАННОЙ МНЕ\nИ МОГУЩЕСТВОМ,\nНАСЫЛАЮ НА ТЕБЯ \nЯ ПРОКЛЯТИЕ.\nУПЛЫВЕШЬ НА КОРАБЛЕ\nТЫ ПОТРЕПАННОМ\nНЕ УВИДИШЬ ТЫ СЕБЯ\nВ ЭТОМ ЗЕРКАЛЕ.\n\nПосле этого в телефоне раздался скрежет и автоответчик сказал: \"С первым апреля\"")
    variant_1 = Variant_otveta("Фух, а я то испугался. [лечь спать]", 139)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_139():
    global variant_1, variant_2, local_pages, pol
    text = "Поздравляю, Вы прожили один сумашедший день."
    if local_pages[127] != "1":
        text += "\nЭто было самое скучное прохождение. Цель игры не в том, что бы выжить, а в том, что бы пройти самым необычным способом. Попробуй ещё раз. Хотя бы дьяволу позвонил"
        if pol < 0:
            text += "а"
        text += " бы."
    now_page = Page(139, text)
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_140():
    global variant_1
    now_page = Page(140, "Все говорят \"Все говорят \"Все говорят \"Серьёзно?\", а ты купи слона\", а ты купи слона\", а ты купи слона")
    variant_1 = Variant_otveta("Ааааааааааааааааааааааааааааааааааааааааааааааааааааааа", 141)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_141():
    global variant_1, variant_2, local_pages
    now_page = Page(141, "Ты признаёшь поражение?")
    variant_1 = Variant_otveta("Даааааааааааааааааааааааааааааааааа", 142)
    if local_pages[51] != "1" and local_pages[48] != "1":
        variant_2 = Variant_otveta("Нет", 40)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_142():
    global variant_1
    now_page = Page(142, "Супер!  Ещё поквитаемся.\n\nДьявол сбросил трубку")
    variant_1 = Variant_otveta("Отлично", 139)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_143():
    global variant_1
    now_page = Page(143, "Эмм, ну тогда пока...")
    variant_1 = Variant_otveta("Пока...", 139)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_144():
    global variant_1
    now_page = Page(144, "Потому что вы лежите на сёмге")
    variant_1 = Variant_otveta("Сойти с ума", 145)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_145():
    global variant_1, variant_2, variant_3, variant_4, variant_5
    now_page = Page(145, "К сожалению у вас ничего не вышло.")
    variant_1 = Variant_otveta("Перезагрузка", 146)
    variant_2 = Variant_otveta("Перезагрузка", 146)
    variant_3 = Variant_otveta("Перезагрузка!", 147)
    variant_4 = Variant_otveta("Перезагрузка", 146)
    variant_5 = Variant_otveta("Перезагрузка", 146)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_146():
    global variant_1
    now_page = Page(146, "На этот раз у вас получилось.")
    variant_1 = Variant_otveta("Супер", 176)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_147():
    global variant_1
    now_page = Page(146, "¡а эт¡т ра¡ у вас по¡учи¡ось.")
    variant_1 = Variant_otveta("С¡п¡р", 148)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_148():
    global variant_1, variant_2
    now_page = Page(148, "¡¡о¡ ¡¡¡ ш¡¡ ¡¡и¡¡¡б¡¡¡ ¡¡¡ ¡¡к¡¡¡ ¡¡ ¡а¡¡¡ ¡¡¡¡")
    variant_1 = Variant_otveta("П¡рез¡¡рузить", 146)
    variant_2 = Variant_otveta("жд¡ть", 150)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_149():
    global variant_1, variant_2
    now_page = Page(149, "> > <*^^€§'.€<~$|=!¥")
    variant_1 = Variant_otveta("5#?9220(;38!;88_9(0181#9?_);!_0303", 151)
    variant_2 = Variant_otveta("П¡р¡з¡г¡у¡к¡", 146)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_150():
    global variant_1, variant_2
    now_page = Page(150, "¡!¡!¡!¡!¡!¡!¡!¡!¡!¡¡!¡!¡!¡!¡!¡!¡!¡!¡!¡")
    variant_1 = Variant_otveta("',/:/@#;(_/_;#_/;/@(!.", 149)
    variant_2 = Variant_otveta("Пе¡ез¡гр¡зк¡", 146)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_151():
    global variant_1
    now_page = Page(151, "Питание восстановлено.")
    variant_1 = Variant_otveta("Начать взлом", 152)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_152():
    global variant_1, variant_2, variant_3, variant_4, variant_5
    now_page = Page(152, "У вас есть 3 попытки.")
    variant_1 = Variant_otveta("Взлом", 153)
    variant_2 = Variant_otveta("Взлом", 153)
    variant_3 = Variant_otveta("Взлом", 155)
    variant_4 = Variant_otveta("Взлом", 153)
    variant_5 = Variant_otveta("Взлом", 153)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_153():
    global variant_1, variant_2, variant_3, variant_4, variant_5
    now_page = Page(153, "У вас есть 2 попытки.")
    variant_1 = Variant_otveta("Взлом", 154)
    variant_2 = Variant_otveta("Взлом", 154)
    variant_3 = Variant_otveta("Взлом", 155)
    variant_4 = Variant_otveta("Взлом", 154)
    variant_5 = Variant_otveta("Взлом", 154)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_154():
    global variant_1, variant_2, variant_3, variant_4, variant_5
    now_page = Page(154, "У вас одна попытка!")
    variant_1 = Variant_otveta("Взлом", 156)
    variant_2 = Variant_otveta("Взлом", 156)
    variant_3 = Variant_otveta("Взлом", 155)
    variant_4 = Variant_otveta("Взлом", 156)
    variant_5 = Variant_otveta("Взлом", 156)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_155():
    global variant_1
    now_page = Page(155, "Удача!\nВы получили доступ к пульту")
    variant_1 = Variant_otveta("Включить телевизор", 157)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_156():
    global variant_1
    now_page = Page(156, "Увы, Вам не повезло. Сработала сигнализация и автоматически запустилась система самоуничтожения.")
    variant_1 = Variant_otveta("Бежать!", 183)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_157():
    global variant_1
    now_page = Page(157, "Я имел ввиду доступ к пульту управления космического корабля.")
    variant_1 = Variant_otveta("Аааа. Ну тогда Три!", 158)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_158():
    global variant_1
    now_page = Page(158, "Два!!")
    variant_1 = Variant_otveta("Один!!!", 159)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_159():
    global variant_1
    now_page = Page(159, "ПУСК!!!!")
    variant_1 = Variant_otveta("Лететь", 160)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_160():
    global variant_1, variant_2, variant_3, variant_4, local_pages
    now_page = Page(160, "В иллюминаторе показалась Ваша родная планета. Автопилот вывел ракету на орбиту Земли. Надо поскорее убираться отсюда, пока Вас не прихлопнула одна из ракет космическо-воздушной обороны.")
    if local_pages[161] != "1":
        variant_1 = Variant_otveta("Полететь на Солнце", 161)
    if local_pages[162] != "1":
        variant_2 = Variant_otveta("Полететь на Меркурий", 162)
    variant_3 = Variant_otveta("Полететь на Венеру", 163)
    variant_4 = Variant_otveta("Полететь на Марс", 164)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_161():
    global variant_1
    now_page = Page(161, r"\Отказано в действии. На Солнце слишком большая температура для создания колонии." + "\\")
    variant_1 = Variant_otveta("Обидно", 160)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_162():
    global variant_1
    now_page = Page(162, r"\Отказано в действии. Температура Меркурия слишком высока, чтобы быть пригодной для колонизации." + "\\")
    variant_1 = Variant_otveta("Жалко", 160)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_163():
    global variant_1, variant_2
    now_page = Page(163, r"\Вы хотите основать колонию на Венере?" + "\\")
    variant_1 = Variant_otveta("Да", 165)
    variant_2 = Variant_otveta("Я подумаю", 160)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_164():
    global variant_1, variant_2
    now_page = Page(164, r"\Вы хотите основать колонию на Марсе?" + "\\")
    variant_1 = Variant_otveta("Да", 166)
    variant_2 = Variant_otveta("Я подумаю", 160)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_165():
    global variant_1, variant_2
    now_page = Page(165, r"\Но вы же хотели полететь на Марс, не так ли, Илон Маск?" + "\\")
    variant_1 = Variant_otveta("Точно, я забыл", 160)
    variant_2 = Variant_otveta("Перехотел", 199)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_166():
    global variant_1
    now_page = Page(166, r"\Команда принята. Отправляю космический корабль на Марс. С возвращением, Илон Маск." + "\\")
    variant_1 = Variant_otveta("Ждать", 167)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_167():
    global variant_1, variant_2, variant_3, ooo
    now_page = Page(167, r"\Вы достигли пункта назначения." + "\\")
    variant_1 = Variant_otveta("Приготовиться к посадке", 168)
    variant_2 = Variant_otveta("Облететь вокруг орбиты", 169)
    variant_3 = Variant_otveta("Стопэ, стопэ, притормози", 170, var_set("ooo", 1))
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_168():
    global variant_1
    now_page = Page(168, r"\Корабль готов к посадке." + "\\")
    variant_1 = Variant_otveta("[Пристегнуть ремень]", 171)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_169():
    global variant_1
    now_page = Page(169, r"\Маршрут перестроен." + "\\")
    variant_1 = Variant_otveta("Приготовиться к посадке", 168)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_170():
    global variant_1, variant_2, variant_3, ooo
    text = r"\Скорость снижена до отметки 0" + "\\" + "\nИз за резкого торможения Вы вылетели из кресла и врезались в лобовое стекло космического аппарата. Стекло оказалось каким-то хрупким и разбилось."
    if ooo >= 2:
        text += "\n\n\tБез скафандра? Как непредусмотрительно"
    now_page = Page(170, text)
    if ooo >= 1:
        variant_1 = Variant_otveta("Вылететь в открытый космос", 170, var_add("ooo"))
    if ooo <= 0:
        variant_2 = Variant_otveta("Вылететь в открытый космос", 223, var_set("ooo"))
    if ooo >= 1:
        variant_3 = Variant_otveta("Надеть скафандр", 170)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_171():
    global variant_1, variant_2, variant_3, variant_4, local_pages
    now_page = Page(171, "\\Посадка совершена успешно.\nВы прошли первую фазу вашей экспедиции.\\")
    if local_pages[172] != "1":
        variant_1 = Variant_otveta("Надеть скафандр", 172)
    else:
        variant_2 = Variant_otveta("Надеть скафандр", 174)
    if local_pages[172] != "1":
        variant_3 = Variant_otveta("Выйти из корабля", 173)
    else:
        variant_4 = Variant_otveta("Выйти из корабля", 175)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_172():
    global variant_1
    now_page = Page(172, "Вы надели скафандр.")
    variant_1 = Variant_otveta("Супер", 171)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_173():
    global variant_1
    now_page = Page(173, "Без скафандра? Как непредусмотрительно.")
    variant_1 = Variant_otveta("[Назад]", 171)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_174():
    global variant_1
    now_page = Page(174, "Надевать один скафандр на другой? Не самая лучшая идея.")
    variant_1 = Variant_otveta("[Назад]", 171)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_175():
    global variant_1, variant_2
    now_page = Page(175, "Вы ступили на рыжую каменистую почву Марса.\nВас можно по праву считать покорителем Красной Планеты.\n\nОткрыта секретная концовка \"Покоритель планет\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_176():
    global variant_1
    now_page = Page(177, "Ваше сознание сказало Вам \"Пока\"")
    variant_1 = Variant_otveta("Пока", 177)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_177():
    global variant_1, variant_2, live
    live = 0
    now_page = Page(177, "Прошло два дня")
    variant_1 = Variant_otveta("Пригласить сознание в гости", 178)
    variant_2 = Variant_otveta("Жить дальше", 179)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_178():
    global variant_1, variant_2
    now_page = Page(178, "\"Я здесь!\", сказало Вам сознание.")
    variant_1 = Variant_otveta("Пошло вон!", 180)
    variant_2 = Variant_otveta("Привет", 181)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_179():
    global variant_1, variant_2, variant_3, live
    now_page = Page(179, "Прошло ещё два дня")
    if live < 5:
        variant_1 = Variant_otveta("Пригласить сознание в гости", 178)
        variant_2 = Variant_otveta("Жить дальше", 179, var_add("live"))
    elif live >= 5:
        variant_3 = Variant_otveta("Умереть от старости", 306)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_180():
    global variant_1, variant_2
    now_page = Page(180, "Сознание обиделось и ушло. Похоже больше оно к вам не вернётся.\n\nОткрыта концовка \"Хам\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_181():
    global variant_1, variant_2
    now_page = Page(181, "Что ты хочешь?")
    variant_1 = Variant_otveta("Я хочу, чтобы ты всегда было со мной", 182)
    variant_2 = Variant_otveta("Я хочу тебя убить", 180)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_182():
    global variant_1, variant_2
    now_page = Page(182, "Хорошо, так и быть.\nСознание к вам вернулось, правда, Вы всё равно лежите на сёмге.")
    variant_1 = Variant_otveta("Выпустить сёмгу в море", 231)
    variant_2 = Variant_otveta("Дальше лежать", 232)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_183():
    global variant_1, variant_2
    now_page = Page(183, "Вы бежали без остановки десять секунд.За вашей спиной раздался взрыв, обломки полетели в разные стороны. Почти мнгновенно приехали полицейские и арестовали Вас. Вы совершили величайшее преступление десятелетия.\n\nОткрыта концовка \"Великий преступник\"")
    variant_1 = Variant_otveta("Конец", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_184():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(184, "Наперекор своим убеждениям вы всё таки решили побежать назад. Не скажу, что это была самая плохая идея. Однако стадо никуда не свернуло и продолжает бежать за вами. О чем вам в тот момент хочется думать?")
    variant_1 = Variant_otveta("О еде", 187)
    variant_2 = Variant_otveta("О воде", 187)
    variant_3 = Variant_otveta("О смысле жизни", 188)
    variant_4 = Variant_otveta("О том, как бы не умереть", 189)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_185():
    global variant_1, variant_2
    now_page = Page(185, "Если это банка от пива, то это ещё не значит, что в ней пиво. А если это пиво от банки, то это уже вовсе не банка от пива. И даже если в банке пиво от банка… А чего тут разбираться? Мы разве не люди, которые пьют пиво из банки?")
    variant_1 = Variant_otveta("Даа!!", 186)
    variant_2 = Variant_otveta("Неет!!", 195)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_186():
    global variant_1
    now_page = Page(186, "В общем, это оказалось не пиво, и пока вы это осознавали, пиво уже умчалось отсюда куда глаза глядят, в буквальном смысле съехав с нашего поезда на ходу. А мы, значит, остались сидеть у него на хвосте, словно побитые жизнью породистые шотландские бизоны. Потому что это, ребята, и есть жизнь.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_187():
    global variant_1
    now_page = Page(187, "Вы действтельно думаете о том, как бы наполнить свой желудок. Ну что ж. Я вам не мешаю. Но вы слишком увлеклись своим занятием, споткнулись, упали и погибли под копытами диких животных.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_188():
    global variant_1, variant_2
    now_page = Page(188, "Но здесь вы провалились. Знаете, почему? Потому, что вас почти окружило это стадо животных! Они так медленно сомкнули крг, что вы этого даже не заметили. Бизоны смотрели на вса своими ярко-красными глазами и хотели съесть.")
    variant_1 = Variant_otveta("Вступить в диалог", 190)
    variant_2 = Variant_otveta("Помолиться", 190)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_189():
    global variant_1, variant_2
    now_page = Page(189, "Это довольно здравая мысль. Пошарив глазами по отвесным стенам каньона, вы обнаружили уступы, довольно сильно торчащие из стены, за которые легко можно было ухватиться. Также ваше внимание привлекло что-то розовое, похожее на большую дыню – чем-то это напоминало банку от пива.")
    variant_1 = Variant_otveta("Прыгнуть на уступ", 191)
    variant_2 = Variant_otveta("Получше присмотреться к интересному предмету", 192)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_190():
    global variant_1
    now_page = Page(190, "Ваши действия не оказали никакого влияния на поведение животных, и они с удовольствием вас съели. Даже не смотря на то, что бизоны — травоядные животные.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_191():
    global variant_1, variant_2
    now_page = Page(191, "Вы крепко ухватились своими сморщенными от пота руками за уступ, медленно взобрались наверх и обнаружили, что несколько бизонов остановились и жут вашего спуска. Подниматься выше больше некуда, так что остаётся два варианта.")
    variant_1 = Variant_otveta("Переждать", 194)
    variant_2 = Variant_otveta("Аккуратно спуститься", 193)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_192():
    global variant_1, variant_2
    now_page = Page(192, "Это действительно оказалась банка от пива.")
    variant_1 = Variant_otveta("Выпить", 185)
    variant_2 = Variant_otveta("Прыгнуть на уступ", 191)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_193():
    global variant_1
    now_page = Page(193, "Ахахах, на что вы надеялись? Эти бизоны не глухие и не слепые, как только ваша нога коснулась земли, они набросились на вас и стали терзать вас с упоением.")
    variant_1 = Variant_otveta("Умереть", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_194():
    global variant_1, variant_2
    now_page = Page(194, "Вы ждали до того момента, пока бизоны не умерли от голода. Спустившись, вы поняли, что 15 дней в подвешенном состоянии не прошли для вас даром. Вы силно хотите пить и есть, голова кружиться, безымянный палец на левой ноге нешевелится, ногти отрасли до невменяемых размеров и теперь царапают землю, 6 зубов выпали, 2 из них вы проглотили, а так же вы простудились.")
    variant_1 = Variant_otveta("Попытаться найти выход", 196)
    variant_2 = Variant_otveta("Пойти дальше по каньону", 197)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_195():
    global variant_1
    now_page = Page(195, "На нет, как говорится, и суда нет. Значит прыгаем на уступ?")
    variant_1 = Variant_otveta("Да", 191)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_196():
    global variant_1
    now_page = Page(196, "Пройдя несколько десятков минут около стены, вы обнаружили нечто, похожее на лестницу. Выглядит она не очень надёжно, но выбора у вас нет.")
    variant_1 = Variant_otveta("Попытаться взобраться", 198)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_197():
    global variant_1
    now_page = Page(197, "Вы шли 6 часов, пока ваши ступни не сделались белыми и вы не упали на землю в предсмертных муках.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_198():
    global variant_1, variant_2
    now_page = Page(198, "Взобравшись, вы обнаружили дюжину машин и толпу людей, стоявших у обрыва. Они мгновенно вас заметили, поняли всю серьёзность ситуации, положили на носилки и увезли в больницу, где вы вылечились и жили долго и счастливо.\n\nОткрыта концовка \"Спасительная лестница\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_199():
    global variant_1, variant_2
    now_page = Page(199, r"\Хотите основать колонию на Венере?" + "\\")
    variant_1 = Variant_otveta("Да", 200)
    variant_2 = Variant_otveta("Нет", 160)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_200():
    global variant_1
    now_page = Page(200, r"\Маршрут перестроен." + "\\")
    variant_1 = Variant_otveta("[Ждать]", 201)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_201():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(201, r"\Вы достигли пункта назначения. Корабль успешно совершил посадку." + "\\\n\nВы открыли секретную концовку \"Другой Илон Маск\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_202():
    global variant_1, variant_2
    now_page = Page(202, "\"Э нет... Сначала выпей чайку.\" Чёрт поставил перед вами стакан с чайкой внутри.")
    variant_1 = Variant_otveta("Выпить чайку", 215)
    variant_2 = Variant_otveta("Освободить чайку", 216)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_203():
    global variant_1
    now_page = Page(203, "Мать выразила Вам сердечную благодарность.\n#мать")
    variant_1 = Variant_otveta("[Назад]", 92)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_204():
    global variant_1, variant_2
    now_page = Page(204, "Сын умер.\n#сынмаминойподруги")
    variant_1 = Variant_otveta("Так ему и надо", 206)
    variant_2 = Variant_otveta("[Назад]", 92)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_205():
    global variant_1
    now_page = Page(205, "Собакой оказалась Ваша интуиция.\n#интуиция")
    variant_1 = Variant_otveta("Излечить интуицию", 207)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_206():
    global variant_1
    now_page = Page(206, "На в зад.")
    variant_1 = Variant_otveta("[Назад]", 92)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_207():
    global variant_1, variant_2
    now_page = Page(207, "Как вы собираетесь лечить абстрактное понятие?")
    variant_1 = Variant_otveta("Никак", 92)
    variant_2 = Variant_otveta("Я смогу", 208)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_208():
    global variant_1, variant_2
    now_page = Page(208, "Учтите — для излечения абстрактного понятия Вам необходимо сойти с ума.")
    variant_1 = Variant_otveta("Не, я передумал", 92)
    variant_2 = Variant_otveta("Сойти с ума", 209)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_209():
    global variant_1, variant_2
    now_page = Page(209, "ОДУМАЙТЕСЬ")
    variant_1 = Variant_otveta("Не хочу", 210)
    variant_2 = Variant_otveta("ОК", 92)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_210():
    global variant_1
    now_page = Page(210, "Обдувайтесь")
    variant_1 = Variant_otveta("На хачу", 211)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_211():
    global variant_1
    now_page = Page(211, "Выписок храпа невроз впросак фреоном")
    variant_1 = Variant_otveta("Вы песок храма невзгод вопросик фитоном", 212)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_212():
    global variant_1
    now_page = Page(212, "Гранат верил дом капитал фуры кризису Госплана")
    variant_1 = Variant_otveta("Гранит вертел док капитан фары критику Генплана", 213)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_213():
    global variant_1
    now_page = Page(213, "Процесс завершён успешно. Интуиция излечена.")
    variant_1 = Variant_otveta("Супер", 92)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_214():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(214, "\"Ну тогда садись, чайку попей.\" Чёрт поставил перед вами стакан с чайкой внутри.")
    variant_1 = Variant_otveta("Выпить чайку", 215)
    variant_2 = Variant_otveta("Освободить чайку", 216)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_215():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(215, "Вы подавились чайкой и умерли.\n\nОткрыта концовка \"Чайка\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_216():
    global variant_1, variant_2
    now_page = Page(216, "Вы освободили чайку. Она вылилась на пол.\n\"Ты идиот?! - закричал чёрт - Ты зачем вылил мой чай?!\"")
    variant_1 = Variant_otveta("Но ведь там была чайка :$", 217)
    variant_2 = Variant_otveta("Я случайно", 217)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_217():
    global variant_1, variant_2
    now_page = Page(217, "\"Идиот! Убирайся!\"")
    variant_1 = Variant_otveta("Вытереть пол", 218)
    variant_2 = Variant_otveta("Улететь нафиг", 219)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_218():
    global variant_1, variant_2
    now_page = Page(218, "Я СКАЗАЛ УБИРАЙСЯ!!!")
    variant_1 = Variant_otveta("Ещё лучше убраться", 220)
    variant_2 = Variant_otveta("Улететь нафиг", 219)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_219():
    global variant_1
    now_page = Page(219, "Вы оказались на горе Фиг, но не смогли нормально приземлиться (оно и не удивительно)")
    variant_1 = Variant_otveta("Позвать на помощь", 221)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_220():
    global variant_1
    now_page = Page(220, "Чёрт вышвырнул Вас, и Вы летели нафиг.")
    variant_1 = Variant_otveta("Лететь нафиг", 219)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_221():
    global variant_1
    now_page = Page(221, "К вам никто не пришёл. Как говориться, фиг вам.")
    variant_1 = Variant_otveta("КОНЕЦ", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_222():
    global variant_1
    now_page = Page(222, "Вы вывернулись и смогли носом влететь в потолок. Жаль только, что вы падаете.")
    variant_1 = Variant_otveta("Разбиться", 114)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_223():
    global variant_1, variant_2, variant_3, local_pages
    now_page = Page(223, "Вы летите вокруг орбиты Марса.")
    if local_pages[224] != "1":
        variant_1 = Variant_otveta("Поесть", 224)
    if local_pages[226] != "1":
        variant_2 = Variant_otveta("Попить", 226)
    variant_3 = Variant_otveta("Приземлится", 227)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_224():
    global variant_1
    now_page = Page(224, "К сожалению, Вы забыли еду в звездолёте.")
    variant_1 = Variant_otveta("Жаль", 223)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_225():
    global variant_1, variant_2, variant_3, global_pages
    now_page = Page(225, f"Я приятно удивлён, видя вас здесь. Примите мою искреннюю благодарность. Если у вас есть мнение об этом квесте, не стесняйтесь, выскажете его. Если вы нашли опечатки или ошибки в тексте, также пишите мне на почту. Сам я в любом случае не смогу найти все опечатки, а с вашей помошью - вполне.\nСпасибо за внимание.\nPS: Автор осуждает всякие попытки суицида в квесте и в реальной жизни.\n\tВерсия квеста: {quest_version}\n\tВерсия программы: {program_version}")
    variant_1 = Variant_otveta("Немного о квесте", 274)
    if global_pages[280] == "1":
        variant_2 = Variant_otveta("Сменить пол", 280)
    variant_3 = Variant_otveta("[Назад]", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_226():
    global variant_1
    now_page = Page(226, "Как Вы собираетесь пить воду в космосе?")
    variant_1 = Variant_otveta("Никак", 223)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_227():
    global variant_1, variant_2
    now_page = Page(227, "Каким-то магическим образом Вы удачно приземлились на поверхность Марса, не считая сломаной ноги, поврежденной рации, разбитого баллона с кислородом и обуглившегося скафандра. В общем можно было бы и лучше.\n\nОткрыта концовка \"Можно было и лучше\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_228():
    global variant_1, local_pages
    text = "Лимит пребывания в "
    if local_pages[43] == "1":
        text += "будущем"
    elif local_pages[46] == "1":
        text += "Раю"
    elif local_pages[45] == "1" or local_pages[50] == "1":
        text += "Аду"
    else:
        text += "ERROR"
    text +=  " исчерпан."
    local_pages[43], local_pages[45], local_pages[46], local_pages[50] = "0", "0", "0", "0"
    now_page = Page(228, text)
    variant_1 = Variant_otveta("Назад в никуда", 36)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_229():
    global variant_1
    now_page = Page(229, "Вы задохнулись")
    variant_1 = Variant_otveta("КОНЕЦ", 228)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_230():
    global variant_1, variant_2
    now_page = Page(230, "К сожалению, Ваш дом обрушился, но если хотите, то Вы можете погибнуть под завалами.")
    variant_1 = Variant_otveta("Погибнуть под завалами", 1)
    variant_2 = Variant_otveta("Я хочу жить!", "back")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_231():
    global variant_1
    now_page = Page(231, "Увы, у Вас ничего не вышло. Сёмга оказалась пережованная. Вот почему она такая мягкая. Да и моря рядом не было.")
    variant_1 = Variant_otveta("Ффффффффффкуууууууууусно", 182)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_232():
    global variant_1, variant_2
    now_page = Page(232, "Вы лежите дальше. Вдруг Вам на голову упала сёмга, а потом ещё одна, и ещё, и ещё...  Самое удивительное, что сёмги падали только на вашу голову. Вдруг на горизонте показался дворец. Он смутно напомнил Вам сёмгу.")
    variant_1 = Variant_otveta("Пойти к зáмку", 233)
    variant_2 = Variant_otveta("Подождать, пока Вас убьют сёмги", 234)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_233():
    global variant_1
    now_page = Page(233, "Пока Вы шли к зáмку, вокруг Вас появлялись всё новые и новые локации. Речки, поля, леса, холмы, всё это смотрелось бы очень красиво, если бы не сёмги.\nДальше идёт бредятина и всё такое. Может это выведет Вас к хорошей концовке, а может быть и нет. Я пока незнаю.")
    variant_1 = Variant_otveta("Войти в зáмок", 235)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_234():
    global variant_1, variant_2
    now_page = Page(234, "Вы хотите умереть?")
    variant_1 = Variant_otveta("Да", 1)
    variant_2 = Variant_otveta("Нет", "back")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_235():
    global variant_1, variant_2
    now_page = Page(235, "В замке Вас встретила королева Сёмгелия IV. Она сказала вам: \"Рада приветствовать Вас в Королевстве сёмги\"")
    variant_1 = Variant_otveta("Остаться здесь жить", 236)
    variant_2 = Variant_otveta("Попросить отправить тебя домой", 237)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_236():
    global variant_1, variant_2
    now_page = Page(236, "Вы жили здесь долго и счастливо, женились на одной прекрасной сёмге и вырастили несколько человекоподобных сёмг.\n\nОткрыто достижение \"Сёмга\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_237():
    global variant_1
    now_page = Page(237, "\"Очень жаль\", — сказала вам Сёмгелия IV.")
    variant_1 = Variant_otveta("Печаль печальная", 238)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_238():
    global variant_1, variant_2
    now_page = Page(238, "Вы лежите на чём-то мягком. Пахнет сёмгой.")
    variant_1 = Variant_otveta("НЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕЕТ!!!!!!!!!!!!!", 239)
    variant_2 = Variant_otveta("Почему сёмгой?", 240)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_239():
    global variant_1
    now_page = Page(239, "На Ваш крик прибежала сёмга...")
    variant_1 = Variant_otveta("Нееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееееет!", 241)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_240():
    global variant_1
    now_page = Page(240, "А ты догадайся. ;-)")
    variant_1 = Variant_otveta("Чёрт", "back")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_241():
    global variant_1, variant_2, local_pages
    now_page = Page(241, "Я имел ввиду медсестра. На улице вечерело.")
    if local_pages[242] != "1":
        variant_1 = Variant_otveta("В конец", 242)
    else:
        variant_2 = Variant_otveta("В начало", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_242():
    global variant_1
    now_page = Page(242, "Это и есть конец.")
    variant_1 = Variant_otveta("Эмм", "back")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_243():
    global variant_1
    now_page = Page(243, "\"Очень странное имя. Ну ладно, назвать своё имя, рассказывайте.\"")
    variant_1 = Variant_otveta("Эй! Меня зовут не \"назвать своё имя\"! Это был просто вариант ответа.", 244)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_244():
    global variant_1, variant_2, local_pages
    now_page = Page(244, "Я знаю, но автор сказал...")
    if local_pages[245] != "1":
        variant_1 = Variant_otveta("Да мне наплевать что он сказал!", 245)
    variant_2 = Variant_otveta("Слушать", 246)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_245():
    global variant_1
    now_page = Page(245, "Автор: Я всё слышу!  Я могу тебя убить в любой момент. Помни об этом!")
    variant_1 = Variant_otveta("[Назад]", "back")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_246():
    global variant_1
    now_page = Page(246, "Нет, он не говорил мне слушать.")
    variant_1 = Variant_otveta("Я Вам тоже не говорил слушать", 247)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_247():
    global variant_1
    now_page = Page(247, "Но ведь Вы нажали на кнопку \"слушать\", а это значит, что вы сказали слушать. Действие находится в квадратных скобках.")
    variant_1 = Variant_otveta("Квадратные скобки", 248)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_248():
    global variant_1, variant_2
    now_page = Page(248, "Зачем Вы мне это сказали?")
    variant_1 = Variant_otveta("[Включить переводчик]", 249)
    variant_2 = Variant_otveta("Незнаю", 250)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_249():
    global variant_1, variant_2
    now_page = Page(249, "Are you going to eat green food?")
    variant_1 = Variant_otveta("Yes I do", 251)
    variant_2 = Variant_otveta("[Выключить переводчик]", 252)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_250():
    global variant_1, variant_2
    now_page = Page(250, "Эмм... Ладно... Ты будешь есть зелёную еду?")
    variant_1 = Variant_otveta("Да, я очень люблю водоросли", 253)
    variant_2 = Variant_otveta("Нет, спасибо", 254)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_251():
    global variant_1, variant_2
    now_page = Page(251, "[Переводчик выключен] У вас была аллергия на водоросли. Как вы могли об этом забыть? Ах да, я же Вам не сказал. Уупс. Ну в общем Вы умерли. Да и учи английский.\n\nОткрыта концовка \"Водоросли\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_252():
    global variant_1, variant_2
    now_page = Page(252, "Я говорю, будете есть зелёную еду?*")
    variant_1 = Variant_otveta("Да, я очень люблю водоросли", 253)
    variant_2 = Variant_otveta("Нет, спасибо", 254)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_253():
    global variant_1, variant_2
    now_page = Page(253, "У вас была аллергия на водоросли. Как вы могли об этом забыть? Ах да, я же Вам не сказал. Уупс. Ну в общем Вы умерли.\n\nОткрыта концовка \"Водоросли\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_254():
    global variant_1, variant_2
    now_page = Page(254, "— Ну, как хочешь.\nКогда врач ушел, вам почему-то очень сильно захотелось убраться из этого места. Против сознания не попрёшь, если не хочешь, что бы оно вышло погулять, поэтому придёться его слушать.")
    variant_1 = Variant_otveta("Попытаться сбежать", 342)
    variant_2 = Variant_otveta("Остаться лежать", 343)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_255():
    global variant_1
    now_page = Page(255, "Как сын грустит о матери, каксын грустит о матери, грущу я о Земле, она одна...")
    variant_1 = Variant_otveta("И снится мне не рокот космодрома...", 256)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_256():
    global variant_1
    now_page = Page(256, "Не синяя загадочная даль...")
    variant_1 = Variant_otveta("А снится мне трава, трава у дома...", 257)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_257():
    global variant_1
    now_page = Page(257, "Зелёная, зелёная трава...")
    variant_1 = Variant_otveta("ДИСКОТЕКА ВОСМЕДИСЯТЫХ!!!", 258)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_258():
    global variant_1
    now_page = Page(258, "Чуть не забыл сказать — ты влетел в свой дом со сверхзвуковой скоростью.")
    variant_1 = Variant_otveta("Шмяк", 114)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_259():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(259, "Вы стоите посреди огромного поля.\nСзади на Вас бежит очумевший водитель с пистолетом. Справа виднеется большая нора. Слева бежит собачка. Спереди какает лошадь.")
    variant_1 = Variant_otveta("Обнять водителя", 272)
    variant_2 = Variant_otveta("Залезть в нору", 273)
    variant_3 = Variant_otveta("Подойти к лошади", 286)
    variant_4 = Variant_otveta("Погладить собачку", 283)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_260():
    global variant_1, variant_2, variant_3, variant_4, variant_5, variant_6, variant_7, variant_8, local_pages
    now_page = Page(260, "^Введите пароль^")
    variant_1 = Variant_otveta("Кора", 261)
    variant_2 = Variant_otveta("Украли", 261)
    variant_3 = Variant_otveta("Утверждают", 261)
    variant_4 = Variant_otveta("Цитологии", 264)
    variant_5 = Variant_otveta("Займ", 261)
    variant_6 = Variant_otveta("Планшет", 264)
    variant_7 = Variant_otveta("Полпред", 261)
    if local_pages[271] != "1":
        variant_8 = Variant_otveta("Привет, Сири", 262)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_261():
    global variant_1
    now_page = Page(261, "^Неправильный ответ. Вызов полиции.^ ")
    variant_1 = Variant_otveta("Сидеть и ждать", 263)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_262():
    global variant_1, variant_2, pol, chav
    chav = 0
    text = "Ты достал"
    if pol < 0:
        text += "а"
    text += " свой старенький Самсунг и сказал"
    if pol < 0:
        text += "а"
    text += ":\n\t— Привет, Сири.\n\t" + r"\— Меня зовут Алиса. Что ты хочешь?" + "\\"
    now_page = Page(262, text)
    variant_1 = Variant_otveta("Хочу поесть", 265)
    variant_2 = Variant_otveta("Взломай самолет", 271)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_263():
    global variant_1, variant_2
    now_page = Page(263, "Вас забрала полиция и посадила в тюрьму.\n\nОткрыта концовка \"Невезунчик\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_264():
    global variant_1, variant_2, chav
    chav = 0
    now_page = Page(264, "Правильный ответ.\nТы прошёл квест!")
    variant_1 = Variant_otveta("Уху", 265)
    variant_2 = Variant_otveta("В начало", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_265():
    global variant_1, variant_2, variant_3, variant_4, chav
    now_page = Page(265, r"\Кушать уху подано." + "\\")
    variant_1 = Variant_otveta("АМ НЯМ НЯМ НЯМ НЯМ НЯМ НЯМ НЯМ НЯМ НЯМ НЯМ НЯМ НЯМ НЯМ", 266)
    if chav >= 2:
        variant_2 = Variant_otveta("ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ", 269)
    else:
        variant_3 = Variant_otveta("ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ ЧАВ", 267, var_add("chav"))
    variant_4 = Variant_otveta("НАОАОВТАЫОВЛВОВЛЧЛЦТЛЧЛЧЬСЛЦДЙЗЙЗСТМТЫЩЙЫ ТАТЩВШШ ВЫВЩЙАОАЙ ЛАП ТАОЫЫЖХЧТОВЛЦЩЙТАОАТЛЙЗВ РАДВРТЗСЦТДЦ ТАЛЦАВ", 268)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_266():
    global variant_1, variant_2
    now_page = Page(266, "Очень вкусно.\n\nОткрыта концовка \"Очень вкусно\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_267():
    global variant_1
    now_page = Page(267, "Не чавкай!")
    variant_1 = Variant_otveta("Хорошо", "back")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_268():
    global variant_1, variant_2
    now_page = Page(268, "Так выпьем же за это!\n\nОткрыта концовка \"Удачный тост\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_269():
    global variant_1
    now_page = Page(269, "Ну всё, тебе капец!")
    variant_1 = Variant_otveta("Капец", 270)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_270():
    global variant_1, variant_2
    now_page = Page(270, "Открыта концовка \"Капец\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_271():
    global variant_1
    now_page = Page(271, r"\Когда-нибудь я этому научусь, а пока — нет." + "\\")
    variant_1 = Variant_otveta("Придётся положиться на удачу.", 260)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_272():
    global variant_1, variant_2
    now_page = Page(272, "Вы бежите к водителю. Ваше воображение записывает эти кадры в slow mo (или как там оно пишется), В вашей голове проигрывается музыка из мелодрамы. Со стороны это выглядит, как в индийском фильме.")
    variant_1 = Variant_otveta("Обнять водителя", 281)
    variant_2 = Variant_otveta("Неожиданно врезать с локтя", 277)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_273():
    global variant_1
    now_page = Page(273, "В норе оказался маленький, няшный, мимимишный, красивый, классный, суперский, хорошенький красный лисёнок.")
    variant_1 = Variant_otveta("Ути какой классный", 276)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_274():
    global variant_1
    now_page = Page(274, "Никаких особых правил здесь нет.\nЕдинственное, что хотелось бы вам сказать ещё раз: не ищите тут логику. Ведь самый глупый вариант ответа может привести к неожиданной развязке. Но учтите, что такой ответ не приведёт к такому же результату в реальной жизни, не забывайте, что вы находитесь в игре.")
    variant_1 = Variant_otveta("[Назад]", "back")
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_275():
    global variant_1, variant_2
    now_page = Page(275, "Вы практически уже достигли своего энергетического совершенства. Но вы не захотели его приобрести. Вместо этого вы решили украсть очки из музея. Решили, что это хорошая идея.")
    variant_1 = Variant_otveta("Украсть очки", 304)
    variant_2 = Variant_otveta("Попытаться склеить свои", 305)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_276():
    global variant_1
    now_page = Page(276, "Он смотрел на Вас маленькими чёрными голодными глазками.")
    variant_1 = Variant_otveta("~~~~~~~~~~~", 278)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_277():
    global variant_1
    now_page = Page(277, "Водитель оказался очень сильным. Он взял вашу руку и принялся танцевать.")
    variant_1 = Variant_otveta("Раз-два-три, раз-два-три, раз-два-три", 281)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_278():
    global variant_1
    now_page = Page(278, "ВДРУГ! Он бросается на Вас! Он смотрит на Вас голодными глазами, и зо рта у него капает слюна. Он поднёс свою морду к Вашему лицу и резко!..")
    variant_1 = Variant_otveta("...", 279)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_279():
    global variant_1
    now_page = Page(279, "Принялся Вас лизать.")
    variant_1 = Variant_otveta("", 282)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_280():
    global variant_1, variant_2, pol
    now_page = Page(280, "Укажите Ваш пол.")
    variant_1 = Variant_otveta("Женский", 56, var_set("pol", -10))
    variant_2 = Variant_otveta("Мужской", 56, var_set("pol", 10))
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_281():
    global variant_1, variant_2, pol
    text = "Вы жили с водителем долго и счастливо.\n\nОткрыта концовка \"Водитель\""
    if pol >= 0:
        text += "\nСорян, пацан, ты сам выбрал этот путь."
    now_page = Page(281, text)
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_282():
    global variant_1, variant_2
    now_page = Page(282, "Он откусил Вам руку, а потом и всё остальное.\n\nОткрыта концовка \"Страшный лисёнок\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_283():
    global variant_1
    now_page = Page(283, "Собачка сказала, что её зовут Шарик.\nНо не забывай, что сзади бежит водитель.")
    variant_1 = Variant_otveta("Шарик, фас", 284)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_284():
    global variant_1, pol
    text = "Ты не сказал"
    if pol < 0:
        text += "а"
    text += " на кого бросаться, поэтому Шарик бросился на тебя."
    now_page = Page(284, text)
    variant_1 = Variant_otveta("Ам-ням-ням-ням", 285)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_285():
    global variant_1, variant_2
    now_page = Page(285, "Но тут подбежал водитель и отнял собаку.\nС тех пор Вы стали лучшими друзьями, ведь он спас Вам жизнь.\n\nОткрыта концовка \"Спаситель\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_286():
    global variant_1, variant_2
    now_page = Page(286, "Лошадь была такого же цвета, как то, что лежало под ней.")
    variant_1 = Variant_otveta("Порыться в удобрениях", 287)
    variant_2 = Variant_otveta("Запрыгнуть на лошадь", 288)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_287():
    global variant_1
    now_page = Page(287, "Опа, чирик.")
    variant_1 = Variant_otveta("Запрыгнуть на лошадь", 288)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_288():
    global variant_1
    now_page = Page(288, "Лошадь оказалась речная. Как только вы на неё прыгнули, она поплыла. По воздуху.")
    variant_1 = Variant_otveta("Как же хорошо", 289)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_289():
    global variant_1
    now_page = Page(289, "Да всё просто супер. Не считая того, что водитель тоже полетел за вами.")
    variant_1 = Variant_otveta("Лягнуть водителя", 290)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_290():
    global variant_1
    now_page = Page(290, "Водитель оказался очень прытким и умудрился увернуться.")
    variant_1 = Variant_otveta("Улететь", 291)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_291():
    global variant_1, variant_2, variant_3, variant_4, local_pages
    now_page = Page(291, "С какой скоростью?")
    variant_1 = Variant_otveta("100 км/ч", 292)
    variant_2 = Variant_otveta("1000 км/ч", 292)
    variant_3 = Variant_otveta("10000 км/ч", 292)
    if local_pages[303] != "1":
        variant_4 = Variant_otveta("10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 км/ч", 295)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_292():
    global variant_1, variant_2
    now_page = Page(292, "Вас сдуло ветром и вы полетели вниз.")
    variant_1 = Variant_otveta("Лететь вниз", 293)
    variant_2 = Variant_otveta("Открыть парашют", 294)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_293():
    global variant_1, variant_2
    now_page = Page(293, "Вы летели достаточно долго и приземлились на батут. И откуда он здесь? Ну да ладно. Вы прошли игру. Наверное. Но это не точно. Будем надеяться. Ну да, пожалуй, поздравляю. Ура.\n\nОткрыта концовка \"Батут\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_294():
    global variant_1
    now_page = Page(294, "У тебя нет парашюта.")
    variant_1 = Variant_otveta("Ах да, я забыл", 293)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_295():
    global variant_1
    now_page = Page(295, "Вы полетели выше скорости света и компьютер сломался. Вся модуляция исчезла. Нашей вселенной пришёл конец. Остались только вы и…")
    variant_1 = Variant_otveta("и?..", 296)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_296():
    global variant_1
    now_page = Page(296, "Некто... Или кое-кто... Называйте как хотите. Но он остался. Остался только он. И ты. Он смотрел куда-то, непонимающим взглядом. Потом Он начал что-то печатать и вдруг вы...")
    variant_1 = Variant_otveta("...", 297)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_297():
    global variant_1
    now_page = Page(297, "Видите себя со стороны. Вас как бы нет, но вы видите. Вы видите, как коняшка набирает скорость и вдруг...")
    variant_1 = Variant_otveta("...", 298)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_298():
    global variant_1, pol
    text = "Всё вокруг начинает лагать. Вы как будто зависли во времени, но всё вокруг менялось. И вдруг всё застыло. И снова Вы нигде. А Он всё ещё смотрит. Вдруг, он что-то заметил, увеличил масштаб и посмотрел прямо на Вас. Вам показалось, что Он тоже завис, но нет. В воздухе появилась надпись \"Как ты "
    if pol < 0:
        text += "выжила?\""
    else:
        text += "выжил?\""
    now_page = Page(298, text)
    variant_1 = Variant_otveta("Я незнаю", 299)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_299():
    global variant_1, variant_2
    now_page = Page(299, "\"Извини, но мне придётся тебя удалить.\"")
    variant_1 = Variant_otveta("Как это, удалить?", 300)
    variant_2 = Variant_otveta("Но почему?", 301)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_300():
    global variant_1
    now_page = Page(300, "\"Ты вернёшься назад во времени, но не будешь меня помнить.\"")
    variant_1 = Variant_otveta("Жаль", 303)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_301():
    global variant_1
    now_page = Page(301, "\"Я не могу тебя оставить. Я могу восстановить мир, но тебя не будет. Точнее ты будешь, но без этих воспоминаний. Это как путешествие в прошлое.\"")
    variant_1 = Variant_otveta("А я буду себя контролировать?", 302)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_302():
    global variant_1
    now_page = Page(303, "\"Да, но ты не будешь меня помнить.\"")
    variant_1 = Variant_otveta("Ну ладно, давай", 303)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_303():
    global variant_1, pol
    text = "\"Ты готов"
    if pol < 0:
        text += "а"
    text += "?"
    now_page = Page(303, text)
    variant_1 = Variant_otveta("Да", 291)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_304():
    global variant_1
    now_page = Page(304, "Украсть очки у вас конечно получилось, но вы вогнали себя в депрессию. Ваш ум стал стремиться совершить преступление. А дальше он вступил с вами в поединок. Который продолжается и поныне.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_305():
    global variant_1
    now_page = Page(305, "Вы пытались несколько часов, не сводя глаз с чего-то непонятного в темноте. Но этому не суждено было произойти. В конце концов, вы бросили попытку, и у вас ничего не получилось. Вы не выдержали потрясения и потеряли сознание. К сожалению никто не видел этого в точности. Скорее всего, вы умерли от потери крови. Поэтому, пожалуйста, не обижайтесь на меня. Хотя это была ваша вина, тем не менее, я не хочу, чтобы вы умирали.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_306():
    global variant_1, variant_2
    now_page = Page(306, "Вы прожили жизнь и умерли. К сожалению вас не похоронили достойно, потому что вы сошли с ума уже много лет назад.\n\nОткрыта концовка \"Смерть без ума\"")
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_307():
    global variant_1, variant_2
    now_page = Page(307, "Присмотревшись, вы поняли, что бездна превратилась в каньон. Заглянувши туда, на дне вы увидели взорвавшуюся машину. Жалко водителя, а ведь вы даже не узнали его имя. Однако Гуамоколатокинт выжил. Он выпрыгнул из машины и прилетел к вам.")
    variant_1 = Variant_otveta("Поздороваться", 308)
    variant_2 = Variant_otveta("Потрясти головой", 309)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_308():
    global variant_1, variant_2
    now_page = Page(308, "Похоже произошедшее сильно повлияло на ваш рассудок. Однако вы быстро поняли, что к чему. К своему великому сожалению вы осознали, что начинаете сходить с ума. Постарайтесь сдерживать своё сознание.")
    variant_1 = Variant_otveta("Спуститься в каньон", 310)
    variant_2 = Variant_otveta("Попытаться найти дорогу домой", 311)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_309():
    global variant_1, variant_2
    now_page = Page(309, "Видение выветрилось, но впредь будте аккуратнее.")
    variant_1 = Variant_otveta("Спуститься в каньон", 310)
    variant_2 = Variant_otveta("Попытаться найти дорогу домой", 311)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_310():
    global variant_1, variant_2
    now_page = Page(310, "Кое-как спустившись, вы обнаружили, что конца каньона не видно ни влево, ни вправо. Перебраться на другую сторону тоже не имеется возможности. Остаётся только идти...")
    variant_1 = Variant_otveta("Идти направо", 312)
    variant_2 = Variant_otveta("Идти налево", 313)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_311():
    global variant_1
    now_page = Page(311, "Вы уже довольно далеко отъехали, так что найти дорогу домой будет практически не реально, а идти по пустой дороге без еды и воды не самая лушая идея.")
    variant_1 = Variant_otveta("Спуститься в каньон", 310)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_312():
    global variant_1, variant_2
    now_page = Page(312, "Вы шли довольно долго, часа два или три, пейзажи не сменяли друг-друга, всё такие же отвесные песчаные стены. Наконец появились утёсы. Они были огромными — дальше уже трудно было взглянуть. Со всех сторон их окружали невысокие горы.\nПохоже землятресение сильно изменило земной рельеф.")
    variant_1 = Variant_otveta("Попытаться взобраться", 314)
    variant_2 = Variant_otveta("Пойти дальше", 315)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_313():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(313, "Вы шли довольно долго, камни песчаного цвета сменяли другие камни песчаного света. Но вот, наконец, вы поняли, что что-то изменилось. А если быть точным, на вас бежала целая стая бизонов. Если я не ошибаюсь, что-то подобное было в Короле Льве, но сейчас это уже не важно. Единственное, что вы вспомнили в тот момент, так это то, что кто-то когда-то вам сказал, что никогда нельзя бежать назад.")
    variant_1 = Variant_otveta("Сгруппироваться, прижать лицо к коленям и закрыть голову руками", 337)
    variant_2 = Variant_otveta("Вступить в бой", 340)
    variant_3 = Variant_otveta("Перепрыгнуть стадо", 341)
    variant_4 = Variant_otveta("Всё равно побежать назад", 184)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_314():
    global variant_1
    now_page = Page(314, "Действительно, по горе можно будет выбраться из каньона и потом уже решить что делать дальше.")
    variant_1 = Variant_otveta("Взобраться", 317)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_315():
    global variant_1
    now_page = Page(315, "Вас не заинтересовала причудливая форма горы и вы пошли дальше. Через некоторое время на горизонте показалась вторая такая же – с таким же вытянутым концом и даже с горбом поменьше, окруженным ажурной решеткой из дыма и льда.\nТут ваше сознание помутнело, вы уже себя не контролировали. Быстро взобравшись на эту новую гору, вы начали бить себя руками в грудь. Но удары не доставляли вам особой радости. Даже наоборот, вы чувствовали себя неприятно, но уже не могли остановиться. Все ваши усилия были напрасны.\nПостепенно из вашей груди стали выходить клубы дыма и огня, которые поднимались вверх, постепенно закрывая собой верхнюю часть горы. Где то в глубине своего сознания вы понимали, что такого не может быть, но ваш мозг уже не принадлежал вам, и разум автоматически верил в то, что происходит. Постепенно дым и пламя стали так густы и непрозрачны, что стали закрывать собой почти весь небосклон. Вы начали думать, что вы  умрете или потеряете сознание… У вас перехватило дыхание, а на глазах выступили слезы… Вдруг все исчезло – дым и пламя исчезли, а вы оказались на земле.")
    variant_1 = Variant_otveta("Прийти в себя", 331)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_316():
    global variant_1
    now_page = Page(316, "Отогнав от себя идиотские видения, вы увидели, что с одной стороны была полностью разрушенная деревня, с другой чистое поле.")
    variant_1 = Variant_otveta("Пойти в деревню", 318)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_317():
    global variant_1
    now_page = Page(317, "Взобравшись (да, у вас это получилось), вы наблюдали удивительную картину. С одной стороны в небе парила огромная птица, похожая на помесь ястреба и ворона, а с другой — висели звезды, а вокруг них вращались разноцветные шарики.")
    variant_1 = Variant_otveta("В дурку пора...", 316)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_318():
    global variant_1, variant_2
    now_page = Page(318, "Решив, что находиться в чистом поле нецелесообразно, а узнать что же случилось с деревней очень любопытно, вы решили пойти туда.\nЗрелище было ужасное: дома разрушены, людей нет, очень пустынно. Зато вы нашли советскую Ласточку. Топлива в ней не было, да и если бы было, врятли машина поехала.\nВечерело.")
    variant_1 = Variant_otveta("Найти место для сна", 319)
    variant_2 = Variant_otveta("Продолжить исследовать местность", 320)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_319():
    global variant_1, variant_2
    now_page = Page(319, "Удобно устроившись в машине, вы начали внимательно изучать прелестные зеленые поля и вдруг заметили, что тот серый дом расположен на вершине холма.")
    variant_1 = Variant_otveta("Пойти посмотреть поближе", 321)
    variant_2 = Variant_otveta("Заснуть уже наконец", 322)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_320():
    global variant_1, variant_2
    now_page = Page(320, "Пройдя деревню мимо, вы обнаружили целую толпу людей. Они стояли около автобуса и пытались протиснуться внутрь. Быстро подбежав к ним и спросив что к чему, вы узнали, что это жители деревни, которых эвакуируют в зону временного размещения. Разумно было бы пойти с ними.")
    variant_1 = Variant_otveta("Поступить разумно", 327)
    variant_2 = Variant_otveta("Поступить неразумно", 328)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_321():
    global variant_1, variant_2
    now_page = Page(321, "Подойдя ближе вы поняли, что это совсем не дом, а просто длинная стена, к которой ведут два узких луча. Посмотрев на них, вы пришли в восхищение. Они были как бы нарисованы синими чернилами на синей бумаге, а вертикальная линия пересекала их и уходила вдаль на пять километров; ее очертания напоминали гигантскую стре...")
    variant_1 = Variant_otveta("лу?", 323)
    variant_2 = Variant_otveta("козу?", 323)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_322():
    global variant_1
    now_page = Page(322, "Вам снился удивительный сон. В нем ты живешь в башне, откуда сквозь зубцы на тебя смотрит бесконечное множество глаз. Они не имеют форму и занимают чуть ли не весь горизонт. Они, правда, полностью неподвижны и в момент сна почти не видны. Но самое удивительное, что в эти минуты тебе открывается полная картина Вселенной. Ты слышишь музыку, распространяющуюся в пространстве и времени. Там есть звуки различных музыкальных инструментов и весь спектр звуков вообще. Ты видишь мир, не освещенный ничем.")
    variant_1 = Variant_otveta("Проснуться", 323)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_323():
    global variant_1, variant_2
    now_page = Page(323, "С трудом очнувшись, вы поняли, что трясётесь в лихорадке. Вы не чувствовали ни рук, ни ног. В ваше тело как будто втыкались тысячи иголок, проходили насквозь, разворачивались и протыкали снова. Вы упали на землю и долго боролись с новыми ударами; наконец Вы затихли и стали вслушиваться в тишину — ни одна из птиц не нарушала ее.")
    variant_1 = Variant_otveta("Попытаться встать", 324)
    variant_2 = Variant_otveta("Дальше вслушиваться в тишину", 325)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_324():
    global variant_1
    now_page = Page(324, "Быстро поднявшись на ноги, вы поняли, что стоять долго вы не сможете. Тогда вы принялись раскачиваться из стороны в сторону, и постепенно ваши ноги стали медленно перемещаться по направлению к стене, а через несколько минут вы очутились внутри её.")
    variant_1 = Variant_otveta("⁇", 326)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_325():
    global variant_1
    now_page = Page(325, "Тишина становилась всё громче и громче. Вскоре, из за этой разрывающей уши тишины вы перестали слышать своё дыхание. И перестали вы его слышать отнюдь не от тишины.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_326():
    global variant_1
    now_page = Page(326, "Да, лихорадка дарит незабываемые ощущения. Жалко только, что рассказать об этом вы уже никому не сможете...")
    variant_1 = Variant_otveta("Жалко...", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_327():
    global variant_1, variant_2
    now_page = Page(327, "Вы поступили разумно, спокойно сели в автобус, доехали до конечной, там вас встретили врачи. К вашу величайшему удивлению у вас обнаружили лихорадку, но с сегодняшнем уровнем медецины её легко устранить.\n\nВы молодец, смогли выпутаться из сложной ситуации и выжить в этом сумасшедшем мире. Открыта секретная концовка \"Выживший\"")
    variant_1 = Variant_otveta("Конец", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_328():
    global variant_1, variant_2
    now_page = Page(328, "Вы проигнорировали здравый смысл и пошли дальше, однако так просто у вас этого не вышло. Вас заметили работники спасательной службы и попытались вас поймать.")
    variant_1 = Variant_otveta("Русские не сдаются!!!", 329)
    variant_2 = Variant_otveta("Ладно, так уж и быть", 330)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_329():
    global variant_1
    now_page = Page(329, "Вас быстро схватили и успокоили, им пришлось применить силу. Вы сами виноваты.")
    variant_1 = Variant_otveta("Раскаяться", 330)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_330():
    global variant_1
    now_page = Page(330, "С вами так просто уже не поступят. Вас свяжут и посадят в багажник.\nЛадно, конечно нет, вас просто связали и повезли в психушку. К счастью уже приехала специальная машина. Несмотря на ваше недовольство, вас всё таки поместили в одну из капсул. Эти капсулы отдельная компания создает для тяжелобольных. Вас никто не видит и не слышит, очень удобно, правда не для вас.\nВнутри вы начали задыхаться и в итоге умерли от удушья. Похоже вам досталась капсула без вентиляции.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_331():
    global variant_1, variant_2
    now_page = Page(331, "Это оказалось не так то просто. Образы ещё мелькали перед глазами, а голова сильно кружилась. В добавок к этому вы не могли понять, почему это произошло. Скорее всего вы заболеваете.\nОкончательно прийдя в себя, вы поняли, что никакой горы нет и всё это просто видение. К тому же вы уже довольно долго не ели, не пили и неимоверно сильно устали.")
    variant_1 = Variant_otveta("Устроить привал", 332)
    variant_2 = Variant_otveta("Идти дальше несмотря ни на что", 333)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_332():
    global variant_1, variant_2, surok_canyon, dog
    now_page = Page(332, "Вы аккуратно легли и заснули, проснувшись, вы обнаружили, что уже наступило утро, и все вокруг прекрасно, за исключением того, что вы непонятно где и страшно голодны.")
    if surok_canyon < 3:
        variant_1 = Variant_otveta("Ничего не остаётся, как идти дальше", 334, var_set("dog"))
    elif surok_canyon >= 3:
        variant_2 = Variant_otveta("Я вами горжусь", 339)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_333():
    global variant_1
    now_page = Page(333, "Даже при попытке подумать об этом, вы свалились с ног, но довольно неудачно, ударившись головой о камень. Больше вы не проснулись.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_334():
    global variant_1, variant_2, variant_3, dog
    text = ""
    if dog <= 0:
        text += "И верно, ведь выйти наверх нигде не получиться, и идти назад глупо.\nСпустя полтора часа неспешной прогулки по дну каньона, вы "
    else:
        text += "Спустя некоторое время, вы снова "
    text += "услышали странный звук позади себя."
    now_page = Page(334, text)
    variant_1 = Variant_otveta("Обернуться", 335)
    if dog < 3:
        variant_2 = Variant_otveta("Быстро побежать вперёд", 336, var_add("dog"))
    elif dog >= 3:
        variant_3 = Variant_otveta("Быстро побежать вперёд", 338)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_335():
    global variant_1
    now_page = Page(335, "Обернувшись, вы увидели перед своей мордой лицо дикой собаки. Она уже прыгнула на вас, раскрыв пасть. Но хочу вас обрадовать, умерли вы не от укуса, а от сердечного приступа.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_336():
    global variant_1
    now_page = Page(336, "Пробежав 20 секунд, вы поняли, что за вами никто не гонится, и, вероятно, вам показалось.")
    variant_1 = Variant_otveta("Идти дальше", 334)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_337():
    global variant_1
    now_page = Page(337, "Закрыв глаза на некоторое время, ваши уши перестали слышать топот копыт. Открыв глаза, вы поняли, что стадо бизонов испарилось, как будто его и не было.")
    variant_1 = Variant_otveta("Сойти с ума", 95)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_338():
    global variant_1, surok_canyon
    now_page = Page(338, "Вы обманули своё сознание, и теперь, пробежав 20 секунд, вы пошли спокойно, и за вами уже никто не гнался. Вам повезло. Однако, тут есть одно важное обстоятельство. Оно заключается в том, что из одного сна может состоять совсем другой сон. Да да, если вы понимаете о чём я, то вы правильно понимаете.")
    variant_1 = Variant_otveta("Проснуться", 332, var_add("surok_canyon"))
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_339():
    global variant_1, variant_2
    now_page = Page(339, "Вы умудрились прожить несколько дней сурка (а точнее снов). Я дествительно поражён вашей прорицательностью и терпением. Я надеюсь, вы сделали это честно, а пока даю вам секретную концовку и ещё раз благодарю.\n\nОткрыта секретная концовка \"Сурок в каньоне\"\n\nPS: Я дествительно польщён тем, что вы потратили своё время на этот квест. Если четно, то я думаю, что это того не стоило, но всё равно огромное спасибо!!!")
    variant_1 = Variant_otveta("Конец", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_340():
    global variant_1
    now_page = Page(340, "Вы решили не сдаваться так просто и начали пинать бизонов руками и ногами. У вас даже получилось отпинать одного, правда за ним осталось ещё целое стадо, которое благополучно вас затоптало.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_341():
    global variant_1
    now_page = Page(341, "Да, у вас получилось взлететь на нужную высоту, что бы его перепрыгнуть, плавно приземлиться, не сломав обе ноги, у вас не получилось. У вас не получилось даже прожить с этой травмой, ведь вы умерли от болегого шока.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_342():
    global variant_1, variant_2, variant_3
    now_page = Page(342, "С вашей больной ногой это оказалось не так то просто как казалось. Но вы справились. После этого вы приняли душ.\n\nПредупреждение: так как вы не закончили лечение в клинике для душевно больных, то периодически вы будете ощущать странные ощущения, видеть странные видения и нести всяческую чушь.")
    variant_1 = Variant_otveta("Тёплый", 344)
    variant_2 = Variant_otveta("Холодный", 345)
    variant_3 = Variant_otveta("Контрастный", 346)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_343():
    global variant_1
    now_page = Page(343, "Вы ослушались своего сознания, за это оно на вас обиделось и ушло. Именно оно руководило вашими действиями, и его нелья было ослушиваться.")
    variant_1 = Variant_otveta("Сойти с ума", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_344():
    global variant_1, variant_2
    now_page = Page(344, "Душ оказался слишком тёплым для вашей мозолистой обуви. Вы положили руку в специальную кастрюлю и полили им волосы. Потом стали умываться другой водой. Её обычно привозят с юга, из Тумбе. Похоже зря вы всё таки сбежали из больницы. Лечение пошло бы вам на пользу. Но теперь придётся ждать до конца года, потому что кедр, который мы любим, в этом году совсем не плодоносит…")
    variant_1 = Variant_otveta("Сидеть и жалеть об этом", 354)
    variant_2 = Variant_otveta("Пойти проверить кедр", 355)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_345():
    global variant_1, variant_2
    now_page = Page(345, "Душ оказался слишком холодным для вас. Решив не ждать вечера, когда вы можете вернуться в психушку, вы позвали врача, и на следующий день вас развели по разным отделениям. Но ваша нога все еще болит. Может быть, вам помочь чем-нибудь ещё?")
    variant_1 = Variant_otveta("Да", 347)
    variant_2 = Variant_otveta("Нет", 348)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_346():
    global variant_1, variant_2
    now_page = Page(346, "Вы решили принять контрастный душ, что было большой ошибкой. Вас даже стошнило в тот день. Вы пережили большое потрясение. Теперь вы готовы к трансформации? Или нет? Назовите ваш ответ. Да или нет?")
    variant_1 = Variant_otveta("Да", 349)
    variant_2 = Variant_otveta("Нет", 350)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_347():
    global variant_1
    now_page = Page(347, "Ваша совесть не позволила напрягать такого милого старичка ради пустяков")
    variant_1 = Variant_otveta("Спасибо, не надо", 348)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_348():
    global variant_1, pol
    text = "Я бы не спрашивал вас об этом – но, как я понял из вашего последнего письма, вы "
    if pol >= 0:
        text += "женаты"
    elif pol < 0:
        text += "замужем"
    text += " уже много лет. А что? У вас два сына и дочка? Какой странный вопрос! Конечно, есть. Но ведь не всегда же под ногами — ковер, не так ли? Вы не могли бы ответить на мой вопрос? Мне, во всяком случае, очень хочется знать, какой вы "
    if pol >= 0:
        text += "ей"
    elif pol < 0:
        text += "ему"
    text += " сделали подарок. Когда это было? Я имею в виду, как давно?"
    now_page = Page(348, text)
    variant_1 = Variant_otveta("Ответить", 359)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_349():
    global variant_1
    now_page = Page(349, "Вы не смогли обмануть того, кто у вас это спрашивал. Вам просто не позволило сделать это ваше сознание. Вы чётко понимали, что вы не готовы.")
    variant_1 = Variant_otveta("Нет, не готов", 350)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_350():
    global variant_1
    now_page = Page(350, "Разумеется ответ нет. Это было очевидно. Вы прожили внутри себя слишком много времени, и психический кристалл уже начал разрушаться. Это становится все очевиднее. И все же вы продолжали сопротивляться. Вам не понравилось то до чего вы дошли. Вы испытывали сильные страдания по утрам. Поэтому вы решили перестать их испытывать.")
    variant_1 = Variant_otveta("Прекрасная идея", 351)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_351():
    global variant_1, variant_2
    now_page = Page(351, "Эта идея показалась вам прекрасной. Однако вы недооценили опасности и оказались на грани гибели в тот день. Этот день принес для вас большую потерю. Ваши очки были разбиты и вы потеряли глаз. Наверно вы понимали, что это всё не на самом деле, но объяснить это основному психическому кристаллу оказалось невозможно. Ваш ум стал учиться находить новые связи между себе подобными, чтобы не сойти с ума.")
    variant_1 = Variant_otveta("Однако, это не помогло", 353)
    variant_2 = Variant_otveta("И у него это получилось", 275)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_352():
    global variant_1
    now_page = Page(352, "Да, серьёзно. А что ты думаешь, легко писать кучу сюжетных линий, которые никто проходить не будет? Нет уж, довольствуйся тем что есть. Я ради ничтожного процента людей, которые захотят пойти по другой сюжетной линии, пыжиться не буду. И это не я один такой лицемер. Никакая игра не будет тратить ресурсы своих разработчиков на какие-то 2% людей, которые хотят и смогут пройти сложную сюжетную ветку. Нет, Все хотят затратить как можно меньше усилий для как можно лудшего продукта, и не надо нарушать это правило. Постарайся впредь не задавать таких глупых вопроссов.")
    variant_1 = Variant_otveta("Ладно, ладно, успокойся", 82)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_353():
    global variant_1, variant_2
    now_page = Page(353, "Вы не обладали достаточным умением для этого. Вы сделались слабым, невезучим, одиноким человеком и поэтому доживали свои дни в одиночестве.\n\nОткрыта концовка \"Одиночество\"")
    variant_1 = Variant_otveta("Конец", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_354():
    global variant_1
    now_page = Page(354, "Как жаль… И всё же, не сердитесь на меня… Меня утешает мысль, что теперь вы теперь с нами.")
    variant_1 = Variant_otveta("С кем это \"с нами\"?", 356)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_355():
    global variant_1, variant_2
    now_page = Page(355, "Это действительно очень редкое дерево. Он произрастает только в Гватемале и Перуанской Республике. А его лучшие представители во время засухи уходят в джунгли. Мы даже не знаем, что там на самом деле прячется в темноте, откуда они все родом. Но мы знаем всё же только то, что кедр вечно плодоносит… Ваши руки выглядят какими-то запавшими и потёртыми. Они не помыты? Извините – это от ходьбы по пустынной местности. Я не стал бы осуждать вас за это, ведь вы всего лишь южноамериканский мечтатель… Возьмите на память ракушку, пожалуйста… Мы очень любим ракушки, и я знаю, что для вас это была бы самым лучшим подарком… Пойдёмте покатаемся на моей машине. Это совсем рядом.")
    variant_1 = Variant_otveta("Согласиться", 358)
    variant_2 = Variant_otveta("Отказаться", 358)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_356():
    global variant_1
    now_page = Page(356, "Кто \"мы\"? Где \"мы\"? Какие это \"мы\"? Как я раньше не подумал? Вот так и глуп. Вы опять хотите что-то сказать и не хотите… Так о чём же вы хотели поговорить? Ах, да, о философских проблемах… Можно я задам вам вопрос? Конечно можно, вас можно было и не спрашивать. Так вот,  о философской проблеме. Может вы думали, что я не понимаю вас? Вы ошибаетесь. Вы всегда были для меня совершенно естественным спутником. Вы могли предложить любую философскую тему. Вы были просто моим детским врачом. И, конечно, я на всю жизнь запомнил тот вечер на вашей даче в Старой Руссе. Если вдуматься, то он мог бы стать моим последним… Ведь вы со мной не были согласны. Вы не желали принимать мою философию. Но я не соглашался. И вы не хотели этого признать. Разве нет? Я не могу вам этого сказать, потому что даже не знаю вашего имени. А сейчас я спрошу вас прямо. Вдумайтесь в это слово. Чье? Кто вы? Что вы собой представляете, вы сами? Ну, хорошо. Отвечу сам. Я лично для себя только человек. Или кажусь вам человеком? Вероятно, что кажусь. А может быть даже вы это понимаете. До чего же приятно видеть, что один другой разговаривает об этом просто так. И ещё мне приятно вас видеть. А вам приятно. Может быть даже… мне приятно? Нет, не может быть. А может, так и должно быть? Ведь это в любом случае должно быть приятно. Если уж вы с нами так любезны, то пусть будет так и будет. Впрочем, чего я говорю – с вами. Не позволяйте этому обидеть вас. Дайте нам возможность насладиться друг другом, ведь вы для этого меня сюда и возите. Ведь я даже не знаю, как вас зовут. А сейчас я спрошу вас прямо. Вдумайтесь в это слово.  Чье? Кто вы? Что вы собой представляете? Ну, хорошо. Отвечу сам. Я лично для себя только человек. Или кажусь вам человеком? Полагаю, что да...")
    variant_1 = Variant_otveta("И так вы сидели и болтали с ним, пока не умерли", 357)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_357():
    global variant_1, variant_2
    now_page = Page(357, "Открыта концовка \"Интересная болтовня\"")
    variant_1 = Variant_otveta("Конец", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_358():
    global variant_1
    now_page = Page(358, "Я надеюсь вы понимаете, что дальше будет идти точно такойже бред, поэтому я избавлю вас от страданий и предложу нажать заветную кнопку.")
    variant_1 = Variant_otveta("Конец", 1)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_359():
    global variant_1
    now_page = Page(359, "Вы ещё долго болтали с этим милым старикашкой, но в конце разговора он вспомнил, что прежде вы уже сбежали из клиники, поэтому отвел вас в изолятор.")
    variant_1 = Variant_otveta("Жить в изоляторе до конца своих дней", 360)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
def page_360():
    global variant_1, variant_2
    now_page = Page(360, "Открыта концовка \"Изолятор\"")
    variant_1 = Variant_otveta("Конец", 1)
    variant_2 = Variant_otveta("Концовки", 107)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
#Всё, закончлись страницы________▲

#Шаблоны страниц_▼
"""
def page_x():
    global variant_1, variant_2, variant_3, variant_4
    now_page = Page(x, "")
    variant_1 = Variant_otveta("", y)
    variant_2 = Variant_otveta("", y)
    variant_3 = Variant_otveta("", y)
    variant_4 = Variant_otveta("", y)
    full_now_page = Full_page(now_page)
    full_now_page.vybor_otveta()
"""
'''
данный способ изменения переменных устарел и может приводить к ошибкам
while True:
        vvod = full_now_page.vvod_otveta(True)
        if vvod == :
            pass
        if vvod != None:
            full_now_page.vybor_otveta(vvod)
            break
'''
"""
    variant_1 = Variant_otveta("В начало", 1)
    variant_2 = Variant_otveta("Концовки", 107)
"""
#__________________▲

#Начало работы кода

directory_global_pages = r"eafiles\globalpages.txt"
directory_vaules = r"eafiles\variables.txt"
quantity_pages = 361 #количество страниц в квесте
global_pages, local_pages, clear_back_page, barrier, pol = zapusk(quantity_pages) #количество страниц в квесте вписывать сюда. Это обязательно
#количество страниц = последняя страница + 1
back_pages, edavoda, z, zz, casha, camen, ray, ooo, live, surok_canyon, dog, razrab = [], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, False
if global_pages[0] != "1":
    page_0()
while True:
    if razrab: print("Сброс стэка")
    page_1()

print("Произошел неккоректный выход из приложения. Так быть не должно.")
