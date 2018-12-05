from pandas import to_datetime, date_range
from pandas.tseries.offsets import CustomBusinessDay
from ummalqura.hijri_date import HijriDate
from functools import lru_cache

def school_days(choice: bool) -> str:
    days = { True: 'Mon Tue Wed Thu Fri Sat',
            False: 'Mon Tue Wed Thu Fri'
           }

    return days[choice]
	
@lru_cache(maxsize=256)
def generate_civil_holidays(civilyear: int) -> list:  
	return to_datetime([   str(civilyear) + '-11-18',   # عيد الاستقلال 18 نونبر
	
	                       # عيد رأس السنة الميلادية
	                       str(civilyear+1) + '-01-01',
						   
						   # عيد تقديم وثيقة الاستقلال
						   str(civilyear+1) + '-01-11',
						   
						   # عيد الشغل
						   str(civilyear+1) + '-05-01'])

@lru_cache(maxsize=256)
def generate_religious_holidays(hijriyear: int) -> list:
    hijridaysoff = [ str(hijriyear) + '-01-01',  #  فاتح محرم
	
					 # المولد النبوي يومي 12 و 13 ربيع الأول
					 str(hijriyear) + '-03-12', 
					 str(hijriyear) + '-03-13',
					 
					 # عيد الفطر من 28 رمضان إلى 2 شوال
					 str(hijriyear) + '-09-28',
					 str(hijriyear) + '-09-29',
					 str(hijriyear) + '-09-30',
					 str(hijriyear) + '-10-01',
					 str(hijriyear) + '-10-02',
					 
					 # عيد الأضحى
					 str(hijriyear) + '-12-10' ]
					 
	# convert date to Gregorian
    religiousdaysoff = list(map(HijriDate.get_georing_date, hijridaysoff))
					 
    return to_datetime(religiousdaysoff)

# generate school vacations days
def generate_school_vacations(datetuples: list) -> list:
    expand_interval_func = lambda interval: date_range(*interval)
	
    return list(map(expand_interval_func, datetuples))
	

def generate_school_weeks(workingdates: list) -> list:
    schoolweeknum = 0
    prevweekofyear = -1 # arbtrary value to begin loop school week count
    totalworkingdates = len(workingdates)
    weekrows = []

    for i in range(totalworkingdates):
        if workingdates[i].weekofyear != prevweekofyear:
            schoolweeknum += 1

        weekrows.append(schoolweeknum)
        prevweekofyear = workingdates[i].weekofyear
    
    return weekrows

def generate_school_all_holidays(civilyear: int, vacations: list) -> list:
    # get hijri year from 1st September of a gregorian year
    hijridate = HijriDate.get_hijri_date(str(civilyear)+'-09-01')
    hijriyear = int(hijridate.partition('-')[0])

    # sum up total school holidays	
    allholidays = generate_civil_holidays(civilyear)
    allholidays = allholidays.append(generate_religious_holidays(hijriyear))
    allholidays = allholidays.append(generate_religious_holidays(hijriyear+1))  # if 1st moharram occurs inside current year
    allholidays = allholidays.append(generate_school_vacations(vacations))
	
    return allholidays
	
def generate_school_dates(datebegin: str, dateend: str, vacations: list, is_saturday_included=False) -> list:
    civilyear = int(datebegin.partition('-')[0])
    schoolholidays = generate_school_all_holidays(civilyear, vacations)

    # generate the working school days after
    # removing holidays and weekends
    bdays = CustomBusinessDay(holidays=schoolholidays, weekmask=school_days(is_saturday_included))
    workingdays = date_range(datebegin, dateend, tz='Africa/Casablanca', freq=bdays)
	
    return workingdays