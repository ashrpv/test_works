
Результаты парсинга:
1. `parsing_summary.csv`  - сводка по каждому диалогу
2. `conv_data_parsed.csv` - test_data с разметкой реплик по их содержимому (insight)
  
Обозначения в parsing_summary и conv_data_parsed:  
  
`greeting`/`farewell` - приветствие/прощание  
`manager_introduction`/`company_introduction` - представление менеджером себя/компании  

В `parsing_summary` - номер строки из test_data, в `conv_data_parsed` - True/False.  
  
  
`good_manager` - в диалоге одновременое есть и приветствие и прощание  
True/False - везде.  
  
  

`manager_name` - имя менеджера  
`company_name` - название компании  
