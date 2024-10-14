from utils.exception import MyError


class LocalServiceConnector:

    @staticmethod
    def invoke_local_function(function, function_input: dict):
        """
        Method to invoke the local function
        Args:
            function (Callable): The local function to be invoked
            function_input (str): The input to pass to the function
        Returns:
            The output of the invoked function
        Raises:
            MyError: if the function cannot be invoked
        """
        try:
            # Invoking the local function with the provided input
            return function(function_input)
        except Exception as e:
            raise MyError(error_code=500, error_message=f"Error invoking function: {str(e)}")
