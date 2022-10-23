import pandas as pd
import numpy as np
from unidecode import unidecode
from utils import compute_ier, compute_isr, format_thousands


def main():
    xls = pd.ExcelFile(
        "raw/2021_4420220629_0306360636.2048552596.xlsx"
    )

    df = xls.parse("Base")

    df.columns = [unidecode(col).lower().replace(" ", "_") for col in df.columns]

    df = df.iloc[:, :-2]

    tab_color = pd.pivot_table(
        df, index="cbo", columns="raca", aggfunc="size", fill_value=0
    )
    tab_color.columns = [
        unidecode(col).lower().replace(" ", "_") for col in tab_color.columns
    ]
    tab_color.drop(["amarela", "nao_informado"], inplace=True, axis=1)
    tab_wage = pd.pivot_table(df, index="cbo", values="salario", aggfunc="mean")

    df = pd.concat([tab_color, tab_wage], axis=1)
    df.index = [str(i) for i in df.index]

    pop = pd.read_csv('aux/populacao_prop.csv')
    pop = pop[pop['uf_sigla']=='SP']
    p = pop[['proporcao_preta', 'proporcao_parda']].sum(axis=1).values[0]

    result_ieer = compute_ier(
        data=df,
        groups=["branca", "preta", "parda"],
        reference_groups=["preta", "parda"],
        reference_value=p,
        wage_column="salario",
    )

    print("Resultado IEER:\n\n")
    print(
        result_ieer[["ier_naolideranca", "ier_gerencia", "ier_diretoria", "ier_ponderado"]]
        .head(1)
        .to_markdown(index=False)
    )

    result_isr = compute_isr(
        data=df,
        groups=["branca", "preta", "parda"],
        reference_groups=["preta", "parda"],
        reference_value=p
    )


    print(f"\n\nResultado ISR: {format_thousands(result_isr.isr.sum())}")


if __name__ == "__main__":
    main()