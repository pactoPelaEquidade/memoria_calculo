from collections import defaultdict

import pandas as pd
import numpy as np

df = pd.read_excel('aux/cbo_superior.xlsx')
df.head()

def print_centered(string):
    print('#' * (len(string) + 4))
    print('# ' + string + ' #')
    print('#' * (len(string) + 4))

def def_value():
    return 6000

occ_educ = defaultdict(def_value)
for i in df.cbo_2002:
    occ_educ[i]=12000

def truncate(number):
    '''
    Truncate a number to fit interval [-1, 1]
    '''
    if (isinstance(number, float)) or (isinstance(number, int)):
        if (number >= -1) & (number <= 1):
            return number
        elif number < -1:
            return -1
        elif number > 1:
            return 1
        else:
            return np.nan
    else:
        raise ValueError("Please enter an integer or float")


def compute_ier(
    data: pd.DataFrame,
    groups: list,
    reference_groups: list,
    reference_value: float,
    wage_column: str,
):
    """
    Compute the IER for a dataframe like:

    |    cbo |   branca |   parda |   preta |  remmedia |
    |-------:|---------:|--------:|--------:|----------:|
    | 121005 |        2 |       0 |       0 |  31857.8  |
    | 121010 |       11 |      10 |       0 |  77975    |
    | 123115 |        1 |       0 |       0 |  62736.2  |
    | 123310 |        1 |       0 |       0 |  43000    |
    | 123705 |        1 |       0 |       0 |  16110    |
    | 131115 |        1 |       0 |      20 |  30000    |
    | 131120 |        1 |      30 |       0 |  10034.5  |
    | 142105 |        1 |       0 |       0 |  14266.4  |
    | 142110 |        2 |      21 |       0 |  16825.1  |
    obs: cbo as index of the dataframe and a string

    Args:
        data: Dataframe with the data to be analyzed.
        groups: List of strings with the names of all groups.
        reference_groups: List of strings with the names of the groups to be used as reference.
        reference_value: Float with the population value to be used as reference.
        wage_column: String with the name of the column with the wage.
    """
    print_centered("Dados recebidos:")
    print(data.round(2).to_markdown())
    data["n"] = data[groups].sum(axis=1)
    data["x"] = data[reference_groups].sum(axis=1)
    data["p"] = reference_value
    data["b"] = data["x"] / data["n"]

    print_centered("Calculando o index_rs:")
    data["index_rs"] = (data["b"] - data["p"]) / (
        data["p"] * pow((1 - data["p"]) / data["p"], data["b"])
    )
    data["index_rs"] = data["index_rs"].apply(truncate)
    # remove where index_rs wasn't compute (cause by occ without white and blacks workers)
    data = data[~data.index_rs.isna()]
    print(data.round(2).to_markdown())
    #     tab = data.round(2)
    data["mass_wage_occ"] = data["n"] * data[wage_column]
    mass_wage_prop_global = (
        data[[(int(k[:2]) != 12) & (int(k[:2]) != 14) for k in data.index]][
            "mass_wage_occ"
        ]
        / data[[(int(k[:2]) != 12) & (int(k[:2]) != 14) for k in data.index]][
            "mass_wage_occ"
        ].sum()
    )
    print_centered("Calculando a massa salarial média de cada de ocupaçao:")
    print(data.round(2).to_markdown())
    # calcula ier apenas para ocupações que não são de diretores e gerentes
    data["ier_naolideranca"] = truncate(
        np.dot(
            np.array(
                data[[(int(k[:2]) != 12) & (int(k[:2]) != 14) for k in data.index]][
                    "index_rs"
                ]
            ),
            np.array(mass_wage_prop_global),
        )
    )

    # vetor da proproção da massa salarial de gerentes
    mass_wage_prop_gerencia = (
        data[[int(k[:2]) == 14 for k in data.index]]["mass_wage_occ"]
        / data[[int(k[:2]) == 14 for k in data.index]]["mass_wage_occ"].sum()
    )
    mass_wage_prop_diretoria = (
        data[[int(k[:2]) == 12 for k in data.index]]["mass_wage_occ"]
        / data[[int(k[:2]) == 12 for k in data.index]]["mass_wage_occ"].sum()
    )
    # ier gerencia é o produto vetorial do vetor de pesos com do índice a nível da ocupação
    data["ier_gerencia"] = truncate(
        np.dot(
            np.array(data[[int(k[:2]) == 14 for k in data.index]]["index_rs"]),
            np.array(mass_wage_prop_gerencia),
        )
    )
    data["ier_diretoria"] = truncate(
        np.dot(
            np.array(data[[int(k[:2]) == 12 for k in data.index]]["index_rs"]),
            np.array(mass_wage_prop_diretoria),
        )
    )
    # se não tem diretor ier de diretoria é nulo and so on
    has_dict = {
        "diretoria": "12" in data.index.str[:2],
        "gerencia": "14" in data.index.str[:2],
        "naolideranca": len(
            [k for k in data.index.str[:2].unique() if k not in ["12", "14"]]
        )
        > 0,
    }

    no_occ = {k: v for k, v in has_dict.items() if not v}
    for key in no_occ.keys():
        data[f"ier_{key}"] = np.nan

    # ier ponderado é a média dos iers
    data["ier_ponderado"] = np.nanmean(
        [data["ier_diretoria"], data["ier_gerencia"], data["ier_naolideranca"]]
    )
    #     data.drop("ier_pond", axis=1, inplace=True)

    return data

def compute_isr(data: pd.DataFrame,
    groups: list,
    reference_groups: list,
    reference_value: float,):
    """
    Compute the IER for a dataframe like:

    |    cbo |   branca |   parda |   preta |
    |-------:|---------:|--------:|--------:|
    | 121005 |        2 |       0 |       0 |
    | 121010 |       11 |      10 |       0 |
    | 123115 |        1 |       0 |       0 |
    | 123310 |        1 |       0 |       0 |
    | 123705 |        1 |       0 |       0 |
    | 131115 |        1 |       0 |      20 |
    | 131120 |        1 |      30 |       0 |
    | 142105 |        1 |       0 |       0 |
    | 142110 |        2 |      21 |       0 |
    obs: cbo as index of the dataframe and a string
    """
    print_centered("Dados recebidos:")
    print(data.round(2).to_markdown())
    data["inv_educ"] = data.index.map(occ_educ)
    data["n"] = data[groups].sum(axis=1)
    data["x"] = data[reference_groups].sum(axis=1)
    data["p"] = reference_value
    data["b"] = data["x"] / data["n"]
    data['isr'] = data['n']*(data['p'] - data['b'])*data['inv_educ']

    print_centered("Calculando isr por ocupação")
    print(data.round(2).to_markdown())

    return data

# format string as thousands separator round to 2 decimals
def format_thousands(x):
    return 'R$ ' + f"{x:,.2f}"