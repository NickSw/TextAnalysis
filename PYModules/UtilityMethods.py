# -*- coding: utf-8 -*-

import re
import cmath
import pymorphy2 as pym


# Метод разбивает строку на слова и возвращает словарь найденых слов с их индексами в строке
# {'Слова':[(начальный индекс вхождения 1, конечный индекс вхождения 1),(начальный индекс вхождения 2, конечный индекс вхождения 2),...]}
def get_word_positions(text):
    # Убирает лишние символы и сдвигает индексы соответственно
    def temp(tp):
        r = re.finditer('\w+', tp[2])
        s = next(r)
        return tp[0] + s.start(0), tp[0] + s.start(0) + (s.end(0) - s.start(0)), s.group(0)

    tmp = {}
    for m in re.finditer('[\W|\s]?(\w+)[\W|\s]?', text):
        w = temp((m.start(0), m.end(0), m.group(0)))
        if w[2] in tmp.keys():
            tmp[w[2]].append((w[0], w[1]))
        else:
            tmp[w[2]] = [(w[0], w[1])]

    return tmp


# Метод выделяет из списка слов значемые (существительные)
# и стоп слова (Союзы, Местоимения, Предлоги, Частицы, Междометия, Цифры)
# и иностранные слова
def get_morph_words(words):
    significant_words = []
    insignificant_words = []
    latin_words = []
    morph_analyzer = pym.MorphAnalyzer()
    for word in words:
        if 'NOUN' in morph_analyzer.parse(word)[0].tag:
            significant_words.append(word)
        elif ('CONJ' or 'NPRO' or 'PREP' or 'PRCL' or 'INTJ' or 'NUMR') in morph_analyzer.parse(word)[0].tag:
            insignificant_words.append(word)
        elif morph_analyzer.parse(word)[0].tag.POS is None:
            latin_words.append(word)
    return significant_words, insignificant_words, latin_words


# Метод возвращает все аналитические параметры текста
def get_text_stats(text):
    words = get_word_positions(text)

    # Количество символов
    symbol_count = len(text)

    # Количество символов без пробелов
    symbol_count_no_wp = len(re.sub('\s+', '', text))

    # Количество слов
    word_count = sum([len(x) for x in words.values()])

    # Количество букв
    letter_count = sum([len(w) for w in words.keys()])

    morph_words = get_morph_words(words)

    # Количество иностранных слов
    word_latin_count = len(morph_words[2])

    try:
        # Процент воды
        text_water_perc = sum([len(words[mw]) for mw in morph_words[1]]) / sum(
            [len(words[mw]) for mw in morph_words[0]]) * 100
    except ZeroDivisionError:
        text_water_perc = 100

    # Количество знаков пунктуации
    punctuation_count = len([x for x in text if re.match('[^\w\s\d]', x)])

    # Значимые слова отсортированные по количеству
    significant_words_sorted = sorted([(x, len(words[x])) for x in morph_words[0]], key=lambda item: item[1],
                                      reverse=True)

    try:
        if len(significant_words_sorted) > 0:
            # Классическая тошнота текста
            classic_text_nausea = round(cmath.sqrt(significant_words_sorted[0][1]).real, 2)
            # Академическая тошнота текста
            academician_text_nausea = round(significant_words_sorted[0][1] / word_count * 100, 2)
        else:
            classic_text_nausea = 0
            academician_text_nausea = 0
    except Exception as ex:
        print(ex)
    return (('Общее количество слов', word_count),
            ('Общее количество символов (с пробелами)', symbol_count),
            ('Общее количество символов (без пробелов)', symbol_count_no_wp),
            ('Общее количество букв', letter_count),
            ('Количество иностранных слов', word_latin_count),
            ('Общее количество знаков пунктуации', punctuation_count),
            ('Классическая тошнота документа', classic_text_nausea),
            ('Аккадемическая тошнота документа', academician_text_nausea),
            ('Процент воды', text_water_perc))
