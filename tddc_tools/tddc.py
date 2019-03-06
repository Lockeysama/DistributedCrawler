# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: tddc.py
@time: 2019-03-05 16:38
"""
import os
import sys

import click


@click.group()
def tddc():
    """TDDC Tools."""


@tddc.command()
@click.option(
    '--type',
    prompt=('Please Input Worker Type:\n0.manager_api\n1.timing_crawler '
            '\n2.timing_parser\n3.keep_crawler\n4.proxies_checker\nInput Option Number'),
    help='timing_crawler | timing_parser | keep_crawler | proxies_checker.'
)
@click.option('--name', prompt='Please Input Project Name', help='Input Project Name.')
@click.option('--path', prompt='Please Input Project Path', default='.', help='Project Path. Default "./"')
def create(type, name, path):
    types = {
        '0': 'manager_api',
        '1': 'timing_crawler',
        '2': 'timing_parser',
        '3': 'keep_crawler',
        '4': 'proxies_checker'
    }
    _type = types.get(type)
    if not _type:
        print('Type Not Found.')
        exit(0)
    path = path[:-1] if path[-1] == '/' else path
    cur_path = '{}/{}'.format(path, name)
    os.mkdir(cur_path)
    site_packages_path = None
    for p in sys.path:
        if 'site-packages' in p:
            site_packages_path = p
            break
    if not site_packages_path:
        print('site-packages Path Not Found.')
        exit(0)
    os.system('cp -rf {} {}'.format(
        '{}/tddc_tools/templates/{}/*'.format(site_packages_path, _type),
        cur_path
    ))
    os.system('find {} -name "__pycache__" | xargs rm -rf'.format(cur_path))
    os.system('rm -rf {}/__init__.py'.format(cur_path))
    print('Created Success.')
    if _type == 'manager_api':
        print('PS: "manager_api" only Restful API, Front End Need Additional Deployment.')


if __name__ == '__main__':
    tddc()
