import sqlite3 as sq

db = sq.connect('tg.db')
cur = db.cursor()
async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS accounts("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "    # порядковый уникальный id
                "tg_id INTEGER, "                           # id в телеграмме
                "type_route INTEGER, "                      # тип маршрута, 1-оффлайн, 2-онлайн
                "chosen_rout INTEGER, "                     # выбранный маршрут
                "get_points INTEGER, "                      # количество собранных геоточек (0 по умолчанию)
                "bm_id INTEGER, "                           # id сообщения бота которое он изменяет
                "flag INTEGER, "                            # флаг на отправление локации
                "flag_1 INTEGER)")                          # флаг на изменение локации

    cur.execute("CREATE TABLE IF NOT EXISTS ofl_routes("    # оффлайн маршруты с описанием
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "preview TEXT, "                            # превью (описание двумя-тремя словами)
                "caption TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS onl_routes("    # онлайн маршруты с трансляцией геопозиции
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "preview TEXT, "                            # превью (описание двумя-тремя словами)
                "number_points INTEGER, "                   # общее количество геоточек, не более 7
                "lat1 REAL, "                            
                "lon1 REAL, "
                "lat2 REAL, "
                "lon2 REAL, "
                "lat3 REAL, "                            # # # # # # # # # # # # # # # # #
                "lon3 REAL, "                            # широта и долгота каждой точки #
                "lat4 REAL, "                            # # # # # # # # # # # # # # # # #
                "lon4 REAL, "
                "lat5 REAL, "
                "lon5 REAL, "
                "lat6 REAL, "
                "lon6 REAL, "
                "lat7 REAL, "
                "lon7 REAL, "
                "lat8 REAL, "
                "lon8 REAL, "
                "lat9 REAL, "
                "lon9 REAL, "
                "lat10 REAL, "
                "lon10 REAL)")

    db.commit()

async def cmd_start_db(user_id): # добавление тг id юзера
    user = cur.execute("SELECT * FROM accounts WHERE tg_id == {key}".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO accounts (tg_id) VALUES ({key})".format(key=user_id))
        cur.execute("UPDATE accounts SET get_points = 0, flag = 0, flag_1 = 0 WHERE tg_id = {key}".format(key=user_id))
        db.commit()

async def show_flag(user_id): # флаг на отправку геолокации
    flag = cur.execute("SELECT flag FROM accounts WHERE tg_id = {id}".format(id=user_id)).fetchone()[0]
    cur.execute("UPDATE accounts SET flag = 1 WHERE tg_id = {id}".format(id=user_id))
    db.commit()
    return int(flag)

async def flag1(id): # флаг на изменение сообщения с расстоянием
    cur.execute("UPDATE accounts SET flag_1 = 1 WHERE tg_id = {id}".format(id=id))
    db.commit()

async def flag1_set0(id): # обнуление флага
    cur.execute("UPDATE accounts SET flag_1 = 0 WHERE tg_id = {id}".format(id=id))
    db.commit()
async def flag1_view(id): # получение значения флага
    flag1 = cur.execute("SELECT flag_1 FROM accounts WHERE tg_id = {id}".format(id=id)).fetchone()[0]
    return int(flag1)

async def add_offline_rout(mess, mess1 ): #создание оффлайн маршрута
    cur.execute("INSERT INTO ofl_routes (preview, caption) VALUES (?, ?)", (mess, mess1, ))
    db.commit()

async def add_online_rout(mess): #создание онлайн маршрута
    mess = tuple(mess)
    cur.execute("INSERT INTO onl_routes (preview, number_points, lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4, lat5, lon5, lat6, lon6, lat7, lon7, lat8, lon8, lat9, lon9, lat10, lon10) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", mess)
    db.commit()

async def show_offline(): # вывод доступных оффлайн маршрутов
    cur.execute("SELECT id, preview FROM ofl_routes")
    a = []
    for rout in cur.fetchall():
        a.append(f'{rout[0]} {rout[1]}\n')
    return ' '.join(a)

async def show_online(): # вывод доступных онлайн маршрутов
    cur.execute("SELECT id, preview FROM onl_routes")
    a = []
    for rout in cur.fetchall():
        a.append(f'{rout[0]} {rout[1]}\n')
    return ' '.join(a)

async def set_type_ofl(id): # офлайн тип
    cur.execute("UPDATE accounts SET type_route = 1 WHERE tg_id = {key}".format(key=id))
    db.commit()

async def set_type_onl(id): # онлайн тип
    cur.execute("UPDATE accounts SET type_route = 2 WHERE tg_id = {key}".format(key=id))
    db.commit()

async def set_number(number, id): # запись номера маршрута
    cur.execute("UPDATE accounts SET chosen_rout = ? WHERE tg_id = ?", (number, id))
    db.commit()

async def get_caption_off(id): # забирание описания оффлайн маршрута
    cur.execute("SELECT chosen_rout FROM accounts WHERE tg_id = ?", (id, ))
    number = int(cur.fetchone()[0])
    cur.execute("SELECT caption FROM ofl_routes WHERE id = ?", (number, ))
    return (cur.fetchone()[0])

async def get_cords(id): #получение координат конкретной точки на маршруте, общего количества точек и точек которые юзер прошёл
    point = cur.execute("SELECT get_points FROM accounts WHERE tg_id = {key}".format(key=id)).fetchone()[0] + 1 # номер точки
    rout = cur.execute("SELECT chosen_rout FROM accounts WHERE tg_id = {key}".format(key=id)).fetchone()[0]     # номер маршрута
    all_points = cur.execute("SELECT number_points FROM onl_routes WHERE id = {key}".format(key=rout)).fetchone()[0]
    lat = str(f"lat{point}")
    lon = str(f"lon{point}")
    a=[]
    a.append(cur.execute("SELECT {key} FROM onl_routes WHERE id = {rout}".format(key=lat, rout=rout)).fetchone()[0])
    a.append(cur.execute("SELECT {key} FROM onl_routes WHERE id = {rout}".format(key=lon, rout=rout)).fetchone()[0])
    a.append(all_points)
    a.append(point)
    return a

async def set_bm_id(id, bm_id):
    cur.execute("UPDATE accounts SET bm_id = {bm_id} WHERE tg_id = {id}".format(bm_id=bm_id, id=id))
    db.commit()

async def show_bm_id(id):
    bm_id = cur.execute("SELECT bm_id FROM accounts WHERE tg_id = {id}".format(id=id)).fetchone()[0]
    return int(bm_id)

async def plus_get_point(id): # увеличение собранных точек на 1
    a = cur.execute("SELECT get_points FROM accounts WHERE tg_id = {key}".format(key=id)).fetchone()[0]
    cur.execute("UPDATE accounts SET get_points = {a} WHERE tg_id = {id}".format(a=a+1, id=id))
    db.commit()
    return a

async def delete_prog(id): # удаляет прогресс
    cur.execute("UPDATE accounts SET type_route=0, chosen_rout=0, get_points=0, flag = 0, flag_1 = 0 WHERE tg_id={key}".format(key=id))
    db.commit()

async def delete_route_onl(id): # удаление оффлайн маршрута
    cur.execute("DELETE FROM onl_routes WHERE id = {key}".format(key=id))
    db.commit()

async def delete_route_ofl(id): # удаление онлайн маршрута
    cur.execute("DELETE FROM ofl_routes WHERE id = {key}".format(key=id))
    db.commit()