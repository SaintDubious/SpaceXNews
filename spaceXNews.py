from __future__ import print_function

def lambda_handler(event, context):
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
    card_title = "Welcome"
    reprompt_text = ""
    should_end_session = True
    speech_output = "You can ask me about the previous or next SpaceX launch."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_launch_info(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""

    if 'NextLast' in intent['slots']:
        next_last = intent['slots']['NextLast']['value']
    else:
        next_last = "last"

    if next_last == "next":
        speech_output = speech_for_next_launch()
    else:
        speech_output = speech_for_last_launch()

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def speech_for_next_launch():
    return speech_for_unknown_next_launch()

def speech_for_last_launch():
    return "At 1:21 a.m. Eastern Time on May 6, SpaceX successfully launched a Falcon Nine rocket. " \
           "The first stage landing attempt on the autonomous spaceport drone ship, \"Of Course I Still Love You\", " \
           "was also successful."

def speech_for_unknown_next_launch():
    return "I don't know when the next launch is. If you have some information, please send it to me at " \
           "spacex news at dubious soft dot com"

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }