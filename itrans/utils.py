import json
import subprocess


def get_time_file(filename, extension, file_path):
    response = {'status': False, 'errors': []}
    try:
        # result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
        #   file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
                                    file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        file_json = json.loads(result.stdout)
        if extension == '.webm':
            duration = file_json['streams'][0]["tags"]['DURATION']
            d = str(duration).split(".")
            h, m, s = d[0].split(':')
            duration = int(h) * 3600 + int(m) * 60 + int(s)
            file_type = 'video/webm'
        else:
            extension = extension.replace('.', '')
            file_type = '%s/%s' % (file_json['streams'][0]['codec_type'], 'mpeg' if extension == 'mp3' else extension)
            duration = file_json['streams'][0]['duration']
        print('file_type:', file_type)
        print('duration:', duration)
        response["data"] = '%ss' % int(float(duration))
        response["type"] = file_type
        response["status"] = True
    except Exception as e:
        print('Exception:', repr(e))
    return response


def get_file_minute(length):
    response = {'status': False, 'errors': [], "data": ""}
    try:
        length = (float(length.replace("s", "")) / 60.0)
        value_with_point = length
        value_without_point = float(int(length))
        if value_without_point < value_with_point:
            length += 1.0
        else:
            length = value_without_point
        return int(length)
    except Exception as e:
        response['errors'].append(repr(e))
        print('Exception:', repr(e))
    return response
