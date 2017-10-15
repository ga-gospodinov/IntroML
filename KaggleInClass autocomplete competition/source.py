import codecs # windows ¯\_(ツ)_/¯

# объявим где хранятся исходные данные
PATH_TRAIN = '../input/train.csv'
PATH_TEST = '../input/test.csv'

# объявим куда сохраним результат
PATH_PRED = 'pred.csv'

## Из тренировочного набора собираем статистику о встречаемости слов и словосочетаний

# максимальная длина чанка в тестовой выборке
max_word2_chunk_len = 23 

# создаем списки словарей для хранения статистики (для разной длины чанка)
word_stat_dicts = []
most_freq_dicts = []
#создаем словарь для хранения статистики наблюдения словосочетаний
word12_probability = {}
for i in range(max_word2_chunk_len - 1):
    word_stat_dicts.append({})
    most_freq_dicts.append({})

# открываем файл на чтение в режиме текста
fl = codecs.open(PATH_TRAIN, 'r', encoding='utf-8')

# считываем первую строчку - заголовок (она нам не нужна)
fl.readline()

# в цикле читаем строчки из файла
for line in fl:
    # разбиваем строчку на три строковые переменные
    Id, Sample, Prediction = line.strip().split(',')
    # строковая переменная Prediction - содержит в себе словосочетание из 2 слов, разделим их
    word1, word2 = Prediction.split(' ')

    # если текущее словосочетание еще не встречалось, то добавим его в словарь и установим счетчик этого слова в 0
    if (word1, word2) not in word12_probability:
        word12_probability[(word1, word2)] = 0
    # увеличим значение счетчика по текущему словосочетанию на 1
    word12_probability[(word1, word2)] += 1

    for i in range(2, min(max_word2_chunk_len, len(word2)) + 1):
        key = word2[:i]
        # если такого ключа еще нет в словаре, то создадим пустой словарь для этого ключа
        if key not in word_stat_dicts[i - 2]:
            word_stat_dicts[i - 2][key] = {}
        # если текущее слово еще не встречалось, то добавим его в словарь и установим счетчик этого слова в 0
        if word2 not in word_stat_dicts[i - 2][key]:
            word_stat_dicts[i - 2][key][word2] = 0
        # увеличим значение счетчика по текущему слову на 1
        word_stat_dicts[i - 2][key][word2] += 1
    
# закрываем файл
fl.close()

## Строим модель

# проходим по каждому словарю word_stat_dict
for i in range(0, max_word2_chunk_len + 1 - 2):
    for key in word_stat_dicts[i]:
        # для каждого ключа получаем наиболее вероятное слово и записываем его в словарь most_freq_dict
        most_freq_dicts[i][key] = max(word_stat_dicts[i][key], key=word_stat_dicts[i][key].get)

## Выполняем предсказание

# открываем файл на чтение в режиме текста
fl = open(PATH_TEST, 'r', encoding='utf-8')

# считываем первую строчку - заголовок (она нам не нужна)
fl.readline()

# открываем файл на запись в режиме текста
out_fl = open(PATH_PRED, 'w', encoding='utf-8')

# записываем заголовок таблицы
out_fl.write('Id,Prediction\n')

# в цикле читаем строчки из тестового файла
for line in fl:
    # разбиваем строчку на две строковые переменные
    Id, Sample = line.strip().split(',')
    # строковая переменная Sample содержит в себе полностью первое слово и кусок второго слова, разделим их
    word1, word2_chunk = Sample.split(' ')
    prnt = False
    # вычислим ключ для заданного фрагмента второго слова
    for i in range(min(len(word2_chunk), max_word2_chunk_len), 1, -1):
        key = word2_chunk[:i]
        if key in word_stat_dicts[i - 2]:
            results = {}
            for word in word_stat_dicts[i - 2][key]:
                if (word1, word) in word12_probability:
                    results[word] = word12_probability[(word1, word)]
            # P(word2|word1) = P(word1 & word2) / P(word1) => наиболее вероятному word2 
            # для данного word1 соответствует максимальная вероятность P(word1 & word2)
            if len(results) > 0:
                out_fl.write('%s,%s %s\n' % (Id, word1, max(results, key=results.get)))
                prnt = True
                break
            # если нет словосочетаний с word1, то выбираем наиболее вероятное word2 
            elif key in most_freq_dicts[i - 2]:
                out_fl.write('%s,%s %s\n' % (Id, word1, most_freq_dicts[i - 2][key]))
                prnt = True
                break
    if not prnt:
        # иначе пишем наиболее часто встречающееся словосочетание в целом
        out_fl.write('%s,%s\n' % (Id, 'что она'))
# закрываем файлы

fl.close()
out_fl.close()