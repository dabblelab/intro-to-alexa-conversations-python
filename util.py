import logging
from ask_sdk_core.handler_input import HandlerInput
import ask_sdk_core.utils as ask_utils

"""
Helper method to find if a request is for a certain apiName.
"""
def isApiRequest(handler_input, api_name):
    try:
        return ask_utils.request_util.get_request_type(handler_input) == 'Dialog.API.Invoked' and handler_input.request_envelope.request.apiRequest.name == api_name
    except Exception as ex:
        logging.error(ex)
        return False


"""
Helper method to get API arguments from the request envelope.
"""
def getApiArguments(handler_input):
    try:
        return handler_input.request_envelope.request.apiRequest.arguments
    except Exception as ex:
        logging.error(ex)
        return False


"""
Helper method to get API slots from the request envelope.
"""
def getApiSlots(handler_input):
    try:
        return handler_input.request_envelope.request.apiRequest.slots
    except Exception as ex:
        logging.error(ex)
        return False