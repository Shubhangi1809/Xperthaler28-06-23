# Function to check parameter is present in api call or missing
def getparameter(request, param_name):
    param_value = request.data.get(param_name)
    if param_value is None or param_value == '':
        raise ValueError
    else:
        return param_value