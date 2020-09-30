import requests


def valid_ids(group_id, token, api_version):
    payload = {'group_id': group_id, 'access_token': token, 'v': api_version}
    response = requests.get('https://api.vk.com/method/groups.getMembers', params=payload)
    response_dict = response.json()
    group_ids = response_dict['response']['items']
    allowed_ids = []
    for item in group_ids:
        is_allowed = requests.get(f'https://api.vk.com/method/messages.isMessagesFromGroupAllowed?user_id={item}',
                                  params=payload).json()["response"]["is_allowed"]
        if is_allowed:
            allowed_ids.append(item)
    return allowed_ids

