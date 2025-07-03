import os
import pandas as pd

rates_path = os.path.join("data", "operation_rates.xlsx")


def calculate_labor_cost(employee: str, operation: str, quantity: int) -> float:
    if not os.path.exists(rates_path):
        return 0.0
    try:
        df = pd.read_excel(rates_path)
    except:
        return 0.0

    match = df[(df["Сотрудник"] == employee) & (df["Операция"] == operation)]
    if match.empty:
        return 0.0

    rate = match["Ставка"].values[0]
    try:
        return float(rate) * quantity
    except:
        return 0.0

