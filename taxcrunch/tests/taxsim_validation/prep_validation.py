import os
import pandas as pd

CURRENT_PATH = os.path.abspath(os.path.dirname("file"))


def translate(taxsim_in, taxcrunch_in):
    """
    Translate taxsim input to tax-cruncher input
    """

    path = os.path.join(CURRENT_PATH, taxsim_in)
    taxsim_df = pd.read_csv(path, delim_whitespace=True, header=None)

    taxcrunch_df = pd.DataFrame()
    taxcrunch_df.loc[:, 0] = taxsim_df.loc[:, 0]
    taxcrunch_df.loc[:, 1] = taxsim_df.loc[:, 1]
    taxcrunch_df.loc[:, 2] = taxsim_df.loc[:, 2]
    taxcrunch_df.loc[:, 3] = taxsim_df.loc[:, 3]
    taxcrunch_df.loc[:, 4] = taxsim_df.loc[:, 4]
    taxcrunch_df.loc[:, 5] = taxsim_df.loc[:, 5]
    taxcrunch_df.loc[:, 6] = taxsim_df.loc[:, 7]
    taxcrunch_df.loc[:, 7] = taxsim_df.loc[:, 8] - taxsim_df.loc[:, 7]
    taxcrunch_df.loc[:, 8] = taxsim_df.loc[:, 9] - taxsim_df.loc[:, 8]
    taxcrunch_df.loc[:, 9] = taxsim_df.loc[:, 6] - taxsim_df.loc[:, 9]
    taxcrunch_df.loc[:, 10] = taxsim_df.loc[:, 10]
    taxcrunch_df.loc[:, 11] = taxsim_df.loc[:, 11]
    taxcrunch_df.loc[:, 12] = taxsim_df.loc[:, 12]
    taxcrunch_df.loc[:, 13] = taxsim_df.loc[:, 13]
    taxcrunch_df.loc[:, 14] = taxsim_df.loc[:, 14]
    taxcrunch_df.loc[:, 15] = taxsim_df.loc[:, 15]
    taxcrunch_df.loc[:, 16] = 0
    taxcrunch_df.loc[:, 17] = 0
    taxcrunch_df.loc[:, 18] = 0
    taxcrunch_df.loc[:, 19] = 0
    taxcrunch_df.loc[:, 20] = taxsim_df.loc[:, 16]
    taxcrunch_df.loc[:, 21] = taxsim_df.loc[:, 17]
    taxcrunch_df.loc[:, 22] = taxsim_df.loc[:, 18]
    taxcrunch_df.loc[:, 23] = taxsim_df.loc[:, 19]
    taxcrunch_df.loc[:, 24] = taxsim_df.loc[:, 20]
    taxcrunch_df.loc[:, 25] = taxsim_df.loc[:, 21]
    taxcrunch_df.loc[:, 26] = taxsim_df.loc[:, 22]
    taxcrunch_df.loc[:, 27] = taxsim_df.loc[:, 23]
    taxcrunch_df.loc[:, 28] = taxsim_df.loc[:, 24]
    taxcrunch_df.loc[:, 29] = taxsim_df.loc[:, 25]
    taxcrunch_df.loc[:, 30] = taxsim_df.loc[:, 26]

    taxcrunch_df = taxcrunch_df.drop(columns=[2, 25, 26])
    taxcrunch_df.to_csv(taxcrunch_in, index=False, header=False)


if __name__ == "__main__":
    translate("taxsim_in_a18.csv", "taxcrunch_in_a18.csv")
    translate("taxsim_in_c18.csv", "taxcrunch_in_c18.csv")
