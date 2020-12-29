### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")

def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response

### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """
    # Gets slots' values
    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    
    # Gets the invocation source, for Lex dialogs "DialogCodeHook" is expected.
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # for the first violation detected.
        
        ### YOUR DATA VALIDATION CODE STARTS HERE
        
        #Get all slots
        slots = get_slots(intent_request)

        # Validate user's input using the validate_data function
        validation_result = validate_data(age, investment_amount)
        
        # Use the elicitSlot dialog action to re-prompt
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None 
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )
        
        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    
    initial_recommendation = get_investment_recommendation(risk_level)
    
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} Thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )

### Data Validation ###
def validate_data(age, investment_amount):
    age = parse_int(age)
    investment_amount = parse_int(investment_amount)
    # Validate user age data, should be between 1 and 64
    if age is None:
        return build_validation_result(
            False,
            "age",
            "You must provide your age to use this service. "
            "Please provide your age."
        )
    elif age <= 0:
        age = relativedelta(datetime.now()).years
        return build_validation_result(
            False,
            'age',
            "You must be at least 1 years old to use this service. "
            "Please provide a different age.")
    elif age >= 65:
        return build_validation_result(
            False,
            "age",
            "To use this service, you must not be 65 and older. "
            "Please provide a different age.")
    # Validate user investment amount data, should be > 5000
    elif investment_amount is None:
        return build_validation_result(
            False,
            "investmentAmount",
            "The investment amount should be equal to or greater than 5000. "
            "Please provide an investment amount.")
    elif investment_amount < 5000:
        return build_validation_result(
            False,
            "investmentAmount",
            "The investment amount should be equal to or greater than 5000. "
            "Please provide a different investment amount.")
    
    # True results are returned if age and investment amount are valid
    return build_validation_result(True, None, None)

def get_investment_recommendation(risk_level):
    
    if risk_level == None:
        return "100% bonds (AGG), 0% equities (SPY)",
    elif risk_level == "Very Low":
        return "80% bonds (AGG), 20% equities (SPY)",
    elif risk_level == "Low":
        return "60% bonds (AGG), 40% equities (SPY)"
    elif risk_level == "Medium":
        return "40% bonds (AGG), 60% equities (SPY)"
    elif risk_level == "High":
        return "20% bonds (AGG), 80% equities (SPY)"
    elif risk_level == "Very High":
        return "0% bonds (AGG), 100% equities (SPY)"
    else:
        return None


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)