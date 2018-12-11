from mailmerge import MailMerge
from pandas import read_csv
import os

def create_tsk_journal(datasrc: str, template: str, output: str, **kwargs):
    try:
        data = read_csv(datasrc)
    except FileNotFoundError as e:
        e.errno    = -1
        e.filename = datasrc
        e.strerror = 'ملف بيانات المذكرة غير موجود'
        return e

    if 'weekrange' in kwargs:
        filter = str(kwargs['weekrange'][0]) + '<= weeknum <= ' + str(kwargs['weekrange'][1])
        weekplan = data.query(filter)
    else:
        weekplan = data

    fields = weekplan.to_dict('records')
    document = MailMerge(template)
    document.merge_pages(fields)
    document.write(output)

    # for windows only systems
    # is like double clicking on the file
    if 'openit' in kwargs and kwargs['openit']:
        os.startfile(output)


template = 'TASKBOARDFORM.docx'
output = 'المذكرة اليومية.docx'
datasrc = '../journal/df.csv'

k = 11
weekrng= (k, k)
e = create_tsk_journal(datasrc, template, output, openit=True) 

# works of any plateform
# import subprocess
# subprocess.call(['C:\\Program Files\\Microsoft Office\\Office12\\winword.exe',
                 # 'C:\\Users\\pc\\Documents\\devenv\\view\\المذكرة اليومية.docx'])