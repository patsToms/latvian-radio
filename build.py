#!/usr/bin/env python3

'''
    pip3 install python-slugify
'''

import json
import subprocess
from typing import NamedTuple
import os
import glob
from slugify import slugify


DIST_PATH = 'dist/'
STREAMS_BUILD_FILE = 'streams.json'


class FFProbeResult(NamedTuple):
    return_code: int
    json: str
    error: str


'''
    https://stackoverflow.com/a/61927951
'''
def ffprobe(file_path) -> FFProbeResult:
    command_array = ["ffprobe",
                     "-v", "quiet",
                     "-print_format", "json",
                     "-show_format",
                     "-show_streams",
                     file_path]
    result = subprocess.run(command_array,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
    return FFProbeResult(return_code=result.returncode,
                         json=result.stdout,
                         error=result.stderr)


def build_json(radios):
    build_path = DIST_PATH + STREAMS_BUILD_FILE
    streams_json_file = open(build_path, "w")
    streams_json_file.write(json.dumps(radios, indent=4, ensure_ascii=False))
    streams_json_file.close()
    print('Streams build in ' + build_path)


def build_strm(radios):

    strm_path = DIST_PATH + 'strm/'

    print('Clearing ' + strm_path)

    strm_files = glob.glob(strm_path + '*')

    for strm_file in strm_files:
        os.remove(strm_file)

    for radio in radios:
        strm_file_path = strm_path + radio['title'] + '.strm'
        print('Writing ' + strm_file_path)
        strm_file = open(strm_file_path, 'w')
        strm_file.write(radio['stream']['url'])
        strm_file.close()

    print('Done building strm files')


def build_pls(radios):

    pls_path = DIST_PATH + 'pls/'

    print('Clearing ' + pls_path)

    pls_files = glob.glob(pls_path + '*')

    for pls_file in pls_files:
        os.remove(pls_file)

    for radio in radios:
        pls_file_path = pls_path + slugify(radio['title']) + '.pls'
        print('Writing ' + pls_file_path)
        strm_file = open(pls_file_path, 'w')
        pls_content = '''\
[playlist]
File1={url}
Title1={title}
NumberOfEntries=1'''.format(title=radio['title'], url=radio['stream']['url'])
        strm_file.write(pls_content)
        strm_file.close()


def build_m3u(radios):
    m3u_path = DIST_PATH + 'm3u/'

    print('Clearing ' + m3u_path)

    m3u_files = glob.glob(m3u_path + '*')

    for m3u_file in m3u_files:
        os.remove(m3u_file)

    for radio in radios:
        m3u_file_path = m3u_path + slugify(radio['title']) + '.m3u'
        print('Writing ' + m3u_file_path)
        strm_file = open(m3u_file_path, 'w')
        m3u_content = '''\
#EXTM3U
#EXTINF:1,{title}
{url}'''.format(title=radio['title'], url=radio['stream']['url'])
        strm_file.write(m3u_content)
        strm_file.close()


if __name__ == '__main__':

    with open('streams.json') as json_file:
        radio_stations = json.load(json_file)['radio_stations']

    radios_output = []

    for radio_station in radio_stations:

        print('Probing ' + radio_station['title'])
        for stream in radio_station['streams']:

            ffprobe_result = ffprobe(file_path=stream)

            if ffprobe_result.return_code == 0:

                stream_ffprobe = json.loads(ffprobe_result.json)

                if not stream_ffprobe['streams']:
                    print('Stream' + 'for ' + radio_station['title'] + ' is offline')
                    continue

                stream_title = ''

                if 'icy-name' in stream_ffprobe['format']['tags']:
                    stream_title = stream_ffprobe['format']['tags']['icy-name']
                else:
                    stream_title = radio_station['title']

                stream_title = stream_title+ ' ' + \
                    str(int(stream_ffprobe['streams'][0]['bit_rate'])/1000) + 'kbit ' + \
                    stream_ffprobe['streams'][0]['codec_name']

                stream_data = {
                    'title': stream_title,
                    'stream': {
                            'url': stream_ffprobe['format']['filename'],
                            'codec': stream_ffprobe['streams'][0]['codec_name'],
                            'channels': stream_ffprobe['streams'][0]['channels'],
                            'bit_rate': int(stream_ffprobe['streams'][0]['bit_rate'])
                    }
                }

                radios_output.append(stream_data)

    build_json(radios_output)
    build_strm(radios_output)
    build_pls(radios_output)
    build_m3u(radios_output)