#!/usr/bin/env python3
#
# score.py
#
# Execute: ./score.py urls.txt rapports.csv


from datetime import datetime
import json
import subprocess
from urllib.parse import urlparse
from collections import OrderedDict

import pandas as pd
import matplotlib.pyplot as plt
import pylab


class ShellError(Exception):
    pass


def execute_lighthouse(url):
    o = urlparse(url)
    report_name = o.path[1:].replace('/', '--')
    hostname = o.hostname
    cmd = ['lighthouse {} '
           '--output=json --output-path=./reports/{}--{}.json'.format(
                url,
                hostname,
                report_name
            )]
    status = subprocess.call(cmd, shell=True)
    if status != 0:
        raise ShellError


def get_reports(urls_filename):
    with open(urls_filename, 'r') as desc:
        urls = desc.readlines()
    for url in urls:
        try:
            execute_lighthouse(url.strip())
        except ShellError:
            continue


def aggregate_reports(report_filenames, csv_filename):
    scores = list()
    for report_filename in report_filenames:
        score = compute_score(report_filename)
        scores.append(score)
    df = pd.DataFrame(scores)
    df.to_csv(csv_filename, index=False)
    return df


def compute_score(report_filename):
    score = OrderedDict()
    with open(report_filename, 'r') as desc:
        content_json = json.load(desc)
    score['url'] = content_json.get('url', None)
    date = content_json.get('generatedTime', None)
    if date:
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        score['date'] = datetime.strftime(date, '%Y-%m-%d')
    for reportCategory in content_json.get('reportCategories', list()):
        category = reportCategory.get('id', None)
        note = reportCategory.get('score', None)
        score[category] = round(note, 2)
    return score


def show_aggregated_reports(csv_filename):
    df = pd.read_csv(csv_filename)
    df.plot.line(x='url', style='-o', legend=True)
    plt.xlabel('')
    pylab.ylim([0, 100])
    plt.xticks(rotation=90)
    plt.yticks(rotation=90)
    pylab.savefig("scores.png",
                  additional_artists=[],
                  bbox_inches="tight")


if __name__ == "__main__":
    import sys
    import glob

    args = sys.argv[1:]
    urls_filename = args[0]
    csv_filename = args[1]

    get_reports(urls_filename)
    report_filenames = glob.glob('./reports/*.json')
    df = aggregate_reports(report_filenames, csv_filename)
