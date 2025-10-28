import pandas as pd

path = 'owid-covid-data.csv'
df = pd.read_csv(path, delimiter=',', encoding='latin-1')
df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year

# Функции для обработки данных
def group_by_value(df: str) -> int:
    return df.groupby('year')

def grouping_countries(df: str) -> str:
    return df['location'].unique()


def number_of_cases(dataframes: int, countries: str) -> list[int, float, str]:
    results = []
    for year, data in dataframes:
        for country in countries:
            country_data = data[data['location'] == country]
            total_cases = country_data['total_cases'].sum()
            total_deaths = country_data['total_deaths'].sum()
            people_vaccinated = country_data['people_vaccinated'].sum()
            results.append({
                'year': year,
                'location': country,
                'total_cases': total_cases,
                'total_deaths': total_deaths,
                'people_vaccinated': people_vaccinated
            })
    return results

def create_results_df(results: list[int, str]) -> list[int, float]:
    return pd.DataFrame(results)

def total_number_of_vaccinated(df: str, results_df: str ) -> int:
    merged_df = pd.merge(df, results_df, on=['year', 'location'], how='inner')
    return merged_df['people_vaccinated'].sum()

def total_number_of_recovered(df: str, year_data: int) -> float:
    merged_df = pd.merge(df, year_data, on=['year', 'location'], how='left')
    if 'total_recovered' in merged_df.columns:
        return merged_df['total_recovered'].sum(skipna=True)
    else:
        print("Ошибка: столбец 'total_recovered' отсутствует в merged_df!")
        return 0

def calculate_stats(df: str, year: int, country: str) -> None:

    # Cтатистика по COVID-19 для заданной страны и года
    df_year_country = df[(df['year'] == year) & (df['location'] == country)].copy()

    if df_year_country.empty:
        print(f"Нет данных для {country} в {year}")
        return None

    # Преобразование типов
    for col in ['total_cases', 'total_deaths', 'people_vaccinated']:
        if col in df_year_country.columns:
            df_year_country[col] = pd.to_numeric(df_year_country[col], errors='coerce').fillna(0)

    # Рассчитываем статистику
    total_cases = df_year_country['total_cases'].max()
    total_deaths = df_year_country['total_deaths'].max()
    people_vaccinated = df_year_country['people_vaccinated'].max()

    # Рассчитываем выздоровевших
    if 'total_cases' in df_year_country and 'total_deaths' in df_year_country:
        total_recovered = total_cases - total_deaths
    else:
        total_recovered = 0

    # Рассчитываем проценты
    mortality_rate = (total_deaths / total_cases) * 100 if total_cases > 0 else 0
    recovery_rate = (total_recovered / total_cases) * 100 if total_cases > 0 else 0
    vaccinated_rate = (people_vaccinated / df_year_country['population'].max()) * 100 if 'population' in df_year_country and df_year_country['population'].max() > 0 else 0
    return {
        'total_cases': total_cases,
        'total_deaths': total_deaths,
        'total_recovered': total_recovered,
        'people_vaccinated': people_vaccinated,
        'mortality_rate': mortality_rate,
        'recovery_rate': recovery_rate,
        'vaccinated_rate': vaccinated_rate
    }

# Определяем годы и страны для анализа
year = int(input('Укажите год: '))
countries = df['location'].unique()

# Выводим статистику для каждой страны и года
for country in countries:
    stats = calculate_stats(df, year, country)

    if stats:
        print(f"Год: {year}, Страна: {country}:")
        print(f"  Количество заболевших: {stats['total_cases']:.0f}, "
                f"Количество выздоровевших: {stats['total_recovered']:.0f} ({stats['recovery_rate']:.2f}%), "
                f"Количество умерших: {stats['total_deaths']:.0f} ({stats['mortality_rate']:.2f}%), "
                f"Количество привитых: {stats['people_vaccinated']:.0f} ({stats['vaccinated_rate']:.2f}%)\n")