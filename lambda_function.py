import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_core.dispatch_components import AbstractResponseInterceptor
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

import util

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RecordColorApiHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return util.isApiRequest(handler_input, 'RecordColor')

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # First get our request entity and grab the color passed in the API call
        args = util.getApiArguments(handler_input)
        color = args['color']

        # Store the favorite color in the session
        sessionAttributes = handler_input.attributes_manager.session_attributes
        sessionAttributes['favoriteColor'] = color

        response = {
            "apiResponse": {
                "color": color
            }
        }

        return response

class IntroToAlexaConversationsButtonEventHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and handler_input.request_envelope.request.arguments[0] == 'SetFavoriteColor'

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.add_directive({
            "type": 'Dialog.DelegateRequest',
            "target": 'AMAZON.Conversations',
            "period": {
                "until": 'EXPLICIT_RETURN'
            },
            "updatedRequest": {
                "type": 'Dialog.InputRequest',
                "input": {
                    "name": 'SpecifyFavoriteColor',
                    "slots": {
                        "name": {
                            "name": 'color',
                            "value": handler_input.request_envelope.request.arguments[1]
                        }
                    }
                }
            }
        }).response

class GetFavoriteColorApiHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return util.isApiRequest(handler_input, 'GetFavoriteColor')

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Get the favorite color from the session
        sessionAttributes = handler_input.attributes_manager.session_attributes

        if sessionAttributes['favoriteColor']:
            color = sessionAttributes['favoriteColor']

        response = {
            "apiResponse": {
                "color" : color
            }
        }

        return response


class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can tell me your favorite color or ask me what your favorite color is. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

# *****************************************************************************
# Generic session-ended handling logging the reason received, to help debug in error cases.
# Ends Session if there is an error


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


# The intent reflector is used for interaction model testing and debugging.
# It will simply repeat the intent the user said. You can create custom handlers
# for your intents by defining them above, then also adding them to the request
# handler chain below.
class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


# *****************************************************************************
# These simple interceptors just log the incoming and outgoing request bodies to assist in debugging.

class LoggingRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        print("Request received: {}".format(handler_input.request_envelope.request))


class LoggingResponseInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        print("Response generated: {}".format(response))


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.
sb = SkillBuilder()

# register request / intent handlers
sb.add_request_handler(RecordColorApiHandler())
sb.add_request_handler(GetFavoriteColorApiHandler())
sb.add_request_handler(IntroToAlexaConversationsButtonEventHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

# register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# register interceptors
sb.add_global_request_interceptor(LoggingRequestInterceptor())
sb.add_global_response_interceptor(LoggingResponseInterceptor())

lambda_handler = sb.lambda_handler()