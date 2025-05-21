import requests
from bs4 import BeautifulSoup
import urllib.parse

def parse_html(url, base_url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        institutes = []
        exclude_texts = ["УВАЖАЕМЫЕ СТУДЕНТЫ", "ВОЗМОЖНЫ ИЗМЕНЕНИЯ В РАСПИСАНИИ"]

        for h4 in soup.find_all(['h4']):
            text = h4.get_text(strip=True)
            if (h4.get('class') == ['name-schedule'] or
                    (h4.get('style') and 'text-align: center;' in h4.get('style'))):
                if not any(exclude in text for exclude in exclude_texts):
                    institutes.append({'name': text, 'forms': []})

        current_institute = None
        current_form = None

        elements = soup.find_all(['h4', 'button', 'div', 'b'])
        i = 0
        while i < len(elements):
            element = elements[i]

            if element.name == 'h4':
                text = element.get_text(strip=True)
                if (element.get('class') == ['name-schedule'] or
                        (element.get('style') and 'text-align: center;' in element.get('style'))):
                    if not any(exclude in text for exclude in exclude_texts):
                        current_institute = next((inst for inst in institutes if inst['name'] == text), None)
                        current_form = None

            elif element.name == 'button' and 'accordion-button' in element.get('class', []):
                form_text = element.get_text(strip=True)
                current_form = {'name': form_text, 'files': []}
                if current_institute and not any(f['name'] == form_text for f in current_institute['forms']):
                    current_institute['forms'].append(current_form)

            elif element.name == 'div' and 'document' in element.get('class', []):
                file_title_tag = element.find('h5')
                file_link_tag = element.find_all('a')[-1]

                file_name = file_title_tag.get_text(strip=True) if file_title_tag else "Без названия"
                raw_link = file_link_tag.get('href') if file_link_tag else None

                if raw_link:
                    # Преобразуем в абсолютную ссылку с кодированием имени файла
                    path_head, file_part = raw_link.rsplit('/', 1)
                    encoded_file_part = urllib.parse.quote(file_part)
                    full_link = f"{base_url}{path_head}/{encoded_file_part}"
                else:
                    full_link = "Ссылка не найдена"

                # Ищем дату изменений
                change_date = ""
                j = i + 1
                while j < len(elements):
                    next_elem = elements[j]
                    if next_elem.name == 'b':
                        date_text = next_elem.get_text(strip=True)
                        if "изменения от" in date_text.lower():
                            change_date = date_text.split("от")[-1].strip()
                            break
                    elif next_elem.name in ['div', 'button', 'h4']:
                        break
                    j += 1

                if current_form:
                    current_form['files'].append({
                        'title': file_name,
                        'link': full_link,
                        'date': change_date
                    })

            i += 1

        # Вывод
        for institute in institutes:
            print(institute['name'])
            for form in institute['forms']:
                print("\t", form['name'])
                for file in form['files']:
                    print(f"\t\t{file['title']} - {file['link']} - {file['date']}")
            print()

        return {
            'success': True,
            'data': institutes,
            'error': None
        }

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
        return {
            'success': True,
            'data': institutes,
            'error': None
        }

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return {
            'success': False,
            'data': None,
            'error': f"Произошла ошибка: {e}"
        }


# Формат data:
# {
#     'name': 'Название института',
#     'forms': [
#         {
#             'name': 'Название формы обучения',
#             'files': [
#                 {
#                     'title': 'Название файла',
#                     'link': 'Полная ссылка на файл',
#                     'date': 'Дата изменений'
#                 },
#                 ...
#             ]
#         },
#         ...
#     ]
# }