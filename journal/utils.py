from pandas import DataFrame
import numpy as np
from functools import lru_cache

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

# return the next column that contains the
# selected course. if it spans to more that one session
# then function returns the course content that is next
# to the previous feeded column
@lru_cache(maxsize=256)
def next_lesson_column(lessoncol: int, initcol: int, week: int, prevweek: int, group: str, course: str, session: int) -> int:
    if week == prevweek:
        if course == 'تربية إسلامية' or course == 'اجتماعيات': # content of col 1 then 2 every week (march beat)
            lessoncol = lessoncol + 1 if lessoncol <2 else 1
            # breakpoint()
        if course == 'قراءة':
            if group == '3+4': # content of col 1 3x then 2 then 3 every week (common time beat)
                lessoncol = lessoncol + 1 if 2< session <=4 else 1
                # import pdb
                # pdb.set_trace()
                # pdb.set_trace = lambda: 1
            if group == '5+6': # content of col 1 2x then 2 every week (walz beat)
                lessoncol = lessoncol + 1 if 2< session <=3 else 1
    else:
        lessoncol = initcol

    return lessoncol

