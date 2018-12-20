from dategen import generate_school_dates, generate_school_weeks
from utils import find_group_course, next_lesson_column
from ummalqura.hijri_date import HijriDate
from pandas import DataFrame, merge


def fill_school_dates(daterange: tuple, vacation_dates: list, is_saturdayschool=False) -> DataFrame:
    dates = generate_school_dates(daterange, vacation_dates, is_saturdayschool)
    days  = list(map(int, dates.strftime('%w')))
    daynames = list(map(lambda x: HijriDate.day_dict[x], dates.day_name()))
    weeks = generate_school_weeks(dates)

    df = DataFrame({'weeknum': weeks,
                    'day' : days,
                    'schooldate': daynames + dates.strftime(' %d.%m.%Y')})

    df = df.reindex(df.index.rename('id'))
	
    return df

def fill_year_timetable(schooldates: DataFrame, timetable: DataFrame) -> DataFrame:
    df = merge(schooldates, timetable, on=schooldates.columns[1], how='left')
    df.fillna(value=' ')
    df.drop(df.columns[1], axis=1, inplace=True) # delete column 'day'
    df = df.reindex(df.index.rename('id'))
    return df
	
	
def fill_year_course_content(course: list, courserepartition: DataFrame, yeartimetable: DataFrame) -> DataFrame:
    weekcolumn = 0
    prev  = { 'weeknum': -1, 'course': '', 'bigtxt': '' }
    count = { 'session': 0, 'bigtxtsession': 0, 'card': 0 }    
    df = {'lessons': yeartimetable[0],
          'group'  : yeartimetable[1],
          'session': yeartimetable[2],
          'card'   : yeartimetable[3]}


    lessons = find_group_course(course, df, 2)
    lessoncolumn = course[1]
    
    # loop through the course and replace it with its content
    # from the repartition table
    for cell in lessons:
        day = cell[0]
        weeknum = df['lessons'].iloc[day, weekcolumn]
        period = cell[1]

        if weeknum >= 34:
            return

        coursename = df['lessons'].iloc[day, period]
        session = df['session'].iloc[day, period]
        card = df['card'].iloc[day, period]

        lessoncolumn = next_lesson_column(lessoncolumn, course[1], weeknum, prev['weeknum'], course[3], course[0], count['session'])
        subject = courserepartition.iloc[weeknum, lessoncolumn] # weeknum-1 will include تقويم تشخيصي week

        # get the next session in a week
        if 'تشخيص' not in subject:
            if prev['course'] == subject:
                count['session'] = count['session'] + 1
                sessioncounter = count['session']
            elif prev['bigtxt'] == subject:
                count['bigtxtsession'] = count['bigtxtsession'] + 1
                sessioncounter = count['bigtxtsession']
            else:
                count['session'] = 1 if weeknum != prev['weeknum'] else count['session']
                count['card'] = count['card'] + 1
                sessioncounter = count['session']

        df['lessons'].iat[day, period] = coursename.replace(course[0], subject)
        df['session'].iat[day, period] = session.replace(course[0], str(sessioncounter))
        df['card'].iat[day, period] = card.replace(course[0], str(count['card']))

        # save previous long text lesson
        if course[0] == 'قراءة' and (lessoncolumn == 2 or lessoncolumn == 3):
            prev['bigtxt'] = subject

        prev['course'] = subject if prev['bigtxt'] != subject else prev['course']
        prev['weeknum'] = weeknum

    return df['lessons']