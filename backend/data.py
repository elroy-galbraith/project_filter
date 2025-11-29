from models import Call

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
        category="Infrastructure: Power"
    ),
    Call(
        id="CALL-1043",
        time="14:02:38",
        audio_file="assets/call_2_calm.wav",
        transcript="The bridge at Spanish Town Road has high water levels, but traffic is still moving slowly.",
        confidence=0.88,
        pitch_avg=142,
        energy_avg=0.03,
        distress_score=22,
        is_distress=False,
        status="AUTO-LOGGED",
        location="Spanish Town Rd",
        category="Infrastructure: Roads"
    ),
    Call(
        id="CALL-1044",
        time="14:03:01",
        audio_file="assets/call_3_calm.wav",
        transcript="Water service is currently off in the Portmore area. We have been without water since this morning.",
        confidence=0.91,
        pitch_avg=128,
        energy_avg=0.025,
        distress_score=18,
        is_distress=False,
        status="AUTO-LOGGED",
        location="Portmore, St. Catherine",
        category="Infrastructure: Water"
    ),
    Call(
        id="CALL-1045",
        time="14:03:12",
        audio_file="assets/call_4_panic.wav",
        transcript="[wind/rain] ...di wata... [unintelligible] ...a mi waist... pickney dem... [crying] ...beg unnu send help now... [unintelligible]",
        confidence=0.31,
        pitch_avg=289,
        energy_avg=0.11,
        distress_score=94,
        is_distress=True,
        status="HUMAN REVIEW",
        location="Unknown - Cell Tower: Portland Parish",
        category="LIFE SAFETY"
    )
]
