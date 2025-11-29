from models import Call, NLPExtraction

CALL_LOG = [
    Call(
        id="CALL-1042",
        time="14:02:15",
        audio_file="assets/call_1_calm.wav",
        transcript="Reporting a downed utility pole on Nelson Street. It is blocking the main entrance to the hospital.",
        confidence=0.92,
        pitch_avg=135,
        energy_avg=0.02,
        distress_score=15,
        is_distress=False,
        status="AUTO-LOGGED",
        location="Nelson St, Kingston",
        category="Infrastructure: Power",
        lat=18.0179,
        lng=-77.7919,
        nlp_extraction=NLPExtraction(
            location="Main road, Black River",
            landmark="Hospital entrance",
            hazard_type="Downed utility pole",
            blocked_access="Yes - hospital",
            people_count=None,
            resource_need="JPS / Line clearance crew"
        )
    ),
    Call(
        id="CALL-1043",
        time="14:02:38",
        audio_file="assets/call_2_calm.wav",
        transcript="The bridge at Santa Cruz has high water levels. Traffic is not moving. The road is impassable.",
        confidence=0.88,
        pitch_avg=142,
        energy_avg=0.03,
        distress_score=22,
        is_distress=False,
        status="AUTO-LOGGED",
        location="Santa Cruz, St. Elizabeth",
        category="Infrastructure: Roads",
        lat=18.0891,
        lng=-77.8513,
        nlp_extraction=NLPExtraction(
            location="Santa Cruz Bridge",
            landmark=None,
            hazard_type="Flooding - road impassable",
            blocked_access="Yes - bridge",
            people_count=None,
            resource_need="Traffic diversion / NWA alert"
        )
    ),
    Call(
        id="CALL-1044",
        time="14:03:01",
        audio_file="assets/call_3_calm.wav",
        transcript="Water service is currently off in the Savanna-la-Mar area. We have been without water since the storm passed.",
        confidence=0.91,
        pitch_avg=128,
        energy_avg=0.025,
        distress_score=18,
        is_distress=False,
        status="AUTO-LOGGED",
        location="Savanna-la-Mar, Westmoreland",
        category="Infrastructure: Water",
        lat=18.2194,
        lng=-78.1333,
        nlp_extraction=NLPExtraction(
            location="Savanna-la-Mar (area-wide)",
            landmark=None,
            hazard_type="Water service outage",
            blocked_access=None,
            people_count="Area-wide impact",
            resource_need="NWC restoration crew"
        )
    ),
    Call(
        id="CALL-1045",
        time="14:03:12",
        audio_file="assets/call_4_panic.wav",
        transcript="[wind/rain] ...di wata... [unintelligible] ...a mi waist... pickney dem... [crying] ...five a wi pan di roof... beg unnu send help now... [unintelligible]",
        confidence=0.31,
        pitch_avg=289,
        energy_avg=0.11,
        distress_score=94,
        is_distress=True,
        status="HUMAN REVIEW",
        location="Unknown - Cell Tower: New Hope, St. Elizabeth",
        category="LIFE SAFETY",
        lat=18.0567,
        lng=-77.8234,
        nlp_extraction=NLPExtraction(
            location="Rooftop (Cell tower: New Hope)",
            landmark=None,
            hazard_type="Flood - Rising water",
            blocked_access="Trapped - cannot move",
            people_count="5 (includes children)",
            resource_need="IMMEDIATE EVACUATION - Boat/Helicopter"
        )
    )
]
