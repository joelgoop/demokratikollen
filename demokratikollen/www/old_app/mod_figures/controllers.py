# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  json

from demokratikollen.www.app import db, PartyVote, PolledPoint, Party, Member, ChamberAppointment
from demokratikollen.www.app.helpers.cache import cache

from demokratikollen.core.utils.mongodb import MongoDBDatastore

from sqlalchemy import func

import datetime as dt
import calendar

mod_figures = Blueprint('figures', __name__, url_prefix='/figures')

########
# Routes

@mod_figures.route('/party_bias/<partyA_abbr>_vs_<partyB_abbr>.<string:format>')
def party_bias(partyA_abbr, partyB_abbr, format):
    if format == 'html':
        return "Not implemented"
    if format == 'json':
        #@cache.memoize()
        def get_data():
            s=db.session
            A_id = s.query(Party.id).filter(Party.abbr==partyA_abbr).one()[0]
            B_id = s.query(Party.id).filter(Party.abbr==partyB_abbr).one()[0]

            mdb = MongoDBDatastore()
            mongodb = mdb.get_mongodb_database() 
            mongo_collection = mongodb.party_covoting

            record= mongo_collection.find_one({"partyA": A_id, "partyB": B_id})
            del record['_id']
            return record

    data = get_data()
    return json.jsonify(data)




@mod_figures.route('/voteringsfrekvens.<string:format>')
def voteringsfrekvens(format):
    if format == 'html':
        return render_template('/figures/voteringsfrekvens.html')
    if format == 'json':
        @cache.memoize()
        def generate_data(time_format):
            if time_format == 'dow':
                # get polls grouped on day of week
                poll_agg = db.session.query(func.date_part('dow', PolledPoint.poll_date), func.count(PolledPoint.id)) \
                    .group_by(func.date_part('dow', PolledPoint.poll_date))  \
                    .order_by(func.date_part('dow', PolledPoint.poll_date))

                weekdays = ['Söndag', 'Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag']

                data = []
                for poll in poll_agg:
                    data.append(dict(label=weekdays[int(poll[0])], value=poll[1]))
                return data

            if time_format == 'month':
                poll_agg = db.session.query(func.date_part('month', PolledPoint.poll_date), func.count(PolledPoint.id)) \
                    .group_by(func.date_part('month', PolledPoint.poll_date))  \
                    .order_by(func.date_part('month', PolledPoint.poll_date))

                months = ['Jan.', 'Feb.', 'Mars', 'Apr.', 'Maj', 'Juni', 'Juli', 'Aug.', 'Sep.', 'Okt.', 'Nov.', 'Dec.']
                data = []
                for poll in poll_agg:
                    data.append(dict(label=months[int(poll[0])-1], value=poll[1]))
                return data

        if 'time' in request.args:
            time_format = request.args['time']
        else:
            time_format = 'dow'

        data = generate_data(time_format)
        
        return json.jsonify(key='voteringsfrekvens', values=data)
    else:
        return render_template('404.html'), 404

@mod_figures.route('/partipiskan', methods=['GET'])
@cache.cached()
def partipiskan():

    s = db.session

    parties = s.query(Party).join(Member).join(ChamberAppointment) \
                .filter(ChamberAppointment.start_date > dt.date(2002,9,1)).distinct().all()

    data = dict(key="% Polls with party split", values=list())

    for party in parties:
        q = s.query(PartyVote, PolledPoint).join(PolledPoint).join(Party) \
            .filter(Party.id==party.id)\
            .order_by(PolledPoint.poll_date.asc())

        num_polls = 0
        num_piska = 0
        num_defectors = list()
        for (pv, poll) in q:
            counts = [pv.num_yes, pv.num_no, pv.num_abstain]
            winner = max(counts)
            total = sum(counts)
            grand_total = total + pv.num_absent
            num_polls += 1
            if winner != total: 
                num_piska += 1
                num_defectors.append(total-winner)
                
        if num_polls > 0:
            data['values'].append( dict(label=party.abbr, value=num_piska/num_polls) )




    return render_template("/figures/partipiskan.html",
                            header_figures_class='active',
                            header_partipiskan_class='active',
                            data = data)

