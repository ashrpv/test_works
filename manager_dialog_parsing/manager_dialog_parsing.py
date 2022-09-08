"""
Результаты парсинга:
1. 'parsing_summary.csv'  - сводка по каждому диалогу
2. 'conv_data_parsed.csv' - test_data с разметкой реплик по их содержимому (insight)

Обозначения в parsing_summary и conv_data_parsed:
greeting/farewell - приветствие/прощание
manager_introduction/company_introduction - представление менеджером себя/компании
В parsing_summary - номер строки из test_data, в conv_data_parsed - True/False.

good_manager - в диалоге одновременое есть и приветствие и прощание
True/False - везде.

manager_name - имя менеджера
company_name - название компании
"""

!pip install -U spacy
!python -m spacy download ru_core_news_lg

import pandas as pd
import spacy
nlp = spacy.load('ru_core_news_lg')

# Наборы слов для обнаружения целевых реплик (привествие, прощание, представление себя и компании):
GREETING = ['здравствуйте', 'добрый день', 'добрый вечер', 'доброе утро', 'приветствую']
MANAGER_INTRO = ['меня зовут', 'мое имя', 'это']
COMPANY_INTRO = ['компания', 'фирма', 'организация']
FAREWELL = ['до свидания', 'хорошего вечера', 'всего хорошего', 'всего доброго', 'до завтра', 'до встречи']

start_end_terms = {'greeting':GREETING,
                   'farewell':FAREWELL
                  }

intro_terms = {'manager_introduction':MANAGER_INTRO,
               'company_introduction':COMPANY_INTRO
              }

# Функции для проверки вхождения слов-маркеров в реплики:
def phrase_in(string, phrase):
  for word in phrase.split():
    if word not in string:
      return False
  return True

def contain(dialog, words):
  for word in words:
    for row in dialog.iterrows():
      text = row[1].text.lower()
      if phrase_in(text, word):
        return row[0], True
  return dialog.index[0], False

# Функция для выделения имени менеджера:
def manager_name_extr(idx):
  text = conv_data.loc[idx, 'text']
  doc = nlp(text)
  ents = [token.text for token in doc if token.pos_ == 'PROPN']
  if ents:
    return ents[0]
  return None

# Функция для выделения названия компании:
def company_name_extr(idx):
  text = conv_data.loc[idx, 'text']
  doc = nlp(text)
  nbor = [token.nbor() for token in doc if token.text == 'компания'][0]
  r_childs = [c for c in nbor.rights]
  r_nbors = nbor.nbor()
  if r_childs and r_nbors:
   comp_name = nbor.text + ' ' + (r_childs and r_nbors).text
  else:
   comp_name = nbor.text
  return comp_name

conv_data = pd.read_csv('test_data.csv')

# Спарсим разговоры менеджеров по отдельности:
dialog_ids = conv_data.dlg_id.unique()
# Результат парсинга сохраним в новый DataFrame:
summary = pd.DataFrame()
summary.index.rename('dialog', inplace=True)

for dl_id in dialog_ids:
  good_manager = True # good_manager - по умолчанию считаем всех менеджеров "хорошими"

  dialog = conv_data.query(f'role == "manager" and dlg_id == {dl_id}')

  # Проверка приветсвия и прощания:
  for term, words in start_end_terms.items():
    index, flag = contain(dialog, words)
    if flag:
      summary.loc[dl_id, f'{term}'] = index
    else:
      summary.loc[dl_id, f'{term}'] = flag

  # Если приветствие или прощание отсутствует, почетное звание "хорошего менеджера" снимается:
  summary.loc[dl_id, 'good_manager'] = bool(summary.loc[dl_id, 'greeting']) and bool(summary.loc[dl_id, 'farewell'])

  # Проверка того, что менеджер представился и выделение его имени:
  index, flag = contain(dialog, MANAGER_INTRO)
  manager_name = manager_name_extr(index)
  if manager_name:
      summary.loc[dl_id, 'manager_introduction'] = index
      summary.loc[dl_id, 'manager_name'] = manager_name
  else:
      summary.loc[dl_id, 'manager_introduction'] = False
      summary.loc[dl_id, 'manager_name'] = None

  # Проверка того, что менеджер назвал компанию и выделение её названия:
  index, flag = contain(dialog, COMPANY_INTRO)
  if flag:
    company_name = company_name_extr(index)
    if company_name:
        summary.loc[dl_id, 'company_introduction'] = index
        summary.loc[dl_id, 'company_name'] = company_name
  else:
     summary.loc[dl_id, 'company_introduction'] = False
     summary.loc[dl_id, 'company_name'] = None

summary.to_csv('parsing_summary.csv')

def insight_filler(idx, summary):
  insights = []
  sum_row = summary.loc[conv_data.loc[idx, 'dlg_id']]
  if idx == sum_row.greeting:
    insights.append('greeting = True')
    insights.append(f"good_manager = {sum_row.good_manager}")
  if idx == sum_row.farewell:
    insights.append('farewell = True')
    insights.append(f"good_manager = {sum_row.good_manager}")
  if idx == sum_row.manager_introduction:
    insights.append('manager_introduction = True')
    insights.append(f"manager_name = {sum_row.manager_name}")
  if idx == sum_row.company_introduction:
    insights.append('company_introduction = True')
    insights.append(f"company_name = {sum_row.company_name}")
  return insights

for idx in conv_data.index:
  conv_data.loc[idx, 'insight'] = ', '.join(insight_filler(idx, summary))
conv_data.to_csv('conv_data_parsed.csv')