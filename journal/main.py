from populatetables import fill_school_dates, fill_year_timetable, fill_year_course_content
from utils import prefix_columns_from
from pandas import read_csv, concat
import csv

import timeit, math
start = timeit.default_timer()

startdate = '2018-09-24'
enddate = '2019-06-23'
is_saturdayschool = False
vacation_dates = [ ('2018-10-28', '2018-11-06'), ('2019-01-20', '2019-01-27'), ('2019-03-31', '2019-04-14') ]

timetable = read_csv('conf/tmmawad.csv')
tmtclass  = read_csv('conf/tmclasses.csv')
course    = read_csv('conf/courses.csv')

df  = fill_school_dates(startdate, enddate, vacation_dates)
dfcrs = fill_year_timetable(df, timetable)
dfgrp = fill_year_timetable(df, tmtclass)
dfy = [ dfcrs.copy(), dfgrp.copy()]

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
   repart = read_csv(crs[2] + '.csv')
   dsfy = fill_year_course_content(crs, repart, dfy)

prefix = 'crs_'
idxcol = 2

dfcrs.columns = prefix_columns_from(idxcol, dfcrs, prefix)
dfc = concat([dsfy, dfcrs], axis=1)

dfc.to_csv('df.csv', index=False,
                     quotechar='"', quoting=csv.QUOTE_ALL, 
                        na_rep=' ', encoding='utf-8-sig')

# print( dfc.head(2) )
# from pathlib import Path
# Path.cwd()

stop = timeit.default_timer()
print('مدة الإنجاز الإجمالية : %.2f ثواني' % round(stop - start, 2))