"""
Bot - Latest version
"""


# this function checks for a neutral iceberg if the enemy has enough penguins to conquer it from us after we conquer it.
def safe_neutral(game, iceberg, my_iceberg):
    turns = distance_between_iceberges(game, my_iceberg, iceberg)
    penguins_per_turn = 0
    if iceberg != game.get_bonus_iceberg():
        penguins_per_turn = iceberg.penguins_per_turn
    enemies = sorted(game.get_enemy_icebergs(), key=lambda x: x.penguin_amount * (-1))
    for enemy in enemies:
        enemy_amount = enemy.penguin_amount + turns * enemy.penguins_per_turn  # * penguins_per_turn
        if enemy_amount >= enemy.get_turns_till_arrival(iceberg) * penguins_per_turn:
            if iceberg == game.get_bonus_iceberg() or enemy_can_conquer(game, iceberg, enemy, my_iceberg):
                return False, enemy_amount - distance_between_iceberges(game, enemy, iceberg) * penguins_per_turn
    if distance_from_myself(game, iceberg) > distance_from_enemy(game, iceberg):
        return False, 20
    return True, 10


# check if the enemy can conquer the iceberg after I will conquer it.
def enemy_can_conquer(game, iceberg, enemy, source):
    turns = distance_between_iceberges(game, source, iceberg)
    my_icebergs = sorted(game.get_my_icebergs(), key=lambda x: x.get_turns_till_arrival(iceberg))
    for i in range(turns):
        flag1 = True
        arrival = i + distance_between_iceberges(game, enemy, iceberg)
        if arrival > turns:
            continue
        else:
            enemy_amount = enemy.penguin_amount + i * enemy.level
            iceberg_amount = (arrival - turns) * iceberg.penguins_per_turn + 1
            if enemy_amount >= iceberg_amount:
                return True
    return False


# for sorting the groups by arrival in case that two or more of the groups arrive together.
def sort_by_arrival(game, iceberg):
    if iceberg.owner == game.get_enemy():
        return group_turns(game, iceberg) * 10 + 1
    return group_turns(game, iceberg) * 10


def next_group_while_the_iceberg_is_neutral(game, group, counter, level, x):
    neutral_ice = True
    if group.penguin_amount > abs(counter):  # If the glacier that was neutral, became myself:
        neutral_ice = False
    counter += group.penguin_amount
    if group.owner == game.get_enemy():
        counter *= (-1)
    return counter, neutral_ice


def next_group_while_the_iceberg_is_not_neutral(game, group, counter, level, x, last):
    if group.owner == game.get_myself():
        counter += group.penguin_amount + (group_turns(game, group) - last) * level * x
    else:
        counter += (group_turns(game, group) - last) * level * x - group.penguin_amount
    return counter


# The function checks what the amount of penguins in the iceberg will be after all the groups reach it. It returns whether the iceberg neutral, the amount of penguins and the time the last group arrived
def iceberg_future_params(game, curent_iceberg, initial_amount_of_penguin, level, distance):
    last = 0  # the time the last group arrived
    neutral_ice = False
    if curent_iceberg.owner == game.get_neutral():  # if the iceberg is neutral
        neutral_ice = True
    all_groups = filter(lambda x: x.destination == curent_iceberg, game.get_all_penguin_groups())
    counter = initial_amount_of_penguin
    all_penguin_groups = sorted(all_groups, key=lambda x: sort_by_arrival(game, x))
    for group in all_penguin_groups:
        if distance >= 0 and group_turns(game, group) > distance and counter < 0 and not neutral_ice:
            if last != 0:
                return True, last, counter
        x = 0
        if counter > 0:
            x = 1
        elif counter < 0:
            x = -1
        if neutral_ice:  # if the iceberg is still neutral
            counter, neutral_ice = next_group_while_the_iceberg_is_neutral(game, group, counter, level, x)
        else:  # if the iceberg is not neutral
            counter = next_group_while_the_iceberg_is_not_neutral(game, group, counter, level, x, last)
        last = group_turns(game, group)
    if counter == 0:
        neutral_ice == True
    return neutral_ice, last, counter


def iceberg_condition_at_the_time_of_my_arrival(game, curent_iceberg, initial_amount_of_penguin, level, distance):
    return iceberg_future_params(game, curent_iceberg, initial_amount_of_penguin, level, distance)


def sort_by_arrival_bridge(game, iceberg, source, destination):
    if iceberg.owner == game.get_enemy():
        return group_turns_new_bridge(game, iceberg, source, destination) * 10 + 1
    return group_turns_new_bridge(game, iceberg, source, destination) * 10


def iceberg_future_bridge_version(game, curent_iceberg, initial_amount_of_penguin, level, source):
    last = 0  # the time the last group arrived
    x = 0  # the iceberg owner
    neutral_ice = False
    if curent_iceberg.owner == game.get_neutral():  # if the iceberg is neutral
        neutral_ice = True
    all_groups = filter(lambda x: x.destination == curent_iceberg, game.get_all_penguin_groups())
    counter = initial_amount_of_penguin
    all_penguin_groups = sorted(all_groups, key=lambda x: sort_by_arrival_bridge(game, x, source, curent_iceberg))
    for group in all_penguin_groups:
        x = 0
        if counter > 0:
            x = 1
        elif counter < 0:
            x = -1
        if neutral_ice:  # if the iceberg is still neutral
            counter, neutral_ice = next_group_while_the_iceberg_is_neutral(game, group, counter, level, x)
        else:  # if the iceberg is not neutral
            if group in game.get_my_penguin_groups():
                counter += group.penguin_amount + (
                            group_turns_new_bridge(game, group, source, curent_iceberg) - last) * level * x
            else:
                counter += (group_turns_new_bridge(game, group, source,
                                                   curent_iceberg) - last) * level * x - group.penguin_amount
        last = group_turns_new_bridge(game, group, source, curent_iceberg)
    if counter == 0:
        neutral_ice == True
    return neutral_ice, last, counter


# return for every iceberg the amount of penguins in the iceberg will be after all the groups reach it  , using the function  iceberg_future_params
def iceberg_future(game, iceberg):
    if iceberg == game.get_bonus_iceberg():
        if iceberg.owner == game.get_myself():
            return iceberg_future_params(game, iceberg, iceberg.penguin_amount, 0, -1)
        else:
            return iceberg_future_params(game, iceberg, iceberg.penguin_amount * (-1), 0, -1)
    if iceberg.owner == game.get_enemy():
        return iceberg_future_params(game, iceberg, iceberg.penguin_amount * (-1), iceberg.penguins_per_turn, -1)
    if iceberg.owner == game.get_myself():
        return iceberg_future_params(game, iceberg, iceberg.penguin_amount, iceberg.penguins_per_turn, -1)
    if iceberg.owner == game.get_neutral():
        return iceberg_future_params(game, iceberg, iceberg.penguin_amount * (-1), iceberg.penguins_per_turn, -1)


def iceberg_future_bridge(game, source, destination):
    if destination == game.get_bonus_iceberg():
        if iceberg.owner == game.get_myself():
            return iceberg_future_bridge_version(game, destination, destination.penguin_amount, 0, source)
        else:
            return iceberg_future_bridge_version(game, destination, destination.penguin_amount * (-1), 0, source)
    if destination.owner == game.get_enemy():
        return iceberg_future_bridge_version(game, destination, destination.penguin_amount * (-1),
                                             destination.penguins_per_turn, source)
    if destination.owner == game.get_myself():
        return iceberg_future_bridge_version(game, destination, destination.penguin_amount,
                                             destination.penguins_per_turn, source)
    if destination.owner == game.get_neutral():
        return iceberg_future_bridge_version(game, destination, destination.penguin_amount * (-1),
                                             destination.penguins_per_turn, source)


def safe_to_upgrade(game, my_iceberg):
    if my_iceberg.penguin_amount < my_iceberg.upgrade_cost:
        return False
    if iceberg_future_params(game, my_iceberg, (my_iceberg.penguin_amount - my_iceberg.upgrade_cost),
                             my_iceberg.penguins_per_turn + 1, -1)[2] < 0:
        return False
    enemy_icebergs = game.get_enemy_icebergs()
    for enemy_iceberg in enemy_icebergs:
        if enemy_iceberg.penguin_amount > (
                my_iceberg.penguin_amount - my_iceberg.upgrade_cost) + distance_between_iceberges(game, enemy_iceberg,
                                                                                                  my_iceberg) * (
                my_iceberg.penguins_per_turn + 1):
            return False
    return True


def safe_to_send(game, my_iceberg, penguin_amount, destination):
    number = \
    iceberg_future_params(game, my_iceberg, my_iceberg.penguin_amount - (penguin_amount), my_iceberg.penguins_per_turn,
                          -1)[2]
    if number < 0:
        return False
    enemy_icebergs = game.get_enemy_icebergs()
    for enemy_iceberg in enemy_icebergs:
        if enemy_iceberg.penguin_amount > (my_iceberg.penguin_amount - penguin_amount) + distance_between_iceberges(
                game, enemy_iceberg, my_iceberg) * (my_iceberg.penguins_per_turn):
            my_icebergs = game.get_my_icebergs()
            my_icebergs.remove(my_iceberg)
            flag = True
            for my_ice in my_icebergs:
                if my_ice.get_turns_till_arrival(my_iceberg) < enemy_iceberg.get_turns_till_arrival(
                        my_iceberg) or my_ice.penguin_amount > enemy_iceberg.penguin_amount:
                    flag = False
            if flag:
                return False
    return True


# the average distance from enemy icebergs
def distance_from_enemy(game, iceberg):
    counter = 0
    for ice in game.get_enemy_icebergs():
        counter += ice.get_turns_till_arrival(iceberg) / ice.penguins_per_turn
    return float(counter + 1) / len(game.get_enemy_icebergs())


# the average distance from enemy icebergs
def distance_from_myself(game, iceberg):
    counter = 0
    for ice in game.get_my_icebergs():
        counter += ice.get_turns_till_arrival(iceberg) / (ice.penguins_per_turn)
    return float(counter + 1) / len(game.get_my_icebergs())


# Returns the amount of penguins needed to conquer an iceberg by a particular iceberg
def penguins_required_real(game, iceberg, my_iceberg):
    distance = distance_between_iceberges(game, my_iceberg, iceberg)
    return penguins_cost(game, iceberg, my_iceberg)


# Returns the amount of penguins needed to conquer an iceberg from a particular distance
def penguins_cost(game, iceberg, my_iceberg):
    penguins = 1000
    distance = distance_between_iceberges(game, my_iceberg, iceberg)
    is_neutral, last, penguin_amount = iceberg_future(game, iceberg)
    if iceberg == game.get_bonus_iceberg():
        if is_neutral:
            if distance > last:
                if safe_neutral(game, iceberg, my_iceberg)[0] or penguin_amount == 0:
                    return abs(penguin_amount)
                else:
                    return abs(penguin_amount) + safe_neutral(game, iceberg, my_iceberg)[1]
            else:
                return 1000
        elif distance > last:
            return abs(penguin_amount)
        else:
            return 1000
    if iceberg.owner == game.get_neutral():
        if is_neutral:
            if distance > last:
                if safe_neutral(game, iceberg, my_iceberg)[0] or penguin_amount == 0:
                    return abs(penguin_amount)
                else:
                    return abs(penguin_amount) + iceberg.penguins_per_turn * (distance) + \
                           safe_neutral(game, iceberg, my_iceberg)[1]
            return 1000
        s = filter(lambda x: x.destination == iceberg, game.get_all_penguin_groups())
        f = sorted(s, key=lambda x: group_turns(game, x))
        if f and f[0].owner == game.get_myself():
            return abs(penguin_amount)
            i, t, c = iceberg_condition_at_the_time_of_my_arrival(game, iceberg, iceberg.penguin_amount * (-1),
                                                                  iceberg.penguins_per_turn, distance)
            if i and c == 0:
                return 1
            if i and distance > t:
                return abs(c) + (distance - t) * iceberg.penguins_per_turn
            elif i:
                return abs(c)
        elif distance > last:  # or distance>first_not_neutral:# and iceberg.owner!=game.get_myself():
            return abs(penguin_amount) + iceberg.penguins_per_turn * (distance - last)
        else:
            return 1000
    elif iceberg.owner == game.get_myself():
        i, t, c = iceberg_condition_at_the_time_of_my_arrival(game, iceberg, iceberg.penguin_amount,
                                                              iceberg.penguins_per_turn, distance)
        if i and c == 0:
            penguins = 1
        if i and distance > t:
            penguins = abs(c) + (distance - t) * iceberg.penguins_per_turn
        elif i:
            penguins = abs(c)
    if distance > last:
        penguins1 = abs(penguin_amount) + iceberg.penguins_per_turn * (distance + 1 - last)
        if penguins1 < penguins:
            return penguins1
        return penguins
    else:
        penguins1 = abs(penguin_amount)
        if penguins1 < penguins:
            return penguins1
        return penguins


def iceberg_value(game, iceberg):
    distance1 = distance_from_enemy(game, iceberg)
    distance2 = distance_from_myself(game, iceberg)
    s = filter(lambda x: x.destination == iceberg, game.get_all_penguin_groups())
    f = sorted(s, key=lambda x: group_turns(game, x))
    if iceberg == game.get_bonus_iceberg():
        return float(distance2) / (float(distance1 * len(
            game.get_my_icebergs()) * game.bonus_iceberg_penguin_bonus) / game.bonus_iceberg_max_turns_to_bonus)
    elif iceberg_future(game, iceberg)[2] > 0:
        return upgrade_value(game, iceberg)
    elif iceberg.owner == game.get_myself() or (f and f[0].owner == game.get_myself()):
        level = iceberg.penguins_per_turn
        return float(0.001 * distance2) / ((distance1 * level))
    else:
        level = iceberg.penguins_per_turn
        return float(distance2) / ((distance1 * level))


def upgrade_value(game, iceberg):
    distance1 = distance_from_enemy(game, iceberg)
    distance2 = 1  # distance_from_myself(game, iceberg)
    return float(0.01 * distance2) / (distance1)


def distance_between_iceberges(game, source, destination):
    bridge_duration = 0
    for bridge in source.bridges:
        if destination in bridge.get_edges():
            bridge_duration = bridge.duration
            break
    if bridge_duration == 0:
        return source.get_turns_till_arrival(destination)
    distance = source.get_turns_till_arrival(destination)
    if distance / game.iceberg_bridge_speed_multiplier > bridge_duration:
        distance = (
                               distance / game.iceberg_bridge_speed_multiplier - bridge_duration) * game.iceberg_bridge_speed_multiplier + bridge_duration
    else:
        distance = distance / game.iceberg_bridge_speed_multiplier
    return int(distance)  # source.get_turns_till_arrival(destination)# distance


def group_turns(game, group):
    bridge_duration = 0
    destination = group.destination
    source = group.source
    real_distance = source.get_turns_till_arrival(destination)
    for bridge in source.bridges:
        if destination in bridge.get_edges():
            bridge_duration = bridge.duration
            break
    if bridge_duration == 0:
        return group.turns_till_arrival
    distance = group.turns_till_arrival
    if distance > bridge_duration:
        if real_distance % 2 == 0:
            distance = (distance - bridge_duration) * game.iceberg_bridge_speed_multiplier + bridge_duration
        else:
            distance = ((distance - bridge_duration) * game.iceberg_bridge_speed_multiplier - 1) + bridge_duration
    else:
        distance = distance
    return int(distance)  # group.turns_till_arrival## distance


def group_turns_new_bridge(game, group, source, destination):
    if group.destination != destination or group.source != source:
        return group_turns(game, group)
    bridge_duration = game.iceberg_max_bridge_duration
    distance = group.turns_till_arrival
    if distance / game.iceberg_bridge_speed_multiplier > bridge_duration:
        distance = (distance / 2 - bridge_duration) * 2 + bridge_duration  # /game.iceberg_bridge_speed_multiplier
    else:
        distance = distance / game.iceberg_bridge_speed_multiplier
    return int(distance) + 1  # group.turns_till_arrival## distance+1


def bridge_value(game, source, destination):
    # checks if the bridg is already exist
    for bridge in source.bridges:
        if destination in bridge.get_edges():
            return -1
    bridg_cost = game.iceberg_bridge_cost
    if source.penguin_amount < bridg_cost or not source.can_create_bridge(destination) or not safe_to_send(game, source,
                                                                                                           bridg_cost,
                                                                                                           destination):
        return -1
    is_neutral, last_group_bridge, value_with_bridge = iceberg_future_bridge(game, source, destination)
    if value_with_bridge < 0:
        return -1
    is_neutral, last_group_not_bridge, value_without_bridge = iceberg_future(game, destination)
    a = value_with_bridge - value_without_bridge
    if last_group_bridge < last_group_not_bridge:
        if destination != game.get_bonus_iceberg():
            if value_without_bridge < 0 and not is_neutral:
                a = value_with_bridge - value_without_bridge + (
                            last_group_not_bridge - last_group_bridge) * destination.level * 2
            else:
                a = value_with_bridge - value_without_bridge + (
                            last_group_not_bridge - last_group_bridge) * destination.level
        else:
            a = value_with_bridge - value_without_bridge + (last_group_not_bridge - last_group_bridge) * (len(
                game.get_my_icebergs()) * game.bonus_iceberg_penguin_bonus) / game.bonus_iceberg_max_turns_to_bonus
    if value_without_bridge < 0 and a < 0 and not is_neutral:
        return 0
    return a - bridg_cost


def p_bridge(game, source, destination):
    turns = source.get_turns_till_arrival(destination)
    a = penguins_cost(game, destination, (turns - 1) / 2 + 1) + 4
    if a < source.penguin_amount and safe_to_send(game, source, a, destination):
        return a - 4
    b = penguins_cost(game, destination, turns)
    return b


def max_penguins_to_send(game, iceberg):
    penguin_amount = iceberg.penguin_amount
    while penguin_amount != 0:
        if safe_to_send(game, iceberg, penguin_amount, iceberg):
            break
        penguin_amount -= 5
    i = 4
    while i != 0:
        if safe_to_send(game, iceberg, penguin_amount + i, iceberg):
            return penguin_amount + i
        i -= 1
    return penguin_amount


def do_turn(game):
    j = game.get_my_icebergs()[0]
    print(game.get_time_remaining())
    is_helping = []  # All the icebergs that performed any action in this turn
    is_ok_list = []
    need_upgrade = []
    list1 = []
    can_help = []  # list of icebergs and and the max penguin_amount they can send
    for iceberg in game.get_my_icebergs():
        if iceberg_future(game, iceberg)[2] > 0:
            can_help.append((iceberg, max_penguins_to_send(game, iceberg)))
    print(can_help)
    my_iceberg_for_bridge = filter(
        lambda x: iceberg_future(game, x)[2] >= 0 and safe_to_send(game, x, game.iceberg_bridge_cost, x),
        game.get_my_icebergs())
    # filter all iceberg that need help or need to upgrade
    icebergs = filter(lambda x: iceberg_future(game, x)[2] <= 0 or (x.owner == game.get_myself() and x.level < 4),
                      game.get_all_icebergs())
    for my_iceberg in my_iceberg_for_bridge:
        destinations = sorted(game.get_all_icebergs(), key=lambda x: bridge_value(game, my_iceberg, x) * (-1))
        if int(bridge_value(game, my_iceberg, destinations[0])) >= 0:
            my_iceberg.create_bridge(destinations[0])
            is_helping.append(my_iceberg)
            continue
    if game.get_bonus_iceberg() and iceberg_future(game, game.get_bonus_iceberg())[
        2] <= 0:  # if bonus iceberg is not going to be mine.
        icebergs.append(game.get_bonus_iceberg())  # insert bonus iceberg to the  list of the icebergs that need help
    sorted_all_icebergs = sorted(icebergs, key=lambda x: iceberg_value(game, x))
    # Go over all  icebergs that need help or upgrade.
    for iceberg in sorted_all_icebergs:
        if iceberg in is_helping:  # if my_iceberg has already done some action- skip
            is_ok_list.append(iceberg)
            continue
        # sort my iceberg by distance to current iceberg that need help
        my_icebergs = sorted(can_help, key=lambda x: x[0].get_turns_till_arrival(iceberg))
        if iceberg_future(game, iceberg)[2] > 0:  # if the iceber is not in risk
            is_ok_list.append(iceberg)
            need_upgrade.append(iceberg)
            if iceberg.owner == game.get_myself():  # the iceberg is mine and need to upgrade
                if iceberg not in is_helping:  # and iceberg not in is_help:
                    if iceberg in my_icebergs:
                        my_icebergs.remove(iceberg)
                    if iceberg.can_upgrade() and safe_to_upgrade(game, iceberg):
                        iceberg.upgrade()
                        is_helping.append(iceberg)
                        need_upgrade.remove(iceberg)
                    continue
                else:
                    continue
            else:
                continue
        # go over all my_icebergs that can help to current iceberg
        if iceberg.owner == game.get_myself():
            list1.append(iceberg)
        for my_iceberg in my_icebergs:
            if my_iceberg[
                0] in is_helping:  # or my_iceberg in is_helping:# if my_iceberg has already done some action- skip
                continue
            destination_penguin_amount = penguins_required_real(game, iceberg, my_iceberg[
                0])  # p_bridge(game, my_iceberg, iceberg)#penguins_required_real(game, iceberg, my_iceberg)
            if iceberg.owner == game.get_neutral() and len(
                    list1) > 0:  # and distance_from_myself(game, iceberg)>distance_from_enemy(game, iceberg):#risk_icebergs and iceberg.owner==game.get_enemy():# and len(game.get_my_icebergs())<=len(game.get_enemy_icebergs()):
                destination_penguin_amount += 100  # =int(destination_penguin_amount*1.1)
            if my_iceberg[1] > destination_penguin_amount:
                if (my_iceberg[0].get_turns_till_arrival(
                        iceberg)) / 2 + 1 <= 300 - game.turn:  # or iceberg_value(game,my_iceberg)>iceberg_value(game, iceberg):
                    print
                    my_iceberg[0], "sends", (destination_penguin_amount + 1), "penguins to", iceberg
                    my_iceberg[0].send_penguins(iceberg, destination_penguin_amount + 1)
                    is_ok_list.append(iceberg)
                    is_helping.append(my_iceberg[0])
                    if iceberg.owner == game.get_myself():
                        list1.remove(iceberg)
                    break
    list1 = []
    list2 = []
    for iceberg in sorted_all_icebergs:
        is_help = []
        if iceberg in need_upgrade:
            list1.append(iceberg)
        if iceberg in is_ok_list:  # or iceberg.owner==game.get_neutral():
            continue
        elif iceberg.owner != game.get_enemy():
            list1.append(iceberg)
        if iceberg.owner == game.get_myself():
            list2.append(iceberg)
        my_icebergs = sorted(can_help, key=lambda x: distance_between_iceberges(game, x[0], iceberg))
        percent = 0.0
        for my_iceberg in my_icebergs:
            if my_iceberg[0] in is_helping:
                continue
            if my_iceberg[
                0] in is_helping:  # or my_iceberg in is_helping:# if my_iceberg has already done some action- skip
                continue
            destination_penguin_amount = penguins_required_real(game, iceberg, my_iceberg[0])
            if destination_penguin_amount >= 1000:
                continue
            if iceberg.owner == game.get_enemy() and len(list1) > 0 and distance_from_myself(game,
                                                                                             iceberg) > distance_from_enemy(
                    game, iceberg):
                destination_penguin_amount += 100  # =int(destination_penguin_amount*1.1)
            if iceberg.owner != game.get_myself() and len(list2) > 0:
                continue
            if destination_penguin_amount <= 0:
                continue
            elif ((1 - percent) * destination_penguin_amount) + 1 <= my_iceberg[1]:
                is_help.append([my_iceberg[0], (1 - percent) * (destination_penguin_amount + 1)])
                percent = 1
            else:
                is_help.append([my_iceberg[0], my_iceberg[1]])
                percent += float(my_iceberg[1]) / (destination_penguin_amount + 1)
            if percent >= 1:
                for ice in is_help:
                    ice[0].send_penguins(iceberg, int(ice[1]))
                    print
                    ice[0], "sends2", int(ice[1]), "penguins to", iceberg
                    is_helping.append(ice[0])
                is_ok_list.append(iceberg)
                if iceberg.owner != game.get_enemy():
                    list1.remove(iceberg)
                if iceberg.owner == game.get_myself():
                    list2.remove(iceberg)
                break
