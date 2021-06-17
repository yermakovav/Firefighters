from flask import Flask, render_template

import requests

import dateparser

import config

app = Flask(__name__)


@app.route('/')
def index():
    data = get_data()
    cleaned_data = prepare_data(data)
    return render_template('index.html', data=cleaned_data)


def get_data():
    rows_url = config.API_MAIN_URL + 'datasets/1950/rows'
    count_url = config.API_MAIN_URL + 'datasets/1950/count'

    r = requests.get(count_url, params={'api_key': config.API_KEY})
    if not r.ok:
        raise Exception ('failed to get dataset rows count: {0}'.format(r.text))

    print ('Rows returned: ', r.text)

    limit = int(r.text)
    skip = 0
    step = 100

    data = []
    while len(data) < limit:
        params = {
            '$top': step,
            '$skip': skip,
            'api_key': config.API_KEY,
        }
        r = requests.get (rows_url, params=params)
        if not r.ok:
            raise Exception ('failed to load rows: {0}'.format(r.text))

        j = r.json()
        for element in j:
            data.append(element)

        skip += step

    return data

#чистим данные джейсоновские, их удобнее смотреть в редакторах джейсона

def prepare_data(data):
    result = []

    for element in data:
        if 'Cells' in element and element ['Cells'] is not None:
            cell = element['Cells']

            if 'MonthReport' in cell and 'Calls' in cell:
                result.append({
                    'month_name': cell['MonthReport'],
                    'calls_count': cell['Calls'],
                    'date': dateparser.parse(cell['MonthReport']),
                })

    return result


data = get_data()
cleaned_data = prepare_data(data)
print('Cleaned data: ', cleaned_data)



if __name__ == '__main__':
    app.run()
