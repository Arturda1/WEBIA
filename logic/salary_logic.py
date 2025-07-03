import os
import pandas as pd
from datetime import datetime


def get_salary_table(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Возвращает таблицу зарплаты за указанный период.
    """
    log_path = os.path.join("data", "operations_log.xlsx")
    rates_path = os.path.join("data", "operation_rates.xlsx")

    # Проверка существования файлов
    if not os.path.exists(log_path):
        raise FileNotFoundError("Файл operations_log.xlsx не найден")
    if not os.path.exists(rates_path):
        raise FileNotFoundError("Файл operation_rates.xlsx не найден")

    # Загрузка логов операций
    try:
        df = pd.read_excel(log_path)
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке operations_log.xlsx: {str(e)}")

    if df.empty:
        return pd.DataFrame(columns=["Сотрудник", "Операция", "Кол-во", "Ставка", "Начислено"])

    # Загрузка ставок
    try:
        rates = pd.read_excel(rates_path)
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке operation_rates.xlsx: {str(e)}")

    rates_dict = dict(zip(rates["Операция"], rates["Ставка"]))

    # Преобразование даты
    df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")
    df = df.dropna(subset=["Дата"])

    # Фильтрация по датам
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Дата должна быть в формате YYYY-MM-DD")

    df = df[(df["Дата"] >= start_dt) & (df["Дата"] <= end_dt)]

    # Начисления
    df["Ставка"] = df["Операция"].map(rates_dict).fillna(0)
    df["Начислено"] = df["Кол-во"].fillna(0) * df["Ставка"]

    result = df[["Сотрудник", "Операция", "Кол-во", "Ставка", "Начислено"]]
    result = result.groupby(["Сотрудник", "Операция", "Ставка"], as_index=False)["Кол-во", "Начислено"].sum()

    return result
