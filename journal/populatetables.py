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
    df = merge(schooldates, timetable, on=schooldates.columns[1], how='left')
    df.drop(df.columns[1], axis=1, inplace=True) # delete column 'day'
    df = df.reindex(df.index.rename('id'))
	
    return df
	
	
def fill_year_course_content(course: list, courserepartition: DataFrame, yeartimetable: DataFrame) -> DataFrame:
    columnoffset = 2 # explain why is this
    weekcolumn = 0
    
    dfz = yeartimetable[0]
	
    findfunc = lambda x: x.str.contains(course[0], na=False)
	
    # check if the lesson is in the subset of the courses' list
    coursename = yeartimetable[0].iloc[:, columnoffset:].apply(findfunc)
    classgroup = yeartimetable[1].iloc[:, columnoffset:].values == course[3] # <- can be: 3+4, 5+6

    criterion = [coursename, classgroup]
				  
    # get coordinate list of all matching courses
    lessons = zip(*np.where(criterion[0] & criterion[1]))
    
    # lessoncolumn = 1
    
    # loop through the course and replace it with its content
    # from the repartition table
    prevweeknum = -1
    lessoncolumn = course[1]
	
    for cell in lessons:
        
        cellcolumn = cell[1] + columnoffset
        weeknum = dfz.iloc[cell[0], weekcolumn]
        courselocation = dfz.iloc[cell[0], cellcolumn]

		# move to next column if weeknum is unchanged
		## move to next column if nb of lesson_col > 1: lessoncolumn++
        if course[0] == 'تربية إسلامية':
           if weeknum == prevweeknum:
                lessoncolumn = lessoncolumn + 1 if lessoncolumn <2 else 1
                # print(course[0], courserepartition.iloc[weeknum - 1, lessoncolumn], lessoncolumn)

        prevweeknum = weeknum
        
        coursecontent = courserepartition.iloc[weeknum - 1, lessoncolumn]
        dfz.iat[cell[0], cellcolumn] = courselocation.replace(course[0], course[0] + ' : ' + str(coursecontent))
		
    return dfz