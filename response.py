import pymysql
import base64

total_amount = 0
total_discount = 0
end_flag = True
target_content = ''
target_text = ''

# store sql values waiting to be executed
sandwich_panini_values = []
cold_drinks_values = []
snakes_values = []
hot_drinks_values = []
cookie_shortbread_values = []
others_values = []
trans_values = []

deals_values = []
pays_values = []
deal_id_current = 1000


class DataBase(object):

    def __init__(self):
        name = 'testdb'
        password = 'KYU542722'
        self.conn = pymysql.connect('localhost', 'root', str(password), str(name), charset='utf8')
        self.cursor = self.conn.cursor()

    def __enter__(self):
        # return cursor and assign after 'as'
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


def get_deal_items():
    # get deal items
    cold_drinks = []
    hot_drinks = []
    sandwich_panini = []
    snakes = []
    cookie_shortbread = []

    deal_items = [cold_drinks, hot_drinks, sandwich_panini, snakes, cookie_shortbread]
    get_deal_sqls_where = ['classid IN (4)', 'classid IN (1,2,3)', 'classid IN (0, 5, 7)',
                           'classid = 8 AND name REGEXP \'chips|popcorn|piece of fruit\'',
                           'classid = 8 AND name REGEXP \'cookie|shortbread\'']
    with DataBase() as db:
        for i, s in enumerate(get_deal_sqls_where):
            db.execute('SELECT DISTINCT productid FROM products WHERE ' + s + ';')
            data = db.fetchall()
            for d in data:
                deal_items[i].append(d[0])

    deal_a = set(sandwich_panini)|set(cold_drinks)|set(snakes)
    deal_b = set(hot_drinks)|set(cookie_shortbread)

    return deal_items, deal_a, deal_b


deal_items, deal_a, deal_b = get_deal_items()


def build_action_refill(where, what):
    text = "<action>\n"
    text += "<type>refill</type>\n"
    text += "<where>" + where + "</where>\n"
    text += "<what>" + base64.b64encode(what.encode('utf-8')).decode() + "</what>\n"
    text += "</action>\n"
    return text


def build_action_append(where, what):
    text = "<action>\n"
    text += "<type>append</type>\n"
    text += "<where>" + where + "</where>\n"
    text += "<what>" + base64.b64encode(what.encode('utf-8')).decode() + "</what>\n"
    text += "</action>\n"
    return text


def build_action_total(value):
    text = "<action>\n"
    text += "<type>total</type>\n"
    text += "<value>" + str(value) + "</value>\n"
    text += "</action>\n"
    return text


def build_action_reset():
    text = "<action>\n"
    text += "<type>reset</type>\n"
    text += "</action>\n"
    return text


# check if deals satisfy
def check_deals(item_id, deal_id_current):

    global total_amount
    global total_discount
    global end_flag
    global target_text
    global target_content

    if item_id in deal_a:
        # if deal exists
        while len(sandwich_panini_values) * len(snakes_values) * (len(cold_drinks_values) + len(hot_drinks_values)) > 0:
            # delete previous two records in transactions
            if len(hot_drinks_values) > 0:
                deal_a_dri = hot_drinks_values.pop()
            else:
                deal_a_dri = cold_drinks_values.pop()
            deal_a_san = sandwich_panini_values.pop()
            deal_a_sna = snakes_values.pop()

            # update item number -- if num > 2: pop and add again
            if deal_a_san[3] > 1:
                deal_a_san[3] -= 1
                sandwich_panini_values.append(deal_a_san)
            if deal_a_dri[3] > 1:
                deal_a_dri[3] -= 1
                cold_drinks_values.append(deal_a_dri)
            if deal_a_sna[3] > 1:
                deal_a_sna[3] -= 1
                snakes_values.append(deal_a_sna)

            # get discount_value
            discount = deal_a_sna[-1]
            total_discount += discount
            deal_id_current += 1


            others_values.append([-1, None, None, 1, None, discount / 100])
            deals_values.append([deal_id_current, 'Meal_Deal', deal_a_san[0]])
            deals_values.append([deal_id_current, 'Meal_Deal', deal_a_dri[0]])
            deals_values.append([deal_id_current, 'Meal_Deal', deal_a_sna[0]])

            # apply discount
            total_amount -= discount

            # update target_text
            target_text += "<div style = 'word-spacing:20px' >Meal_Deal applied -&pound;{}</div>".format(
                discount / 100) + '<br>'
            target_content += target_text

    # if deal_b
    elif item_id in deal_b:
        # if deal exists
        while len(hot_drinks_values) * len(cookie_shortbread_values) > 0:
            # delete previous two records in transactions
            deal_b_cookie = cookie_shortbread_values.pop()
            deal_b_hot_dri = hot_drinks_values.pop()

            # update item number -- if num > 2: pop and add again
            if deal_b_cookie[3] > 1:
                deal_b_cookie[3] -= 1
                cookie_shortbread_values.append(deal_b_cookie)
            if deal_b_hot_dri[3] > 1:
                deal_b_hot_dri[3] -= 1
                hot_drinks_values.append(deal_b_hot_dri)

            # get discount_value
            discount = deal_b_cookie[-1] * 0.5
            total_discount += discount
            deal_id_current += 1

            # insert new deal_a record in transactions and deals
            others_values.append([-2, None, None, 1, None, discount / 100])
            deals_values.append([deal_id_current, 'Cookie_Deal', deal_b_cookie[0]])
            deals_values.append([deal_id_current, 'Cookie_Deal', deal_b_hot_dri[0]])

            # apply discount
            total_amount -= discount

            # update target_text
            target_text += "<div style = 'word-spacing:20px' >Cookie_Deal applied -&pound;{}</div>".format(
                discount / 100) + '<br>'
            target_content += target_text


def server_response(params):
    action = params[0].split('=')[1]

    text = ''

    global total_amount
    global total_discount
    global end_flag
    global target_text
    global target_content

    global sandwich_panini_values
    global cold_drinks_values
    global snakes_values
    global hot_drinks_values
    global cookie_shortbread_values
    global others_values
    global trans_values

    global deals_values
    global pays_values
    global deal_id_current

    # transaction begins
    if action == 'status':
        print('it\'s start page!')
        # page = params[1].split('=')[1]

        # 1. start order
        if end_flag:

            # 1. total_amount -- used in backend then assigned to frontend
            total_amount = 0
            total_discount = 0
            # 2. target_text
            target_text = 'Welcome!'
            target_content = ''
            # 3. title_text unchanged and reset in the frontend when repsonse reset
            # 4. update sql values
            sandwich_panini_values = []
            cold_drinks_values = []
            snakes_values = []
            hot_drinks_values = []
            cookie_shortbread_values = []
            others_values = []
            trans_values = []

            deals_values = []
            pays_values = []

            # get deal_id_current before check deals
            with DataBase() as db:
                db.execute('SELECT max(deal_id) FROM deals;')
                data = db.fetchone()
                if data[0] is not None:
                    deal_id_current = data[0]
                else:
                    deal_id_current = 1000

            # 5. response_text
            text = '<?xml version="1.0" encoding="UTF-8"?>\n'
            text += "<response>\n"
            # 5.1 return current total value
            text += build_action_total(total_amount)
            # 5.2  assign value to 'target'
            text += build_action_append("target", target_text)
            # 5.3 last action in response -- reset -- reset target, title and setTotal
            text += build_action_reset()
            text += "</response>\n"

        # 2. continuing order -- switch between page 1 and page 2
        # do nothing!
        else:
            text = '<?xml version="1.0" encoding="UTF-8"?>\n'
            text += "<response>\n"
            # 5.1 return current total value
            text += build_action_total(total_amount)
            # 5.2  assign value to 'target'
            text += build_action_refill("target", target_content)
            # 5.3 last action in response -- reset -- reset target, title and setTotal
            text += "</response>\n"

    # reset transaction -- then just send reset response but nothing
    elif action == 'clr':
        print('it\'s clr page!')

        end_flag = True

        # 1. total_amount -- used in backend then assign to frontend
        total_amount = 0
        total_discount = 0
        # 2. target_text
        target_text = 'Welcome!'
        target_content = ''
        # 3. title_text unchanged and reset in the frontend when repsonse reset
        # 4. update sql values
        sandwich_panini_values = []
        cold_drinks_values = []
        snakes_values = []
        hot_drinks_values = []
        cookie_shortbread_values = []
        others_values = []
        trans_values = []

        deals_values = []
        pays_values = []

        # get deal_id_current before check deals
        with DataBase() as db:
            db.execute('SELECT max(deal_id) FROM deals;')
            data = db.fetchone()
            if data[0] is not None:
                deal_id_current = data[0]
            else:
                deal_id_current = 1000

        # 5. response_text
        text = '<?xml version="1.0" encoding="UTF-8"?>\n'
        text += "<response>\n"
        # 5.1 return current total value
        text += build_action_total(total_amount)
        # 5.2  assign value to 'target'
        text += build_action_refill("target", target_text)
        # 5.3 last action in response -- reset -- reset target, title and setTotal
        text += build_action_reset()
        text += "</response>\n"

    # add item
    elif action == 'plu':
        print('it\'s plu page!')

        end_flag = False

        # 1. get params
        refund = int(params[1].split('=')[1])
        item_num = int(params[2].split('=')[1])
        plu_code = str(params[3].split('=')[1])

        # get price from products table
        with DataBase() as db:
            db.execute('SELECT productid, name, shift, price FROM products WHERE plu = {};'.format(plu_code))

            data = db.fetchone()
            item_id = data[0]
            item_name = data[1]
            item_shift = data[2]
            price = data[3]

            # get shift name
            if item_shift in [1, 2, 3]:
                # print('item_shift:', item_shift)
                db.execute('SELECT name FROM shift WHERE shiftid = {};'.format(item_shift))
                shift_name = db.fetchone()[0]
            else:
                shift_name = ''

        # 2. add item to its group
        if item_id in deal_items[2]:
            sandwich_panini_values.append([item_id, None, None, item_num, plu_code, None])
        elif item_id in deal_items[0]:
            cold_drinks_values.append([item_id, None, None, item_num, plu_code, None])
        elif item_id in deal_items[3]:
            snakes_values.append([item_id, None, None, item_num, plu_code, None, price])
        elif item_id in deal_items[1]:
            hot_drinks_values.append([item_id, None, None, item_num, plu_code, None])
        elif item_id in deal_items[4]:
            cookie_shortbread_values.append([item_id, None, None, item_num, plu_code, None, price])
        else:
            others_values.append([item_id, None, None, item_num, plu_code, None])

        # 3. calculate total_amount and discount
        single_amount_sum = price * item_num
        total_amount += single_amount_sum

        # 4. update target_text
        target_text = "<div style = 'word-spacing:20px' > {} {} {}pcs &pound;{} &pound;{}</div>" \
                      .format(str(item_name), shift_name, str(item_num), str(price / 100), str(single_amount_sum / 100)) + '<br>'
        target_content += target_text

        # 5. check if deals satisfy
        check_deals(item_id, deal_id_current)

        # 6. response_text
        text = '<?xml version="1.0" encoding="UTF-8"?>\n'
        text += "<response>\n"
        # 6.1 return current total value
        text += build_action_total(total_amount)
        # 6.2  assign value to 'target'
        text += build_action_append("target", target_text)
        text += "</response>\n"

    elif action == 'program':
        print('it\'s program page!')

        end_flag = False

        # 1. get params
        refund = int(params[1].split('=')[1])
        item_num = int(params[2].split('=')[1])
        item_pos = int(params[3].split('=')[1])
        item_shift = int(params[4].split('=')[1])

        if params[5].split('=')[1] == '':
            ins_value = 'None'
        else:
            ins_value = int(params[5].split('=')[1])

        with DataBase() as db:
            # get price and shift name
            if item_shift in [1, 2, 3]:
                db.execute('SELECT productid, name, price FROM products WHERE pos = {} AND shift = {};'.format(item_pos, item_shift))
                data = db.fetchone()
                item_id = data[0]
                item_name = data[1]
                price = data[2]

                db.execute('SELECT name FROM shift WHERE shiftid = {};'.format(item_shift))
                shift_name = db.fetchone()[0]
            elif item_pos in range(1, 13):
                db.execute('SELECT productid, name, price FROM products WHERE pos = {};'.format(item_pos))
                data = db.fetchone()
                item_id = data[0]
                item_name = data[1]
                price = data[2]
                shift_name = 'small'
            else:
                db.execute('SELECT productid, name, price FROM products WHERE pos = {};'.format(item_pos))
                data = db.fetchone()
                item_id = data[0]
                item_name = data[1]
                price = data[2]
                shift_name = ''

        # 2. add item to its group
        if item_id in deal_items[2]:
            sandwich_panini_values.append([item_id, item_pos, item_shift, item_num, None, None])
        elif item_id in deal_items[0]:
            cold_drinks_values.append([item_id, item_pos, item_shift, item_num, None, None])
        elif item_id in deal_items[3]:
            snakes_values.append([item_id, item_pos, item_shift, item_num, None, None, price])
        elif item_id in deal_items[1]:
            hot_drinks_values.append([item_id, item_pos, item_shift, item_num, None, None])
        elif item_id in deal_items[4]:
            cookie_shortbread_values.append([item_id, item_pos, item_shift, item_num, None, None, price])
        else:
            others_values.append([item_id, item_pos, item_shift, item_num, None, None])

        # 3. calculate total_amount and discount
        single_amount_sum = price * item_num
        total_amount += single_amount_sum

        # 4. update target_text
        target_text = "<div style = 'word-spacing:20px' > {} {} {}pcs &pound;{} &pound;{}</div>" \
                      .format(str(item_name), shift_name, str(item_num), str(price / 100), str(single_amount_sum / 100)) + '<br>'
        target_content += target_text

        # 5. check if deals satisfy
        check_deals(item_id, deal_id_current)

        # 6. response_text
        text = '<?xml version="1.0" encoding="UTF-8"?>\n'
        text += "<response>\n"
        # 6.1 return current total value
        text += build_action_total(total_amount)
        # 6.2  assign value to 'target'
        text += build_action_append("target", target_text)
        text += "</response>\n"

    # get cash and close transaction
    elif action == 'cash':
        print('it\'s cash page!')

        end_flag = True

        # 1. get params
        refund = int(params[1].split('=')[1])
        payment = int(params[2].split('=')[1])
        cash = int(params[3].split('=')[1])

        # pay by cash
        if payment == 1:
            change = cash - total_amount / 100
        # pay by credit/credit card -- change = 0 and no refund
        else:
            change = 0

        # create values for pays
        pays_values.append([payment, total_amount / 100, refund, cash, round(change, 2), total_discount/100])

        # 2. concatenate transaction values
        trans = [sandwich_panini_values, cold_drinks_values, snakes_values, hot_drinks_values, cookie_shortbread_values, others_values]
        for i in trans:
            # delete price
            if i == snakes_values:
                for j in snakes_values:
                    p = j.pop()
                    print('pop price: ', p)
            elif i == cookie_shortbread_values:
                for j in cookie_shortbread_values:
                    p = j.pop()
                    print('pop price: ', p)

            trans_values += i

        # 3. update database
        # get payment name and current transaction_id
        with DataBase() as db:
            db.execute('SELECT name FROM payment_method WHERE methodid = {};'.format(payment))
            data = db.fetchone()
            payment_method = data[0]

            # get old transaction_id and transaction_id ++
            db.execute('SELECT MAX(transaction_id) FROM transactions;')
            data = db.fetchone()

            if data[0] is not None:
                old_transaction_id = data[0]
                new_transaction_id = old_transaction_id + 1
            else:
                new_transaction_id = 1

            # 3. execute sqls
            # transactions table
            print('execute sqls ********************************************************')
            sql_trans = 'INSERT INTO transactions(transaction_id, product_id, pos, shift, num, plu, discount) ' \
                        'VALUES(%s, %s, %s, %s, %s, %s, %s)'
            sql_deals = 'INSERT INTO deals(transaction_id, deal_id, deal_name, product_id) ' \
                        'VALUES(%s, %s, %s, %s)'
            sql_pays = 'INSERT INTO pays(transaction_id, payment, total_amount, refund, cash, change_amount, total_discount) ' \
                        'VALUES(%s, %s, %s, %s, %s, %s, %s)'

            if trans_values:
                for i in trans_values:
                    print('trans values are: ', [new_transaction_id] + i)
                    db.execute(sql_trans, [new_transaction_id] + i)

            # deals table
            if deals_values:
                for i in deals_values:
                    print('deals values are: ', [new_transaction_id] + i)
                    db.execute(sql_deals, [new_transaction_id] + i)

            # pays table
            if pays_values:
                for i in pays_values:
                    print('pays values are: ', [new_transaction_id] + i)
                    db.execute(sql_pays, [new_transaction_id] + i)

            print('sqling successful!***************************************')

        # 4. target_text
        target_text = '<div style = \'word-spacing:20px\' > Pay by: {} </div>'.format(str(payment_method)) + '<br>' + \
                      '<div style = \'word-spacing:20px\' > Pay value: &pound;{} </div>'.format(str(cash))
        # 5. title_text
        title_text = 'Change &pound;{:.2f}'.format(change)

        # 6. response_text
        text = '<?xml version="1.0" encoding="UTF-8"?>\n'
        text += "<response>\n"
        # 4.1 return current total value
        text += build_action_total(total_amount)
        # 4.2  assign value to 'target'
        text += build_action_append("target", target_text)
        # 4.3 assign value to 'title'
        text += build_action_refill("title", title_text)
        # 4.4 last action in response -- reset
        text += build_action_reset()
        text += "</response>\n"

    return text
