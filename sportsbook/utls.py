from .models import Event
from django.utils import timezone


def get_live_sports():
    qs = Event.objects.raw('''select sport, 
        lower(sport) as lower_sport 
        from public.sportsbook_event as e 
        where e.start_time >= now() 
        group by e.sport;''')
    return qs


def get_event_qs(sport, odd_type):
    qs = Event.objects.raw('''select 
        game_id, start_time, e.home, away,
        handicap, total, e.h_score, e.a_score, og.id as ogid,
        a_line_id, a_line.price as a_line_price,
        h_line_id, h_line.price as h_line_price,
        a_sprd_id, a_sprd.price as a_sprd_price,
        h_sprd_id, h_sprd.price as h_sprd_price,
        over_id, ovr.price as over_id_price,
        under_id, undr.price as under_id_price
        from sportsbook_event as e 
        left join sportsbook_oddsgroup as og on e.game_id=og.event_id
        left join sportsbook_odds as h_sprd on og.a_sprd_id=h_sprd.odd_id
        left join sportsbook_odds as a_sprd on og.a_sprd_id=a_sprd.odd_id
        left join sportsbook_odds as h_line on og.h_line_id=h_line.odd_id
        left join sportsbook_odds as a_line on og.a_line_id=a_line.odd_id
        left join sportsbook_odds as ovr on og.over_id=ovr.odd_id
        left join sportsbook_odds as undr on og.under_id=undr.odd_id
        where e.live_status=0 and e.sport='{}' and og."type"='{}' and e.start_time >= '{}'
        order by start_time
        '''.format(sport, odd_type, timezone.now()))
    return qs


def get_featured_games():
    qs = Event.objects.raw('''select 
        game_id, start_time, e.home, away, e.sport,
        handicap, total, e.h_score, e.a_score, og.id as ogid,
        a_line_id, a_line.price as a_line_price,
        h_line_id, h_line.price as h_line_price,
        a_sprd_id, a_sprd.price as a_sprd_price,
        h_sprd_id, h_sprd.price as h_sprd_price,
        over_id, ovr.price as over_id_price,
        under_id, undr.price as under_id_price
        from sportsbook_event as e 
        left join sportsbook_oddsgroup as og on e.game_id=og.event_id
        left join sportsbook_odds as h_sprd on og.a_sprd_id=h_sprd.odd_id
        left join sportsbook_odds as a_sprd on og.a_sprd_id=a_sprd.odd_id
        left join sportsbook_odds as h_line on og.h_line_id=h_line.odd_id
        left join sportsbook_odds as a_line on og.a_line_id=a_line.odd_id
        left join sportsbook_odds as ovr on og.over_id=ovr.odd_id
        left join sportsbook_odds as undr on og.under_id=undr.odd_id
        where e.live_status=0 and e.featured=true and og."type"='Game' and e.start_time >= '{}'
        order by start_time
        '''.format(timezone.now()))
    return qs


def get_ml_gs():
    qs = Event.objects.raw('''select t.game_id, t.id, t."type",
        case when h_sprd_val < 0 then h_sprd_val * -1 else h_sprd_val end as val,
        case when h_sprd_val < 0 then t.away else t.home end as team
        from (select e.game_id, e.away, e.home, og.id, og."type",
            sum(case when bv."type"='h_line' then bv.value 
            when bv."type"='a_line' then 0 end 
            - case when bv."type"='a_line' then bv.value 
            when bv."type"='h_line' then 0 end) 
            as h_sprd_val
            from sportsbook_event as e
            left join sportsbook_oddsgroup as og on e.game_id = og.event_id
            left join betslip_betvalue as bv on og.id = bv.odd_group_id
            where og.live_status = 0 and (bv."type" = 'h_line' or bv."type"='a_line')
            group by e.game_id, og.id, e.away, e.home, og."type"
            ) as t
        order by val desc limit 10''')
    return qs


def get_total_qs():
    qs = Event.objects.raw('''select t.id, t.game_name, t.tot, t."type", t.game_id,
        case when over_val < 0 then over_val * -1 else over_val end as val,
        case when over_val < 0 then 'U' else 'O' end as ou
            from (select og.id, og."type", e.game_id,
            e.away || ' @ ' || e.home as game_name, 
            max(bv.total) as tot,
            sum(case when bv."type"='over' then bv.value 
            when bv."type"='under' then 0 end 
            - case when bv."type"='under' then bv.value 
            when bv."type"='over' then 0 end) 
            as over_val
            from sportsbook_event as e
            left join sportsbook_oddsgroup as og on e.game_id = og.event_id
            left join betslip_betvalue as bv on og.id = bv.odd_group_id
            where e.live_status = 0 and (bv."type" = 'over' or bv."type"='under')
            group by og.id, e.away, e.home, og."type", e.game_id
            ) as t
        order by val desc limit 10;''')
    return qs


def get_sprd_qs():
    qs = Event.objects.raw('''select t.id, t."type", t.game_id,
        case when ml_val < 0 then ml_val * -1 else ml_val end as val,
        case when ml_val < 0 then t.handicap * -1 else t.handicap end as handicap,
        case when ml_val < 0 then t.away else t.home end as team
        from (select og.id, e.away, e.home, og."type", e.game_id,
            MAX(bv.handicap) as handicap,
            sum(case when bv."type"='h_sprd' then bv.value 
            when bv."type"='a_sprd' then 0 end 
            - case when bv."type"='a_sprd' then bv.value 
            when bv."type"='h_sprd' then 0 end) 
            as ml_val
            from sportsbook_event as e
            left join sportsbook_oddsgroup as og on e.game_id = og.event_id
            left join betslip_betvalue as bv on og.id = bv.odd_group_id
            where bv.status = 0 and (bv."type" = 'h_sprd' or bv."type"='a_sprd')
            group by og.id, e,game_id, e.home, e,away, og."type"
            ) as t
        order by val desc limit 10''')
    return qs
