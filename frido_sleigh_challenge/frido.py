import subprocess
import base64
import os
import requests

def parse_and_write_images(data):
    image_data = data.get('images')

    image_dirname = 'unknown_images'
    if not 'unknown_images' in os.listdir():
        os.mkdir(image_dirname)

    for item in image_data:
        fname = item.get('uuid')
        image = item.get('base64')
        image_bytes = base64.b64decode(image)
        with open(f"{image_dirname + os.sep + fname}.png", 'wb') as fh:
            fh.write(image_bytes)

def parse_output(output):
    words_to_find = 'Waiting For Threads to Finish...'
    results = output.split(words_to_find)[1].splitlines()
    parsed_results = []
    for line in results:
        if not line: continue
        fname = line.split()[2].split('/')[1]
        category = line.split()[5]
        parsed_results.append((category, fname))
    return parsed_results

def main():
    print(f'[*] Establishing session with {url}')
    s = requests.Session()
    resp = s.get(url)

    print(f'[*] Navigating to {captcha_url} and downloading the images')
    resp = s.post(captcha_url)
    data = resp.json()

    print('[*] Writing images to disk for analysis')
    parse_and_write_images(data)

    print('[*] Analyzing images...')
    output = subprocess.getoutput('python3 predict_images_using_trained_model.py')
    parsed_output = parse_output(output)
    print('[*] Analysis complete!')

    selections = data.get("select_type")
    print(f'[*] Sending back images of {selections}')
    selection_uuids = []
    for item in parsed_output:
        if item[0] in selections:
            selection_uuids.append(item[1].split('.')[0])
    answers = ','.join(selection_uuids)
    post_data = {'answer': answers}
    resp = s.post(captcha_ans_url, post_data)
    print(resp.text)


if __name__ == '__main__':

    url = 'https://fridosleigh.com/'
    captcha_url = url + 'api/capteha/request'
    captcha_ans_url = url + 'api/capteha/submit'
    main()