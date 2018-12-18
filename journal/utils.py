from pandas import DataFrame
import numpy as np

# add prefix for column names of a dataframe
def prefix_columns_from(indexcol: int, df: DataFrame, prefix: str) -> list:
    firstcols = list(df.iloc[:,:indexcol].columns)
    lastcols  = list(df.iloc[:,indexcol:].columns)
    renamedcols = list(map(lambda x: prefix + x, lastcols))
    newcols = firstcols + renamedcols

    return newcols

# return coordinate (tuple) list of all matching
# courses for a class group
# colshift --> restrict search from the specified column# (default: all)
def find_group_course(course: list, dataset: DataFrame, colshift: int = 0) -> list:
    findfunc = lambda x: x.str.contains(course[0], na=False)

    # check if the lesson is in the subset of the courses' list
    coursename = dataset['lessons'].iloc[:, colshift:].apply(findfunc)

    # mask all non matching group of the criterion
    classgroup = dataset['group'].iloc[:, colshift:].values == course[3] # <- can be: 3+4, 5+6
    criterion = [coursename, classgroup]

    result = np.where(criterion[0] & criterion[1])
    return zip(result[0], result[1] + colshift)

