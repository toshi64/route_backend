from threading import Thread
from daily_material.services import generate_curriculum_from_final_analysis

def trigger_curriculum_generation(session_id: int):
    thread = Thread(target=generate_curriculum_from_final_analysis, args=(session_id,))
    thread.start()
