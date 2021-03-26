import configparser
from multiprocessing import cpu_count
import os
import sys


def config_reader(filename, log):
    section = 'server_options'
    config_data = {}
    path = f"{os.getcwd().rsplit('/', 1)[0]}/{filename}" if os.getcwd() != '/my_nginx' else filename
    if not os.path.isfile(path):
        log.error('wrong path to config file')
        sys.exit(1)
    with open(path) as f:
        file_content = f'[{section}]\n' + f.read()
    config = configparser.RawConfigParser(inline_comment_prefixes='#', delimiters=' ', strict=True)
    try:
        config.read_string(file_content)
        config_data['document_dir'] = config.get(section, 'document_root')
        config_data['port'] = config.getint(section, 'port')
        config_data['cpu_count'] = config.getint(section, 'cpu_limit')
    except configparser.Error as e:
        log.error(f'error in config sections:\n{e}')
        sys.exit(1)
    # if not os.path.isdir(config_data['document_dir']):
    #     log.error('wrong path to document_dir file')
    #     sys.exit(1)
    config_data['conn_timeout'] = 10
    config_data['parallel_conn'] = 500
    config_data['host'] = 'localhost'
    if config_data['port'] <= 0:
        config_data['port'] = 80
    if config_data['cpu_count'] <= 0:
        config_data['cpu_count]'] = cpu_count()
    return config_data
