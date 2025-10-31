import random

class UserAgentRotationMiddleware(object):
    """
    This middleware rotates the User-Agent for each request to make
    the scraper look more like different human users.
    """
    # A list of common User-Agents to choose from
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    ]

    def process_request(self, request, spider):
        """
        This method is called for each request being sent.
        It randomly selects a User-Agent from the list and assigns it to the request header.
        """
        # Select a random User-Agent and assign it to the request
        user_agent = random.choice(self.USER_AGENTS)
        request.headers['User-Agent'] = user_agent
        spider.logger.info(f"Using User-Agent: {user_agent}") # Log the user agent