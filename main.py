import multiprocessing
import time
from random import randint

import vk_api
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import data_base


def mailing(owner_id, event_id):
    token = ''
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    with data_base.session_scope() as session:
        chat_ids = session.query(data_base.ChatIds).all()
        for id in chat_ids:
            vk.messages.send(peer_id=id.chat_id, random_id=(randint(-2_147_483_648, 2_147_483_647)),
                             attachment=f"wall{owner_id}_{event_id})")
        print("Сообщения разосланы")


def first_group(group_id, token):
    engine = create_engine('sqlite:///chat_ids.sqlite', echo=False)
    data_base.init_db(engine)
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, group_id, wait=25)
    smi_tags = ["#АктивистЭМИТ", "#АнонсЭМИТ", "#ВнеЭМИТ", "#ЛичностьЭМИТ", "#НовостиЭМИТ", "#ПартнерыЭМИТ",
                "#ПослевкусиеЭМИТ", "#СтудСоветЭМИТ", "#УмныйЭМИТ", "#1337pacan"]
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    session: Session
                    with data_base.session_scope() as session:
                        if session.query(data_base.ChatIds).get(event.object['peer_id']) is None:
                            session.add(data_base.ChatIds(event.object['peer_id']))
                            print(f'Новая беседа:{event.object["peer_id"]}')
                if event.type == VkBotEventType.WALL_POST_NEW:
                    if any(tags in event.object['text'] for tags in smi_tags):
                        mailing(event.object['owner_id'], event.object['id'])
        except Exception as pain:
            print(f"В первом процессе произошел: {pain}")


def second_group(group_id, service_token):
    engine = create_engine('sqlite:///chat_ids.sqlite', echo=False)
    data_base.init_db(engine)
    vk_session = vk_api.VkApi(token=service_token)
    vk = vk_session.get_api()
    while True:
        try:
            response = vk.wall.get(owner_id=group_id, count=1)
            with data_base.session_scope() as session:
                if session.query(data_base.PostHistory).get(response['items'][0]['id']) is None:
                    print("У нас тут новый пост во второй группе")
                    session.add(data_base.PostHistory(response['items'][0]['id']))
                    # Если мониторим не репосты, то нужно убрать ['copy_history'][0]
                    mailing(response['items'][0]['copy_history'][0]['owner_id'],
                            response['items'][0]['copy_history'][0]['id'])
            time.sleep(20)
        except Exception as pain:
            print(f"Во втором процессе проиозшел: {pain}")


if __name__ == '__main__':
    try:
        # Данные вк
        token = ''
        service_token = ''
        first_id = ''
        second_id = '-'  # Обязательно с минусом!!!
        api_version = '5.52'

        # Мультипроцесс
        first_process = multiprocessing.Process(target=first_group, args=(first_id, token))
        first_process.start()
        second_process = multiprocessing.Process(target=second_group, args=(second_id, service_token))
        second_process.start()
    except (KeyboardInterrupt, SystemExit) as e:
        print("Помянем...")
    except Exception as genericException:
        print(f"Че-то совсем плохо: {genericException}")
        pass
