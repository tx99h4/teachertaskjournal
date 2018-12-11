from pandas import DataFrame

def prefix_columns_from(indexcol: int, df: DataFrame, prefix: str):
    firstcols = list(df.iloc[:,:indexcol].columns)
    lastcols  = list(df.iloc[:,indexcol:].columns)
    renamedcols = list(map(lambda x: prefix + x, lastcols))
    newcols = firstcols + renamedcols

    return newcols