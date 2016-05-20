from __future__ import print_function

def main(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
         "amzn1.echo-sdk-ams.app.cf87f5fa-e41b-47f1-b0ad-cf610e2d090a"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    print("on_intent intent_name=" + intent_name )

    # Dispatch to your skill's intent handlers
    if intent_name == "GetLaunchInfo":
        return get_launch_info(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    speech_output = "I know a little bit about the SpaceX launch schedule. " \
    "Are you interested in the next launch, or the last one?"
    return build_response(session_attributes, build_speechlet_response(
        False, speech_output, speech_output))

def handle_session_end_request():
    session_attributes = {}
    speech_output = "Good Bye."
    return build_response(session_attributes, build_speechlet_response(
        True, speech_output, speech_output))

def get_launch_info(intent, session):
    card_title = intent['name']
    session_attributes = {}

    if 'NextLast' in intent['slots']:
        next_last = intent['slots']['NextLast']['value'].lower()
    else:
        next_last = "last"

    if (next_last == "next" or next_last == "coming" or next_last == "upcoming" or
        next_last == "imminent" or next_last == "ensuing" or next_last == "following" or
        next_last == "subsequent" or next_last == "future" or next_last == "impending" or
        next_last == "later"):
        speech_output = speech_for_next_launch()
        card_text = card_text_for_next_launch()
    elif (next_last == "last" or next_last == "previous" or next_last == "past" or
          next_last == "preceding" or next_last == "earlier" or next_last == "prior"):
        speech_output = speech_for_last_launch()
        card_text = card_text_for_last_launch()
    else:
        raise ValueError("Invalid next or last modifier: " + next_last)

    return build_response(session_attributes, build_speechlet_response(
        True, speech_output, card_text))

def speech_for_next_launch():
    return speech_for_unknown_next_launch()

def card_text_for_next_launch():
    return card_text_for_unknown_next_launch()

def speech_for_last_launch():
    return "At 1:21 a.m. Eastern Time on May 6, SpaceX successfully launched a Falcon Nine rocket. " \
           "The first stage landing attempt on the autonomous spaceport drone ship, the \"Of Course I Still Love You\", " \
           "was also successful."

def card_text_for_last_launch():
    return speech_for_last_launch()

def speech_for_unknown_next_launch():
    return "I don't know when the next launch is. If you have some information, please send it to me at " \
           "spacex info at dubious soft dot com"

def card_text_for_unknown_next_launch():
    return "I don't know when the next launch is. If you have some information, please send it to me at " \
           "spacexinfo@dubiousoft.com"

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(shouldEnd, output, card_text):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SpaceX Info',
            'content': card_text
        },
        'shouldEndSession': shouldEnd
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    
