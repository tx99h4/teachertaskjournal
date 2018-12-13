from dategen import generate_school_dates, generate_school_weeks
from utils import find_group_course
from ummalqura.hijri_date import HijriDate
from pandas import DataFrame, merge


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
    df.fillna(value=' ')
    df.drop(df.columns[1], axis=1, inplace=True) # delete column 'day'
    df = df.reindex(df.index.rename('id'))
    return df
	
	
def fill_year_course_content(course: list, courserepartition: DataFrame, yeartimetable: DataFrame) -> DataFrame:
    columnoffset = 2 # explain why is this
    weekcolumn = 0
    
    df = {'lessons': yeartimetable[0],
          'group'  : yeartimetable[1],
          'session': yeartimetable[2],
          'card'   : yeartimetable[3]}


    lessons = find_group_course(course, df, columnoffset)
    
    # lessoncolumn = 1
    
    # loop through the course and replace it with its content
    # from the repartition table
    prev  = { 'weeknum': -1, 'course': '', 'bigtxt': '' }
    count = { 'session': 0, 'bigtxtsession': 0, 'card': 0 }

    # lessoncolumn = course[1]

    for cell in lessons:
        day = cell[0]
        weeknum = df['lessons'].iloc[day, weekcolumn]
        period = cell[1] + columnoffset

        if weeknum >= 34:
            return

        coursename = df['lessons'].iloc[day, period]
        session = df['session'].iloc[day, period]
        card = df['card'].iloc[day, period]

        # get the next session in a week
        if weeknum == prev['weeknum']:
            if course[0] == 'تربية إسلامية' or course[0] == 'اجتماعيات': # content of col 1 then 2 every week
                lessoncolumn = lessoncolumn + 1 if lessoncolumn <2 else 1
                # breakpoint()
            if course[0] == 'قراءة':
                if course[3] == '3+4': # content of col 1 3x then 2 then 3 every week (common time beat)
                    lessoncolumn = lessoncolumn + 1 if 3< count['session'] <=5 else 1
                    # import pdb
                    # pdb.set_trace()
                    # pdb.set_trace = lambda: 1
                if course[3] == '5+6': # content of col 1 2x then 2 every week (walz beat)
                    lessoncolumn = lessoncolumn + 1 if 2< count['session'] <=3 else 1
        else:
            count['session'] = 1
            lessoncolumn = course[1]

        subject = courserepartition.iloc[weeknum - 1, lessoncolumn]

        if 'تشخيص' not in subject:
            if prev['course'] == subject:
                count['session'] = count['session'] + 1
                sessioncounter = count['session']
            elif prev['bigtxt'] == subject:
                count['bigtxtsession'] = count['bigtxtsession'] + 1
                sessioncounter = count['bigtxtsession']
            else:
                sessioncounter = count['session']
                count['card'] = count['card'] + 1
        else:
            sessioncounter = 1
            count['card'] = 1

        df['lessons'].iat[day, period] = coursename.replace(course[0], subject)
        df['session'].iat[day, period] = session.replace(course[0], str(sessioncounter))
        df['card'].iat[day, period] = card.replace(course[0], str(count['card']))

        # save previous long text lesson
        if course[0] == 'قراءة' and (lessoncolumn == 2 or lessoncolumn == 3):
            prev['bigtxt'] = subject

        prev['course'] = subject if prev['bigtxt'] != subject else prev['course']
        prev['weeknum'] = weeknum

    return df['lessons']