import re
import sys
import glob
import pickle


# format for baseball named entity
team = r"日本ハム|広島|オリックス|楽天|ロッテ|ソフトバンク|西武|巨人|中日|阪神|ヤクルト|DeNA|ＤｅＮＡ"

count = r"(\d+|初|延長(10|11|12))回"

pitcher = r"先発|中継ぎ|抑え|継投|失点|回まで|回途中|締め"


def format_text(text):
    # fix number format
    text = re.sub(r'０', "0", text)
    text = re.sub(r'一|１', "1", text)
    text = re.sub(r'二|２', "2", text)
    text = re.sub(r'三|３', "3", text)
    text = re.sub(r'四|４', "4", text)
    text = re.sub(r'五|５', "5", text)
    text = re.sub(r'六|６', "6", text)
    text = re.sub(r'七|７', "7", text)
    text = re.sub(r'八|８', "8", text)
    text = re.sub(r'九|９', "9", text)

    # fix string format
    # text = re.sub(team, "[チーム名]", text)
    # text = re.sub(place, "[試合会場]", text)
    # text = re.sub(batting_order, "[打順]", text)
    # text = re.sub(batting_position, "[打撃位置]", text)
    # text = re.sub(homerun_result, "[本塁打結果]", text)
    # text = re.sub(batting_result, "[打撃結果]", text)
    # text = re.sub(batting_pos_res, "[打撃位置][打撃結果]", text)
    # text = re.sub(point, "[得点]", text)
    # text = re.sub(pitcher, "[投手]", text)
    # text = re.sub(day, "[日付]", text)
    # text = re.sub(state, "[状況]", text)
    # text = re.sub(count, "[回数]", text)
    # text = re.sub(game_result, "[試合結果]", text)
    # text = re.sub(r"[0-9]+", "[数字]", text)
    # text = re.sub(r"奪[数字]振", "奪三振", text)  # 奪三振用
    return text


def extract_team_name(text):
    # extract team names
    team_names = re.findall(team, text)
    team_names = list(set(team_names))

    return team_names


def extract_count(text):
    # find count
    count_phrase = re.findall(count, text)

    return count_phrase


def extract_player_name(item, text):
    extracted_names = []
    for name in item:
        if len(name) == 1:
            continue

        if re.findall(name, text):
            extracted_names.append(name)

    # return last name
    last_name = ""
    m = 0
    for name in extracted_names:
        if text.find(name) > m:
            m = text.find(name)
            last_name = name

    return last_name


def read_files():
    files = glob.glob("./data/data/*")
    items = []
    for file_path in files:
        with open(file_path, "rb") as f:
            item = pickle.load(f)
        items.append(item)
    return items


def read_players_name():
    with open("./players_dataset.pickle", "rb") as f:
        item = pickle.load(f)

    players = []
    for team_name, team_players in item.items():
        players.extend(team_players)

    long_name_list = []  # 大谷翔平
    middle_name_list = []  # 大谷翔
    short_name_list = []  # 大谷
    for player in players:
        if len(player) > 1:
            long_name_list.append(player[0] + player[1])
            middle_name_list.append(player[0] + player[1][0])
        short_name_list.append(player[0])

    return long_name_list + middle_name_list + short_name_list

items = read_files()
players_item = read_players_name()
cnt = 0

articles_info = []
for item in items[]:
    text = item["body"]
    norm_text = format_text(text)
    sentences = norm_text.split("。")

    # extract game information
    game_card = extract_team_name(text)  # ex: ["阪神", "中日"]
    # year ex: 2016, month ex: 3, date ex: 25
    game_year = item["date"].split("年")[0]
    game_month = item["date"].split("年")[1].split("月")[0]
    game_date = item["date"].split("年")[1].split("月")[1].split("日")[0]

    article_info = {}
    article_info["card"] = game_card
    article_info["year"] = int(game_year[1:])
    article_info["month"] = int(game_month)
    article_info["date"] = int(game_date)

    article_plays = []  # 記事になったプレイ
    for sentence in sentences:
        # print(sentence)  # debug
        extracted_count = extract_count(sentence)
        if re.findall(r"その裏", sentence):
            extracted_count = count_buf

        extracted_player_name = extract_player_name(players_item, sentence)

        if extracted_count and extracted_player_name:
            if re.findall(pitcher, sentence):
                # for pitcher sentence
                article_plays.append(("pitch",
                                      extracted_count[-1][0],
                                      extracted_player_name))

                """
                print("pitch",
                      extracted_count[-1][0],
                      extracted_player_name)
                """

            else:
                # for batter sentence
                article_plays.append(("batting",
                                      extracted_count[-1][0],
                                      extracted_player_name))

                """
                print("batting",
                      extracted_count[-1][0],
                      extracted_player_name)
                """

        # print()  # debug
        count_buf = extracted_count

    article_info["article_plays"] = article_plays
    articles_info.append(article_info)

with open("./articles_info.pickle", "wb") as f:
    pickle.dump(articles_info, f)
