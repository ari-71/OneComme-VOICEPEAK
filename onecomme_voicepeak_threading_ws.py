# Copyright (c) 2025 あり（ https://x.com/no_71_ari）
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

# わんコメ-VOICEPEAK 連携スクリプト（わんコメ バージョン5以降をご利用ください）
# v0.0.1

import json
import os
import re
import unicodedata
import subprocess
import asyncio
import uuid
import time
import signal
import random
from queue import Queue

import websockets
import config

async def ws_recv(websocket, comment_que):
    """websocket受信処理"""

    try:
        print('読み上げが可能な状態です... このスクリプトを停止する場合は ctrl + c で停止してください')

        voice_volume = config.VOICE_VOLUME
        voice_speed = '100'
        voice_pitch = '0'

        #重複読み上げ対策用にコメントIDを保存していく
        read_ids = set()

        while True:
            #データを受信するまで待つ（ブロッキング）
            data = json.loads(await websocket.recv())

            if data['type'] == 'connected':

                if config.DEBUG_FLAG:
                    print('わんコネからの接続情報を確認しました')

                # TODO: いい感じにする
                onecomme_volume = data['data']['config']['speech']['volume']
                # afplay用
                # voice_volume = str(round(float(onecomme_volume) * 2.0 * float(config.VOICE_VOLUME), 2))
                # ffplay用
                voice_volume = str(int(round(float(onecomme_volume ) * 1.0 * float(config.VOICE_VOLUME), 1)))

                if float(data['data']['config']['speech']['rate']) < 1.0:
                    voice_speed = str(round(100.0 - ((1.0 - float(data['data']['config']['speech']['rate'])) * 50.0 / 0.9)))
                else:
                    voice_speed = str(round(100.0 + ((float(data['data']['config']['speech']['rate'] - 1.0) * 100.0 / 2.5))))

                if float(data['data']['config']['speech']['pitch']) < 1.0:
                    voice_pitch = str(round(0.0 - float(1.0 - data['data']['config']['speech']['pitch']) * 300.0 / 0.9))
                else:
                    voice_pitch = str(round(float(data['data']['config']['speech']['pitch'] - 1.0) * 300.0))

                if config.DEBUG_FLAG:
                    print('わんコネの初期設定をしました')
                    print('読み上げボリューム：' + voice_volume)
                    print('読み上げ速度：' + voice_speed)
                    print('読み上げピッチ：' + voice_pitch)

            elif data['type'] == 'config':
                # TODO: いい感じにする
                # afplay用
                # voice_volume = str(round(float(data['data']['speech']['volume']) * 2.0 * float(config.VOICE_VOLUME), 2))
                # ffplay用
                voice_volume = str(int(round(float(data['data']['speech']['volume']) * 1.0 * float(config.VOICE_VOLUME), 1)))

                if float(data['data']['speech']['rate']) < 1.0:
                    voice_speed = str(round(100.0 - ((1.0 - float(data['data']['speech']['rate'])) * 50.0 / 0.9)))
                else:
                    voice_speed = str(round(100.0 + ((float(data['data']['speech']['rate'] - 1.0) * 100.0 / 2.5))))

                if float(data['data']['speech']['pitch']) < 1.0:
                    voice_pitch = str(round(0.0 - float(1.0 - data['data']['speech']['pitch']) * 300.0 / 0.9))
                else:
                    voice_pitch = str(round(float(data['data']['speech']['pitch'] - 1.0) * 300.0))

                if config.DEBUG_FLAG:
                    print('わんコネの設定変更を反映しました')
                    print('読み上げボリューム：' + voice_volume)
                    print('読み上げ速度：' + voice_speed)
                    print('読み上げピッチ：' + voice_pitch)

            elif data['type'] == 'comments':

                for commnent in data['data']['comments']:

                    #送られてきたデータに読み上げるテキストがある場合のみ処理を行う
                    #重複読み上げを防ぐために過去に読み上げたコメントIDをチェック
                    if (
                        'speechText' not in commnent['data'] or 
                        commnent['data']['id'] in read_ids
                        ):
                        continue

                    #読み上げるファイル名で使用する
                    comment_id = str(uuid.uuid4())

                    # DEBUG: ラインを出力
                    if config.DEBUG_FLAG:
                        print('------\nコメントID : ' + commnent['data']['id'])

                    #コメントの感情の初期値
                    happy = config.EMOTION_HAPPY
                    sad = config.EMOTION_SAD
                    fun = config.EMOTION_FUN
                    angry = config.EMOTION_ANGRY
                    bosoboso = config.EMOTION_BOSOBOSO
                    doyaru = config.EMOTION_DOYARU
                    honwaka = config.EMOTION_HONWAKA
                    teary = config.EMOTION_TEARY
                    ochoushimono = config.EMOTION_OCHOUSHIMONO

                    #タグの削除（絵文字や不具合文字なども含む）
                    read_comment = str(commnent['data']['speechText']).replace('&lt;', '<').replace('&gt;', '>')
                    read_comment = re.compile(r"<[^>]*?>").sub(' 略 ', read_comment)
                    read_comment = read_comment.replace("｀", "")
                    read_comment = read_comment.replace("`", "")
                    read_comment = read_comment.replace("\\", " ")

                    #半角カタカナを全角カタカナに
                    read_comment = unicodedata.normalize('NFKC', read_comment)

                    #コメントの改行やコーテーションを削除
                    read_comment = read_comment.replace('\n', ' ').replace('&quot;', ' ').replace('&#39;', ' ').replace('"', ' ')

                    #URL省略
                    read_comment = re.sub('https?://[A-Za-z0-9_/:%#$&?()~.=+-]+?(?=https?:|[^A-Za-z0-9_/:%#$&?()~.=+-]|$)', ' URL略 ', read_comment)

                    # wをワラと読むようにする

                    #絵文字から感情データを追加
                    if config.EMOTION_COMMENT:
                        if '😊' in read_comment:
                            happy = '100'
                            honwaka = '100'
                        if '😢' in read_comment:
                            sad = '100'
                            teary = '100'
                        if '😆' in read_comment:
                            fun = '100'
                            doyaru = '100'
                            ochoushimono = '100'
                        if '😡' in read_comment:
                            angry = '100'
                        if '😶‍🌫️' in read_comment:
                            bosoboso = '100'

                    #コメントの文字数がオーバーした場合は強制カットして、以下略をつける
                    if len(read_comment) > config.MAX_NUM_CHARACTERS:
                        read_comment = read_comment[:config.MAX_NUM_CHARACTERS] + ' 以下略'

                    #読み上げボイスをランダムにする
                    read_voice_narrator = config.VOICE_NARRATOR
                    if config.VOICE_NARRATOR == 'Japanese Female x':
                        read_voice_narrator = 'Japanese Female ' + str(random.randrange(1, 4, 1))
                    if config.VOICE_NARRATOR == 'Japanese Male x':
                        read_voice_narrator = 'Japanese Male ' + str(random.randrange(1, 4, 1))

                    #読み上げの性別変更
                    if config.SEX_COMMENT:
                        if '👨' in read_comment and read_voice_narrator != 'Japanese Female Child':
                            read_voice_narrator = read_voice_narrator.replace('Female', 'Male')
                            read_voice_narrator = read_voice_narrator.replace('Miyamai Moca', 'Frimomen')
                        if '👩' in read_comment:
                            read_voice_narrator = read_voice_narrator.replace('Male', 'Female')
                            read_voice_narrator = read_voice_narrator.replace('Frimomen', 'Miyamai Moca')

                    #読み上げファイル作成コマンド作成
                    read_command = [
                        config.VOICEPEAK_APP_FILEPATH,
                        "-s", read_comment,
                        "--speed", voice_speed,
                        "--pitch", voice_pitch,
                        "-o", config.OUTPUT_VOICE_DIRPATH + 'vp_' + comment_id + '.wav',
                        "-n", read_voice_narrator
                    ]
                    option = []
                    if 'Japanese' in read_voice_narrator:
                        option = ['-e', 'happy=' + happy + ',sad=' + sad + ',fun=' + fun + ',angry=' + angry]
                    elif 'Miyamai Moca' in read_voice_narrator:
                        option = ['-e', 'bosoboso=' + bosoboso + ',doyaru=' + doyaru + ',honwaka=' + honwaka + ',angry=' + angry + ',teary=' + teary]
                    elif 'Frimomen' in read_voice_narrator:
                        option = ['-e', 'happy=' + happy + ',angry=' + angry + ',sad=' + sad + ',ochoushimono=' + ochoushimono]
                    elif 'Kasane Teto' in read_voice_narrator:
                        # TODO: とりあえず固定値
                        option = ['-e', 'teto-overactive=0,teto-low-key=0,teto-whisper=0,teto-powerful=0,teto-sweet=0']

                    if len(option) > 0:
                        read_command.extend(option)

                    if config.DEBUG_FLAG:
                        print(read_command)

                    #読み上げファイル作成
                    for i in range(config.MAX_RETRY):
                        if config.DEBUG_FLAG:
                            #read_command_result = 1 #失敗テスト用
                            p = subprocess.Popen(read_command, shell = True)
                        else:
                            p = subprocess.Popen(read_command, shell = True, stderr = subprocess.PIPE)

                        read_command_result = p.wait()

                        if read_command_result == 0:
                            #キューに追加する（別スレッドでデキューする）
                            await comment_que.put((comment_id, voice_volume))
                            print('success')

                            #コメントIDを保存
                            read_ids.add(commnent['data']['id'])
                            break
                        elif i == config.MAX_RETRY - 1:
                            if config.DEBUG_FLAG:
                                print('ファイル作成失敗 ' + str(i + 1) + '回目')
                            await comment_que.put((comment_id, voice_volume))
                            break
                        else:
                            if config.DEBUG_FLAG:
                                print('ファイル作成失敗 ' + str(i + 1) + '回目')
                                print(read_command)
                            time.sleep(0.5)

                    else:
                        if config.DEBUG_FLAG:
                            print('わんコメの読み上げが有効になっていません : ' + commnent['service'])
    except Exception as e:
        print('このスクリプトの異常動作もしくはわんコメのアプリケーション終了を検知しました。このスクリプトをctrl + cで終了してください')
        print(f"\"{e}\"")

async def func_make(comment_que):
    """ 音声データ作成用関数 """
    """ websocket接続処理 """
    try:
        #固定のため直書き
        async with websockets.connect("ws://127.0.0.1:11180/sub?p=comments,config") as websocket:
            print('わんコメとの接続が完了しました。')
            await ws_recv(websocket,comment_que)

    except Exception as e:
        print('WebSocketの接続ができません。このスクリプトをctrl + cで一度終了し、わんコメを立ち上げてから再度起動してください。')
        print(f"\"{e}\"")

async def func_read(comment_que):
    """ 音声データ読み上げ用関数 """

    #キューに入ってるファイルを一つづつ読み上げる
    while True:

        #コメントのキューを取得するまで待つ（キューが空になるとブロッキング）
        comment_tuple = await comment_que.get()

        #読み上げファイル存在チェック
        file_name = 'vp_' + str(comment_tuple[0]) + '.wav'
        read_file_path = config.OUTPUT_VOICE_DIRPATH + file_name
        # FFPLAYは環境変数を理解しないので変換
        read_file_path = os.path.expandvars(read_file_path)
        is_file = os.path.isfile(read_file_path)

        #読み上げ音量
        read_volume = comment_tuple[1]
        # TODO: optionをプレイヤーごとに切り替えできるようにしたい
        # afplay
        # play_cmd = [
        #     config.PLAYER_FILEPATH,
        #     read_file_path ,
        #     '-v', read_volume,
        # ]
        # FFPLAY用のoption
        play_cmd = [
            config.PLAYER_FILEPATH,
            '-nodisp',
            '-autoexit',
            '-volume', read_volume,
            read_file_path
        ]

        if is_file:
            if config.DEBUG_FLAG:
                proc = subprocess.Popen(play_cmd, shell = True)
            else:
                proc = subprocess.Popen(play_cmd, shell = True, stderr = subprocess.PIPE)

            proc.wait()
            #読み上げファイルを削除
            os.remove(read_file_path)

        #ファイルが存在しない場合はエラーメッセージを読み上げる
        else:
            if config.DEBUG_FLAG:
                print('読み上げ実行失敗。以下のファイルが存在していません')
                print(read_file_path)
            is_file = os.path.isfile(config.EXCEPTION_OUTPUT_VOICE_FILEPATH)
            if is_file:
                if config.DEBUG_FLAG:
                    proc = subprocess.Popen(play_cmd, shell = True)
                else:
                    proc = subprocess.Popen(play_cmd, shell = True, stderr = subprocess.PIPE)
            else:
                if config.DEBUG_FLAG:
                    print('読み上げができなかった場合（エラー等）に読み上げるwavファイルがないので無音です。')
                    print('読み上げ失敗用のwavファイルを用意し、.envのEXCEPTION_OUTPUT_VOICE_FILEPATHを設定してください')

async def main():
    """メイン処理"""

    #ctrl+cでスクリプト終了
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    #コメントデータキュー
    comment_que = asyncio.Queue()

    print('スクリプト起動...')
    await asyncio.gather(
        func_make(comment_que), #コメント音声データ作成
        func_read(comment_que) #コメント読み上げ処理
    )

    #通常はここまで処理は来ない
    print('スレッド関連のエラー発生')

if __name__ == '__main__':
    asyncio.run(main())
