import os
import requests
import telegram
import textwrap
import time


def send_message_to_tg(bot, chat_id, new_attempts):
    if new_attempts["is_negative"]:
        text = "К сожалению в работе нашлись ошибки"
    else:
        text = "Преподавателю всё понравилось, можно приступать к работе"

    text = textwrap.dedent(f'''\
    У вас проверили работу "{new_attempts['lesson_title']}"

    {text}
    https://dvmn.org{new_attempts['lesson_url']}''')
    bot.send_message(chat_id=chat_id, text=text)


def main():
    dvmn_token = os.environ["DVMN_TOKEN"]
    tg_token = os.environ["TG_TOKEN"]
    chat_id = os.environ["CHAT_ID"]
    bot = telegram.Bot(token=tg_token)

    headers = {
        "Authorization": f"Token {dvmn_token}",
    }
    params = None
    while True:
        try:
            response = requests.get("https://dvmn.org/api/long_polling/",
                                    headers=headers, params=params)
            response.raise_for_status()
        except requests.HTTPError:
            time.sleep(5)
            continue
        except ConnectionError:
            time.sleep(5)
            continue
        except requests.exceptions.ReadTimeout:
            continue

        decoded_response = response.json()
        if decoded_response["status"] == "timeout":
            params = {"timestamp": decoded_response["timestamp_to_request"]}
        elif decoded_response["status"] == "found":
            new_attempts = decoded_response["new_attempts"][0]
            send_message_to_tg(bot, chat_id, new_attempts)
            params = {"timestamp": decoded_response["last_attempt_timestamp"]}


if __name__ == "__main__":
    main()