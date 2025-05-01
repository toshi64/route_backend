from ..models import SurveyResponse, Session

def save_survey_response(data, user):
    session_id = data.get('session_id')
    if not session_id:
        return {'status': 'error', 'message': 'session_id is required.'}

    try:
        session = Session.objects.get(session_id=session_id, user=user)
    except Session.DoesNotExist:
        return {'status': 'error', 'message': 'Session not found for this user.'}

    survey = SurveyResponse.objects.create(
        user=user,
        session=session,
        question_1=data.get('question_1', ''),
        answer_1=data.get('answer_1', ''),
        question_2=data.get('question_2', ''),
        answer_2=data.get('answer_2', ''),
        question_3=data.get('question_3', ''),
        answer_3=data.get('answer_3', ''),
        question_4=data.get('question_4', ''),
        answer_4=data.get('answer_4', ''),
        question_5=data.get('question_5', ''),
        answer_5=data.get('answer_5', ''),
        question_6=data.get('question_6', ''),
        answer_6=data.get('answer_6', ''),
    )

    return {
        'status': 'success',
        'survey_id': survey.id,
        'message': 'Survey response saved successfully.'
    }
