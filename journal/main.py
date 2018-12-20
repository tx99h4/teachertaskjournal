from populatetables import fill_school_dates, fill_year_timetable, fill_year_course_content
from utils import prefix_columns_from
from pandas import read_csv, concat
import csv

import timeit, math
start = timeit.default_timer()

# let it be launched from the view project
if __name__ == "__main__":
    WIR = ''
else:
    WIR = '../journal/'

daterange = ('2018-10-01', '2019-06-23')
is_saturdayschool = False
vacation_dates = [ ('2018-10-28', '2018-11-06'), ('2019-01-20', '2019-01-27'), ('2019-03-31', '2019-04-14') ]

timetable = read_csv(WIR + 'conf/tmmawad.csv')
tmtclass  = read_csv(WIR + 'conf/tmclasses.csv')
course    = read_csv(WIR + 'conf/courses.csv')

df  = fill_school_dates(daterange, vacation_dates)
dfgrp = fill_year_timetable(df, tmtclass)
dfcrs = fill_year_timetable(df, timetable)
dfsess = dfcrs.copy()
dfcard = dfcrs.copy()

dfy = [ dfcrs.copy(), dfgrp, dfsess, dfcard ]

# print(dfz.head(3))
# z = len(dfz.index)
#x = repart.query('week == 1')['lesson'][0]
#dfz['week'].replace('نشاط علمي', "'"+x+"'", inplace=True, regex=True)
# print(dfz == 'نشاط علمي')
# dfz.query('week == 1') = 'X'

for i in course.index:
   crs = course.iloc[i]
   # if crs[3] contains X+Y -> create repart df = x + Y
   # if crs[3] contains X+Y -> create repart df = x + Y
   repart = read_csv(WIR + crs[2] + '.csv')
   dsfy = fill_year_course_content(crs, repart, dfy)

idxcol = 2
prefix = {'course': 'crs_', 'session': 'sess_', 'card': 'card_'}

dfcrs.columns = prefix_columns_from(idxcol, dfcrs, prefix['course'])
dfsess.columns = prefix_columns_from(idxcol, dfsess, prefix['session'])
dfcard.columns = prefix_columns_from(idxcol, dfcard, prefix['card'])

dfc = concat([dfy[0], dfcrs, dfsess, dfcard], axis=1)

dfc.replace(r'(.*)/(.*)', r'\1\n\2', regex=True, inplace=True)
dfc.to_csv('../view/df.csv', index=False, na_rep=' ', encoding='utf-8-sig')

# print( dfc.head(2) )
# from pathlib import Path
# Path.cwd()

stop = timeit.default_timer()
print('مدة الإنجاز الإجمالية : %.2f ثواني' % round(stop - start, 2))