from flask import Blueprint
# from flask.ext.security import current_user
from util import *
from modules.api import placeholderdata
from helpers import generate_port, AdmiralHelper

api_user = Blueprint('api_user', __name__)
prepare_api_blueprint(api_user)


@api_user.route('/api_req_member/get_incentive', methods=['GET', 'POST'])
def get_incentive():
    return svdata({
        'api_count': 0
    })  # What?


@api_user.route('/api_req_hensei/change', methods=['GET', 'POST'])
def change_position():
    # TODO UNFUCK THIS CODE UP
    admiral = get_token_admiral_or_error()
    ships = admiral.admiral_ships.all()

    # Get request parameters
    fleet_id = int(request.values.get("api_id")) - 1
    ship_id = int(request.values.get("api_ship_id")) - 1
    ship_pos = int(request.values.get("api_ship_idx"))
    fleet = admiral.fleets.all()[fleet_id]
    fships = fleet.ships.all()

    nlist = [ship for ship in fships]
    nlist = sorted(nlist, key=lambda x: x.local_fleet_id)

    if ship_id == -2:
        # Delete ship.
        oldship = fships[ship_pos]
        shipid = oldship.local_fleet_id
        fships.remove(oldship)
        # Get the rest of the ships, and bump it down.
        for n, ship in enumerate(fships):
            ship.local_fleet_id -= 1
            fships[n] = ship
        fleet.ships = fships

    elif len(fships)-1 < ship_pos:
        ships[ship_id].local_fleet_id = ship_pos
        fships.append(ships[ship_id])
        fleet.ships = fships
    else:
        oldship = fships[ship_pos]
        # Get original ship ID
        original_id = 0
        for n, ship in enumerate(fships):
            if ship == oldship:
                original_id = n
                break

        # Generate a brand new fleet.
        nfleet = db.Fleet()
        for n, ship in enumerate(fships):
            if ship.id not in [original_id, ship_id]:
                ship.local_fleet_id = n
                nfleet.ships.append(ship)
            elif ship.id == original_id:
                ship.local_fleet_id = ship_id
                nfleet.ships.append(ship)
            elif ship.id == ship_id:
                ship.local_fleet_id = original_id
                nfleet.ships.append(ship)
        nfleet.id = fleet.id
        fleet = nfleet

    db.db.session.merge(fleet)
    db.db.session.commit()
    return svdata({})

@api_user.route('/api_get_member/basic', methods=['GET', 'POST'])
def basic():
    return svdata(AdmiralHelper.get_admiral_basic_info())


@api_user.route('/api_get_member/furniture', methods=['GET', 'POST'])
def furniture():
    # TODO: Implement this properly
    admiral = get_token_admiral_or_error()
    return svdata([{
        'api_member_id': admiral.id,
        'api_id': item.id,
        'api_furniture_type': item.type,
        'api_furniture_no': item.no,
        'api_furniture_id': item.id
    } for item in []])


@api_user.route('/api_get_member/slot_item', methods=['GET', 'POST'])
def slot_item():
    # TODO: Implement this properly
    admiral = get_token_admiral_or_error()
    return svdata([{'api_id': item.id, 'api_slotitem_id': item.itemid, 'api_locked': 0} for item in []])


@api_user.route('/api_get_member/useitem', methods=['GET', 'POST'])
def useitem():
    # TODO: Implement this properly
    admiral = get_token_admiral_or_error()
    return svdata([{
        'api_member_id': admiral.id,
        'api_id': item.id,
        'api_value': item.count,
        'api_usetype': item.type,
        'api_category': item.category,
        'api_name': item.name,  # WHY
        'api_description': ["", ""],
        'api_price': 0,
        'api_count': item.count
    } for item in []])



@api_user.route('/api_get_member/kdock', methods=['GET', 'POST'])
def kdock():
    # TODO: Implement this properly
    admiral = get_token_admiral_or_error()
    return svdata([{
        'api_member_id': admiral.id,
        'api_id': dock.id,
        'api_state': dock.state,
        'api_created_ship_id': dock.ship,
        'api_complete_time': dock.complete,  # TODO: Convert this to JST
        'api_complete_time_str': dock.complete.strftime('%Y-%M-%d %H:%M:%S'),
        'api_item1': dock.fuel,
        'api_item2': dock.ammo,
        'api_item3': dock.steel,
        'api_item4': dock.baux,
        'api_item5': dock.cmats
    } for dock in []])


@api_user.route('/api_get_member/unsetslot', methods=['GET', 'POST'])
def unsetslot():
    # TODO: Figure out what the hell this even is!
    return svdata(placeholderdata.unsetslot)


@api_user.route('/api_port/port', methods=['GET', 'POST'])
def port():
    api_token = request.values.get('api_token', None)
    if api_token is None:
        abort(403)
    port = generate_port.generate_port(api_token)['api_data']
    return svdata(port)


@api_user.route('/api_req_init/firstship', methods=['GET', 'POST'])
# Kancolle literally doesn't care, as long as it gets something back
def firstship():
    admiral = get_token_admiral_or_error()
    if admiral.setup:
        return svdata({'api_result_msg': "Nice try.", 'api_result': 200})
    shipid = request.values.get("api_ship_id")
    new_admiral = AdmiralHelper.setup(shipid, admiral)
    db.db.session.add(new_admiral)
    db.db.session.commit()
    return svdata({'api_result_msg': 'shitty api is shitty', 'api_result': 1})


@api_user.route('/api_get_member/ship2', methods=['GET', 'POST'])
def ship2():
    return json.dumps({})

# Generic routes for anything not implemented.

@api_user.route('/api_req_init/<path:path>', methods=['GET', 'POST'])
def misc(path):
    return svdata({'api_result_msg': '申し訳ありませんがブラウザを再起動し再ログインしてください。', 'api_result': 201})


@api_user.route('/api_get_member/<path:path>', methods=['GET', 'POST'])
def misc2(path):
    return svdata({'api_result_msg': '申し訳ありませんがブラウザを再起動し再ログインしてください。', 'api_result': 201})
