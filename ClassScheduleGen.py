#!/usr/bin/env python3
# -*- coding:utf-8 -*

import JXFWLogin
import json
import argparse
import time
import csv


class ClassScheduleGen(JXFWLogin.AuthserverLogin):

    URL_CS = 'http://jxfw.gdut.edu.cn/xsgrkbcx!getDataList.action'
    DATA_POST = {
        'zc': '',
        'xnxqdm': '201802',
        'page': '1',
        'rows': '100',
        'sort': 'kxh',
        'order': 'asc'
    }

    def getjson(self):
        temp = input('请输入你要查询的学期(格式为年份+学期，默认为201802):\n')
        self.DATA_POST['xnxqdm'] = temp if temp.isdigit(
        ) and temp != '' else '201802'
        cs = self._session.post(self.URL_CS, data=self.DATA_POST)
        yield cs.json()
        for i in range(2, round(cs.json()['total'] / 100)+1):
            self.DATA_POST['page'] = i
            yield self._session.post(self.URL_CS, data=self.DATA_POST).json()

START_LIST = {
    '01': '08:30',
    '03': '10:25',
    '05': '13:50',
    '06': '14:40',
    '08': '16:30',
    '10': '18:30'
}

END_LIST = {
    '02': '10:05',
    '04': '12:00',
    '07': '16:15',
    '09': '18:05',
    '12': '20:55'
}

START_LIST_EXT = {
    '01': '08:15',
    '03': '10:10',
    '05': '13:30',
    '06': '14:20',
    '08': '16:15',
    '10': '18:30'
}

END_LIST_EXT = {
    '02': '09:50',
    '04': '11:45',
    '05': '13:30',
    '07': '15:50',
    '09': '17:50',
    '12': '20:55'
}

HELP_DESCRIPTION = '一个用于生成GDUT课程表的脚本'
parser = argparse.ArgumentParser(
    prog='./ClassScheduleGen.py', description=HELP_DESCRIPTION)
group = parser.add_mutually_exclusive_group()
group.add_argument('--csv', action='store_true', help='生成 CSV 格式')
group.add_argument('--ics', action='store_true', help='生成 ICS 格式')
parser.add_argument('--ext', action='store_true', help='使用龙洞和东风路校区的课程时间')
args = parser.parse_args()


def to_csv():
    csg = ClassScheduleGen()
    with open('ClassSchedule.csv', 'w', newline='') as f:
        headers = ['Subject', 'Location', 'Start Date',
                   'Start Time', 'End Date', 'End Time', 'Description']
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        for i in csg.getjson():
            for j in i['rows']:
                writer.writerow(
                    {
                        'Subject': j['kcmc'],  # 课程
                        'Location': j['jxcdmc'],  # 上课地点
                        'Start Date': j['pkrq'].replace('-', '/'),  # 上课时间
                        'Start Time': START_LIST[j['jcdm'][:2]],  # 上课开始时间
                        'End Date': j['pkrq'].replace('-', '/'),  # 上课时间
                        'End Time': END_LIST[j['jcdm'][-2:]],  # 上课结束时间
                        'Description': (j['sknrjj']).replace('\n', ' ')
                    }
                )
    print('处理完成')


def to_ics():
    csg = ClassScheduleGen()
    timenow = time.strftime('%Y%m%dT%H%M%SZ', time.localtime())
    with open('ClassSchedule.ics', 'w') as f:
        f.writelines([
            'BEGIN:VCALENDAR\n',
            'PRODID:GDUTClassScheduleGen\n',
            'VERSION:2.0\n',
            'CALSCALE:GREGORIAN\n',
            'METHOD:PUBLISH\n',
            'X-WR-CALNAME:GDUT课程表\n',
            'X-WR-TIMEZONE:Asia/Shanghai\n'
        ])
        for i in csg.getjson():
            for j in i['rows']:
                f.writelines([
                    'BEGIN:VEVENT\n',
                    'DTSTART:{}T{}Z\n'.format(j['pkrq'].replace('-', ''), START_LIST[j['jcdm'][:2]].replace(':', '')+'00'),
                    'DTEND:{}T{}Z\n'.format(j['pkrq'].replace('-', ''), END_LIST[j['jcdm'][-2:]].replace(':', '')+'00'),
                    'DTSTAMP:{}\n'.format(timenow),
                    'UID:{}{}@gdutcs\n'.format(j['pkrq'].replace('-', ''), END_LIST[j['jcdm'][-2:]].replace(':', '')+'00'),
                    'CREATED:{}\n'.format(timenow),
                    'DESCRIPTION:{}\n'.format(j['sknrjj'].replace('\n', ' ')),
                    'LAST-MODIFIED:{}\n'.format(timenow),
                    'LOCATION:{}\n'.format(j['jxcdmc']),
                    'SEQUENCE:0\n',
                    'STATUS:CONFIRMED\n',
                    'SUMMARY:{}\n'.format(j['kcmc']),
                    'TRANSP:OPAQUE\n',
                    'END:VEVENT\n'
                ])
        f.write('END:VCALENDAR\n')
    print('处理完成')


if __name__ == '__main__':
    if args.ext:
        START_LIST = START_LIST_EXT
        END_LIST = END_LIST_EXT
    if args.csv:
        to_csv()
    if args.ics:
        to_ics()
    if not args.csv and not args.ics:
        print('请选择生成的格式或使用 -h/--help 查看选项')
