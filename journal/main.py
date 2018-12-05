from populatetables import fill_school_dates, fill_year_timetable, fill_year_course_content
from pandas import read_csv
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
dfy = [ fill_year_timetable(df, timetable), fill_year_timetable(df, tmtclass) ]

# print(dfz.head(3))
# z = len(dfz.index)
#x = repart.query('week == 1')['lesson'][0]
#dfz['week'].replace('نشاط علمي', "'"+x+"'", inplace=True, regex=True)
# print(dfz == 'نشاط علمي')
# dfz.query('week == 1') = 'X'

for i in course.index:
   crs = course.iloc[i]
   repart = read_csv(crs[2] + '.csv')
   dsfy = fill_year_course_content(crs, repart, dfy)

   
dsfy.to_csv('df.csv', index=False,
                     quotechar='"', quoting=csv.QUOTE_ALL, 
                        na_rep=' ', encoding='utf-8-sig')




# from pathlib import Path
# Path.cwd()

stop = timeit.default_timer()
print('مدة الإنجاز الإجمالية : %.2f ثواني' % round(stop - start, 2))