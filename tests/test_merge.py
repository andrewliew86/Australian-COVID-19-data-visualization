import os
import pandas as pd

def merge_sample_rows():
    dataset = {
        'covid19_confirmed.csv': 'Confirmed',
        'covid19_deaths.csv': 'Deaths',
        'covid19_recovered.csv': 'Recovered',
    }
    df_list = []
    base_dir = os.path.join(os.path.dirname(__file__), '..')

    for file, col_name in dataset.items():
        path = os.path.join(base_dir, file)
        df = pd.read_csv(path, nrows=5)
        df = df.loc[df['Country/Region'] == 'Australia']
        melt = df.melt(
            id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'],
            var_name='date',
            value_name=col_name,
        )
        df_list.append(melt)

    confirmed_aus, deaths_aus, recovery_aus = df_list
    confirm_deaths = confirmed_aus.merge(
        deaths_aus,
        on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'],
        how='inner',
    )
    combined_dataset = confirm_deaths.merge(
        recovery_aus,
        on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'],
        how='inner',
    )

    combined_dataset['date'] = pd.to_datetime(combined_dataset['date'], format='%m/%d/%y')
    combined_dataset.index = combined_dataset['date']
    combined_dataset.drop(columns=['Lat', 'Long', 'date'], inplace=True)
    return combined_dataset


def test_merge_columns():
    df = merge_sample_rows()
    expected_columns = [
        'Province/State',
        'Country/Region',
        'Confirmed',
        'Deaths',
        'Recovered',
    ]
    for col in expected_columns:
        assert col in df.columns

