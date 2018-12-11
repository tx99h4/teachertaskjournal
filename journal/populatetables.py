from dategen import generate_school_dates, generate_school_weeks
from ummalqura.hijri_date import HijriDate
from pandas import DataFrame, merge
import numpy as np


def fill_school_dates(startdate, enddate: list, vacation_dates: list, is_saturdayschool=False) -> DataFrame:
    schooldates = generate_school_dates(startdate, enddate, vacation_dates, is_saturdayschool)
    schooldays     = list(map(int, schooldates.strftime('%w')))
    schooldaynames = list(map(lambda x: HijriDate.day_dict[x], schooldates.day_name()))
    schoolweeks = generate_school_weeks(schooldates)

    df = DataFrame({'weeknum': schoolweeks,
                    'day' : schooldays,
                    'schooldate': schooldaynames + schooldates.strftime(' %d.%m.%Y')})

    df = df.reindex(df.index.rename('id'))
	
    return df

def fill_year_timetable(schooldates: DataFrame, timetable: DataFrame) -> DataFrame:
    df = merge(schooldates, timetable, on=schooldates.columns[1], how='left').fillna(value=' ')
    df.drop(df.columns[1], axis=1, inplace=True) # delete column 'day'
    df = df.reindex(df.index.rename('id'))
    return df
	
	
def fill_year_course_content(course: list, courserepartition: DataFrame, yeartimetable: DataFrame) -> DataFrame:
    columnoffset = 2 # explain why is this
    weekcolumn = 0
    
    df = {'lessons': yeartimetable[0],
          'group'  : yeartimetable[1] }

    findfunc = lambda x: x.str.contains(course[0], na=False)

    # check if the lesson is in the subset of the courses' list
    coursename = df['lessons'].iloc[:, columnoffset:].apply(findfunc)
    classgroup = df['group'].iloc[:, columnoffset:].values == course[3] # <- can be: 3+4, 5+6

    criterion = [coursename, classgroup]

    # get coordinate list of all matching courses
    lessons = zip(*np.where(criterion[0] & criterion[1]))
    
    # lessoncolumn = 1
    
    # loop through the course and replace it with its content
    # from the repartition table
    prevweeknum = -1
    sessioncount = 1
    lessoncolumn = course[1]

    for cell in lessons:
        
        cellcolumn = cell[1] + columnoffset
        weeknum = df['lessons'].iloc[cell[0], weekcolumn]
        courselocation = df['lessons'].iloc[cell[0], cellcolumn]

        if weeknum > 35:
            break

        # get the next session in a week
        if weeknum == prevweeknum:
            sessioncount = sessioncount + 1
            if course[0] == 'تربية إسلامية': # content of col 1 then 2 every week
                lessoncolumn = lessoncolumn + 1 if lessoncolumn <2 else 1
            if course[0] == 'اجتماعيات':  # content of col 1 then 2 every week
                lessoncolumn = lessoncolumn + 1 if lessoncolumn <3 else 1
            if course[0] == 'قراءة': 
                if course[3] == '3+4': # content of col 1 3x then 2 then 3 every week
                    lessoncolumn = lessoncolumn + 1 if sessioncount >3 else 1
                if course[3] == '5+6': # content of col 1 2x then 2 every week
                    lessoncolumn = lessoncolumn + 1 if sessioncount >3 and lessoncolumn <2 else lessoncolumn
        else:
            sessioncount = 1
            lessoncolumn = course[1]
			
        prevweeknum = weeknum
        
        coursecontent = courserepartition.iloc[weeknum - 1, lessoncolumn]
        df['lessons'].iat[cell[0], cellcolumn] = courselocation.replace(course[0], str(coursecontent))

    return df['lessons']