import math
import sys

import matplotlib.pyplot as plt
import textract
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidgetItem, QWidget, \
    QInputDialog

from PYModules.UtilityMethods import *

app = QApplication(sys.argv)

MainWindow = uic.loadUi('UIFiles/MainWindow.ui')
MainWindow.setWindowTitle('Статистический текстовый анализатор')

SearchResultsWindow = uic.loadUi('UIFiles/SearchResultsWindow.ui')
SearchResultsWindow.setWindowTitle('Результат поиска')

TextAnalysisWindow = uic.loadUi('UIFiles/TextAnalysisWindow.ui')
TextAnalysisWindow.setWindowTitle('Текстовый анализ')

MainWindow.plainTextEdit.setPlainText('Каждая добавляемая операция должна ожидать соответствующей операции '
                                      'удаления в другом потоке, и наоборот. Синхронная очередь не имеет никакой '
                                      'внутренней емкости, даже единичной. Вы не можете заглянуть в синхронную очередь, '
                                      'потому что элемент представлен только при попытке его удаления; вы не можете вставить элемент ('
                                      'используя любой метод), пока другой поток не удалит его: вы не можете обойти очередь потому что '
                                      'обходить нечего. Синхронные очереди похожи на «rendezvous channels», используемые в CSP и Ada.')


def browseAction_click():
    file_info = QFileDialog.getOpenFileName(None, 'Открыть документ',
                                            'C:\\', "Text documents (*.txt *.rtf *.doc *.docx)")
    file_path = file_info[0]
    # print(file_info)

    if file_path:
        if file_path.__contains__("txt"):
            text = open(file_path).read()
            MainWindow.plainTextEdit.setPlainText(text)
        # On windows only for .docx
        # see textract docs for format info
        else:
            text = textract.process(file_path, encoding='cp1251')
            text_decoded = text.decode('cp1251')
            # print(text_decoded)
            MainWindow.plainTextEdit.setPlainText(text_decoded)


def searchAction_click():
    search_tokens, ok_pressed = QInputDialog.getText(None, 'Поиск заданных слов', 'Введите слова:')
    input_text = MainWindow.plainTextEdit.toPlainText()

    # Слова которые ищут
    search_words = get_word_positions(search_tokens)
    if len(search_words) < 1:
        return

    # Все слова текста
    input_words = get_word_positions(input_text)

    # Найденные слова
    found_words = {k: input_words[k] for k in search_words.keys() if k in input_words.keys()}

    # print(found_words)

    table = SearchResultsWindow.tableWidget
    table.setColumnCount(2)
    table.setRowCount(len(found_words))
    table.setHorizontalHeaderLabels(["Слово", "Кол-во повторов"])

    iter_count = 0
    # заполняем таблицу
    for key, value in found_words.items():
        column_words = QTableWidgetItem(key)
        column_words.setFlags(Qt.ItemIsEditable)
        table.setItem(iter_count, 0, column_words)

        column_stats = QTableWidgetItem(str(len(value)))
        column_stats.setFlags(Qt.ItemIsEditable)
        table.setItem(iter_count, 1, column_stats)
        iter_count += 1

    SearchResultsWindow.show()


def textAnalysisAction_click():
    text_stats = get_text_stats(MainWindow.plainTextEdit.toPlainText())

    table = TextAnalysisWindow.tableWidget
    table.setColumnCount(2)
    table.setRowCount(len(text_stats))
    table.setHorizontalHeaderLabels(["Параметры", "Значения"])

    for i, stat in enumerate(text_stats):
        column_words = QTableWidgetItem(stat[0])
        column_words.setFlags(Qt.ItemIsEditable)
        table.setItem(i, 0, column_words)

        column_stats = QTableWidgetItem(str(stat[1]))
        column_stats.setFlags(Qt.ItemIsEditable)
        table.setItem(i, 1, column_stats)

    table.resizeColumnsToContents()
    table.resizeRowsToContents()

    TextAnalysisWindow.show()


def textAnalysisReportAction_click():
    text_analysis_report = QWidget.grab(TextAnalysisWindow.tableWidget)
    dst_path, ok = QFileDialog.getSaveFileName(None, 'Выберите путь',
                                               'C:\\', "Images (*.png *.jpg)")
    if ok:
        text_analysis_report.save(dst_path)


def graphiсAnalysisAction_click():
    input_text = MainWindow.plainTextEdit.toPlainText()
    stop_words = MainWindow.stopWordLineEdit.text()

    word_positions = get_word_positions(input_text)

    stop_words_positions = get_word_positions(stop_words)
    morph_words_positions = get_morph_words(word_positions)
    words_unique_significant = list(set(morph_words_positions[0]) - set(stop_words_positions.keys()))

    russian_words = morph_words_positions[0]
    latin_words = morph_words_positions[2]
    ratio = [len(russian_words), len(latin_words)]

    # print(morph_words_positions)
    # print(stop_words_positions.keys())
    # print(words_unique_significant)
    # print(list(set(words_unique_significant)-set(stop_words_positions.keys())))

    # упорядочить по значимым словам
    words_unique_significant_sorted = sorted([(x, len(word_positions[x])) for x in words_unique_significant],
                                             key=lambda x: x[1], reverse=True)
    words_cut = words_unique_significant_sorted[:10]

    plt.close('all')

    plt.figure("Графический анализ", figsize=(12, 12))

    ax_freq_words = plt.subplot2grid((2, 2), (0, 0))
    ax_freq_words.set_title('Наиболее встречающиеся слова')

    ax_word_ratio = plt.subplot2grid((2, 2), (0, 1))
    ax_word_ratio.set_title('Соотношение иностранных/отечественных слов')

    ax_freq_desc = plt.subplot2grid((2, 2), (1, 0))
    ax_freq_desc.set_title('Частотность слов (по убыванию)')

    ax_zipf = plt.subplot2grid((2, 2), (1, 1))
    ax_zipf.set_title('Закон Ципфа')

    if len(words_cut) > 0:

        ax_freq_words.bar(range(len(words_cut)), [x[1] for x in words_cut], width=0.5,
                          tick_label=[x[0] for x in words_cut])

        ax_word_ratio.pie(ratio, labels=['Отечественные', 'Иностранные'], autopct='%1.1f%%')

        ax_freq_desc.plot(range(len(words_cut)), [x[1] for x in words_cut], range(len(words_cut)),
                          [x[1] for x in words_cut], 'ro')

        ax_zipf.plot(range(len(words_cut)), [x[1] for x in words_cut], '-b', label='Ваш текст')

        # С = (Частота вхождения слова х Ранг частоты) / Число слов.
        zipf_y = []
        for i, x in enumerate(words_cut):
            zipf_y.append(math.ceil(x[1] / (i + 1)))
            # print(zipf_y[i])

        ax_zipf.plot(range(len(words_cut)), zipf_y, '-g', label='Закон Ципфа')
        ax_zipf.set_xticks(range(len(words_cut)))
        ax_zipf.set_xticklabels([x[0] for x in words_cut])
        ax_zipf.legend(loc='upper left')

    plt.tight_layout()
    plt.show()


def exitAction_click():
    sys.exit(app.exec_())

# Подключение методов к кнопкам
MainWindow.browseAction.triggered.connect(browseAction_click)
TextAnalysisWindow.textAnalysisReportButton.clicked.connect(textAnalysisReportAction_click)
MainWindow.searchAction.triggered.connect(searchAction_click)
MainWindow.textAnalysisAction.triggered.connect(textAnalysisAction_click)
MainWindow.graphicAnalysisAction.triggered.connect(graphiсAnalysisAction_click)
MainWindow.exitAction.triggered.connect(exitAction_click)

# Показ главного окна и старт приложения.
MainWindow.show()
sys.exit(app.exec_())
